#!/usr/bin/env python3
"""Convierte entradas con formato: redmine (Textile) a Markdown.
Uso: python3 scripts/redmine2md.py content
"""
import re, sys, pathlib

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
            para.append(inline(lines[i].strip()))
            i += 1
        if not para:
            m = RE_P.match(s)
            para = [inline(m.group(1))] if m else [inline(s)]
            i += 1
        out += ["  \n".join(para), ""]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(out)).strip() + "\n"

def process(path):
    txt = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", txt, re.S)
    if not m:
        return False
    fm, body = m.group(1), m.group(2)
    if not re.search(r"^formato:\s*['\"]?redmine['\"]?\s*$", fm, re.M):
        return False
    t = re.search(r"^title:\s*(.*)$", fm, re.M)
    title = t.group(1).strip().strip("'\"") if t else ""
    fm = re.sub(r"^(\s*-\s*)(['\"]?)#+\s*", r"\1\2", fm, flags=re.M)
    fm = re.sub(r"^formato:.*$", "formato: markdown", fm, flags=re.M)
    path.write_text("---\n" + fm + "\n---\n\n" + convert(body, title), encoding="utf-8")
    return True

if __name__ == "__main__":
    root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "content")
    n = 0
    for p in root.rglob("*.md"):
        if p.name != "_index.md" and process(p):
            print("Convertido:", p)
            n += 1
    print("Total:", n)
