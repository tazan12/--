#!/usr/bin/env python3
"""One-time natural-player migration. Existing audio/video binaries are preserved."""
from pathlib import Path
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'
old = DOCS / 'app.js'
data = DOCS / 'episodes.js'
if old.exists():
    source = old.read_text(encoding='utf-8')
    marker = re.search(r'const stories\s*=\s*', source)
    if not marker:
        raise RuntimeError('Original episode data not found')
    episodes, _ = json.JSONDecoder().raw_decode(source[marker.end():])
else:
    source = data.read_text(encoding='utf-8')
    episodes, _ = json.JSONDecoder().raw_decode(source.split('=', 1)[1].lstrip())
assert len(episodes) == 12
for episode in episodes:
    # Speech now exists in assets/voice/epNN.mp3; these unused cloud links
    # must not ship to the viewer or be accidentally restored later.
    episode.pop('dj', None)
data.write_text('window.DJ_EPISODES = ' + json.dumps(episodes, ensure_ascii=False, indent=2) + ';\n', encoding='utf-8')

html = '''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>DJ의 편지 | 서사가 있는 클래식 라디오</title>
<meta name="description" content="낮고 따뜻한 남성 DJ의 편지, 클래식 연주, 자연스럽게 흐르는 열두 가지 풍경. 무료 클래식 감상 서재."/>
<meta property="og:title" content="DJ의 편지 | 서사가 있는 클래식 라디오"/>
<meta property="og:description" content="이야기와 음악 사이, 마음을 쉬어 가는 시간"/>
<meta property="og:image" content="https://tazan12.github.io/--/assets/dj-cover.webp"/>
<meta name="theme-color" content="#12192b"/>
<meta name="dj-release" content="20261114-natural1"/>
<link rel="canonical" href="https://tazan12.github.io/--/"/>
<link rel="stylesheet" href="./player.css?v=20261114-natural1"/>
<script src="./episodes.js?v=20261114-natural1" defer></script>
<script src="./player.js?v=20261114-natural1" defer></script>
</head>
<body>
<a class="skip-link" href="#stage">음악 감상으로 바로 가기</a>
<main class="dj-app">
<header class="dj-header">
<a class="dj-mark" href="./">☾ DJ의 편지 <small>CLASSICAL · LETTERS · REST</small></a>
<nav aria-label="주 메뉴"><a href="#listen">오늘의 편지</a><a href="#episodes">이야기 서재</a><a href="#write">나에게 쓰는 편지</a></nav>
</header>
<section class="dj-hero" id="listen" aria-label="오늘의 클래식 감상">
<div class="dj-intro"><div class="dj-kicker">A LITTLE ROOM FOR YOUR HEART</div>
<h1>오늘은 음악에게<br/><em>마음을 맡겨요.</em></h1>
<p>이야기가 다가오고, 음악이 곁에 머무는 시간.<br/>풍경은 조용히 흐르도록 두세요.</p>
<div class="dj-cta"><button id="mainPlay" type="button">편지 듣기</button><a href="#episodes">이야기 둘러보기</a></div>
<p class="dj-hint">한국어 남성 DJ · 열두 통의 음악 편지 · 무료 감상</p>
</div>
<div class="dj-stage" id="stage">
<div class="dj-film-window" id="filmWindow">
<video class="dj-scene-video is-front" id="film" muted loop playsinline webkit-playsinline preload="auto" poster="./assets/films/ep01.webp" aria-label="곡에 어울리는 자연 풍경" tabindex="-1"></video>
<video class="dj-scene-video" id="filmNext" muted loop playsinline webkit-playsinline preload="metadata" aria-hidden="true" tabindex="-1"></video>
<div class="dj-film-topline"><span id="filmSceneName">달빛이 머무는 밤</span><span id="filmState">풍경을 준비하고 있어요</span></div>
</div>
<div class="dj-stage-copy">
<span id="stageEpisode">LETTER 01 / 12</span><h2 id="stageTitle">이름 없는 편지를 위한 밤</h2><p id="stageMusic">베토벤 · 월광 소나타 · 제1악장</p>
<div class="dj-audio-row">
<button class="dj-round" id="stagePlay" type="button" aria-label="낭독·음악 듣기">▶</button>
<button class="dj-skip" id="stageNext" type="button" aria-label="다음 음악 편지">⏭</button>
<div class="dj-audio-caption"><span id="phaseLabel">편지와 음악</span><div class="dj-status" id="stageStatus" role="status" aria-live="polite">편지를 듣고, 음악을 맞이할 준비가 되었습니다.</div></div>
</div>
<div class="dj-progress"><span id="clock">0:00</span><input type="range" id="seek" min="0" max="1000" value="0" disabled aria-label="낭독·음악 재생 위치"/><span id="duration">0:00</span></div>
<div class="dj-scene-buttonrow">
<button id="wide" type="button" aria-pressed="false">넓게 감상</button>
<details class="dj-options"><summary>감상 설정</summary><div class="dj-options-panel">
<label><input id="still" type="checkbox"/>풍경을 정지 화면으로 보기</label>
<label for="volume">소리 크기 <input id="volume" type="range" min="0" max="100" value="75"/></label>
<small>기기의 동작 줄이기 설정을 따릅니다. 필요할 때 감상 방식을 바꿀 수 있습니다.</small>
</div></details><span class="dj-status-label">무음 실사 풍경 · 자동으로 이어집니다</span>
</div>
<a id="filmFallback" class="dj-source-help" href="./assets/films/ep01.mp4" target="_blank" rel="noopener noreferrer" hidden>연결이 어려우면 영상 원본 열기</a>
<a id="musicSource" class="dj-source-help" href="https://commons.wikimedia.org/" target="_blank" rel="noopener noreferrer" hidden>연주 음원 원본 확인하기</a>
</div>
</div>
</section>
<section class="dj-reader" aria-labelledby="readerTitle"><div class="dj-sectiontop"><span>오늘의 한 장</span><span>음악은 끝내 다 하지 못한 마음의 문장입니다.</span></div>
<div class="dj-letter"><div class="dj-letter-head" id="readerMood">그리움에 관한 이야기</div><h2 id="readerTitle">이름 없는 편지를 위한 밤</h2><p id="readerText"></p><p class="dj-closing">오늘의 마음을 잠시 내려놓고, 이제 음악을 들어보세요.</p>
<div class="dj-letter-bottom"><button id="readerPlay" type="button">편지 처음부터 듣기</button><button id="musicOnly" type="button">바로 클래식 듣기</button></div></div>
</section>
<section class="dj-library" id="episodes" aria-labelledby="libraryTitle"><div class="dj-sectionhead"><div><span class="dj-kicker">YOUR MUSIC LIBRARY</span><h2 id="libraryTitle">열두 통의 음악 편지</h2><p>지금 마음과 닮은 이야기를 골라 보세요.</p></div><div class="dj-tags" id="moods" role="group" aria-label="감정별 이야기 선택"></div></div><div class="dj-grid" id="cards"></div></section>
<section class="dj-journal" id="write" aria-labelledby="journalTitle"><div><span class="dj-kicker">YOUR OWN LETTER</span><h2 id="journalTitle">오늘의 나에게,<br/>한 줄의 다정함을.</h2><p>당신의 문장은 이 기기의 브라우저에만 보관됩니다.</p></div><div><textarea id="note" rows="5" aria-label="오늘 나에게 쓰는 편지" placeholder="오늘 나에게 꼭 들려주고 싶은 말은…"></textarea><button id="noteSave" type="button">나에게 편지 보관하기</button></div></section>
<footer>DJ의 편지 · 무료 공개 클래식 감상<br/>역사적 사실과 문학적 해석을 구분해 감상해 주세요. 심리 치료를 대체하지 않습니다.<br/>
<a href="./video-sources.html" target="_blank" rel="noopener noreferrer">영상 출처와 이용허락</a> · <a href="https://commons.wikimedia.org/wiki/Category:Audio_files_of_classical_music" target="_blank" rel="noopener noreferrer">클래식 녹음 출처</a>
</footer>
<div class="dj-toast" id="toast" role="status" hidden></div>
<audio id="programAudio" preload="none" hidden></audio>
<noscript><p>음악과 풍경을 감상하려면 브라우저에서 JavaScript를 허용해 주세요.</p></noscript>
</main></body></html>
'''
(DOCS / 'index.html').write_text(html, encoding='utf-8')
# Remove obsolete deployed code, not the actual media or private notes.
for name in ['app.js', 'style.css']:
    (DOCS / name).unlink(missing_ok=True)

(ROOT / 'README.md').write_text('''# DJ의 편지

무료 클래식 라디오와 자연 풍경 감상 웹앱입니다.

- 운영 주소: https://tazan12.github.io/--/
- 배포: GitHub Pages, `docs/` 폴더
- 콘텐츠: 남성 DJ 낭독 12편, 서로 다른 실사 영상 12편, 작품별 이야기
- 영상/음성/표지: `docs/assets/`에 독립 보관
- 클래식 녹음: Wikimedia Commons의 외부 연주 파일. 원본 서버의 접속 제한은 별도입니다.

## 플레이어
`episodes.js`는 이야기 정보, `player.js`는 재생 상태, `player.css`는 화면 배치입니다.
무음 영상은 자동재생을 요청하며 반복 경계에서 두 영상 사이를 짧게 전환합니다.
영상 재생 버튼은 표시하지 않습니다. 자동재생을 막는 브라우저에서는 실제 사용자의 터치나 키 입력에서 다시 시도합니다.
기기의 동작 줄이기 설정과 감상 설정의 정지 화면 선택은 존중합니다.
음성/음악은 하나의 audio 요소를 재사용하여 중복 재생을 방지합니다.

## 권리
무료 공개라도 녹음/영상별 이용허락을 따라야 합니다.
영상 출처는 `docs/video-sources.html`과 `docs/assets/films/manifest.json`에 기록되어 있습니다.
`dj-letter/`는 이전 제작 과정의 코드 기록이며 배포에 포함되지 않습니다.
''', encoding='utf-8')
# Retire the one-time external import. Future runs only verify local assets.
(ROOT / 'scripts' / 'prepare-dj-media.py').write_text('''#!/usr/bin/env python3
"""Verify local media already preserved in GitHub; no external download needed."""
from pathlib import Path
root = Path(__file__).resolve().parents[1] / 'docs' / 'assets'
for n in range(1, 13):
    for folder, ext in [('films', 'mp4'), ('films', 'webp'), ('voice', 'mp3')]:
        p = root / folder / f'ep{n:02}.{ext}'
        assert p.is_file() and p.stat().st_size > 1000, f'Missing media: {p}'
print('PASS: 12 local videos, 12 posters, 12 narrations')
''', encoding='utf-8')

for name in ['episodes.js', 'player.js']:
    subprocess.run(['node', '--check', str(DOCS / name)], check=True)
for path in DOCS.rglob('*'):
    if path.suffix in {'.html', '.js', '.css', '.json', '.md'}:
        text = path.read_text(encoding='utf-8')
        assert 'higgsfield.app' not in text and 'd8j0ntlcm91z4.cloudfront.net' not in text, f'Legacy runtime link: {path}'
assert 'filmToggle' not in html
assert 'id="motion"' not in html
assert 'id="programAudio"' in html
print('PASS: independent assets, no film play overlays, new controller syntax verified')
