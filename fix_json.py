import re, json

with open('frontend/public/scan_results.json', 'rb') as f:
    raw = f.read()

content = raw.decode('utf-8', errors='replace').replace('\r\n', '\n').replace('\r', '\n')

# Fix NaN/Infinity text
content = re.sub(r':\s*NaN\b', ': null', content)
content = re.sub(r':\s*Infinity\b', ': null', content)
content = re.sub(r':\s*-Infinity\b', ': null', content)

# Remove ALL control chars except tab, newline
content = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', content)

# Fix broken "thr: true - this is a JSON key that had a control char in its name
# "thr[\x??]ead..." - replace it by removing broken fundamentals block entirely
# Replace the whole broken fundamentals dict content
content = re.sub(r'\{\s*"thr:[^}]*\}', '{"threshold_break": true}', content)

# The file seems to have duplicate JSON appended at the end - take only the first valid JSON object
try:
    decoder = json.JSONDecoder()
    data, end_idx = decoder.raw_decode(content)
    print('Parsed first JSON object OK, stocks:', len(data['stocks']))
    out = json.dumps(data, ensure_ascii=False, indent=2)
    out = re.sub(r':\s*NaN\b', ': null', out)
    out = re.sub(r':\s*Infinity\b', ': null', out)
    out = re.sub(r':\s*-Infinity\b', ': null', out)
    with open('frontend/public/scan_results.json', 'w', encoding='utf-8', newline='\n') as f:
        f.write(out)
    # Verify
    with open('frontend/public/scan_results.json', 'r', encoding='utf-8') as f:
        verify = f.read()
    json.loads(verify)
    print('Verification PASSED. File is clean and valid.')
except Exception as e:
    print('Error:', e)
    pos = int(str(e).split('char ')[1].rstrip(')')) if 'char' in str(e) else 0
    if pos:
        print(repr(content[pos-100:pos+100]))
