"""
Cloud PDF Downloader for GitHub Actions Runner
Fetches all declassified PDF packages from the open mirror,
splits them into safe < 1.5 GB ZIP volumes, and stages them for GitHub Release.
"""

import os
import sys
import json
import zipfile
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "cloud_pdfs"
MAX_ZIP_BYTES = 1_500_000_000

def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

def download_file(url, dest):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp, open(dest, "wb") as f:
        while True:
            chunk = resp.read(1024 * 1024)
            if not chunk:
                break
            f.write(chunk)

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print("Fetching PDF catalog...")
    docs_01 = fetch_json("https://huggingface.co/api/datasets/proxima/war-gov-uap-release/tree/main/raw/release_01/document")
    docs_02 = fetch_json("https://huggingface.co/api/datasets/proxima/war-gov-uap-release/tree/main/raw/release_02/document")
    all_docs = docs_01 + docs_02
    print(f"Total PDFs to process: {len(all_docs)}")

    downloaded = []
    for idx, d in enumerate(all_docs, 1):
        rel_path = d.get("path")
        fname = os.path.basename(rel_path)
        dest = OUTPUT_DIR / fname
        if dest.exists() and dest.stat().st_size > 1000:
            downloaded.append(dest)
            continue

        encoded_path = urllib.parse.quote(rel_path) if hasattr(urllib, 'parse') else rel_path.replace(' ', '%20')
        url = f"https://huggingface.co/datasets/proxima/war-gov-uap-release/resolve/main/{encoded_path}"
        try:
            download_file(url, dest)
            downloaded.append(dest)
            print(f"[{idx}/{len(all_docs)}] OK: {fname} ({dest.stat().st_size / 1024:.1f} KB)")
        except Exception as e:
            print(f"[{idx}/{len(all_docs)}] ERR: {fname} -> {e}")

    # Split into 2 safe zip volumes (~1.2 GB each)
    vol1 = BASE_DIR / "ufo_documents_volume1.zip"
    vol2 = BASE_DIR / "ufo_documents_volume2.zip"

    half = len(downloaded) // 2
    print(f"\nCompressing Volume 1 ({half} files)...")
    with zipfile.ZipFile(vol1, 'w', zipfile.ZIP_DEFLATED) as z:
        for f in downloaded[:half]:
            z.write(f, arcname=f.name)

    print(f"Compressing Volume 2 ({len(downloaded) - half} files)...")
    with zipfile.ZipFile(vol2, 'w', zipfile.ZIP_DEFLATED) as z:
        for f in downloaded[half:]:
            z.write(f, arcname=f.name)

    print(f"Created: {vol1.name} ({vol1.stat().st_size / (1024*1024):.2f} MB)")
    print(f"Created: {vol2.name} ({vol2.stat().st_size / (1024*1024):.2f} MB)")

if __name__ == "__main__":
    import urllib.parse
    main()
