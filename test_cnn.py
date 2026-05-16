import requests
import re
url = "https://edition.cnn.com/markets/fear-and-greed"
headers = {"User-Agent": "Mozilla/5.0"}
r = requests.get(url, headers=headers)
print(f"Status: {r.status_code}")
# Print a snippet of the text to see where the score is
match = re.search(r'score":([\d\.]+)', r.text)
if match:
    print(f"Match found: {match.group(1)}")
else:
    print("No match found")
    # Search for any number near "Greed"
    match2 = re.search(r'Greed.*?(\d+)', r.text)
    if match2:
        print(f"Secondary match: {match2.group(1)}")
