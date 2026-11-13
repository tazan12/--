#!/usr/bin/env python3
"""Idempotent journal-only refinement. Never changes diary storage or media assets."""
from pathlib import Path
import re, json, shutil
ROOT=Path(__file__).resolve().parents[2]
D=ROOT/'docs'
VERSION='focus-20261114-2'
def replace_once(s,old,new,label):
    if old not in s: raise RuntimeError('Unexpected source: '+label)
    return s.replace(old,new,1)

# Single audio owner: context routing prevents voice from entering the journal.
p=D/'player.js';s=p.read_text(encoding='utf-8')
if 'JOURNAL_FOCUS_AUDIO_V1' not in s:
    s=replace_once(s,'  let volume = 0.75;','''  /* JOURNAL_FOCUS_AUDIO_V1 */
  let journalMode = false, journalSoundEnabled = true;
  let volume = 0.75;''','audio state')
    s=replace_once(s,'  function playProgram() {','''  function playProgram() {
    if (journalMode && !journalSoundEnabled) { invalidateAudio(); updateControls(); return; }
    if (journalMode && phase === 'dj') { beginMusic(); return; }''','play guard')
    s=replace_once(s,'  function startNarration() {','''  function startNarration() {
    if (journalMode) { if (journalSoundEnabled) beginMusic(); return; }''','voice guard')
    s=replace_once(s,'  function beginMusic() {','''  function beginMusic() {
    if (journalMode && !journalSoundEnabled) { invalidateAudio(); updateControls(); return; }''','music guard')
    s=replace_once(s,'  function toggleProgram() {','''  function toggleProgram() {
    if (journalMode) {
      if (wanted || !audio.paused) { journalSoundEnabled=false; invalidateAudio(); audioStatus('음악을 끄고, 조용히 기록합니다.'); updateControls(); }
      else { journalSoundEnabled=true; if (phase==='music' && audio.getAttribute('src') && !audio.ended && !audio.error) playProgram(); else beginMusic(); }
      return;
    }''','context toggle')
    s=replace_once(s,"    $('seek').setAttribute('aria-valuetext', `${$('clock').textContent} / ${$('duration').textContent}`);","""    $('seek').setAttribute('aria-valuetext', `${$('clock').textContent} / ${$('duration').textContent}`);
    window.dispatchEvent(new Event('dj-player-change'));""",'state notification')
    old="    state() { return {episode:index,phase,playing:!audio.paused,wanted}; }"
    new="""    // Journal uses only these explicit, narration-free operations.
    journal(active, enabled=true) {
      journalMode=Boolean(active);
      if (!journalMode) { updateControls(); return; }
      journalSoundEnabled=Boolean(enabled);
      if (!journalSoundEnabled) { invalidateAudio(); audioStatus('음악을 끄고, 조용히 기록합니다.'); updateControls(); return; }
      if (phase==='music' && audio.getAttribute('src') && !audio.ended && !audio.error) {
        if (audio.paused) playProgram(); else updateControls();
      } else beginMusic();
    },
    music(n=index, autoplay=true) {
      if (!Number.isInteger(n) || n<0 || n>=stories.length) return;
      if (journalMode) journalSoundEnabled=Boolean(autoplay);
      if (n!==index) setEpisode(n);
      if (!autoplay) { invalidateAudio(); updateControls(); return; }
      if (phase==='music' && audio.getAttribute('src') && !audio.ended && !audio.error) playProgram();
      else beginMusic();
    },
    state() { return {episode:index,phase,playing:!audio.paused,wanted,journalMode,journalSoundEnabled}; }"""
    s=replace_once(s,old,new,'public audio bridge')
    p.write_text(s,encoding='utf-8')

p=D/'mind-journal.js';s=p.read_text(encoding='utf-8')
if 'JOURNAL_FOCUS_VIEW_V1' not in s:
    block="""
/* JOURNAL_FOCUS_VIEW_V1: sound preference is separate from private diary records. */
const journalSoundKey='dj-letter-journal-music-v1';
let journalSoundEnabled=true;
try { journalSoundEnabled=storage.getItem(journalSoundKey)!=='off'; } catch (_) {}
function rememberJournalSound(value){
 journalSoundEnabled=Boolean(value);
 try { storage.setItem(journalSoundKey,value?'on':'off'); } catch (_) {}
}
function syncJournalSound(){
 const P=window.DJ_PLAYER,a=$('programAudio'),st=P?.state();
 if(!st||!$('journalMusicToggle'))return;
 const n=st.episode,ep=stories[n];
 if(ep){$('journalMusicSelect').value=String(n);const src=`./assets/films/ep${String(n+1).padStart(2,'0')}.webp`;if($('journalMusicCover').getAttribute('src')!==src)$('journalMusicCover').src=src;}
 const active=journalSoundEnabled&&(st.wanted||st.playing);
 $('journalMusicToggle').textContent=active?'음악 끄기':'음악 켜기';
 $('journalMusicToggle').setAttribute('aria-pressed',String(active));
 $('journalMusicToggle').setAttribute('aria-label',active?'마음일기 음악 끄기':'낭독 없이 클래식 음악 켜기');
 $('journalMusicStatus').textContent=!journalSoundEnabled?'음악 꺼짐 · 조용히 기록해요':st.phase==='music'&&st.playing&&a.readyState>=2?'클래식 재생 중 · 낭독 없음':st.wanted?'클래식 연주를 준비하고 있어요':'음악 켜기를 누르면 연주가 시작됩니다';
 if(document.activeElement!==$('journalMusicVolume'))$('journalMusicVolume').value=$('volume').value;
 const bad=journalSoundEnabled&&st.phase==='music'&&!$('musicSource').hidden;
 $('journalMusicSource').hidden=!bad;
 if(bad){$('journalMusicSource').href=$('musicSource').href;$('journalMusicStatus').textContent='음원 연결이 어려워요. 다시 켜거나 원본을 확인해 주세요.';}
}
function setJournalSound(value){
 rememberJournalSound(value);
 if(view==='journal')window.DJ_PLAYER?.journal(true,journalSoundEnabled);
 syncJournalSound();
}
function playJournalTrack(n){
 if(!Number.isInteger(n)||n<0||n>=stories.length)return;
 rememberJournalSound(true);window.DJ_PLAYER?.music(n,true);syncCurrent();
}
function setupJournalSound(){
 $('journalMusicSelect').replaceChildren(...stories.map((ep,i)=>{const o=document.createElement('option');o.value=String(i);o.textContent=`${ep.composer} · ${ep.music}`;return o;}));
 $('journalMusicToggle').onclick=()=>{const st=window.DJ_PLAYER?.state();setJournalSound(!(journalSoundEnabled&&(st?.wanted||st?.playing)));};
 $('journalMusicNext').onclick=()=>{const st=window.DJ_PLAYER?.state();if(!st)return;window.DJ_PLAYER.music((st.episode+1)%stories.length,journalSoundEnabled);syncCurrent();};
 $('journalMusicSelect').onchange=()=>{window.DJ_PLAYER?.music(Number($('journalMusicSelect').value),journalSoundEnabled);syncCurrent();};
 $('journalMusicVolume').oninput=()=>{$('volume').value=$('journalMusicVolume').value;$('volume').dispatchEvent(new Event('input',{bubbles:true}));};
 window.addEventListener('dj-player-change',syncJournalSound);
 window.addEventListener('storage',e=>{if(e.key!==journalSoundKey)return;journalSoundEnabled=e.newValue!=='off';if(!journalSoundEnabled&&view==='journal')window.DJ_PLAYER?.journal(true,false);syncJournalSound();});
 syncJournalSound();
}
"""
    s=replace_once(s,"const blank=d=>",block+"\nconst blank=d=>",'journal helpers')
    s=replace_once(s,"view=name;window.DJ_SCENERY?.setSuspended(name!=='listen');","const previousView=view;view=name;window.DJ_SCENERY?.setSuspended(name!=='listen');",'view transition')
    s=replace_once(s,"syncMini();if(scroll)window.scrollTo", "if(name==='journal'&&previousView!=='journal')window.DJ_PLAYER?.journal(true,journalSoundEnabled);else if(name!=='journal')window.DJ_PLAYER?.journal(false);syncMini();if(scroll)window.scrollTo",'journal context')
    s=replace_once(s,"function playEpisode(n){if(Number.isInteger(n)&&n>=0&&n<stories.length){window.DJ_PLAYER?.select(n,true);syncCurrent();}}", "function playEpisode(n){if(Number.isInteger(n)&&n>=0&&n<stories.length){if(view==='journal')playJournalTrack(n);else window.DJ_PLAYER?.select(n,true);syncCurrent();}}",'recommended track route')
    s=replace_once(s,"$('miniRadio').hidden=view==='listen'||!has;", "$('miniRadio').hidden=view!=='library'||!has;",'no floating diary widget')
    s=replace_once(s,"$('miniToggle').setAttribute('aria-label',a&&!a.paused?'낭독·음악 일시정지':'낭독·음악 듣기');}","$('miniToggle').setAttribute('aria-label',a&&!a.paused?'낭독·음악 일시정지':'낭독·음악 듣기');syncJournalSound();}",'sync sound state')
    s=replace_once(s,"timerEnd=0;window.DJ_PLAYER?.pause();", "timerEnd=0;if(view==='journal')rememberJournalSound(false);window.DJ_PLAYER?.pause();syncJournalSound();",'sleep timer silence')
    old="$('calendarJump').onclick=()=>{$('calendarMonth').scrollIntoView({block:'start',behavior:'smooth'});};"
    new="""$('calendarJump').onclick=()=>{const open=$('write').classList.toggle('calendar-is-open');$('calendarJump').setAttribute('aria-expanded',String(open));$('calendarJump').textContent=open?'달력 · 지난 기록 접기 ↑':'달력 · 지난 기록 펼치기 ↓';};"""
    s=replace_once(s,old,new,'mobile calendar')
    s=s.replace("if(innerWidth<=760)$('selectedDateLabel').scrollIntoView({block:'start',behavior:'smooth'});", "if(innerWidth<=760){$('write').classList.remove('calendar-is-open');$('calendarJump').setAttribute('aria-expanded','false');$('calendarJump').textContent='달력 · 지난 기록 펼치기 ↓';$('selectedDateLabel').scrollIntoView({block:'center',behavior:'auto'});}")
    s=replace_once(s,"importLegacy();loadEntries();loadDay(selected);", "setupJournalSound();importLegacy();loadEntries();loadDay(selected);",'startup order')
    p.write_text(s,encoding='utf-8')

p=D/'index.html';s=p.read_text(encoding='utf-8')
if 'id="journalMusicToggle"' not in s:
    start=s.index('  <header class="mind-heading">');end=s.index('  <button id="calendarJump"',start)
    heading='''  <header class="mind-heading"><div><span class="mind-eyebrow">A QUIET PAGE, JUST FOR YOU</span><h1 id="mindTitle">오늘의 마음, 한 장.</h1><p>음악은 곁에 두고, 이야기는 나에게.</p></div>
    <div class="journal-heading-tools"><div class="theme-choices" id="themeChoices" role="group" aria-label="일기 테마 선택">
      <button type="button" data-theme-choice="moon" aria-pressed="true"><i class="theme-dot" aria-hidden="true"></i>달빛 서재</button>
      <button type="button" data-theme-choice="forest" aria-pressed="false"><i class="theme-dot" aria-hidden="true"></i>숲의 안부</button>
      <button type="button" data-theme-choice="rose" aria-pressed="false"><i class="theme-dot" aria-hidden="true"></i>다정한 오후</button>
    </div><button class="quiet-button" id="openBackup" type="button">기록 보관 · 백업</button></div>
  </header>
  <section class="journal-sound-panel" aria-label="마음일기 배경 음악">
    <img id="journalMusicCover" class="journal-sound-cover" src="./assets/films/ep01.webp" alt=""/>
    <div class="journal-sound-meta"><label class="journal-sound-caption" for="journalMusicSelect">글을 위한 클래식 · 낭독 없이</label><select id="journalMusicSelect" aria-label="일기 배경 음악 선택"></select><span id="journalMusicStatus" class="journal-sound-status" role="status" aria-live="polite">소리 없이 기록할 수도 있어요</span><a id="journalMusicSource" href="https://commons.wikimedia.org/" target="_blank" rel="noopener noreferrer" hidden>연주 원본 확인</a></div>
    <div class="journal-sound-controls"><label class="journal-volume">음량<input id="journalMusicVolume" type="range" min="0" max="100" value="75" aria-label="마음일기 음악 음량"/></label><button id="journalMusicToggle" type="button" aria-pressed="false">음악 켜기</button><button id="journalMusicNext" type="button" aria-label="다음 클래식 곡">다음 곡</button></div>
  </section>
'''
    s=s[:start]+heading+s[end:]
    s=s.replace('<button id="calendarJump" class="mobile-calendar-jump" type="button">달력에서 날짜 고르기 <span aria-hidden="true">↓</span></button>', '<button id="calendarJump" class="mobile-calendar-jump" type="button" aria-expanded="false">달력 · 지난 기록 펼치기 ↓</button>')
    s,n=re.subn(r'(<div class="writing-prompt">.*?</div>)',r'<details class="writing-help"><summary>어디서부터 쓸지 모르겠다면</summary>\1</details>',s,count=1,flags=re.S)
    assert n==1,'Writing prompt missing'
    s=s.replace('id="recommendPlay" type="button">함께 듣기','id="recommendPlay" type="button">연주만 듣기')
    s=s.replace('id="playAttached" type="button" hidden>다시 듣기','id="playAttached" type="button" hidden>연주 다시 듣기')
if './journal-focus.css' not in s:
    s=s.replace('</head>',f'<link rel="stylesheet" href="./journal-focus.css?v={VERSION}"/>\n</head>')
s=re.sub(r'(<meta name="dj-release" content=")[^"]+',r'\g<1>'+VERSION,s)
s=re.sub(r'(\./(?:player|mind-store|mind-journal|scenery|episodes|journal-focus)\.(?:js|css)\?v=)[^"\s]+',r'\g<1>'+VERSION,s)
p.write_text(s,encoding='utf-8')
shutil.copyfile(Path(__file__).with_name('layout.css'),D/'journal-focus.css')

# Preserve diary data during a cache update; only the offline shell version changes.
p=D/'sw.js';s=p.read_text(encoding='utf-8');s=re.sub(r"const VERSION='[^']+'",f"const VERSION='{VERSION}'",s)
if "'./journal-focus.css?v='+VERSION" not in s:s=s.replace("const SHELL=[", "const SHELL=['./journal-focus.css?v='+VERSION,")
s=s.replace('player|episodes|scenery|mind-store|mind-journal)', 'player|episodes|scenery|mind-store|mind-journal|journal-focus)')
p.write_text(s,encoding='utf-8')

# Rebuilds must retain this refinement instead of restoring the previous UX.
builder=ROOT/'scripts'/'build-mind-journal.py'
if builder.exists():
    b=builder.read_text(encoding='utf-8')
    if 'JOURNAL_FOCUS_POSTBUILD' not in b:
        b+='\n# JOURNAL_FOCUS_POSTBUILD\nimport runpy\nfocus=ROOT/"scripts"/"journal-focus"/"refine.py"\nif focus.exists(): runpy.run_path(str(focus),run_name="__main__")\n'
        builder.write_text(b,encoding='utf-8')
report=D/'journal-release.json'
if report.exists():
    data=json.loads(report.read_text());data['release']=VERSION;data['journalAudio']='classical-only, explicit persistent on/off';report.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
ids=re.findall(r'\bid="([^"]+)"',(D/'index.html').read_text())
assert len(ids)==len(set(ids)),'Duplicate HTML IDs'
for name in ['mind-journal.js','player.js']:
    for element in re.findall(r"\$\('([^']+)'\)",(D/name).read_text()):
        assert element in ids, f'Missing #{element} in {name}'
assert (D/'index.html').read_text().count('<video ')==1
assert 'filmToggle' not in (D/'index.html').read_text()
assert 'journalSoundKey' in (D/'mind-journal.js').read_text()
print('PASS: diary-only classical context, explicit sound switch, no store/media changes, balanced UI and cache version.')
