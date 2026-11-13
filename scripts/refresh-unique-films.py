#!/usr/bin/env python3
"""Produce a different licensed Mixkit nature film and poster for each episode.

This runs in GitHub Actions (standard Ubuntu runner with ffmpeg). It replaces the
12 earlier montage files that recycled several source videos.
The edited clips remain silent: spoken narration and classical recordings are
controlled by the existing player in docs/app.js.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
import os
import subprocess
import tempfile
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
FILMS = ROOT / "docs" / "assets" / "films"
FILMS.mkdir(parents=True, exist_ok=True)
SOURCE_PAGE_PREFIX = "https://mixkit.co/free-stock-video/"
SOURCES = [
    (1, "월광 소나타", "달빛", "full-moon-with-a-soft-haze", 4433),
    (2, "트로이메라이", "꽃바람", "pink-flowers-wave-in-the-breeze", 1168),
    (3, "빗방울 전주곡", "창밖의 비", "window-on-a-rainy-day", 2846),
    (4, "엘리제를 위하여", "하얀 꽃", "white-flowers-in-the-breeze", 1187),
    (5, "녹턴", "별이 흐르는 호수", "night-sky-with-stars-at-a-calm-lake-time-lapse", 1704),
    (6, "사랑의 인사", "분홍 꽃", "small-pink-flowers", 1186),
    (7, "첼로 협주곡", "해변의 파도", "waves-coming-to-the-beach", 5016),
    (8, "피아노 협주곡 2번 · 1악장", "산의 아침", "mountainous-area-in-the-alps", 4132),
    (9, "달빛", "저녁 바다", "beautiful-sunset-on-a-bay-from-above", 4999),
    (10, "트롤하우겐의 결혼식 날", "초원의 햇살", "countryside-meadow", 4075),
    (11, "겨울 나그네", "눈 내리는 숲", "snow-falling-in-a-pine-forest", 3352),
    (12, "피아노 협주곡 2번 · 2악장", "흘러가는 구름", "blue-sky-background-as-the-clouds-travel-blown-by-the", 26108),
]

def fetch(url, path):
    last = None
    for attempt in range(5):
        try:
            request = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (compatible; DJLetterFreeVideo/1.0)"}
            )
            with urllib.request.urlopen(request, timeout=50) as response:
                data = response.read()
            if len(data) < 4000 or b"ftyp" not in data[:32]:
                raise ValueError("The downloaded file is not a valid MP4")
            path.write_bytes(data)
            return
        except Exception as exc:
            last = exc
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"Cannot download {url}: {last}")

def process(item):
    n, piece, scene, slug, id_number = item
    stem = f"ep{n:02}"
    with tempfile.TemporaryDirectory(prefix=f"dj-{stem}-") as tmp:
        raw = Path(tmp) / "source.mp4"
        try:
            fetch(f"https://assets.mixkit.co/videos/{id_number}/{id_number}-720.mp4", raw)
        except RuntimeError:
            fetch(f"https://assets.mixkit.co/videos/{id_number}/{id_number}-360.mp4", raw)

        new_video = Path(tmp) / f"{stem}.mp4"
        new_poster = Path(tmp) / f"{stem}.webp"

        # Silent, calm nature footage. Repetition only occurs inside the same
        # individual clip if its original duration is shorter than 14 seconds.
        subprocess.run([
            "ffmpeg", "-y", "-nostdin", "-hide_banner", "-loglevel", "error",
            "-stream_loop", "-1", "-i", str(raw),
            "-t", "14", "-vf",
            "scale=960:540:force_original_aspect_ratio=increase,crop=960:540,"
            "setsar=1,fps=18",
            "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "29",
            "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(new_video)
        ], check=True, timeout=110)

        subprocess.run([
            "ffmpeg", "-y", "-nostdin", "-hide_banner", "-loglevel", "error",
            "-ss", "2", "-i", str(new_video), "-frames:v", "1",
            "-c:v", "libwebp", "-quality", "78", str(new_poster)
        ], check=True, timeout=30)

        if new_video.stat().st_size < 12000 or new_poster.stat().st_size < 1500:
            raise ValueError(f"One of the assets for {stem} is unexpectedly small")

        # Atomic writes after both outputs validate.
        (FILMS / f"{stem}.mp4").write_bytes(new_video.read_bytes())
        (FILMS / f"{stem}.webp").write_bytes(new_poster.read_bytes())
        digest = hashlib.sha256(new_poster.read_bytes()).hexdigest()
        return {"episode": n, "piece": piece, "scene": scene,
                "video": f"assets/films/{stem}.mp4",
                "poster": f"assets/films/{stem}.webp",
                "source_id": id_number,
                "source_url": f"{SOURCE_PAGE_PREFIX}{slug}-{id_number}/",
                "license": "Mixkit Stock Video Free License",
                "poster_hash": digest,
                "bytes": (FILMS / f"{stem}.mp4").stat().st_size}

with ThreadPoolExecutor(max_workers=3) as pool:
    jobs = {pool.submit(process, item): item[0] for item in SOURCES}
    completed = []
    for job in as_completed(jobs):
        item = job.result()
        completed.append(item)
        print(f"CREATED EP{item['episode']:02d} {item['piece']} "
              f"Mixkit #{item['source_id']} {item['bytes']} bytes", flush=True)

completed.sort(key=lambda e: e["episode"])
if len(completed) != 12:
    raise RuntimeError("Missing video clips")
if len({x["source_id"] for x in completed}) != 12:
    raise RuntimeError("Video sources are not unique")
if len({x["poster_hash"] for x in completed}) != 12:
    raise RuntimeError("Duplicate poster frames found")
(FILMS / "manifest.json").write_text(
    json.dumps(completed, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8"
)
print("Validated: 12 UNIQUE source videos, 12 distinct posters.", flush=True)
