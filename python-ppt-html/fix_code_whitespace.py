import os
import re
import glob

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # 1. 修复 .code-block { ... }  — 第05、06、07章
    # 在 .code-block 的规则中，找到第一个 } 前插入 white-space: pre;
    # 匹配 .code-block { ... }，但注意不要匹配媒体查询里的
    pattern1 = re.compile(
        r'(\.code-block\s*\{[^}]+)(\})',
        re.DOTALL
    )
    def repl1(m):
        body = m.group(1)
        if 'white-space' in body:
            return m.group(0)
        return body + 'white-space: pre; ' + m.group(2)
    content = pattern1.sub(repl1, content, count=1)

    # 2. 修复 .slide-content .code { ... }  — 第08、09、10章、绪论、test_ch08
    pattern2 = re.compile(
        r'(\.slide-content\s+\.code\s*\{[^}]+)(\})',
        re.DOTALL
    )
    def repl2(m):
        body = m.group(1)
        if 'white-space' in body:
            return m.group(0)
        return body + 'white-space: pre; ' + m.group(2)
    content = pattern2.sub(repl2, content, count=1)

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[FIXED] {os.path.basename(filepath)}")
    else:
        print(f"[SKIP ] {os.path.basename(filepath)}")

# 处理所有 HTML 文件
targets = glob.glob(os.path.join(os.path.dirname(__file__), '*.html'))
# 排除 index.html 和脚本本身
targets = [t for t in targets if os.path.basename(t) not in ('index.html', 'add_copy_button.py', 'fix_code_whitespace.py')]

for t in sorted(targets):
    fix_file(t)

print("\n全部处理完成。")
