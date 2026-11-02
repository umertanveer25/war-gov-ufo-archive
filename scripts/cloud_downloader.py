"""
Cloud Downloader for GitHub Actions Runner (Batch Matrix Edition)
Fetches a specific batch slice of media assets and packages them into a release ZIP.
"""

import os
import re
import sys
import json
import zipfile
import argparse
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RECORDS_FILE = BASE_DIR / "records.json"
OUTPUT_DIR = BASE_DIR / "cloud_downloads"

DVIDS_BASE = "https://www.dvidshub.net"

def fetch_mp4_url(dvids_id: str) -> str:
    embed_url = f"{DVIDS_BASE}/video/embed/{dvids_id}"
    req = urllib.request.Request(embed_url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            matches = re.findall(r'https?://[^\s"\'<>]+\.mp4[^\s"\'<>]*', html)
            if matches:
                return matches[0]
    except Exception as e:
        print(f"  [WARN] Failed to resolve DVIDS #{dvids_id}: {e}")
    return ""

def download_file(url: str, dest: Path) -> bool:
    if dest.exists() and dest.stat().st_size > 1000:
        return True
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=120) as resp, open(dest, "wb") as f:
            while True:
                chunk = resp.read(1024 * 1024)
                if not chunk:
                    break
                f.write(chunk)
        return True
    except Exception as e:
        print(f"  [ERR] Failed to download {url}: {e}")
        if dest.exists():
            dest.unlink()
        return False

def zip_directory(source_dir: Path, zip_path: Path):
    print(f"\nCompressing {source_dir.name} into {zip_path.name}...")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in source_dir.glob("*"):
            if file.is_file():
                zipf.write(file, arcname=file.name)
    size_mb = zip_path.stat().st_size / (1024 * 1024)
    print(f"Created {zip_path.name} ({size_mb:.2f} MB)")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=0, help="Batch start index")
    parser.add_argument("--size", type=int, default=40, help="Batch size")
    parser.add_argument("--output-zip", type=str, default="batch.zip", help="Output ZIP file name")
    args = parser.parse_args()

    if not RECORDS_FILE.exists():
        print(f"Error: {RECORDS_FILE} not found!")
        sys.exit(1)

    with open(RECORDS_FILE, "r", encoding="utf-8") as f:
        records = json.load(f)

    vids = [r for r in records if r.get("dvidsVideoId")]
    batch = vids[args.start : args.start + args.size]

    batch_dir = OUTPUT_DIR / f"batch_{args.start}"
    batch_dir.mkdir(parents=True, exist_ok=True)

    print(f"Processing Batch [{args.start} to {args.start + len(batch)}] of {len(vids)} total videos.")

    downloaded = 0
    for idx, r in enumerate(batch, 1):
        vid_id = r.get("dvidsVideoId")
        title = r.get("title", f"video_{vid_id}")
        clean_title = re.sub(r'[^A-Za-z0-9._-]+', '_', title)[:80]
        filename = f"{clean_title}__dvids{vid_id}.mp4"
        dest = batch_dir / filename

        print(f"[{idx}/{len(batch)}] Fetching DVIDS #{vid_id}: {clean_title[:35]}...")
        mp4_url = fetch_mp4_url(vid_id)
        if mp4_url:
            if download_file(mp4_url, dest):
                size_mb = dest.stat().st_size / (1024 * 1024)
                print(f"  -> OK ({size_mb:.2f} MB)")
                downloaded += 1
            else:
                print("  -> Download Failed")
        else:
            print("  -> Could not resolve MP4 URL")

    # Zip the downloaded batch
    release_zip = BASE_DIR / args.output_zip
    zip_directory(batch_dir, release_zip)
    print(f"\nBatch completed: {downloaded} files zipped into {release_zip.name}")

if __name__ == "__main__":
    main()
