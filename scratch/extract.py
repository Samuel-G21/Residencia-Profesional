import re

with open('frontend/src/App.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

start = content.find("activeView === 'dashboard' && (")
if start != -1:
    paren_count = 0
    in_block = False
    for i in range(start + len("activeView === 'dashboard' && "), len(content)):
        if content[i] == '(':
            paren_count += 1
            in_block = True
        elif content[i] == ')':
            paren_count -= 1
        
        if in_block and paren_count == 0:
            with open('scratch/dash.jsx', 'w', encoding='utf-8') as out:
                out.write(content[start:i+1])
            break
