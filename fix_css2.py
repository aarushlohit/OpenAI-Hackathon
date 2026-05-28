import re

with open('backend/static/style.css', 'r') as f:
    content = f.read()

# Replace hardcoded light mode colors with CSS variables
replacements = [
    (r'#fffaf2', r'var(--bg-secondary)'),
    (r'#f8f3ea', r'var(--bg-primary)'),
    (r'#efe5d6', r'var(--bg-hover)'),
    (r'#d8cbbb', r'var(--border-subtle)'),
]

for pattern, repl in replacements:
    content = re.sub(pattern, repl, content)

with open('backend/static/style.css', 'w') as f:
    f.write(content)
print("CSS updated.")
