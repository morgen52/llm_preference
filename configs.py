language_keys = {
    'javascript': ['javascript', 'js'],
    'python': ['python', 'py'],
    'java': ['java'],
    'php': ['php'],
    'c++': ['c++', 'cpp', 'cplusplus'],
    'c': ['```c\n'],
    'csharp': ['c#', 'csharp'],
    'ruby': ['ruby'],
    'perl': ['perl'],
    'swift': ['swift'],
    'go': ['```go\n'],
    'scala': ['scala'],
    'r': ['```r\n'],
    'kotlin': ['kotlin'],
    'rust': ['rust'],
    'typescript': ['typescript', 'ts'],
    'shell': ['shell', 'bash'],
    'html': ['html'],
    'css': ['css'],
    'sql': ['sql'],
    'json': ['json'],
    'xml': ['xml'],
    'yaml': ['yaml'],
    'markdown': ['markdown', 'md'],
    'latex': ['latex'],
    'jsx': ['jsx'],
    'tsx': ['tsx'],
    'lua': ['lua'],
    'vb': ['vb', 'vb.net', 'vbnet'],
    'arduino': ['arduino'],
    'wasm': ['wasm', 'webassembly'],
    'makefile': ['makefile', '```make\n', '```cmake\n'],
}

keys2lang = {}
for k, values in language_keys.items():
    for v in values:
        keys2lang[v] = k
        
