#!/usr/bin/env python3
from pathlib import Path
import shutil
ROOT=Path(__file__).resolve().parents[2]
# One-off migration jobs must not overwrite the current journal release later.
archive=ROOT/'maintenance'/'legacy-workflows';archive.mkdir(parents=True,exist_ok=True)
for name in ['migrate-dj-media.yml','finalize-natural-player.yml','repair-playback-stability.yml']:
    p=ROOT/'.github'/'workflows'/name
    if p.exists():shutil.move(str(p),str(archive/name))
p=ROOT/'.github'/'workflows'/'deploy-dj-letter.yml'
s=p.read_text(encoding='utf-8')
if 'Validate the diary and player before publishing' not in s:
    step='''      - name: Validate the diary and player before publishing
        run: |
          node --check docs/player.js
          node --check docs/scenery.js
          node --check docs/mind-journal.js
          node --check docs/sw.js
          node --test tests/mind-store.test.cjs
'''
    anchor='      - name: Configure GitHub Pages\n'
    assert anchor in s;s=s.replace(anchor,step+anchor)
    p.write_text(s,encoding='utf-8')
(ROOT/'README.md').write_text('''# DJ의 편지 · 마음서재

클래식 낭독과 실사 풍경, 날짜별 마음일기가 함께하는 무료 공개 웹앱입니다.

**운영 주소:** https://tazan12.github.io/--/

## 사용자 기능
- 기존 남성 DJ 낭독 12편과 실제 클래식 감상, 곡별 실사 영상
- 날짜별 제목·본문·감정·다정한 한 줄·음악 연결, 달력과 검색
- 달빛 서재 / 숲의 안부 / 다정한 오후 테마
- 좋아하는 편지, 듣기 자동 멈춤, 일기 작성 중 미니 오디오바
- 일기 JSON 백업·복원, 삭제 되돌리기, 다른 창의 변경 충돌 감지
- 오프라인 기본 화면·일기, 브라우저 지원 시 홈 화면 설치

## 데이터와 운영 경계
일기는 사용자의 브라우저 localStorage에만 저장됩니다. 서버 전송, 로그인, 분석 추적, AI API 호출은 없습니다. 저장 내용과 백업은 암호화되지 않습니다. 공용 기기 사용에 주의하고, 브라우저 데이터 삭제 전 백업해야 합니다. 기기 간 자동 동기화는 없습니다. 음악·풍경 영상은 온라인 감상입니다.

## 개발과 배포
- 실제 사이트: `docs/`
- 일기 소스: `scripts/mind-journal/`
- 재빌드: polish.py → refine.py → sustainability.py → build-mind-journal.py
- 저장 테스트: `node --test tests/mind-store.test.cjs`
- 배포: `.github/workflows/release-mind-journal.yml`
- 일반 docs 변경 배포에도 일기 회귀 테스트가 선행합니다.
- 과거 일회성 마이그레이션 워크플로는 `maintenance/legacy-workflows/`에 보존했습니다.

미디어 출처는 사이트 하단에 표시합니다. 무료 공개라도 각 영상·녹음의 이용조건은 유지됩니다. 임상 진단이나 치료를 제공하지 않습니다.
''',encoding='utf-8')
(ROOT/'MAINTENANCE.md').write_text('''# 마음서재 유지보수

## 데이터 손실 방지
1. 일기 스키마의 버전과 키를 임의로 변경하지 않습니다.
2. 개인 일기는 git, 로그, 서버로 전송하지 않습니다. 테스트는 가상 문장만 사용합니다.
3. 복원은 기본적으로 기존 날짜를 보존합니다. 덮어쓰기는 사용자 선택 뒤에만 수행합니다.
4. 읽기 오류는 원본을 지우지 말고 원본 백업 기능으로 복구합니다.
5. 기기별 localStorage이므로 백업을 가져오는 방식으로 이동합니다. 자동 동기화를 표시하지 않습니다.

## 배포 전 검증
- node --check docs/player.js / docs/scenery.js / docs/mind-journal.js / docs/sw.js
- node --test tests/mind-store.test.cjs
- 320·390·768·1280px에서 가로 넘침과 날짜 선택 확인
- 영상 프레임 진행, 낭독 → 음악 연결, 탭 전환 중 오디오 유지
- 일기 작성·자동 저장·다른 날짜·새로고침·백업·복원·삭제 되돌리기
- 브라우저 저장 차단·할당량 오류·다른 창의 갱신 충돌
- 첫 방문 후 오프라인 일기 작성과 재접속

## 서비스워커
오프라인 캐시는 기본 화면과 작은 미리보기만 담습니다. MP4·MP3·움직이는 WebP·외부 음악은 캐시하지 않습니다. 배포 때 SW VERSION과 HTML 자산 버전을 함께 올립니다. 작성 중인 일기를 버리지 않도록 강제 새로고침/skipWaiting은 사용하지 않습니다. 새 버전은 기존 창을 닫고 다시 열면 적용됩니다.

## 콘텐츠 확장
음악 목록은 docs/episodes.js, 실사 영상 출처는 docs/assets/films/manifest.json입니다. 현재 컨트롤러는 12편 구성으로 검증되어 있으므로 곡 수를 늘릴 때 날짜-음악 연결 및 선택 범위 검증도 함께 확장해야 합니다. 기존 episode 순서를 바꾸면 일기의 연결 곡이 달라질 수 있으므로, 순서는 보존하고 향후에는 고정 ID 기반 마이그레이션을 먼저 설계합니다.

## 비용·부하·개인정보
현재는 정적 호스팅이며 별도 데이터베이스나 AI 호출이 없습니다. 서버 비용이 영원히 0원이라고 보장하지 않으며 호스팅 정책·트래픽 조건은 운영자가 확인합니다. 일기 탭에서는 보이지 않는 풍경 재생을 쉬고 오디오만 유지합니다. 추적 SDK·광고를 기본 기능으로 추가하지 않습니다. 민감한 기록은 암호화되지 않았다는 안내를 숨기지 않습니다.
''',encoding='utf-8')
print('Maintenance guide and regression-gated deploy prepared.')
