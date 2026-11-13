#!/usr/bin/env python3
"""Verify local media already preserved in GitHub; no external download needed."""
from pathlib import Path
root = Path(__file__).resolve().parents[1] / 'docs' / 'assets'
for n in range(1, 13):
    for folder, ext in [('films', 'mp4'), ('films', 'webp'), ('voice', 'mp3')]:
        p = root / folder / f'ep{n:02}.{ext}'
        assert p.is_file() and p.stat().st_size > 1000, f'Missing media: {p}'
print('PASS: 12 local videos, 12 posters, 12 narrations')
