import re

with open('frontend/src/App.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace custom activeView logic with react-router-dom if needed
# Actually, I'll just look at how activeView is used
for match in re.finditer(r'activeView.*', content):
    print(match.group(0))
