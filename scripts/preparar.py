#!/usr/bin/env python3
"""Prepara el contenido antes de construir la web (se ejecuta en GitHub Actions y en el instalador).

Carpeta `subir/`:
  subir/entradas, subir/htb, subir/tryhackme  -> archivos .md / .markdown / .txt / .textile (Redmine)
  subir/imagenes                              -> imagenes (se copian a static/img)
Para cada archivo: crea la cabecera si falta (titulo, fecha, descripcion), convierte Redmine/Textile a
Markdown, enlaza las imagenes por nombre y usa como portada la imagen con el mismo nombre que el archivo.
Ademas quita la barra inicial de cover.image en todo el contenido (para que funcione con subcarpeta).
"""
import re, sys, os, json, shutil, subprocess, unicodedata, datetime, pathlib

FENCE = "`" * 3

def norm(s):
    return re.sub(r"\W+", "", s).lower()

def inline(t):
    codes = []
    def keep(m):
        codes.append(m.group(1))
        return "\x00%d\x00" % (len(codes) - 1)
    t = re.sub(r"<code>(.*?)</code>", keep, t)
    t = re.sub(r"(?<![\w@])@(?=\S)([^@\n]+?)(?<=\S)@(?![\w@])", keep, t)
    t = re.sub(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]", lambda m: m.group(2) or m.group(1), t)
    t = re.sub(r"!(?!\s)([\w./:%?&=#~-]+\.(?:png|jpe?g|gif|svg|webp))(?:\(([^)]*)\))?!",
               lambda m: "![%s](%s)" % (m.group(2) or "", m.group(1)), t)
    def link(m):
        text, url = m.group(1), m.group(2)
        tail = ""
        while url and url[-1] in ".,;:!?)":
            tail = url[-1] + tail
            url = url[:-1]
        return "[%s](%s)%s" % (text, url, tail)
    t = re.sub(r'"([^"\n]+)":(\S+)', link, t)
    t = re.sub(r"%\{[^}]*\}([^%\n]*)%", r"\1", t)
    t = re.sub(r"(?<![\w*])\*(?!\s)([^*\n]+?)(?<!\s)\*(?![\w*])", r"**\1**", t)
    def restore(m):
        c = codes[int(m.group(1))]
        return ("`` %s ``" % c) if "`" in c else "`%s`" % c
    return re.sub(r"\x00(\d+)\x00", restore, t)

def fence(lines, lang=""):
    lines = list(lines)
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    nonblank = [l for l in lines if l.strip()]
    if len(nonblank) > 1 and len(lines) - len(nonblank) >= len(nonblank) - 1:
        lines = nonblank
    lines = [l.replace("\u201c", '"').replace("\u201d", '"').replace("\u2018", "'").replace("\u2019", "'")
             .replace("\u2013", "--").replace("\u00a0", " ").rstrip() for l in lines]
    return [FENCE + lang] + lines + [FENCE, ""]

RE_H = re.compile(r"^h([1-6])(?:\([^)]*\)|\{[^}]*\}|[<>=])*\.\s+(.*)$")
RE_P = re.compile(r"^p(?:\([^)]*\)|\{[^}]*\}|[<>=])*\.\s+(.*)$")
RE_BQ = re.compile(r"^bq\.\s+(.*)$")
RE_BC = re.compile(r"^(?:bc|pre)\.(\.?)\s*(.*)$")
RE_LI = re.compile(r"^([*#]+)\s+(.*)$")
RE_TB = re.compile(r"^\|.*\|\s*$")
RE_TOC = re.compile(r"^\{\{>?toc\}\}\s*$")
RE_HR = re.compile(r"^-{3,}\s*$")

def is_block(l):
    s = l.strip()
    return (not s or RE_H.match(l) or RE_P.match(l) or RE_BQ.match(l) or RE_BC.match(l)
            or RE_LI.match(l) or RE_TB.match(l) or RE_TOC.match(l) or RE_HR.match(s)
            or s.startswith("<pre") or s.startswith(FENCE) or s.startswith("<notextile"))

def cells(row):
    row = row.strip().strip("|")
    out = []
    for c in row.split("|"):
        c = re.sub(r"^(?:[_<>=~^]|\\\d+|/\d+|\([^)]*\)|\{[^}]*\})+\.\s*", "", c.strip())
        out.append(inline(c.strip()))
    return out

def convert(body, title):
    lines = body.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    out, i, first_h1 = [], 0, False
    while i < len(lines):
        l = lines[i]
        s = l.strip()
        if not s or RE_TOC.match(s) or s.startswith(("<notextile", "</notextile")):
            i += 1
            continue
        if s.startswith("<pre"):
            m = re.search(r'class="([\w+-]+)"', s)
            lang = m.group(1) if m else ""
            buf = []
            first = re.sub(r"^<pre[^>]*>\s*(<code[^>]*>)?", "", s)
            while True:
                if "</pre>" in first:
                    first = re.sub(r"(</code>)?\s*</pre>.*$", "", first)
                    buf.append(first)
                    break
                buf.append(first)
                i += 1
                if i >= len(lines):
                    break
                first = lines[i]
            out += fence([b for b in buf], lang)
            i += 1
            continue
        if s.startswith(FENCE):
            lang = s[3:].strip()
            buf = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith(FENCE):
                buf.append(lines[i])
                i += 1
            out += fence(buf, lang)
            i += 1
            continue
        m = RE_BC.match(s)
        if m:
            extended, first = m.group(1) == ".", m.group(2)
            buf = [first] if first else []
            i += 1
            while i < len(lines):
                if extended:
                    if re.match(r"^(p|h[1-6]|bq|bc|pre)[^\s]*\.\s", lines[i]):
                        break
                elif not lines[i].strip():
                    break
                buf.append(lines[i])
                i += 1
            out += fence(buf)
            continue
        m = RE_H.match(s)
        if m:
            n, text = int(m.group(1)), m.group(2).strip()
            if n == 1 and not first_h1 and norm(text) == norm(title):
                first_h1 = True
            else:
                out += ["#" * max(n, 2) + " " + inline(text), ""]
            i += 1
            continue
        m = RE_BQ.match(s)
        if m:
            out += ["> " + inline(m.group(1)), ""]
            i += 1
            continue
        if RE_TB.match(s):
            rows = []
            while i < len(lines) and RE_TB.match(lines[i].strip()):
                rows.append(cells(lines[i]))
                i += 1
            w = max(len(r) for r in rows)
            rows = [r + [""] * (w - len(r)) for r in rows]
            out.append("| " + " | ".join(rows[0]) + " |")
            out.append("|" + " --- |" * w)
            for r in rows[1:]:
                out.append("| " + " | ".join(r) + " |")
            out.append("")
            continue
        if RE_LI.match(s):
            prev_top = None
            while i < len(lines) and RE_LI.match(lines[i].strip()):
                m = RE_LI.match(lines[i].strip())
                marks, text = m.group(1), m.group(2)
                mk = "1." if marks[-1] == "#" else "-"
                if len(marks) == 1:
                    if prev_top is not None and prev_top != mk:
                        out.append("")
                    prev_top = mk
                out.append("    " * (len(marks) - 1) + mk + " " + inline(text))
                i += 1
            out.append("")
            continue
        if RE_HR.match(s):
            out += ["---", ""]
            i += 1
            continue
        para = []
        while i < len(lines) and not is_block(lines[i]):
            t = lines[i].strip()
            para.append(inline(t))
            i += 1
        if not para:
            m = RE_P.match(s)
            para = [inline(m.group(1))] if m else [inline(s)]
            i += 1
        out += ["  \n".join(para), ""]
        continue
    return re.sub(r"\n{3,}", "\n\n", "\n".join(out)).strip() + "\n"


DESTINOS = {
    "entradas": "content/entradas",
    "htb": "content/writeups/htb",
    "tryhackme": "content/writeups/tryhackme",
}
EXT_TEXTO = {".md", ".markdown", ".txt", ".textile"}
EXT_IMG = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}

def slugify(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-").lower() or "entrada"

def safe_img(name):
    base, ext = os.path.splitext(name)
    return slugify(base) + ext.lower()

def es_textile(texto, ext):
    if ext == ".textile":
        return True
    t = len(re.findall(r"^(?:h[1-6]\.\s|bc\.\.?\s|bq\.\s)|<pre[ >]|^\|_\.", texto, re.M))
    m = len(re.findall(r"^#{1,6}\s", texto, re.M)) + len(re.findall(r"^" + FENCE, texto, re.M))
    return t > 0 and t >= m

def trocear(texto):
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", texto, re.S)
    if m:
        return m.group(1), m.group(2)
    return None, texto

def fecha_git(path):
    try:
        out = subprocess.run(["git", "log", "--diff-filter=A", "--format=%aI", "--", str(path)],
                             capture_output=True, text=True, timeout=20).stdout.strip().splitlines()
        if out:
            return out[-1]
    except Exception:
        pass
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")

def texto_plano(md):
    md = re.sub(FENCE + r".*?" + FENCE, " ", md, flags=re.S)
    md = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", md)
    md = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", md)
    md = re.sub(r"^#{1,6}.*$", " ", md, flags=re.M)
    md = re.sub(r"^[>\-\*\d\.\s]+", "", md, flags=re.M)
    md = re.sub(r"[`*_|]", "", md)
    return re.sub(r"\s+", " ", md).strip()

def procesar_archivo(path, destino, imagenes):
    ext = path.suffix.lower()
    texto = path.read_text(encoding="utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")
    fm, body = trocear(texto)
    fm = fm or ""

    titulo = None
    t = re.search(r"^title:\s*(.*)$", fm, re.M)
    if t:
        titulo = t.group(1).strip().strip("'\"")
    if not titulo:
        h = re.search(r"^(?:h1\.\s+|#\s+)(.+)$", body, re.M)
        titulo = h.group(1).strip() if h else path.stem.replace("-", " ").replace("_", " ").strip().capitalize()

    textile = es_textile(body, ext)
    if textile:
        body = convert(body, titulo)
    else:
        lineas = body.split("\n")
        for i, l in enumerate(lineas):
            if l.strip():
                m = re.match(r"^#\s+(.+)$", l)
                if m and norm(m.group(1)) == norm(titulo):
                    lineas.pop(i)
                break
        # el titulo ya lo pone la plantilla: cualquier otro "# " pasa a "## "
        dentro = False
        for i, l in enumerate(lineas):
            if l.lstrip().startswith(FENCE) or l.lstrip().startswith("~~~"):
                dentro = not dentro
            elif not dentro and re.match(r"^#\s+\S", l):
                lineas[i] = "#" + l
        body = "\n".join(lineas).strip() + "\n"

    # imagenes por nombre -> /img/nombre-seguro
    def enlace(m):
        alt, url = m.group(1), m.group(2).strip()
        nombre = os.path.basename(url.split("?")[0]).lower()
        if "://" not in url and not url.startswith("/") or url.startswith("./") or url.startswith("imagenes/"):
            if nombre in imagenes:
                return "![%s](/img/%s)" % (alt, imagenes[nombre])
        return m.group(0)
    body = re.sub(r"!\[([^\]]*)\]\(([^)\s]+)\)", enlace, body)

    nuevos = []
    if not re.search(r"^title:", fm, re.M):
        nuevos.append("title: " + json.dumps(titulo, ensure_ascii=False))
    if not re.search(r"^date:", fm, re.M):
        nuevos.append("date: " + fecha_git(path))
    if not re.search(r"^description:", fm, re.M):
        d = texto_plano(body)[:160].rsplit(" ", 1)[0] if len(texto_plano(body)) > 160 else texto_plano(body)
        nuevos.append("description: " + json.dumps(d, ensure_ascii=False))
    if not re.search(r"^cover:", fm, re.M):
        stem = norm(path.stem)
        for orig, seguro in imagenes.items():
            if norm(os.path.splitext(orig)[0]) == stem:
                nuevos.append('cover:\n  image: "img/%s"\n  alt: %s' % (seguro, json.dumps(titulo, ensure_ascii=False)))
                break
    fm_final = "\n".join([x for x in [fm.strip("\n")] + nuevos if x])
    slug = slugify(path.stem)
    salida = pathlib.Path(destino) / (slug + ".md")
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text("---\n" + fm_final + "\n---\n\n" + body, encoding="utf-8")
    return salida, ("Redmine" if textile else "Markdown")

def quitar_barra_portada(raiz):
    n = 0
    for p in pathlib.Path(raiz).rglob("*.md"):
        t = p.read_text(encoding="utf-8")
        nt = re.sub(r"^([ \t]+image:[ \t]*[\"']?)/", r"\1", t, flags=re.M)
        if nt != t:
            p.write_text(nt, encoding="utf-8")
            n += 1
    return n

def main():
    raiz = pathlib.Path("subir")
    imagenes = {}
    carpeta_img = raiz / "imagenes"
    if carpeta_img.is_dir():
        os.makedirs("static/img", exist_ok=True)
        for f in sorted(carpeta_img.iterdir()):
            if f.is_file() and f.suffix.lower() in EXT_IMG:
                seguro = safe_img(f.name)
                shutil.copy(f, pathlib.Path("static/img") / seguro)
                imagenes[f.name.lower()] = seguro
    total = 0
    for sub, destino in DESTINOS.items():
        carpeta = raiz / sub
        if not carpeta.is_dir():
            continue
        for f in sorted(carpeta.iterdir()):
            if f.is_file() and f.suffix.lower() in EXT_TEXTO and f.name.lower() not in ("readme.md", "leeme.md"):
                try:
                    salida, formato = procesar_archivo(f, destino, imagenes)
                    print("  %-9s %-10s -> %s" % (sub, formato, salida))
                    total += 1
                except Exception as e:
                    print("  AVISO: no he podido procesar %s: %s" % (f, e))
    n = quitar_barra_portada("content")
    print("Preparado: %d archivo(s) de subir/, %d imagen(es), %d portada(s) ajustada(s)." % (total, len(imagenes), n))

if __name__ == "__main__":
    main()
