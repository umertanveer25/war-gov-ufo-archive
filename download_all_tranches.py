"""
PURSUE / war.gov UFO Archive Downloader (Tranches 1 to 7)
Uses local records.json to download all declassified files across all tranches.
Bypasses Akamai CDN bot detection by using a visible Chrome browser session.
"""

import os
import sys
import json
import time
import base64
import argparse
from pathlib import Path
from urllib.parse import urlparse

BASE_DIR = Path(__file__).resolve().parent
RECORDS_FILE = BASE_DIR / "records.json"
PDF_DIR = BASE_DIR / "downloads" / "pdfs"
MEDIA_DIR = BASE_DIR / "downloads" / "media"

UFO_PAGE = "https://www.war.gov/UFO/"

JS_DOWNLOAD = """
const url = arguments[0];
const cb = arguments[1];
fetch(url, {credentials:'include'})
  .then(r => {
    if (!r.ok) throw new Error('HTTP ' + r.status);
    return r.arrayBuffer();
  })
  .then(buf => {
    const bytes = new Uint8Array(buf);
    let bin = '';
    const chunk = 0x8000;
    for (let i = 0; i < bytes.length; i += chunk) {
      bin += String.fromCharCode.apply(null, bytes.subarray(i, i + chunk));
    }
    cb({ok: true, b64: btoa(bin), size: bytes.length});
  })
  .catch(e => cb({ok: false, error: String(e)}));
"""

def sanitize_filename(name: str) -> str:
    invalid = '<>:"/\\|?*'
    for c in invalid:
        name = name.replace(c, '_')
    return name.strip()

def main():
    parser = argparse.ArgumentParser(description="Download all PURSUE UFO records (Tranche 1 to Latest)")
    parser.add_argument("--type", choices=["all", "pdf", "vid", "img", "aud"], default="pdf",
                        help="Type of records to download (default: pdf)")
    parser.add_argument("--tranche", type=str, default="all",
                        help="Filter by tranche/release date (e.g., '5/8/2026', 'all')")
    parser.add_argument("--limit", type=int, default=0,
                        help="Max files to download (0 = unlimited)")
    args = parser.parse_args()

    if not RECORDS_FILE.exists():
        print(f"Error: {RECORDS_FILE} not found!")
        sys.exit(1)

    with open(RECORDS_FILE, "r", encoding="utf-8") as f:
        records = json.load(f)

    print(f"Loaded {len(records)} total records from {RECORDS_FILE.name}")

    # Filter by type
    if args.type != "all":
        records = [r for r in records if r.get("type", "").lower() == args.type.lower()]

    # Filter by tranche
    if args.tranche != "all":
        records = [r for r in records if args.tranche in r.get("releaseDate", "")]

    if args.limit > 0:
        records = records[:args.limit]

    print(f"Targets to process: {len(records)} records")
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)

    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
    except ImportError:
        print("\nSelenium is required to bypass Akamai bot detection.")
        print("Install it with:")
        print("  pip install selenium")
        sys.exit(1)

    opts = Options()
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1280,900")
    
    print("\nLaunching Chrome browser session...")
    driver = webdriver.Chrome(options=opts)
    driver.set_script_timeout(300)

    try:
        print(f"Navigating to {UFO_PAGE} to clear Akamai verification...")
        driver.get(UFO_PAGE)
        time.sleep(5)
        print("Akamai session established. Starting downloads...\n")

        downloaded = 0
        skipped = 0
        failed = 0

        for i, r in enumerate(records, 1):
            rec_id = r.get("id")
            title = r.get("title", f"record_{rec_id}")
            rtype = r.get("type", "PDF")
            file_url = r.get("fileUrl", "")

            if not file_url:
                continue

            target_dir = PDF_DIR if rtype == "PDF" else MEDIA_DIR
            parsed_ext = Path(urlparse(file_url).path).suffix or (".pdf" if rtype == "PDF" else ".bin")
            filename = sanitize_filename(f"{rec_id}_{title}")[:120] + parsed_ext
            dest_file = target_dir / filename

            if dest_file.exists():
                print(f"[{i}/{len(records)}] Skipping (already exists): {filename}")
                skipped += 1
                continue

            print(f"[{i}/{len(records)}] Downloading #{rec_id}: {title[:50]}...", end=" ", flush=True)
            try:
                res = driver.execute_async_script(JS_DOWNLOAD, file_url)
                if isinstance(res, dict) and res.get("ok"):
                    data = base64.b64decode(res["b64"])
                    dest_file.write_bytes(data)
                    mb = len(data) / (1024 * 1024)
                    print(f"OK ({mb:.2f} MB)")
                    downloaded += 1
                else:
                    err = res.get("error", "Unknown error") if isinstance(res, dict) else str(res)
                    print(f"FAIL ({err})")
                    failed += 1
            except Exception as e:
                print(f"ERROR ({e})")
                failed += 1

            time.sleep(1)

        print("\n" + "=" * 50)
        print(f"Download Finished! Total: {downloaded} downloaded, {skipped} skipped, {failed} failed.")
        print(f"PDFs:   {PDF_DIR}")
        print(f"Media:  {MEDIA_DIR}")
        print("=" * 50)

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
