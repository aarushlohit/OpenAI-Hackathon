import re

with open('backend/static/style.css', 'r') as f:
    content = f.read()

# Replace hardcoded light colors with color-mix or variables
replacements = [
    (r'rgba\(242,236,223,([0-9.]+)\)', r'color-mix(in srgb, var(--bg-sidebar) calc(\1 * 100%), transparent)'),
    (r'rgba\(255,250,242,([0-9.]+)\)', r'color-mix(in srgb, var(--bg-card) calc(\1 * 100%), transparent)'),
    (r'rgba\(247,244,237,([0-9.]+)\)', r'color-mix(in srgb, var(--bg-primary) calc(\1 * 100%), transparent)'),
    (r'rgba\(255,247,235,([0-9.]+)\)', r'color-mix(in srgb, var(--bg-secondary) calc(\1 * 100%), transparent)'),
    (r'rgba\(232,222,206,([0-9.]+)\)', r'color-mix(in srgb, var(--border) calc(\1 * 100%), transparent)'),
]

for pattern, repl in replacements:
    content = re.sub(pattern, repl, content)

with open('backend/static/style.css', 'w') as f:
    f.write(content)
print("CSS updated.")
