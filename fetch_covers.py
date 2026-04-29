import os
import csv
import re
import time
import requests
from io import BytesIO
from PIL import Image

API_KEY  = "72b088fdc51f94e536039eb065bb8ae7"
HEADERS  = {"Authorization": f"Bearer {API_KEY}"}
CSV_PATHS = [
    r"c:\Users\Kracher\Documents\Project\AccessGamesCataloge\PC_Games.csv",
    r"c:\Users\Kracher\Documents\Project\AccessGamesCataloge\Xbox_Games.csv",
    r"c:\Users\Kracher\Documents\Project\AccessGamesCataloge\PS_Games.csv"
]
OUT_DIR  = r"c:\Users\Kracher\Documents\Project\AccessGamesCataloge\assets\covers"

os.makedirs(OUT_DIR, exist_ok=True)

def slugify(name):
    name = re.sub(r'(?i)xbox series x\|s', '', name)
    name = re.sub(r'(?i)xbox one', '', name)
    name = re.sub(r'(?i)ps5', '', name)
    name = re.sub(r'(?i)ps4', '', name)
    name = name.lower()
    name = re.sub(r"[^a-z0-9\s]", "", name)
    name = re.sub(r"\s+", "-", name)
    name = re.sub(r"-+", "-", name)
    return name.strip('-').strip()

def get_game_id(name):
    try:
        res = requests.get(
            f"https://www.steamgriddb.com/api/v2/search/autocomplete/{requests.utils.quote(name)}",
            headers=HEADERS, timeout=10)
        if res.status_code == 200:
            data = res.json()
            if data.get("success") and data["data"]:
                return data["data"][0]["id"]
    except Exception as e:
        print(f"    Search error: {e}")
    return None

def get_cover_url(game_id):
    try:
        res = requests.get(
            f"https://www.steamgriddb.com/api/v2/grids/game/{game_id}?dimensions=600x900",
            headers=HEADERS, timeout=10)
        if res.status_code == 200:
            data = res.json()
            if data.get("success") and data["data"]:
                return data["data"][0]["url"]
    except Exception as e:
        print(f"    Cover URL error: {e}")
    return None

def download_cover(url, out_path):
    res = requests.get(url, timeout=20)
    res.raise_for_status()
    img = Image.open(BytesIO(res.content)).convert("RGB")
    img = img.resize((300, 450), Image.Resampling.LANCZOS)
    img.save(out_path, "WEBP", quality=82)

# Load all game names from CSVs
all_games = []
combo_items = set()

for path in CSV_PATHS:
    if not os.path.exists(path):
        continue
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if "game" in row:
                all_games.append(row["game"].strip())
            if row.get("is_combo") == "True" and row.get("combo_list", "").strip():
                for item in row["combo_list"].split("|"):
                    combo_items.add(item.strip())

all_names = list(set(all_games + list(combo_items)))

# Find which ones are missing
missing = []
for name in all_names:
    slug = slugify(name)
    if not os.path.exists(os.path.join(OUT_DIR, f"{slug}.webp")):
        missing.append(name)

print(f"Total games: {len(all_names)}")
print(f"Missing covers: {len(missing)}\n")

print("--- Starting downloads ---\n")

ok, fail = 0, 0
for name in sorted(missing):
    slug = slugify(name)
    out_path = os.path.join(OUT_DIR, f"{slug}.webp")
    print(f"[{name}]", end=" ", flush=True)

    gid = get_game_id(name)
    if not gid:
        print("NOT FOUND in SGDB")
        fail += 1
        time.sleep(0.5)
        continue

    url = get_cover_url(gid)
    if not url:
        print("NO COVER IMAGE")
        fail += 1
        time.sleep(0.5)
        continue

    try:
        download_cover(url, out_path)
        print(f"SAVED -> {slug}.webp")
        ok += 1
    except Exception as e:
        print(f"ERROR: {e}")
        fail += 1

    time.sleep(0.4)

print(f"\nDone: {ok} saved, {fail} failed out of {len(missing)} missing.")
