# war-gov-ufo-archive

Automated indexing, cataloging, and cloud-archiving repository for the **Presidential Unsealing and Reporting System for UAP Encounters (PURSUE)** declassified records from `war.gov/ufo`.

---

## 📊 Archive Scope & Statistics (Tranches 1 to 7)

* **Total Catalog Records:** 481 official declassified files
* **Declassification Wave:** Tranche 1 (May 8, 2026) through Tranche 7 (October 23, 2026)
* **Lead Agencies:** Department of War, FBI, NASA, CIA, Department of State, Department of Energy, DIA/AAWSAP, AARO

### Asset Breakdown:
| Type | Count | Description |
| :--- | :--- | :--- |
| **PDF** | 299 | Mission reports, AIIR reports, FBI 302 debriefs, BAASS technical plans |
| **VID** | 136 | Military sensor video feeds, FLIR/thermal footage, gun camera clips |
| **IMG** | 30 | High-resolution photographic scans and incident sketches |
| **AUD** | 16 | Cockpit and mission radio audio recordings |

---

## 🚀 Cloud Archival via GitHub Actions (Zero Local Disk Space)

This repository includes an automated GitHub Action workflow (`.github/workflows/archive.yml`) that runs in the cloud to pull the large video and audio binaries without filling your local hard drive:

1. **Trigger the Workflow:**
   * Go to the **Actions** tab in this GitHub repository.
   * Select **Download and Release UFO Tranches**.
   * Click **Run workflow** (specify batch size or `0` for all).
2. **What GitHub Actions Does:**
   * Spawns an isolated Ubuntu cloud runner.
   * Directly streams the `.mp4` video files from military CloudFront CDNs.
   * Compresses the media into ZIP packages (`ufo_tranches_videos.zip`).
   * Automatically publishes a **GitHub Release** and attaches the ZIP files as downloadable release assets (bypassing git repository 100 MB limits).

---

## 📁 Repository Structure

* `records.json` — Master index of all 481 records across Tranches 1 to 7 with full metadata, descriptions, and file links.
* `uap-csv.csv` — Official tabular dataset.
* `realufo_records.jsonl` — Cross-referenced JSONL records.
* `scripts/cloud_downloader.py` — Cloud streaming script for DVIDS/CloudFront media assets.
* `.github/workflows/archive.yml` — Automated cloud release pipeline.
