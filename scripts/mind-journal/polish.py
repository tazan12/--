#!/usr/bin/env python3
"""Small, idempotent source checks/fixes for the first journal release."""
from pathlib import Path
root=Path(__file__).resolve().parent
p=root/'journal.js';s=p.read_text(encoding='utf-8')
s=s.replace("if(!S||!$('mindJournalReady')&&!$('mindTitle'))return;","if(!S||!$('mindTitle'))return;")
s=s.replace("`${m[1]}한 마음을 적는 동안, 이런 선율은 어떨까요.`","`${m[1]}의 순간을 적는 동안, 이런 선율은 어떨까요.`")
s=s.replace("if('serviceWorker'in navigator&&location.protocol==='https:')", "if('serviceWorker'in navigator&&(location.protocol==='https:'||location.hostname==='localhost'||location.hostname==='127.0.0.1'))")
s=s.replace("$('writeWithTrack').onclick=()=>{if(!save())return;chooseDate(S.dateKey());go('journal');entry.episode=current;renderTrack();changed();};", "$('writeWithTrack').onclick=()=>{if(!save())return;chooseDate(S.dateKey());if(conflict)return;go('journal');entry.episode=current;renderTrack();changed();};")
s=s.replace("$('undoDelete').onclick=()=>{if(!deleted)return;", "$('undoDelete').onclick=()=>{if(!deleted||!save())return;")
s=s.replace("function hashView(){return location.hash==='#write'||location.hash==='#journal'?'journal':location.hash==='#episodes'?'library':'listen';}", "function hashView(){return location.hash==='#write'||location.hash==='#journal'?'journal':location.hash==='#episodes'?'library':'listen';}")
p.write_text(s,encoding='utf-8')
print('Journal source checks completed.')
