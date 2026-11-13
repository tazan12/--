# DJ의 편지 — GitHub Pages 정식 이전

무료 공개 클래식 라디오 서비스의 GitHub Pages 정적 버전입니다.

## 파일과 배포 구조
- **사이트 소스:** `docs/index.html`, `docs/app.js`, `docs/style.css`
- **영상 및 표지:** `docs/assets/films/ep01-ep12.mp4`, 각 포스터, `docs/assets/dj-cover.webp`
- **한국어 남성 DJ 음성:** `docs/assets/voice/ep01-ep12.mp3`
- **자동 배포:** `.github/workflows/deploy-dj-letter.yml`
- **영상·음성 이관 확인:** `.github/workflows/migrate-dj-media.yml` 실행 성공 (미디어는 GitHub에 영구 저장)
- **역사적 React 코드:** `dj-letter/...` 백업본이며 Pages의 배포 대상은 아닙니다.

현재 배포용 영상과 DJ 음성은 **Higgsfield 웹앱 서비스가 중단되어도 작동하도록 GitHub에 독립 저장**했습니다. 클래식 음악의 실연 녹음만 Wikimedia Commons 외부 스트리밍을 사용하므로 원본 서버가 사용 제한을 걸면 개별 곡 재생이 불안정할 수 있습니다.

## GitHub Pages 사이트 활성화 — 저장소 관리자 1회 작업
- 현재 이 저장소는 **private** 상태이며 GitHub Pages 사이트는 아직 비활성화되어 있습니다.
- GitHub Free 이용자는 저장소를 **Public**으로 변경해야 Pages를 공개 배포할 수 있습니다. GitHub Pro 등 Pages 사용권이 있는 경우 private로 유지할 수도 있습니다.
- 저장소 [설정](https://github.com/tazan12/--/settings) → **Pages** → **Build and deployment** → **Source: GitHub Actions**를 선택합니다.
- 이후 [배포 워크플로](https://github.com/tazan12/--/actions/workflows/deploy-dj-letter.yml) → **Run workflow**를 누릅니다.
- 정상 완료하면 예상 주소는 `https://tazan12.github.io/--/`입니다. 실제 공개 여부를 반드시 확인하세요.
- 사전에 동의 없이 기존 Higgsfield 사이트를 먼저 중단하지 마세요. 사이트 전환 중 서비스 공백이 발생할 수 있습니다.

## 기존 Higgsfield 사이트 철수
1. GitHub Pages에서 12편 목록·영상·음성 재생을 확인합니다.
2. 기존 Higgsfield 배포본에서 공개 서비스를 중단하거나, 새 Pages 주소로 이전 안내를 설정합니다.
3. Higgsfield 커뮤니티 목록에서도 공개 게시를 해제합니다.

## 무료 배포와 권리
- 무료·비상업적 공개를 전제합니다. 무료라도 저작권·녹음 저작인접권·클립 이용 조건은 확인해야 합니다.
- 영상은 Mixkit Free License 출처의 클립을 이야기 화면용으로 편집한 자료입니다. 원본을 개별 stock 영상으로 재배포·판매해서는 안 됩니다.
- DJ 음성은 유명인의 목소리를 복제하지 않은 AI 생성 낭독입니다.
