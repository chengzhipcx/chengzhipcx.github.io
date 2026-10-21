import os
import re
import glob

# 需要触发新行的关键字（当不在括号内时）
NEWLINE_KEYWORDS = {
    'def', 'class', 'if', 'for', 'while', 'with', 'try',
    'else', 'elif', 'except', 'finally',
    'return', 'pass', 'break', 'continue',
    'raise', 'assert', 'del', 'global', 'nonlocal', 'yield',
    'print'
}

# 标识符正则
IDENT_RE = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')
# 字符串字面量前缀
STRING_PREFIXES = ('"', "'", 'f"', "f'", 'b"', "b'", 'r"', "r'", 'u"', "u'", 'F"', "F'", 'B"', "B'", 'R"', "R'", 'U"', "U'")

def decode_entities(text):
    text = text.replace('&gt;', '>')
    text = text.replace('&lt;', '<')
    text = text.replace('&amp;', '&')
    text = text.replace('&quot;', '"')
    text = text.replace('&#39;', "'")
    return text

def encode_entities(text):
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    return text

def parse_fragments(inner_html):
    """把代码块 innerHTML 解析为 [{type, class, text}, ...]"""
    fragments = []
    pattern = re.compile(r'(<span\s+class="([^"]+)">(.*?)</span>)|(<br\s*/?>)|([^<]+)', re.DOTALL)
    for m in pattern.finditer(inner_html):
        if m.group(1):
            fragments.append({'type': 'span', 'class': m.group(2), 'text': decode_entities(m.group(3))})
        elif m.group(4):
            fragments.append({'type': 'br', 'text': '\n'})
        elif m.group(5):
            text = decode_entities(m.group(5))
            if text.strip():
                fragments.append({'type': 'text', 'class': None, 'text': text})
    return fragments

def is_identifier(text):
    return bool(IDENT_RE.match(text)) and text not in NEWLINE_KEYWORDS and text not in ('True', 'False', 'None')

def is_string_literal(text):
    t = text.strip()
    return t.startswith(('"', "'", 'f"', "f'", 'b"', "b'", 'r"', "r'", 'F"', "F'", 'B"', "B'", 'R"', "R'"))

def should_trigger_newline(token_text, current_line_first):
    t = token_text.strip()
    if t.startswith('#'):
        return True
    if t in NEWLINE_KEYWORDS:
        return True
    if t == 'import':
        if current_line_first and current_line_first.strip() == 'from':
            return False
        return True
    if t == 'from':
        return True
    return False

def rebuild_code(fragments):
    """把碎片重组为正确的 Python 代码行，返回新的 HTML 字符串"""
    # 先过滤出有效 token
    tokens = []
    for frag in fragments:
        text = frag['text'].strip()
        if text:
            tokens.append({**frag, 'text': text})

    lines = []
    current = []
    paren_depth = bracket_depth = brace_depth = 0

    def flush():
        nonlocal current
        if current:
            lines.append(current)
            current = []

    for i, tok in enumerate(tokens):
        text = tok['text']
        first_token = current[0]['text'] if current else None
        prev_text = current[-1]['text'] if current else None
        next_text = tokens[i + 1]['text'] if i + 1 < len(tokens) else None

        # 1. 注释单独成行
        if text.startswith('#'):
            flush()
            lines.append([tok])
            continue

        # 2. 关键字触发新行
        if paren_depth == 0 and bracket_depth == 0 and brace_depth == 0:
            if should_trigger_newline(text, first_token):
                flush()
                current.append(tok)
                continue

        # 3. 标识符 + 等号 → 新赋值语句（预读）
        if paren_depth == 0 and bracket_depth == 0 and brace_depth == 0:
            if is_identifier(text) and next_text == '=' and current:
                flush()
                current.append(tok)
                continue

        # 4. 字符串字面量跟在某些语句结束后 → 新行
        if paren_depth == 0 and bracket_depth == 0 and brace_depth == 0:
            if is_string_literal(text) and current and prev_text in (')', ']', '}', ':', ';'):
                flush()
                current.append(tok)
                continue

        # 5. 左括号
        if text in ('(', '[', '{'):
            if text == '(': paren_depth += 1
            elif text == '[': bracket_depth += 1
            elif text == '{': brace_depth += 1
            current.append(tok)
            continue

        # 6. 右括号
        if text in (')', ']', '}'):
            current.append(tok)
            if text == ')': paren_depth -= 1
            elif text == ']': bracket_depth -= 1
            elif text == '}': brace_depth -= 1
            if paren_depth == 0 and bracket_depth == 0 and brace_depth == 0:
                flush()
            continue

        # 7. 分号
        if text == ';':
            current.append(tok)
            flush()
            continue

        # 8. 默认
        current.append(tok)

    flush()

    # 生成新的 HTML（保留原有 span class）
    new_html_parts = []
    for line_frags in lines:
        line_parts = []
        for frag in line_frags:
            txt = encode_entities(frag['text'])
            if frag['type'] == 'span' and frag.get('class'):
                line_parts.append(f'<span class="{frag["class"]}">{txt}</span>')
            else:
                line_parts.append(txt)
        new_html_parts.append(' '.join(line_parts))

    return '\n'.join(new_html_parts)

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content
    changed = False

    def replacer(m):
        nonlocal changed
        tag = m.group(1)
        inner = m.group(2)
        fragments = parse_fragments(inner)

        texts = [f['text'].strip() for f in fragments if f['text'].strip()]
        if not texts:
            return m.group(0)

        avg_len = sum(len(t) for t in texts) / len(texts)
        max_len = max(len(t) for t in texts)

        # 判断标准：碎片多、平均短、且没有长token
        is_fragmented = (len(texts) > 5 and avg_len < 8 and max_len < 25)

        if not is_fragmented:
            return m.group(0)

        new_inner = rebuild_code(fragments)
        changed = True
        return f'<div class="{tag}">\n{new_inner}\n</div>'

    content = re.sub(r'<div class="(code-block|code)">(.*?)</div>', replacer, content, flags=re.DOTALL)

    if changed:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[FIXED] {os.path.basename(filepath)}")
    else:
        print(f"[SKIP ] {os.path.basename(filepath)}")

# 处理所有 HTML 文件
targets = glob.glob(os.path.join(os.path.dirname(__file__), '*.html'))
targets = [t for t in targets if os.path.basename(t) not in ('index.html',)]

for t in sorted(targets):
    process_file(t)

print("\n全部处理完成。")
