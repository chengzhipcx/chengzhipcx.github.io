# -*- coding: utf-8 -*-
"""修复幻灯片内容超高时被裁切且无法滚动的问题（幂等）

原理：把每个 .slide 的子内容包进 .slide-inner，
用 margin:auto 实现安全居中（内容超高时自动顶对齐并可滚动），
同时 .slide 加 overflow-y:auto。
"""
import glob
import io

MARKER = "幻灯片溢出滚动修复"

CSS = """
    /* 幻灯片溢出滚动修复 */
    .slide { overflow-y: auto; }
    .slide-inner {
      margin: auto;
      width: 100%;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding-bottom: 60px; /* 避开底部固定翻页按钮 */
    }
"""

JS = """
<script>
// 幻灯片溢出滚动修复：包裹一层 .slide-inner 实现安全居中
document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.slide').forEach(function (s) {
    var inner = document.createElement('div');
    inner.className = 'slide-inner';
    while (s.firstChild) inner.appendChild(s.firstChild);
    s.appendChild(inner);
  });
});
</script>
"""

files = sorted(glob.glob("python-ppt-html/Python基础_*_PPT.html"))
print("found %d files" % len(files))

for path in files:
    with io.open(path, encoding="utf-8", newline="") as f:
        text = f.read()
    if MARKER in text:
        print("SKIP:", path)
        continue
    idx = text.rfind("</style>")
    if idx == -1:
        print("SKIP (no </style>):", path)
        continue
    text = text[:idx] + CSS + text[idx:]
    jidx = text.rfind("</body>")
    if jidx == -1:
        print("SKIP (no </body>):", path)
        continue
    text = text[:jidx] + JS + text[jidx:]
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    print("OK:", path)
