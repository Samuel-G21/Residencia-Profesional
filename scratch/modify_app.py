import re

with open('frontend/src/App.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Add imports for react-router-dom
if 'react-router-dom' not in content:
    content = content.replace("import './App.css';", "import './App.css';\nimport { BrowserRouter as Router, Routes, Route, Link, useNavigate } from 'react-router-dom';")

# We can't easily replace the `activeView === '...' && (` blocks with regex because they span multiple lines and have closing `)` 
# So I'll just change the state `activeView` to be driven by useLocation/useNavigate or leave it for now.
# Since it's complex, I will just report it.
