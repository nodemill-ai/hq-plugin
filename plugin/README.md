# hq 플러그인

nodemill 사내 업무툴 **hq** 를 Claude 에서 쓴다. 연결은 hq Google 로그인 1회 (OAuth) — 모든 호출은 로그인한 구성원 본인 자격으로 기록된다.

## 할 수 있는 것

| 스킬 | 이렇게 말하면 돼요 |
|---|---|
| briefing | "오늘 뭐 해야 돼" |
| task | "ERP 에 재고 화면 시안 태스크, 담당 대표, 마감 다음 금요일" · "내 할 일 뭐 있어" · "HQ-12 마감 금요일로" |
| roadmap | "ERP 로드맵 짜 줘 — 3월까지" · "로드맵 진행 어때" |
| meeting | "주간 미팅 준비" · (CLOVA Note 요약 붙여) "주간 미팅 정리해 줘" |
| schedule | "목요일 3시 광일 미팅 잡아 줘" · "이번 주 일정" |
| wiki | "이거 위키에 올려" · "위키에서 배포 가이드 찾아봐" |
| file | "이 견적서 드라이브에 올려" · "광일 계약서 어디 있어" |
| cost | "11월 14일 회식 법카 12만 8천원" · "AWS 지난달 얼마였지" |
| help | "hq 뭐 할 수 있어" · "영수증 어디서 올려" |

전제: hq 구성원으로 등록된 Google 계정 · claude.ai 유료 플랜 (Pro 이상). GitHub 계정은 필요 없다 — **공개 레포** `nodemill-ai/hq-plugin` 에서 받는다 (스킬 · 서버 주소 · 이 문서뿐, 비밀 없음).

## 1. 설치 — claude.ai 한 곳 (Desktop · 웹 · Claude Code 공통)

1. claude.ai (또는 Claude Desktop) → **맞춤 설정 (Customize) › 플러그인 › 추가 › 마켓플레이스 추가 › 저장소에서 추가** → `nodemill-ai/hq-plugin` 입력 → 추가. "자동 동기화를 사용하려면 Claude GitHub App 에 … 액세스 권한이 있어야 합니다" 경고는 **자동 업데이트에만** 해당한다 — `X` 로 닫고 계속하면 되고, 업데이트는 플러그인 화면의 **업데이트 확인** 으로 수동으로 받는다.
2. 목록에서 플러그인 **hq** 를 열고 **Add**.
3. 플러그인의 **커넥터 (Connectors)** 탭 → `hq` **연결**. "커스텀 커넥터 추가" 대화상자는 **그대로 두고** **추가** → hq 의 Google 로그인 → **연결 허용** 화면에서 "돌아갈 주소" 가 `claude.ai` 인지 확인하고 **허용**.
4. **Google Drive · Google Calendar 커넥터 연결** — claude.ai **설정 › 커넥터** 에서 둘 다 **연결** (회사 Google 계정). 미팅 회의록 · 파일 올리기 · 일정 잡기에 필요하다 (없으면 조회만 된다).
5. 확인: 새 채팅에서 "오늘 뭐 해야 돼" → 브리핑.

같은 계정의 **Claude Code** 에는 다음 세션부터 `hq@synced` 로 자동 동기화된다 (`/reload-plugins` 또는 재시작). 처음 hq 도구를 부를 때 (또는 `/mcp` 에서 `plugin:hq:hq` 선택) 브라우저가 열리고 같은 Google 로그인 → 허용 화면 (돌아갈 주소 = `localhost`) → connected.

업데이트는 플러그인 화면의 **업데이트 확인** (자동 동기화를 켰으면 자동). 연결을 끊으려면 Connectors 탭에서 로그아웃 (Code 는 `/mcp` › Clear authentication). hq 에서 구성원을 비활성화하면 그 사람의 연결은 다음 요청부터 바로 거부된다.

## 2. 하지 말 것 (중복 주의)

Claude Code 에 이 레포를 로컬 마켓플레이스로 따로 설치 (`hq@nodemill`, 개발자용) 하면 hq 서버가 **두 벌** 뜬다 (도구 80개). 구성원은 1 의 synced 만 쓴다.

## 개발자 메모

- 이 레포 (`nodemill-ai/hq-plugin`) 가 플러그인 **원본** 이다 (hq 레포에는 없다). 바꾸면 `scripts/check.sh` → commit · push → 자동 동기화. 규칙은 루트 `CLAUDE.md`.
- 로컬 검토: `claude --plugin-dir ./plugin`, 또는 `/plugin marketplace add <이 레포 경로>` → `/plugin install hq@nodemill` (구성원 계정의 `hq@synced` 와 중복되므로 하나만).
- 로컬 dev 서버 (`hq` 레포 `pnpm dev`) 에 붙이려면 플러그인 대신: `claude mcp add --transport http hq-local http://localhost:3000/api/mcp` → `/mcp` 로그인 (dev DB 구성원의 Google 계정 · OAuth). 스크립트 · curl 은 개인 키 (`pnpm mcp:issue-key <email>` → `Authorization: Bearer hq_…`) — 두 방식을 `/api/mcp` 가 모두 받는다.
- 스킬 프런트매터는 `name` · `description` (+ `license` · `compatibility` · `metadata` · `allowed-tools`) 만 — claude.ai 가 그 외 필드를 거부한다. `scripts/check.sh` 가 검사한다.
- 비공개 레포 (`jaewan-nodemill/hq`) 를 마켓플레이스로 직접 추가하는 건 **추가하는 사람의 GitHub 계정에 그 레포 권한이 있을 때만** 된다 (Claude GitHub App 연결) — 그래서 공개 레포를 쓴다 (claude.com/docs/plugins/overview, 2026-10-30).
- OAuth 디스커버리 · 토큰 경로는 hq 레포 `CLAUDE.md § 구조` (`/api/mcp` · `/.well-known/*` · `/consent`).
