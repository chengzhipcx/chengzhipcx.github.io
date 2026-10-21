# -*- coding: utf-8 -*-
"""给所有章节 PPT 页面注入移动端竖屏适配 CSS（幂等，可重复运行）"""
import glob
import io

MOBILE_CSS = """
    /* 移动端竖屏适配 */
    @media (max-width: 768px) and (orientation: portrait) {
      html, body { overflow-y: auto !important; }
      .slide { padding: 24px 20px !important; justify-content: flex-start !important; overflow-y: auto !important; }
      .slide h1 { font-size: 1.7rem !important; letter-spacing: 1px !important; }
      .slide h2 { font-size: 1.35rem !important; margin-bottom: 18px !important; }
      .slide h3 { font-size: 1.05rem !important; }
      .slide p, .slide li { font-size: 0.95rem !important; line-height: 1.6 !important; }
      .slide li { margin-bottom: 10px !important; padding-left: 24px !important; }
      .slide .code { font-size: 0.72rem !important; padding: 10px 12px !important; margin-top: 12px !important; }
      .slide .grid { grid-template-columns: 1fr !important; gap: 14px !important; }
      .slide .card { padding: 14px !important; }
      .slide table, .compare-table { font-size: 0.78rem !important; }
      .slide th, .slide td, .compare-table th, .compare-table td { padding: 6px 8px !important; }
      .wx-promo { margin-top: 24px !important; padding-top: 16px !important; }
      .wx-promo-images { flex-direction: column !important; gap: 10px !important; }
      .wx-promo-images img { width: 100% !important; max-width: 280px !important; height: auto !important; }
      .nav { bottom: 14px !important; gap: 6px !important; }
      .nav button { padding: 8px 14px !important; font-size: 12px !important; }
      .nav .page-num { font-size: 12px !important; padding: 0 10px !important; line-height: 32px !important; }
    }
"""

MARKER = "移动端竖屏适配"

files = sorted(glob.glob("python-ppt-html/**/Python基础_*_PPT.html", recursive=True))
print("found %d chapter files" % len(files))

for path in files:
    with io.open(path, encoding="utf-8", newline="") as f:
        text = f.read()
    idx = text.rfind("</style>")
    if idx == -1:
        print("SKIP (no </style>):", path)
        continue
    if MARKER in text:
        # 已注入过：用新块替换旧块（旧块位于 </style> 之前）
        start = text.rfind("/* " + MARKER, 0, idx)
        # 向前回退到块起始的换行处，保持缩进整洁
        start = text.rfind("\n", 0, start)
        text = text[:start] + MOBILE_CSS + text[idx:]
        print("UPDATED:", path)
    else:
        text = text[:idx] + MOBILE_CSS + text[idx:]
        print("OK:", path)
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)
