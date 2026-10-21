import os
import re
import glob

# CSS 片段：复制按钮样式
css_snippet = """
  /* ===== 代码复制按钮 ===== */
  pre { position: relative; }
  .copy-btn {
    position: absolute; top: 8px; right: 8px;
    padding: 4px 10px; font-size: 12px; line-height: 1.4;
    color: #ccc; background: rgba(255,255,255,0.1);
    border: 1px solid rgba(255,255,255,0.2); border-radius: 4px;
    cursor: pointer; opacity: 0; transition: opacity 0.2s, background 0.2s;
    font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", sans-serif;
    z-index: 10;
  }
  pre:hover .copy-btn { opacity: 1; }
  .copy-btn:hover { background: rgba(255,255,255,0.25); color: #fff; }
  .copy-btn.copied { color: #4ec9b0; border-color: #4ec9b0; background: rgba(78,201,176,0.15); opacity: 1; }
"""

# JS 片段：复制代码逻辑
js_snippet = """
  // ===== 代码复制功能 =====
  document.querySelectorAll('pre').forEach(pre => {
    const btn = document.createElement('button');
    btn.className = 'copy-btn';
    btn.textContent = '复制';
    btn.type = 'button';
    btn.addEventListener('click', () => {
      const code = pre.querySelector('code');
      const text = code ? code.innerText : pre.innerText;
      navigator.clipboard.writeText(text).then(() => {
        btn.textContent = '已复制';
        btn.classList.add('copied');
        setTimeout(() => { btn.textContent = '复制'; btn.classList.remove('copied'); }, 1500);
      }).catch(() => {
        // fallback
        const ta = document.createElement('textarea');
        ta.value = text;
        ta.style.position = 'fixed';
        ta.style.opacity = '0';
        document.body.appendChild(ta);
        ta.select();
        try { document.execCommand('copy'); } catch (e) {}
        document.body.removeChild(ta);
        btn.textContent = '已复制';
        btn.classList.add('copied');
        setTimeout(() => { btn.textContent = '复制'; btn.classList.remove('copied'); }, 1500);
      });
    });
    pre.appendChild(btn);
  });
"""

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 避免重复注入
    if 'copy-btn' in content:
        print(f"[SKIP] 已存在复制按钮: {filepath}")
        return

    # 在最后一个 </style> 前插入 CSS
    # 找到最后一个 </style>，因为有些文件可能在 body 后面还有 style
    last_style_end = content.rfind('</style>')
    if last_style_end != -1:
        content = content[:last_style_end] + css_snippet + "\n" + content[last_style_end:]
    else:
        print(f"[WARN] 未找到 </style>: {filepath}")

    # 在最后一个 </script> 前插入 JS
    last_script_end = content.rfind('</script>')
    if last_script_end != -1:
        content = content[:last_script_end] + js_snippet + "\n" + content[last_script_end:]
    else:
        print(f"[WARN] 未找到 </script>: {filepath}")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"[DONE] {filepath}")

# 处理所有目标 HTML 文件
targets = glob.glob(os.path.join(os.path.dirname(__file__), 'Python基础_*_PPT.html'))
targets += glob.glob(os.path.join(os.path.dirname(__file__), 'test_ch08.html'))

for t in sorted(targets):
    process_file(t)

print("\n全部处理完成。")
