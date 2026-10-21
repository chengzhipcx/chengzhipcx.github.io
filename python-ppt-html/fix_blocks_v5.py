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

def highlight_code(code, old_style=True):
    tokens = list(tokenize.generate_tokens(io.StringIO(code).readline))
    result = []
    prev_line, prev_col = 1, 0
    prev_tok = None

    kw_cls = 'kw' if old_style else 'keyword'
    str_cls = 'str' if old_style else 'string'
    num_cls = 'num' if old_style else 'number'
    com_cls = 'com' if old_style else 'comment'
    func_cls = 'func' if old_style else 'function'
    var_cls = 'var'

    def add_span(cls, text):
        escaped = html.escape(text)
        return f'<span class="{cls}">{escaped}</span>'

    for i, tok in enumerate(tokens):
        if tok.type in (tokenize.ENDMARKER, tokenize.ENCODING):
            continue

        if tok.type in (tokenize.NL, tokenize.NEWLINE, tokenize.INDENT):
            result.append(tok.string)
            prev_line, prev_col = tok.end
            if tok.type != tokenize.INDENT:
                prev_tok = tok
            continue
        if tok.type == tokenize.DEDENT:
            prev_line, prev_col = tok.end
            continue

        start_line, start_col = tok.start
        if start_line > prev_line:
            result.append('\n' * (start_line - prev_line))
            result.append(' ' * start_col)
        elif start_col > prev_col:
            result.append(' ' * (start_col - prev_col))

        text = tok.string
        if tok.type == tokenize.COMMENT:
            result.append(add_span(com_cls, text))
        elif tok.type == tokenize.STRING:
            result.append(add_span(str_cls, text))
        elif tok.type == tokenize.NUMBER:
            result.append(add_span(num_cls, text))
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
                result.append(add_span(kw_cls, text))
            elif is_func or text in BUILTIN_NAMES:
                result.append(add_span(func_cls, text))
            elif old_style:
                result.append(add_span(var_cls, text))
            else:
                result.append(html.escape(text))
        elif tok.type == tokenize.ERRORTOKEN:
            result.append(html.escape(text))
        else:
            result.append(html.escape(text))

        prev_line, prev_col = tok.end
        if tok.type not in (tokenize.NL, tokenize.INDENT, tokenize.DEDENT):
            prev_tok = tok

    return ''.join(result)

def process_file(filepath):
    content = filepath.read_text(encoding='utf-8')

    has_old_highlight = bool(re.search(r'<span\s+class="(kw|str|num|com|func|var)"', content))
    old_style = has_old_highlight

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

        formatted = None

        # 尝试 black 格式化
        try:
            import black
            mode = black.Mode(line_length=60)
            formatted = black.format_str(raw_code, mode=mode)
            formatted = formatted.rstrip('\n')
        except Exception:
            pass

        # black 失败则尝试 smart_format
        if formatted is None:
            formatted = smart_format(raw_code)

        # 如果格式化结果和原始文本相同，保留原始内容
        if formatted.strip() == raw_code.strip():
            return match.group(0)

        highlighted = highlight_code(formatted, old_style=old_style)
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
