# -*- coding: utf-8 -*-
"""删除章节封面公众号推广区的第二张图（查令十街84号），只保留第一张并居中"""
import glob
import io
import re

PATTERN = re.compile(
    r'(<div class="wx-promo-images">\s*<img[^>]*alt="coder程"[^>]*/>)\s*\n\s*<img[^>]*alt="查令十街84号"[^>]*/>'
)

files = sorted(glob.glob("python-ppt-html/Python基础_*_PPT.html"))
print("found %d files" % len(files))

for path in files:
    with io.open(path, encoding="utf-8", newline="") as f:
        text = f.read()
    new_text, n = PATTERN.subn(r"\1", text, count=1)
    if n == 1:
        with io.open(path, "w", encoding="utf-8", newline="") as f:
            f.write(new_text)
        print("OK:", path)
    else:
        print("SKIP (already removed or pattern mismatch):", path)
