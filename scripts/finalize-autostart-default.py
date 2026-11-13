#!/usr/bin/env python3
"""Apply the requested automatic scenery default; keep an explicit session pause."""
from pathlib import Path
import subprocess
root=Path(__file__).resolve().parents[1]
paths=['scripts/scenery-stable.js','scripts/repair-playback-stability.py','docs/scenery.js','docs/player.js','docs/index.html','docs/playback-release.json']
handler="""  reduce.addEventListener?.('change', event => {
    if (explicitStill) return;
    still = event.matches; $('still').checked = still;
    if (still) pause(); else resume();
  });
"""
for name in paths:
 p=root/name
 s=p.read_text(encoding='utf-8').replace('20261114-stable2','20261114-stable3')
 if name.endswith('scenery.js') or name.endswith('scenery-stable.js'):
  s=s.replace('still = reduce.matches, explicitStill = false','still = false, explicitStill = false')
  s=s.replace(handler,'  // Reduced-motion is respected for UI transitions in CSS. The requested\n  // content plays automatically; only an explicit session choice pauses it.\n')
  assert 'still = reduce.matches' not in s
 if name=='docs/index.html':
  s=s.replace('동작 줄이기는 처음에만 따릅니다. 편지 듣기를 누르면 풍경도 함께 시작합니다. 영상 재생이 제한되면 같은 실사 장면의 호환 형식으로 이어집니다.','풍경은 자동으로 재생됩니다. 정지 화면은 위 설정을 직접 선택했을 때만 적용됩니다. 영상이 제한되면 같은 실사 장면의 호환 형식으로 이어집니다.')
 p.write_text(s,encoding='utf-8')
subprocess.run(['node','--check',str(root/'docs/scenery.js')],check=True)
print('PASS: automatic scenery is the default, no inherited hidden still-mode')
