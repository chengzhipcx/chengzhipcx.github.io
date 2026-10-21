import re, glob, os

def inspect_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 查找 .code-block 和 .code
    blocks = re.findall(r'<div class="code-block">(.*?)</div>', content, re.DOTALL)
    blocks += re.findall(r'<div class="code">(.*?)</div>', content, re.DOTALL)

    if not blocks:
        return

    print(f"\n=== {os.path.basename(path)} ===")
    for i, block in enumerate(blocks[:3]):  # 只显示前3个
        # 提取纯文本
        text = re.sub(r'<[^>]+>', '', block)
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        print(f"\nBlock {i+1} ({len(lines)} tokens):")
        print(' | '.join(lines[:20]))  # 显示前20个token
        if len(lines) > 20:
            print(f"... ({len(lines)-20} more)")

# 检查有问题的文件
targets = [
    'Python基础_第05章_程序控制结构_PPT.html',
    'Python基础_第06章_函数_PPT.html',
    'Python基础_第07章_类_PPT.html',
    'Python基础_第08章_文件异常和模块_PPT.html',
    'Python基础_第09章_有益的探索_PPT.html',
    'Python基础_第10章_Python标准库_PPT.html',
    'Python基础_绪论与环境配置_PPT.html',
    'test_ch08.html',
]

for t in targets:
    p = os.path.join(os.path.dirname(__file__), t)
    if os.path.exists(p):
        inspect_file(p)
    else:
        print(f"[NOT FOUND] {t}")
