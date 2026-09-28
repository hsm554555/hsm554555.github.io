"""Download the English L-Acoustics documents listed in index.csv.

Files are saved under LAcoustics_Docs/ using the zip_path column, which groups
them by the documentation center's own categories. Run: python download.py
"""
import csv
import os
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))


def fetch(row):
    path = os.path.join(HERE, row["zip_path"])
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return "skip", path
    os.makedirs(os.path.dirname(path), exist_ok=True)
    url = urllib.parse.quote(row["url"], safe=":/%")
    try:
        with urllib.request.urlopen(url) as r, open(path, "wb") as f:
            while chunk := r.read(1 << 20):
                f.write(chunk)
        return "ok", path
    except Exception as e:
        if os.path.exists(path):
            os.remove(path)
        return f"fail ({e})", path


with open(os.path.join(HERE, "index.csv"), encoding="utf-8-sig") as f:
    rows = [r for r in csv.DictReader(f) if r["zip_path"]]

with ThreadPoolExecutor(8) as ex:
    for i, (status, path) in enumerate(ex.map(fetch, rows), 1):
        print(f"[{i}/{len(rows)}] {status}: {path}")
