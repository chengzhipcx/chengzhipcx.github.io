# -*- coding: utf-8 -*-
"""给章节 PPT 页面注入代码块复制按钮（CSS + JS，幂等）"""
import glob
import io

CSS_MARKER = "/* 代码复制按钮 */"
JS_MARKER = "// 代码复制按钮"

COPY_CSS = """
    /* 代码复制按钮 */
    pre, .slide-content .code, .code-block { position: relative; }
    .code-copy-btn {
      position: absolute; top: 8px; right: 8px; z-index: 5;
      padding: 4px 10px; font-size: 12px; font-family: inherit;
      color: #d4d4d4; background: rgba(255,255,255,0.12);
      border: 1px solid rgba(255,255,255,0.25); border-radius: 4px;
      cursor: pointer; opacity: 0.75; transition: all 0.2s;
    }
    .code-copy-btn:hover { opacity: 1; background: rgba(255,255,255,0.22); }
    .code-copy-btn.copied { color: #4ade80; border-color: #4ade80; }
"""

COPY_JS = """
<script>
// 代码复制按钮
document.addEventListener('DOMContentLoaded', function () {
  var blocks = document.querySelectorAll('pre, div.code, div.code-block');
  blocks.forEach(function (block) {
    if (block.querySelector('.code-copy-btn')) return;
    var btn = document.createElement('button');
    btn.className = 'code-copy-btn';
    btn.type = 'button';
    btn.textContent = '复制';
    btn.addEventListener('click', function () {
      var clone = block.cloneNode(true);
      var b = clone.querySelector('.code-copy-btn');
      if (b) b.remove();
      var text = clone.textContent
        .replace(/\\u00a0/g, ' ')
        .replace(/[ \\t]+\\n/g, '\\n')
        .replace(/\\s+$/, '');
      function done() {
        btn.textContent = '已复制 ✓';
        btn.classList.add('copied');
        setTimeout(function () {
          btn.textContent = '复制';
          btn.classList.remove('copied');
        }, 1500);
      }
      function fallback() {
        var ta = document.createElement('textarea');
        ta.value = text;
        ta.style.position = 'fixed';
        ta.style.opacity = '0';
        document.body.appendChild(ta);
        ta.select();
        try { document.execCommand('copy'); done(); }
        catch (e) { btn.textContent = '复制失败'; }
        document.body.removeChild(ta);
      }
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(done).catch(fallback);
      } else {
        fallback();
      }
    });
    block.appendChild(btn);
  });
});
</script>
"""

files = sorted(glob.glob("python-ppt-html/Python基础_*_PPT.html"))
print("found %d files" % len(files))

for path in files:
    with io.open(path, encoding="utf-8", newline="") as f:
        text = f.read()
    if CSS_MARKER in text:
        print("SKIP:", path)
        continue
    idx = text.rfind("</style>")
    if idx == -1:
        print("SKIP (no </style>):", path)
        continue
    text = text[:idx] + COPY_CSS + text[idx:]
    jidx = text.rfind("</body>")
    if jidx == -1:
        print("SKIP (no </body>):", path)
        continue
    text = text[:jidx] + COPY_JS + text[jidx:]
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    print("OK:", path)
