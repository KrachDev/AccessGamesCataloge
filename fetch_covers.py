import os
import json
import re
import requests
from io import BytesIO
from PIL import Image

API_KEY = "72b088fdc51f94e536039eb065bb8ae7"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

HTML_PATH = r"c:\Users\Kracher\Downloads\catalog_1.html"
OUT_DIR = r"c:\Users\Kracher\Downloads\assets\covers"

os.makedirs(OUT_DIR, exist_ok=True)

# 1. Parse CATALOG from HTML
with open(HTML_PATH, 'r', encoding='utf-8') as f:
    html_content = f.read()

match = re.search(r'const CATALOG = (\[.*?\]);', html_content, re.DOTALL)
if not match:
    print("Could not find CATALOG in HTML")
    exit(1)

catalog = json.loads(match.group(1))

def normalize_name(name):
    # keep only alphanumeric, lowercase, spaces to dashes
    name = name.lower()
    name = re.sub(r'[^a-z0-9\s]', '', name)
    return re.sub(r'\s+', '-', name).strip()

def get_game_id(name):
    res = requests.get(f"https://www.steamgriddb.com/api/v2/search/autocomplete/{name}", headers=HEADERS)
    if res.status_code == 200:
        data = res.json()
        if data.get('success') and len(data['data']) > 0:
            return data['data'][0]['id']
    return None

def get_cover_url(game_id):
    # try official first
    res = requests.get(f"https://www.steamgriddb.com/api/v2/grids/game/{game_id}?dimensions=600x900", headers=HEADERS)
    if res.status_code == 200:
        data = res.json()
        if data.get('success') and len(data['data']) > 0:
            return data['data'][0]['url']
    return None

success_count = 0

for game in catalog:
    name = game['name']
    norm_name = normalize_name(name)
    out_path = os.path.join(OUT_DIR, f"{norm_name}.webp")
    
    if os.path.exists(out_path):
        print(f"[{name}] Already exists.")
        success_count += 1
        continue
        
    print(f"[{name}] Fetching...")
    game_id = get_game_id(name)
    if not game_id:
        print(f"  -> Not found in search")
        continue
        
    url = get_cover_url(game_id)
    if not url:
        print(f"  -> No cover available")
        continue
        
    try:
        img_res = requests.get(url)
        img_res.raise_for_status()
        img = Image.open(BytesIO(img_res.content))
        img = img.convert("RGB")
        img = img.resize((300, 450), Image.Resampling.LANCZOS)
        img.save(out_path, "WEBP", quality=80)
        print(f"  -> Saved cover successfully")
        success_count += 1
    except Exception as e:
        print(f"  -> Error: {e}")

print(f"\nDone! Processed {success_count}/{len(catalog)} covers.")
