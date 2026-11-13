#!/usr/bin/env python3
"""Build one coherent journal release from the validated static media app."""
from pathlib import Path
import json,re,shutil,struct,zlib,math
ROOT=Path(__file__).resolve().parents[1]
DOCS=ROOT/'docs'; SRC=ROOT/'scripts'/'mind-journal'; BASE=SRC/'base'
VERSION='mind-20261114-1'
BASE.mkdir(parents=True,exist_ok=True)
for name in ['index.html','player.js']:
    target=BASE/name
    if not target.exists():
        source=(DOCS/name).read_text(encoding='utf-8')
        if 'MIND_JOURNAL_RELEASE' in source:
            raise RuntimeError('Original baseline missing: refusing to patch generated HTML')
        target.write_text(source,encoding='utf-8')
html=(BASE/'index.html').read_text(encoding='utf-8')
player=(BASE/'player.js').read_text(encoding='utf-8')
for s in ['id="film"','id="filmMotion"','id="programAudio"','id="write"']:
    assert s in html,s
html=html.replace('<html lang="ko">','<html lang="ko" data-mind-theme="moon">')
html=html.replace('<body>','<body data-app-view="listen">\n<!-- MIND_JOURNAL_RELEASE -->')
html=re.sub(r'<meta name="dj-release" content="[^"]+"/>',f'<meta name="dj-release" content="{VERSION}"/>',html)
html=re.sub(r'\?v=20261114-[a-zA-Z0-9]+',f'?v={VERSION}',html)
html=html.replace('</head>',f'''<meta name="apple-mobile-web-app-capable" content="yes"/>
<meta name="apple-mobile-web-app-title" content="DJ의 편지"/>
<link rel="manifest" href="./manifest.webmanifest"/>
<link rel="apple-touch-icon" href="./assets/app-icon-192.png"/>
<link rel="stylesheet" href="./mind-journal.css?v={VERSION}"/>
<script src="./mind-store.js?v={VERSION}" defer></script>
<script src="./mind-journal.js?v={VERSION}" defer></script>
</head>''')
nav='''<nav aria-label="주 메뉴"><a href="#listen" data-nav-view="listen">음악 감상</a><a href="#write" data-nav-view="journal">마음일기</a><a href="#episodes" data-nav-view="library">음악서재</a></nav><span class="header-datestamp" id="greetingDate"></span>'''
html,n=re.subn(r'<nav aria-label="주 메뉴">.*?</nav>',lambda _:nav,html,count=1,flags=re.S);assert n==1
html=html.replace('<section class="dj-hero" id="listen"','<section class="dj-hero app-view" data-app-view="listen" id="listen"')
html=html.replace('<section class="dj-reader"','<section class="dj-reader app-view" data-app-view="listen"')
html=html.replace('<section class="dj-library" id="episodes"','<section class="dj-library app-view" data-app-view="library" hidden id="episodes"')
html=html.replace('<a href="#episodes">이야기 둘러보기</a>','<a href="#write" data-nav-view="journal">마음 한 줄 남기기</a>')
html=html.replace('<p class="dj-hint">한국어 남성 DJ · 열두 통의 음악 편지 · 무료 감상</p>','''<p class="dj-hint">한국어 남성 DJ · 열두 통의 음악 편지 · 무료 감상</p>
<div class="daily-whisper"><strong>오늘, 당신에게</strong><span id="dailyWhisper">마음에도 숨을 고르는 한 페이지가 필요하니까요.</span></div>''')
html=html.replace('<button id="wide" type="button" aria-pressed="false">넓게 감상</button>','''<button id="wide" type="button" aria-pressed="false">넓게 감상</button>
<button id="likeTrack" class="favorite-button" type="button" aria-pressed="false">♡ 간직하기</button>
<button id="writeWithTrack" type="button">이 곡과 일기 쓰기</button>''')
old='<label for="volume">소리 크기 <input id="volume" type="range" min="0" max="100" value="75"/></label>'
assert old in html
html=html.replace(old,old+'''
<label class="sleep-control" for="sleepTimer">음악 자동 멈춤 <select id="sleepTimer"><option value="0">끄기</option><option value="10">10분</option><option value="20">20분</option><option value="30">30분</option><option value="60">60분</option></select></label><small id="sleepStatus">원하는 만큼만 듣고 편안히 쉬세요.</small>''')
html=html.replace('<div class="dj-grid" id="cards">','''<div class="library-favorites"><h2>다시 꺼내 듣고 싶은 편지</h2><p>좋아하는 음악은 가까운 곳에 남겨 두세요.</p><div id="favoriteList" class="favorite-list"></div></div><div class="dj-grid" id="cards">''')
journal=(SRC/'journal.html').read_text(encoding='utf-8')
html,n=re.subn(r'<section class="dj-journal" id="write".*?</section>',lambda _:journal,html,count=1,flags=re.S);assert n==1
html=html.replace('</footer>','''<br/><button class="app-footer-link" id="footerBackup" type="button">기록 보관과 개인정보 안내</button><p class="connection-note" id="connectionStatus">기기에만 남는 마음 · 무료 음악 서재</p></footer>''')
extras='''
<nav class="app-bottom-nav" aria-label="모바일 메뉴"><a href="#listen" data-nav-view="listen"><span aria-hidden="true">♪</span>감상</a><a href="#write" data-nav-view="journal"><span aria-hidden="true">✎</span>마음일기</a><a href="#episodes" data-nav-view="library"><span aria-hidden="true">♡</span>음악서재</a></nav>
<div class="mini-radio" id="miniRadio" aria-label="음악 조작" hidden><img id="miniImage" alt=""/><div class="mini-copy"><strong id="miniTitle"></strong><small id="miniPhase"></small></div><button id="miniToggle" type="button" aria-label="낭독·음악 듣기">▶</button><button id="miniNext" type="button" aria-label="다음 편지">⏭</button><a href="#listen" data-nav-view="listen">감상으로</a></div>
'''
html=html.replace('</main></body>',extras+'</main></body>')
# Existing playback is retained; remove only the obsolete one-note storage handler.
player=re.sub(r"^\s*\$\('note'\)\.value = .*?;\n",'',player,flags=re.M)
player,n=re.subn(r"  \$\('noteSave'\)\.onclick = \(\) => \{.*?\n  \};\n",'',player,count=1,flags=re.S);assert n==1
api='''  // Stable bridge for journal recommendations, timer and mini-player.
  window.DJ_PLAYER = Object.freeze({
    select(n, autoplay=false) {
      if (!Number.isInteger(n) || n<0 || n>=stories.length) return;
      setEpisode(n); if (autoplay) startNarration();
    },
    pause() {
      invalidateAudio(); audioStatus('음악을 잠시 쉬어 둡니다.'); updateControls();
    },
    state() { return {episode:index,phase,playing:!audio.paused,wanted}; }
  });
'''
assert '  setEpisode(0); renderMoods();' in player
player=player.replace('  setEpisode(0); renderMoods();',api+'  setEpisode(0); renderMoods();')
(DOCS/'index.html').write_text(html,encoding='utf-8')
(DOCS/'player.js').write_text(player,encoding='utf-8')
for source,target in [('journal.css','mind-journal.css'),('journal.js','mind-journal.js'),('store.js','mind-store.js'),('sw.js','sw.js')]:
    shutil.copyfile(SRC/source,DOCS/target)
manifest={'id':'./','name':'DJ의 편지 · 마음서재','short_name':'마음서재','description':'클래식과 함께 남기는 날짜별 마음일기. 기록은 기기에만 보관됩니다.','lang':'ko','start_url':'./?source=installed#write','scope':'./','display':'standalone','background_color':'#12192b','theme_color':'#12192b','icons':[{'src':'./assets/app-icon-192.png','sizes':'192x192','type':'image/png','purpose':'any'},{'src':'./assets/app-icon-512.png','sizes':'512x512','type':'image/png','purpose':'any maskable'}],'shortcuts':[{'name':'오늘의 마음일기','url':'./#write'},{'name':'클래식 감상','url':'./#listen'}]}
(DOCS/'manifest.webmanifest').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
# Small first-party PNG launcher icons; no library or network dependency.
def png_icon(size):
    rows=[]
    for y in range(size):
        row=bytearray([0])
        for x in range(size):
            u,v=x/size,y/size;col=(23,31,51)
            if (u-.49)**2+(v-.43)**2<.19**2 and (u-.57)**2+(v-.37)**2>.17**2:col=(230,197,157)
            if .27<u<.73 and .60<v<.78:
                if v<.615 or v>.765 or u<.285 or u>.715 or abs(v-(.61+abs(u-.5)*.58))<.01:col=(213,180,162)
            if (u-.71)**2+(v-.30)**2<.012**2:col=(241,222,185)
            row.extend(col)
        rows.append(row)
    def chunk(tag,data):return struct.pack('!I',len(data))+tag+data+struct.pack('!I',zlib.crc32(tag+data)&0xffffffff)
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('!2I5B',size,size,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(b''.join(rows),9))+chunk(b'IEND',b'')
for size in [192,512]:(DOCS/'assets'/f'app-icon-{size}.png').write_bytes(png_icon(size))
# Validation occurs before committing: reject broken references or media regressions.
ids=re.findall(r'\bid="([^"]+)"',html)
assert len(ids)==len(set(ids)), 'Duplicate HTML ids'
for source in ['player.js','mind-journal.js','scenery.js']:
    js=(DOCS/source).read_text(encoding='utf-8')
    for id in re.findall(r"\$\('([^']+)'\)",js):
        assert id in ids, f'Missing element #{id} required by {source}'
assert html.count('<video ')==1 and 'filmToggle' not in html
assert 'higgsfield.app' not in html
assert "$('noteSave')" not in player and 'DJ_PLAYER' in player
assert (DOCS/'scenery.js').is_file()
(DOCS/'journal-release.json').write_text(json.dumps({'release':VERSION,'storageSchema':1,'journal':'local-only','mediaEngine':'20261114-stable3','features':['dated journal','calendar','moods','themes','backup-restore','favorites','sleep timer','offline-shell']},indent=2),encoding='utf-8')
print('PASS: journal integrated; one preserved video element; all UI element references resolve.')

# JOURNAL_FOCUS_POSTBUILD
import runpy
focus=ROOT/"scripts"/"journal-focus"/"refine.py"
if focus.exists(): runpy.run_path(str(focus),run_name="__main__")
