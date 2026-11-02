import os
import sys
import json
import urllib.request

OUT_DIR = r"C:\Users\umert\.gemini\antigravity\scratch\war_gov_ufo\downloads\pdfs"
os.makedirs(OUT_DIR, exist_ok=True)

def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

def main():
    print("Fetching file listings for Release 01 and Release 02 documents...")
    docs_01 = fetch_json("https://huggingface.co/api/datasets/proxima/war-gov-uap-release/tree/main/raw/release_01/document")
    docs_02 = fetch_json("https://huggingface.co/api/datasets/proxima/war-gov-uap-release/tree/main/raw/release_02/document")

    all_docs = docs_01 + docs_02
    print(f"Total authentic PDFs found in archive: {len(all_docs)}")

    downloaded = 0
    skipped = 0
    for idx, d in enumerate(all_docs, 1):
        rel_path = d.get("path")
        fname = os.path.basename(rel_path)
        dest = os.path.join(OUT_DIR, fname)
        if os.path.exists(dest) and os.path.getsize(dest) > 1000:
            skipped += 1
            continue

        download_url = f"https://huggingface.co/datasets/proxima/war-gov-uap-release/resolve/main/{rel_path}"
        try:
            req = urllib.request.Request(download_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req) as resp, open(dest, "wb") as f:
                while True:
                    chunk = resp.read(1024 * 1024)
                    if not chunk:
                        break
                    f.write(chunk)
            downloaded += 1
            size_kb = os.path.getsize(dest) / 1024
            print(f"[{idx}/{len(all_docs)}] OK: {fname} ({size_kb:.1f} KB)")
        except Exception as e:
            print(f"[{idx}/{len(all_docs)}] ERR: {fname} -> {e}")

    print("\n" + "=" * 50)
    print(f"Download complete: {downloaded} downloaded, {skipped} skipped.")
    print(f"Total PDFs in {OUT_DIR}: {len(os.listdir(OUT_DIR))}")
    print("=" * 50)

if __name__ == "__main__":
    main()
