# DJ의 편지 — production source backup

2026-11-13 배포된 한국어 클래식 라디오 웹앱의 주요 소스 코드와 디자인 메타데이터 백업입니다.

- **공개 웹앱:** https://dj-letter-radio-2026.higgsfield.app/
- **서비스 목록:** https://higgsfield.ai/supercomputer/apps/2c72fd90-27db-494c-a1cc-44e6a34c93de/view
- **배포 원본 플랫폼:** Higgsfield 웹사이트 프로젝트 (Cloudflare Worker)
- **프로젝트 형태:** React 19 / TanStack Start
- **소스:** app/src/routes/index.tsx, app/src/styles.css, app/src/app-meta.json, app/design-brief.md

기능: 윤아 한국어 DJ 낭독 12편, 클래식 녹음 연결, 감정별 에피소드 목록, 내 편지 브라우저 로컬 보관.

주의: 이 저장 폴더는 **전체 실행 가능한 모노레포가 아니라 사용자 소유 GitHub의 별도 백업**입니다. 플랫폼에서 사용하는 의존 패키지와 배포 설정, 이미지 바이너리는 포함하지 않았습니다. 완전한 재빌드에는 플랫폼 원본 저장소 또는 전체 프로젝트 내보내기가 필요합니다.

오디오 녹음은 외부 CDN에서 읽습니다. 상업 공개 시 각 연주 음원의 이용허락과 생성된 DJ 음성의 사용권을 다시 확인해야 합니다.
