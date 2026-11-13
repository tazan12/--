#!/usr/bin/env python3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
DOCS=ROOT/'docs'; SRC=ROOT/'scripts'/'mind-journal'
p=DOCS/'scenery.js';s=p.read_text(encoding='utf-8')
if 'suspendedByView' not in s:
    s=s.replace("const desired = () => !still && !document.hidden;", "let suspendedByView = false;\n  const desired = () => !still && !document.hidden && !suspendedByView;")
    s=s.replace("    setEpisode, resume, userStart,", "    setEpisode, resume, userStart,\n    setSuspended(value) {\n      suspendedByView = Boolean(value);\n      if (suspendedByView) pause();\n      else { lastProgress = performance.now(); resume(); }\n    },")
    assert 'setSuspended(value)' in s
    p.write_text(s,encoding='utf-8')
p=SRC/'journal.js';s=p.read_text(encoding='utf-8')
old="view=name;document.body.dataset.appView=name;"
new="view=name;window.DJ_SCENERY?.setSuspended(name!=='listen');document.body.dataset.appView=name;"
if new not in s:
    assert old in s;s=s.replace(old,new)
p.write_text(s,encoding='utf-8')
print('Hidden scenery pauses without interrupting radio audio.')
