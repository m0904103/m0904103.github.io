import re, json

with open('frontend/public/scan_results.json', 'rb') as f:
    raw = f.read()

content = raw.decode('utf-8', errors='replace').replace('\r\n', '\n').replace('\r', '\n')
content = re.sub(r':\s*NaN\b', ': null', content)
content = re.sub(r':\s*Infinity\b', ': null', content)
content = re.sub(r':\s*-Infinity\b', ': null', content)

# The issue: 'thr: true' looks like a truncated key - missing closing quote before colon.
idx = content.find('"thr: true')
print('Found at index:', idx)
if idx >= 0:
    print(repr(content[idx-200:idx+200]))
