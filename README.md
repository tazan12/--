# DJ의 편지 · LENTO LETTER

남성 DJ의 한국어 낭독과 클래식 원곡을 연달아 감상하는 무료 라디오 시네마.

## 실행 파일 및 소스
- **GitHub Pages 정적 앱:** [docs/index.html](./docs/index.html), [docs/app.js](./docs/app.js), [docs/style.css](./docs/style.css)
- **React 원본 코드 백업:** [dj-letter/app/src/routes/index.tsx](./dj-letter/app/src/routes/index.tsx)
- **현재 작동 중인 다른 플랫폼의 배포본:** https://dj-letter-radio-2026.higgsfield.app/
- **음악·DJ 음원·실사 영상:** 독립된 원격 미디어 URL을 사용합니다. 정적 웹앱 코드는 GitHub에 저장되어 있습니다.

## GitHub Pages 무료 배포
이 저장소에는 이미 `.github/workflows/deploy-dj-letter.yml` 자동 배포 파일이 들어 있습니다. 배포가 아직 시작되지 않은 이유는 **GitHub Pages 기능을 저장소 설정에서 켜지 않았기 때문**입니다.

1. https://github.com/tazan12/--/settings/pages
2. **Build and deployment → Source → GitHub Actions**를 선택합니다.
3. https://github.com/tazan12/--/actions/workflows/deploy-dj-letter.yml 에서 **Run workflow**를 누릅니다.
4. 성공하면 저장소 프로젝트 페이지 주소가 생성됩니다.

**비공개 저장소 주의:** GitHub Free는 공개 저장소의 Pages를 지원합니다. 비공개 저장소에서 Pages를 쓰려면 GitHub Pro/Team 등 해당 요금제가 필요할 수 있습니다. 무료로 공개 배포하려면 GitHub의 **Settings → General → Change repository visibility**에서 이 저장소를 공개로 변경할 수 있습니다. 변경 시 소스 파일이 공개된다는 점을 확인하세요.

## 저작권 및 서비스 안내
- 광고/결제 없는 무료 배포를 전제로 합니다. 무료라도 미디어 이용허락은 개별 확인이 필요합니다.
- 클래식 작품의 작곡 저작권과 현대 녹음의 연주자/제작자 권리는 구분합니다.
- 음악은 외부 공개 음원 저장소에서 재생하며, 일부 외부 서비스는 접속 빈도에 따라 HTTP 429를 반환할 수 있습니다.
- 영상은 Mixkit 공개 이용허락 자료를 편집한 것을 Higgsfield 공개 서버에서 재생합니다.
- 고품질 한국어 남성 AI DJ 음성은 실제 성우나 유명인의 음성을 복제하지 않은 독립 음성입니다.
