#!/usr/bin/env python3
"""Repair DJ Letter playback without relying on an autoplay bypass.
Uses only the existing, licensed episode footage already in docs/assets/films.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import subprocess, json, re, os, hashlib
ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'
FILMS = DOCS / 'assets/films'
VERSION = '20261114-stable2'


def transcode(n):
    stem = f'ep{n:02}'
    source = FILMS / (stem + '.mp4')
    compatible = FILMS / (stem + '.compat.mp4')
    motion = FILMS / (stem + '.motion.webp')
    if not source.is_file():
        raise RuntimeError(f'Missing original footage: {source}')
    if not compatible.exists():
        subprocess.run(['ffmpeg', '-y', '-nostdin', '-v', 'error', '-i', str(source),
          '-vf', 'fps=24,scale=960:540,setsar=1', '-an', '-c:v', 'libx264',
          '-profile:v', 'baseline', '-level:v', '3.1', '-preset', 'fast', '-crf', '27',
          '-pix_fmt', 'yuv420p', '-bf', '0', '-g', '48', '-keyint_min', '48',
          '-sc_threshold', '0', '-movflags', '+faststart', str(compatible)],
          check=True, timeout=180)
    if not motion.exists():
        subprocess.run(['ffmpeg', '-y', '-nostdin', '-v', 'error', '-i', str(source),
          '-vf', 'fps=12,scale=640:360,setsar=1', '-an', '-c:v', 'libwebp_anim',
          '-quality', '58', '-compression_level', '4', '-loop', '0', str(motion)],
          check=True, timeout=240)
    data = motion.read_bytes()
    if data[:4] != b'RIFF' or b'ANIM' not in data or data.count(b'ANMF') < 10:
        raise RuntimeError(f'Fallback is not a moving scene: {motion}')
    info = json.loads(subprocess.check_output(['ffprobe','-v','quiet','-show_streams',
             '-of','json',str(compatible)]))['streams'][0]
    if 'Baseline' not in info['profile'] or info['pix_fmt'] != 'yuv420p':
        raise RuntimeError(f'Incompatible encoding for {stem}')
    return dict(episode=n, mp4=compatible.stat().st_size, webp=len(data),
                frames=data.count(b'ANMF'), profile=info['profile'],
                sha256=hashlib.sha256(data).hexdigest())


def patch():
    player_path = DOCS / 'player.js'
    s = player_path.read_text(encoding='utf-8')
    if 'const scenery = window.DJ_SCENERY;' not in s:
        s = s.replace("  const films = [$('film'), $('filmNext')];\n", '')
        s = re.sub(r'  let volume = 0\.75, videoEpoch[^\n]*\n', '  let volume = 0.75;\n', s)
        s = re.sub(r'  let inView[^\n]*\n', '', s)
        s = re.sub(r'  const attempts[^\n]*\n', '', s)
        s = re.sub(r'  const labels = \{playing:[^\n]*\n', '', s)
        s = re.sub(r"    const saved = localStorage\.getItem\('dj-letter-still'\);\n    if \(saved !== null\)[^\n]*\n", '', s)
        s = s.replace("  $('still').checked = still;\n", '')
        start = s.index('  films.forEach(v => {')
        end = s.index('  function toast(text)', start)
        s = s[:start] + s[end:]
        start = s.index('  function filmStatus(state)')
        end = s.index('  function clearAudioTimers()', start)
        replacement = "  const scenery = window.DJ_SCENERY;\n  const setFilm = () => scenery.setEpisode(index, scenes[index]);\n  const retryFilm = () => scenery.resume();\n"
        s = s[:start] + replacement + s[end:]
        s = s.replace('  function startNarration() {', '  function startNarration() {\n    scenery.userStart();')
        s = s.replace('  function toggleProgram() {', '  function toggleProgram() {\n    scenery.userStart();')
        s = s.replace("$('musicOnly').onclick = beginMusic;", "$('musicOnly').onclick = () => { scenery.userStart(); beginMusic(); };")
    s = s.replace('20261114-natural1', VERSION)
    assert 'filmNext' not in s and 'videoEpoch' not in s and 'attempts.' not in s
    player_path.write_text(s, encoding='utf-8')
    (DOCS / 'scenery.js').write_text((ROOT / 'scripts/scenery-stable.js').read_text(encoding='utf-8'), encoding='utf-8')

    p = DOCS / 'index.html'; html = p.read_text(encoding='utf-8')
    html = re.sub(r'<video[^>]*id="filmNext"[\s\S]*?</video>\s*', '', html)
    if 'id="filmMotion"' not in html:
        html = html.replace('<div class="dj-film-topline">', '<img id="filmMotion" class="dj-scene-motion" alt="곡에 맞는 실제 풍경의 호환 재생" hidden decoding="async"/><div class="dj-film-topline">')
    html = html.replace('class="dj-scene-video is-front"', 'class="dj-scene-video"')
    html = html.replace('20261114-natural1', VERSION)
    if './scenery.js?' not in html:
        html = html.replace(f'<script src="./player.js?v={VERSION}" defer></script>', f'<script src="./scenery.js?v={VERSION}" defer></script>\n<script src="./player.js?v={VERSION}" defer></script>')
    html = html.replace('기기의 동작 줄이기 설정을 따릅니다. 필요할 때 감상 방식을 바꿀 수 있습니다.', '동작 줄이기는 처음에만 따릅니다. 편지 듣기를 누르면 풍경도 함께 시작합니다. 영상 재생이 제한되면 같은 실사 장면의 호환 형식으로 이어집니다.')
    assert html.count('<video ') == 1 and 'id="filmMotion"' in html and './scenery.js?' in html
    p.write_text(html, encoding='utf-8')

    css_path = DOCS / 'player.css'; css = css_path.read_text(encoding='utf-8')
    if 'STABLE_SINGLE_DECODER' not in css:
        css += '''\n/* STABLE_SINGLE_DECODER: no invisible second decoder or stale front class. */
.dj-scene-video{z-index:2!important;opacity:0!important;transition:opacity .3s ease!important;pointer-events:none!important;display:block!important;visibility:visible!important;filter:none!important}
.dj-film-window.native-visible .dj-scene-video{opacity:1!important}
.dj-scene-motion{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;z-index:1;display:block;pointer-events:none}
.dj-scene-motion[hidden]{display:none!important}
.dj-film-topline{z-index:4!important;pointer-events:none}
@media(prefers-reduced-motion:reduce){.dj-scene-video{transition:none!important}}
'''
    css_path.write_text(css, encoding='utf-8')
    for f in ['player.js','scenery.js','episodes.js']:
        subprocess.run(['node','--check',str(DOCS/f)],check=True)
    assert not re.search(r'higgsfield\.|d8j0ntlcm91z4', html + s + css)


if __name__ == '__main__':
    patch()
    # The smoke-test mode prepares candidate source without re-encoding all assets.
    if os.environ.get('DJ_PATCH_ONLY') != '1':
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = []
            for future in as_completed([pool.submit(transcode,n) for n in range(1,13)]):
                result = future.result(); results.append(result); print(json.dumps(result),flush=True)
        assert len(results) == 12 and len({r['sha256'] for r in results}) == 12
        (DOCS/'playback-release.json').write_text(json.dumps({'release':VERSION,'episodes':sorted(results,key=lambda r:r['episode'])},ensure_ascii=False,indent=2),encoding='utf-8')
    print('PASS: one decoder, no video play overlay, legacy still flag removed, local assets only', flush=True)
