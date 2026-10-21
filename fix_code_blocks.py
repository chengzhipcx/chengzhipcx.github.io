import re
import html
import tokenize
import io
import keyword
import builtins
import subprocess
import sys
from pathlib import Path

BUILTIN_NAMES = set(dir(builtins))
KEYWORDS = set(keyword.kwlist)
BLOCK_KEYWORDS = {'def', 'class', 'if', 'elif', 'else', 'for', 'while', 'with', 'try', 'except', 'finally'}
PYTHON_EXE = r"D:/Programs/Python/Python312/python.exe"

def extract_text_from_html_block(html_content):
    text = re.sub(r'<span[^>]*>', '', html_content)
    text = re.sub(r'</span>', '', text)
    text = html.unescape(text)
    return text

def format_with_black(code):
    try:
        result = subprocess.run(
            [PYTHON_EXE, '-m', 'black', '-', '--line-length', '60'],
            input=code,
            capture_output=True,
            text=True,
            timeout=15
        )
        if result.returncode in (0, 1) and result.stdout.strip():
            return result.stdout
        return None
    except Exception as e:
        print(f"    black error: {e}")
        return None

def highlight_code(code):
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
    
    # 检查是否有 ": 后面同一行还有代码" 的情况
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
    
    # 检查是否逻辑行很少但 token 很多（说明被压缩）
    newline_count = sum(1 for t in tokens if t.type == tokenize.NEWLINE)
    if newline_count <= 2 and len(tokens) > 20:
        return True
    
    # 检查是否有 block 关键字但完全没有 INDENT
    has_indent = any(t.type == tokenize.INDENT for t in tokens)
    if has_block and not has_indent and len(tokens) > 15:
        return True
    
    return False

def process_file(filepath):
    content = filepath.read_text(encoding='utf-8')
    pattern = re.compile(r'(<div\s+class="code-block">)(.*?)(</div>)', re.DOTALL)
    
    changes = 0
    
    def replace_block(match):
        nonlocal changes
        open_tag = match.group(1)
        inner = match.group(2)
        close_tag = match.group(3)
        
        raw_code = extract_text_from_html_block(inner).strip('\n')
        if not raw_code.strip():
            return match.group(0)
        
        if not needs_formatting(raw_code):
            return match.group(0)
        
        formatted = format_with_black(raw_code)
        if not formatted or not formatted.strip():
            return match.group(0)
        
        if formatted.strip() == raw_code.strip():
            return match.group(0)
        
        highlighted = highlight_code(formatted.rstrip('\n'))
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
