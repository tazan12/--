#!/usr/bin/env python3
"""Cache DJ Letter episode videos and original DJ narrations in this repo.

One-time migration: downloadable content is put under docs/assets so that
GitHub Pages no longer depends on the Higgsfield website serving media.
The source videos were edited from Mixkit Stock Video Free License footage.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import json
import re
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
VIDEO_SOURCE = "https://dj-letter-radio-2026.higgsfield.app/assets"
UA = "DJ-Letter-Media-Migration/1.0"
js = (DOCS / "app.js").read_text(encoding="utf-8")
match = re.search(r"const stories\s*=\s*", js)
if not match:
    raise RuntimeError("Episode list is missing in docs/app.js")
stories, _ = json.JSONDecoder().raw_decode(js[match.end():])
if len(stories) != 12:
    raise RuntimeError(f"Expected 12 episodes, found {len(stories)}")

assets = []
for i, episode in enumerate(stories, 1):
    n = f"ep{i:02}"
    assets.extend([
        (f"{VIDEO_SOURCE}/films/{n}.mp4", DOCS / "assets" / "films" / f"{n}.mp4"),
        (f"{VIDEO_SOURCE}/films/{n}.webp", DOCS / "assets" / "films" / f"{n}.webp"),
        (episode["dj"], DOCS / "assets" / "voice" / f"{n}.mp3"),
    ])
assets.append((f"{VIDEO_SOURCE}/dj-cover.webp", DOCS / "assets" / "dj-cover.webp"))

def download(entry):
    url, output = entry
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.is_file() and output.stat().st_size > 1000:
        return f"EXISTS {output.relative_to(ROOT)}"
    err = None
    for attempt in range(4):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(request, timeout=40) as response:
                data = response.read()
            if len(data) < 1000:
                raise RuntimeError("Downloaded file is unexpectedly small")
            if output.suffix == ".mp4" and b"ftyp" not in data[:24]:
                raise RuntimeError("Downloaded file is not an MP4")
            if output.suffix == ".mp3" and not (data.startswith(b"ID3") or data.startswith(b"\xff\xfb") or data.startswith(b"\xff\xf3")):
                raise RuntimeError("Downloaded file is not an MP3")
            temporary = output.with_suffix(output.suffix + ".tmp")
            temporary.write_bytes(data)
            temporary.replace(output)
            return f"OK {output.relative_to(ROOT)} {len(data)} bytes"
        except Exception as exc:
            err = exc
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"Could not fetch {output}: {err}")

with ThreadPoolExecutor(max_workers=4) as pool:
    jobs = [pool.submit(download, item) for item in assets]
    for job in as_completed(jobs):
        print(job.result(), flush=True)

print("Media package complete: 12 videos, 12 posters, 12 DJ audios, 1 cover.")
