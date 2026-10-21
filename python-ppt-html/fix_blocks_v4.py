import re
import html
import tokenize
import io
import keyword
import builtins
from pathlib import Path

BUILTIN_NAMES = set(dir(builtins))
KEYWORDS = set(keyword.kwlist)
BLOCK_KEYWORDS = {'def', 'class', 'if', 'elif', 'else', 'for', 'while', 'with', 'try', 'except', 'finally'}
SIMPLE_STMT = {'return', 'break', 'continue', 'pass', 'raise', 'yield', 'global', 'nonlocal', 'assert', 'del', 'import', 'from'}
ASSIGN_OPS = {'=', '+=', '-=', '*=', '/=', '//=', '%=', '**=', '&=', '|=', '^=', '<<=', '>>='}

def extract_text_from_html_block(html_content):
    text = re.sub(r'<span[^>]*>', '', html_content)
    text = re.sub(r'</span>', '', text)
    text = html.unescape(text)
    return text

def smart_format(code):
    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(code).readline))
    except:
        return code

    stmt_starts = set()
    for i, tok in enumerate(tokens):
        if tok.type != tokenize.NAME:
            continue
        if tok.string in BLOCK_KEYWORDS or tok.string in SIMPLE_STMT:
            stmt_starts.add(i)
            continue
        j = i + 1
        while j < len(tokens) and tokens[j].type in (tokenize.NL, tokenize.COMMENT):
            j += 1
        if j < len(tokens) and tokens[j].type == tokenize.OP:
            if tokens[j].string in ASSIGN_OPS:
                stmt_starts.add(i)
                continue
            if tokens[j].string == '(':
                if i > 0 and tokens[i-1].type == tokenize.NAME and tokens[i-1].string in ('def', 'class'):
                    continue
                stmt_starts.add(i)

    result = []
    indent_level = 0
    expect_block = False
    paren_depth = 0
    in_lambda = 0
    line_start = True

    def insert_newline():
        result.append('\n')
        result.append('    ' * indent_level)

    i = 0
    while i < len(tokens):
        tok = tokens[i]

        if tok.type == tokenize.ENDMARKER:
            break

        if tok.type in (tokenize.NL, tokenize.NEWLINE):
            result.append('\n')
            i += 1
            while i < len(tokens) and tokens[i].type == tokenize.DEDENT:
                indent_level -= 1
                i += 1
            if i < len(tokens) and tokens[i].type != tokenize.ENDMARKER:
                result.append('    ' * indent_level)
            line_start = True
            expect_block = False
            continue

        if tok.type == tokenize.INDENT:
            i += 1
            continue
        if tok.type == tokenize.DEDENT:
            i += 1
            continue

        if tok.string in '([{':
            paren_depth += 1
        elif tok.string in ')]}':
            paren_depth -= 1
            if in_lambda > 0:
                in_lambda -= 1
        elif tok.string == ',' and in_lambda > 0:
            in_lambda -= 1

        if tok.type == tokenize.NAME and tok.string == 'lambda':
            in_lambda += 1

        if tok.type == tokenize.NAME and tok.string in BLOCK_KEYWORDS:
            if in_lambda == 0 and paren_depth == 0:
                if not line_start:
                    result.append('\n')
                    if tok.string in ('elif', 'else', 'except', 'finally'):
                        result.append('    ' * max(0, indent_level - 1))
                    else:
                        result.append('    ' * indent_level)
                expect_block = True
                line_start = True

        if i in stmt_starts and not line_start and paren_depth == 0 and in_lambda == 0:
            if not expect_block:
                if indent_level > 0:
                    result.append('\n')
                    result.append('    ' * max(0, indent_level - 1))
                    indent_level = max(0, indent_level - 1)
                else:
                    insert_newline()
                line_start = True

        result.append(tok.string)
        line_start = False

        if tok.string == ':' and expect_block and paren_depth == 0 and in_lambda == 0:
            j = i + 1
            while j < len(tokens) and tokens[j].type in (tokenize.NL, tokenize.COMMENT):
                j += 1
            if j < len(tokens) and tokens[j].type not in (tokenize.NEWLINE, tokenize.ENDMARKER, tokenize.DEDENT):
                insert_newline()
                indent_level += 1
                line_start = True
            expect_block = False

        i += 1

    formatted = ''.join(result).rstrip('\n') + '\n'
    return formatted

def highlight_code_old(code):
    """旧高亮方案: kw, str, num, com, func, var"""
    tokens = list(tokenize.generate_tokens(io.StringIO(code).readline))
    result = []
    prev_tok = None

    def add_span(cls, text):
        escaped = html.escape(text)
        return f'<span class="{cls}">{escaped}</span>'

    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok.type in (tokenize.ENDMARKER, tokenize.ENCODING):
            i += 1
            continue

        text = tok.string

        if tok.type == tokenize.COMMENT:
            result.append(add_span('com', text))
        elif tok.type == tokenize.STRING:
            result.append(add_span('str', text))
        elif tok.type == tokenize.NUMBER:
            result.append(add_span('num', text))
        elif tok.type == tokenize.NAME:
            is_func = False
            if text not in KEYWORDS and prev_tok and prev_tok.type == tokenize.NAME and prev_tok.string == 'def':
                is_func = True
            elif text not in KEYWORDS:
                j = i + 1
                while j < len(tokens) and tokens[j].type in (tokenize.NL, tokenize.COMMENT, tokenize.INDENT, tokenize.DEDENT):
                    j += 1
                if j < len(tokens) and tokens[j].type == tokenize.OP and tokens[j].string == '(':
                    is_func = True

            if text in KEYWORDS:
                result.append(add_span('kw', text))
            elif is_func or text in BUILTIN_NAMES:
                result.append(add_span('func', text))
            else:
                result.append(add_span('var', text))
        elif tok.type in (tokenize.NL, tokenize.NEWLINE):
            result.append('\n')
        elif tok.type == tokenize.INDENT:
            result.append(text)
        elif tok.type == tokenize.DEDENT:
            pass
        elif tok.type == tokenize.ERRORTOKEN:
            result.append(html.escape(text))
        else:
            result.append(html.escape(text))

        if tok.type not in (tokenize.NL, tokenize.INDENT, tokenize.DEDENT):
            prev_tok = tok
        i += 1

    return ''.join(result)

def highlight_code_new(code):
    """新高亮方案: keyword, string, number, comment, function"""
    tokens = list(tokenize.generate_tokens(io.StringIO(code).readline))
    result = []
    prev_tok = None

    def add_span(cls, text):
        escaped = html.escape(text)
        return f'<span class="{cls}">{escaped}</span>'

    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok.type in (tokenize.ENDMARKER, tokenize.ENCODING):
            i += 1
            continue

        text = tok.string

        if tok.type == tokenize.COMMENT:
            result.append(add_span('comment', text))
        elif tok.type == tokenize.STRING:
            result.append(add_span('string', text))
        elif tok.type == tokenize.NUMBER:
            result.append(add_span('number', text))
        elif tok.type == tokenize.NAME:
            is_func = False
            if text not in KEYWORDS and prev_tok and prev_tok.type == tokenize.NAME and prev_tok.string == 'def':
                is_func = True
            elif text not in KEYWORDS:
                j = i + 1
                while j < len(tokens) and tokens[j].type in (tokenize.NL, tokenize.COMMENT, tokenize.INDENT, tokenize.DEDENT):
                    j += 1
                if j < len(tokens) and tokens[j].type == tokenize.OP and tokens[j].string == '(':
                    is_func = True

            if text in KEYWORDS:
                result.append(add_span('keyword', text))
            elif is_func or text in BUILTIN_NAMES:
                result.append(add_span('function', text))
            else:
                # 新方案中普通变量不加 span
                result.append(html.escape(text))
        elif tok.type in (tokenize.NL, tokenize.NEWLINE):
            result.append('\n')
        elif tok.type == tokenize.INDENT:
            result.append(text)
        elif tok.type == tokenize.DEDENT:
            pass
        elif tok.type == tokenize.ERRORTOKEN:
            result.append(html.escape(text))
        else:
            result.append(html.escape(text))

        if tok.type not in (tokenize.NL, tokenize.INDENT, tokenize.DEDENT):
            prev_tok = tok
        i += 1

    return ''.join(result)

def needs_formatting(raw_code):
    raw_code = raw_code.strip()
    if not raw_code:
        return False
    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(raw_code).readline))
    except:
        return False

    has_block = any(t.type == tokenize.NAME and t.string in BLOCK_KEYWORDS for t in tokens)
    if not has_block:
        return False

    for i, t in enumerate(tokens):
        if t.type == tokenize.NAME and t.string in BLOCK_KEYWORDS:
            for j in range(i+1, len(tokens)):
                if tokens[j].type == tokenize.OP and tokens[j].string == ':':
                    for k in range(j+1, len(tokens)):
                        if tokens[k].type in (tokenize.NEWLINE, tokenize.NL):
                            break
                        if tokens[k].type not in (tokenize.COMMENT, tokenize.INDENT, tokenize.DEDENT, tokenize.ENDMARKER):
                            return True
                    break

    newline_count = sum(1 for t in tokens if t.type == tokenize.NEWLINE)
    if newline_count <= 2 and len(tokens) > 20:
        return True

    has_indent = any(t.type == tokenize.INDENT for t in tokens)
    if has_block and not has_indent and len(tokens) > 15:
        return True

    return False

def process_file(filepath):
    content = filepath.read_text(encoding='utf-8')

    # 判断使用哪种高亮方案
    has_old_highlight = bool(re.search(r'<span\s+class="(kw|str|num|com|func|var)"', content))
    highlight = highlight_code_old if has_old_highlight else highlight_code_new

    # 同时匹配 code-block 和 code
    pattern = re.compile(r'(<div\s+class="(code-block|code)">)(.*?)(</div>)', re.DOTALL)
    changes = 0

    def replace_block(match):
        nonlocal changes
        open_tag = match.group(1)
        inner = match.group(3)
        close_tag = match.group(4)

        raw_code = extract_text_from_html_block(inner).strip('\n')
        if not raw_code.strip():
            return match.group(0)

        if not needs_formatting(raw_code):
            return match.group(0)

        formatted = smart_format(raw_code)

        try:
            import black
            mode = black.Mode(line_length=60)
            formatted = black.format_str(formatted, mode=mode)
            formatted = formatted.rstrip('\n')
        except Exception:
            pass

        if formatted.strip() == raw_code.strip():
            return match.group(0)

        highlighted = highlight(formatted)
        changes += 1
        return f'{open_tag}\n{highlighted}\n{close_tag}'

    new_content = pattern.sub(replace_block, content)

    if changes > 0:
        filepath.write_text(new_content, encoding='utf-8')
        print(f"Fixed {changes} code-block(s) in {filepath.name}")
    else:
        print(f"No changes in {filepath.name}")

    return changes

def main():
    base_dir = Path("d:/projects/codercheng/chengzhipcx.github.io-master/chengzhipcx.github.io-master/python-ppt-html")
    files = sorted(base_dir.glob("Python基础_第*.html"))
    total = 0
    for f in files:
        total += process_file(f)
    print(f"\nTotal fixed: {total} code-block(s)")

if __name__ == '__main__':
    main()
