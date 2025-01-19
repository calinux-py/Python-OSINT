import os
import requests
import re
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# target url. example: https://www.snapchat.com/add/mrbeast
url = ""
os.makedirs("downloaded_media", exist_ok=True)
headers = {"User-Agent": "Mozilla/5.0"}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")
script = soup.find("script", type="application/ld+json")
if script:
    try:
        data = json.loads(script.string)
        entity = data.get("mainEntity", {})
        print("Name:", entity.get("name", ""))
        print("Address:", entity.get("address", ""))
        print("Alternate Name:", entity.get("alternateName", ""))
        print("Description:", entity.get("description", ""))
        print("URL:", entity.get("url", ""))
    except:
        pass
span = soup.find("span", {"data-testid": "subscribersCountText"})
if span:
    print(span.text.strip())
preview_urls = set(re.findall(r'"mediaPreviewUrl"\s*:\s*\{"value"\s*:\s*"([^"]+)"', response.text))
cf_urls = [u for u in re.findall(r'"contentUrl"\s*:\s*"([^"]+)"', response.text) if u.startswith("https://cf-st.sc-cdn.net/")]
all_urls = re.findall(r'(https?://[^\s"\'<>]+)', response.text)
other_urls = [u for u in all_urls if "cf-st.sc-cdn.net" not in u and (re.search(r'\.(png|jpg|jpeg|gif|mp4|webm)(\?|$)', u) or ("?mo=" in u and re.search(r'\.[0-9A-Za-z]+', u)))]
media_urls = cf_urls + other_urls
for m in media_urls:
    full_url = urljoin(url, m)
    if full_url in preview_urls:
        continue
    file_name = os.path.basename(full_url.split("?")[0])
    if "?mo=" in m:
        file_name = os.path.splitext(file_name)[0] + ".mp4"
    file_path = os.path.join("downloaded_media", file_name)
    with requests.get(full_url, stream=True, headers=headers) as media_response, open(file_path, "wb") as f:
        for chunk in media_response.iter_content(chunk_size=1024):
            f.write(chunk)
