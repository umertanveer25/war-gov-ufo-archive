import json

with open(r"C:\Users\umert\.gemini\antigravity\scratch\war_gov_ufo\records.json", "r", encoding="utf-8") as f:
    records = json.load(f)

t7 = [r for r in records if r.get("releaseDate") == "10/23/2026"]
print(f"Total records in Tranche 7: {len(t7)}")
for r in t7:
    title = r.get("title", "")
    rtype = r.get("type", "")
    agency = r.get("agency", "")
    desc = r.get("description", "")
    file_url = r.get("fileUrl", "")
    dvids = r.get("dvidsVideoId", "")
    print(f"[{rtype}] {agency} - {title}")
    if desc:
        print(f"  Summary: {desc[:150]}")
    if file_url:
        print(f"  File: {file_url}")
    if dvids:
        print(f"  DVIDS Video ID: {dvids}")
    print("-" * 60)
