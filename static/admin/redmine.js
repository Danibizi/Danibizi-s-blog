(function (root) {
  var F = "`".repeat(3);
  function norm(s) { return s.replace(/\W+/g, "").toLowerCase(); }

  function inline(t) {
    var codes = [];
    function keep(m, c) { codes.push(c); return "\u0000" + (codes.length - 1) + "\u0000"; }
    t = t.replace(/<code>(.*?)<\/code>/g, keep);
    t = t.replace(/(^|[^\w@])@(?=\S)([^@\n]+?)(?<=\S)@(?![\w@])/g, function (m, pre, c) {
      return pre + keep(m, c);
    });
    t = t.replace(/\[\[([^\]|]+)(?:\|([^\]]+))?\]\]/g, function (m, a, b) { return b || a; });
    t = t.replace(/!(?!\s)([\w./:%?&=#~-]+\.(?:png|jpe?g|gif|svg|webp))(?:\(([^)]*)\))?!/g,
      function (m, u, alt) { return "![" + (alt || "") + "](" + u + ")"; });
    t = t.replace(/"([^"\n]+)":(\S+)/g, function (m, text, url) {
      var tail = "";
      while (url && ".,;:!?)".indexOf(url[url.length - 1]) >= 0) { tail = url[url.length - 1] + tail; url = url.slice(0, -1); }
      return "[" + text + "](" + url + ")" + tail;
    });
    t = t.replace(/%\{[^}]*\}([^%\n]*)%/g, "$1");
    t = t.replace(/(^|[^\w*])\*(?!\s)([^*\n]+?)(?<!\s)\*(?![\w*])/g, "$1**$2**");
    return t.replace(/\u0000(\d+)\u0000/g, function (m, i) {
      var c = codes[+i];
      return c.indexOf("`") >= 0 ? "`` " + c + " ``" : "`" + c + "`";
    });
  }

  function fence(lines, lang) {
    lines = lines.slice();
    while (lines.length && !lines[0].trim()) lines.shift();
    while (lines.length && !lines[lines.length - 1].trim()) lines.pop();
    var nb = lines.filter(function (l) { return l.trim(); });
    var blanks = lines.length - nb.length;
    if (nb.length > 1 && blanks >= 0.6 * (nb.length - 1) && blanks > 0) lines = nb;
    lines = lines.map(function (l) {
      return l.replace(/\u201c|\u201d/g, '"').replace(/\u2018|\u2019/g, "'").replace(/\u2013/g, "--").replace(/\u00a0/g, " ").replace(/\s+$/, "");
    });
    return [F + (lang || "")].concat(lines, [F, ""]);
  }

  var RE_H = /^h([1-6])(?:\([^)]*\)|\{[^}]*\}|[<>=])*\.\s+(.*)$/;
  var RE_P = /^p(?:\([^)]*\)|\{[^}]*\}|[<>=])*\.\s+(.*)$/;
  var RE_BQ = /^bq\.\s+(.*)$/;
  var RE_BC = /^(?:bc|pre)\.(\.?)\s*(.*)$/;
  var RE_LI = /^([*#]+)\s+(.*)$/;
  var RE_TB = /^\|.*\|\s*$/;
  var RE_TOC = /^\{\{>?toc\}\}\s*$/;
  var RE_HR = /^-{3,}\s*$/;

  function isBlock(l) {
    var s = l.trim();
    return !s || RE_H.test(l) || RE_P.test(l) || RE_BQ.test(l) || RE_BC.test(l) || RE_LI.test(l) ||
      RE_TB.test(l) || RE_TOC.test(l) || RE_HR.test(s) || s.indexOf("<pre") === 0 ||
      s.indexOf(F) === 0 || s.indexOf("<notextile") === 0;
  }

  function cells(row) {
    row = row.trim().replace(/^\|/, "").replace(/\|$/, "");
    return row.split("|").map(function (c) {
      c = c.trim().replace(/^(?:[_<>=~^]|\\\d+|\/\d+|\([^)]*\)|\{[^}]*\})+\.\s*/, "");
      return inline(c.trim());
    });
  }

  function convert(body, title) {
    var lines = String(body || "").replace(/\r\n?/g, "\n").split("\n");
    var out = [], i = 0, firstH1 = false;
    while (i < lines.length) {
      var l = lines[i], s = l.trim(), m;
      if (!s || RE_TOC.test(s) || s.indexOf("<notextile") === 0 || s.indexOf("</notextile") === 0) { i++; continue; }
      if (s.indexOf("<pre") === 0) {
        var cm = s.match(/class="([\w+-]+)"/);
        var lang = cm ? cm[1] : "";
        var buf = [];
        var first = s.replace(/^<pre[^>]*>\s*(<code[^>]*>)?/, "");
        while (true) {
          if (first.indexOf("</pre>") >= 0) {
            first = first.replace(/(<\/code>)?\s*<\/pre>.*$/, "");
            buf.push(first);
            break;
          }
          buf.push(first);
          i++;
          if (i >= lines.length) break;
          first = lines[i];
        }
        out = out.concat(fence(buf, lang));
        i++;
        continue;
      }
      if (s.indexOf(F) === 0) {
        var lg = s.slice(3).trim(), b2 = [];
        i++;
        while (i < lines.length && lines[i].trim().indexOf(F) !== 0) { b2.push(lines[i]); i++; }
        out = out.concat(fence(b2, lg));
        i++;
        continue;
      }
      if ((m = s.match(RE_BC))) {
        var ext = m[1] === ".", b3 = m[2] ? [m[2]] : [];
        i++;
        while (i < lines.length) {
          if (ext) { if (/^(p|h[1-6]|bq|bc|pre)[^\s]*\.\s/.test(lines[i])) break; }
          else if (!lines[i].trim()) break;
          b3.push(lines[i]);
          i++;
        }
        out = out.concat(fence(b3, ""));
        continue;
      }
      if ((m = s.match(RE_H))) {
        var n = parseInt(m[1], 10), text = m[2].trim();
        if (n === 1 && !firstH1 && norm(text) === norm(title || "")) firstH1 = true;
        else { out.push("#".repeat(Math.max(n, 2)) + " " + inline(text)); out.push(""); }
        i++;
        continue;
      }
      if ((m = s.match(RE_BQ))) { out.push("> " + inline(m[1])); out.push(""); i++; continue; }
      if (RE_TB.test(s)) {
        var rows = [];
        while (i < lines.length && RE_TB.test(lines[i].trim())) { rows.push(cells(lines[i])); i++; }
        var w = Math.max.apply(null, rows.map(function (r) { return r.length; }));
        rows = rows.map(function (r) { while (r.length < w) r.push(""); return r; });
        out.push("| " + rows[0].join(" | ") + " |");
        out.push("|" + " --- |".repeat(w));
        rows.slice(1).forEach(function (r) { out.push("| " + r.join(" | ") + " |"); });
        out.push("");
        continue;
      }
      if (RE_LI.test(s)) {
        var prevTop = null;
        while (i < lines.length && RE_LI.test(lines[i].trim())) {
          var lm = lines[i].trim().match(RE_LI);
          var marks = lm[1], mk = marks[marks.length - 1] === "#" ? "1." : "-";
          if (marks.length === 1) {
            if (prevTop !== null && prevTop !== mk) out.push("");
            prevTop = mk;
          }
          out.push("    ".repeat(marks.length - 1) + mk + " " + inline(lm[2]));
          i++;
        }
        out.push("");
        continue;
      }
      if (RE_HR.test(s)) { out.push("---"); out.push(""); i++; continue; }
      var para = [];
      while (i < lines.length && !isBlock(lines[i])) { para.push(inline(lines[i].trim())); i++; }
      if (!para.length) {
        var pm = s.match(RE_P);
        para = [inline(pm ? pm[1] : s)];
        i++;
      }
      out.push(para.join("  \n"));
      out.push("");
    }
    return out.join("\n").replace(/\n{3,}/g, "\n\n").trim() + "\n";
  }

  root.redmineToMarkdown = convert;
  if (typeof module !== "undefined") module.exports = convert;
})(typeof window !== "undefined" ? window : globalThis);
