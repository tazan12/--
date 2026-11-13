#!/usr/bin/env python3
from pathlib import Path
root=Path(__file__).resolve().parent
p=root/'journal.js';s=p.read_text(encoding='utf-8')
anchor="window.addEventListener('hashchange',()=>setView(hashView()));"
extra="""$('cards').addEventListener('click',e=>{if(e.target.closest('.dj-card[data-episode]'))go('listen');});
$('calendarJump').onclick=()=>{$('calendarMonth').scrollIntoView({block:'start',behavior:'smooth'});};
"""
if "$('calendarJump').onclick" not in s:
    assert anchor in s;s=s.replace(anchor,extra+anchor)
s=s.replace("b.onclick=()=>chooseDate(date);", "b.onclick=()=>{chooseDate(date);if(innerWidth<=760)$('selectedDateLabel').scrollIntoView({block:'start',behavior:'smooth'});};")
# A local-only empty diary needs no timers, retries or artificial streaks.
s=s.replace("window.addEventListener('hashchange',()=>setView(hashView()));", "window.addEventListener('hashchange',()=>{if(!setView(hashView()))history.replaceState(null,'','#write');});")
p.write_text(s,encoding='utf-8')
p=root/'journal.html';s=p.read_text(encoding='utf-8')
s=s.replace('placeholder="오늘 마음에 남은 장면을 천천히 적어 보세요.\\n단 한 줄이어도, 다 쓰지 못해도 괜찮아요."','placeholder="오늘 마음에 남은 장면을 천천히 적어 보세요. 단 한 줄이어도 괜찮아요."')
needle='<div class="journal-layout">'
if 'id="calendarJump"' not in s:
    s=s.replace(needle,'<button id="calendarJump" class="mobile-calendar-jump" type="button">달력에서 날짜 고르기 <span aria-hidden="true">↓</span></button>\n'+needle)
p.write_text(s,encoding='utf-8')
p=root/'journal.css';s=p.read_text(encoding='utf-8')
if 'mobile-calendar-jump' not in s:
    s+='''\n.mobile-calendar-jump{display:none}\n@media(max-width:760px){.mobile-calendar-jump{display:flex;justify-content:space-between;align-items:center;width:100%;margin:0 0 16px;padding:10px 14px;border:1px solid var(--line);border-radius:11px;background:var(--mind-panel);color:var(--muted);font-size:12px}.theme-choices{margin-bottom:14px}.mind-heading{margin-bottom:19px}.mind-heading p{font-size:11px}}\n'''
p.write_text(s,encoding='utf-8')
print('Navigation and mobile calendar refinements applied.')
