# hq 플러그인

nodemill 사내 업무툴 **hq** 를 Claude 에서 쓴다. 들어 있는 것: 스킬 2개 (`briefing` · `task`) + HQ MCP 서버 연결 (도구 21개 — 태스크 · 프로젝트 · 댓글 · 링크 · 알림 · 브리핑 · 검색). 연결은 **hq Google 로그인 1회** (OAuth) 이고, 모든 호출은 로그인한 구성원 본인 자격으로 기록된다. 키 복사 · 커넥터 수동 추가 · ZIP 업로드가 없다.

전제: hq 구성원으로 등록된 Google 계정 · claude.ai 유료 플랜 (Pro 이상). GitHub 계정은 필요 없다 — 이 플러그인은 **공개 레포** `nodemill-ai/hq-plugin` 에서 받는다 (스킬 · 서버 주소 · 이 문서뿐, 비밀 없음. 서버는 로그인한 구성원에게만 응답한다).

## 1. 설치 — claude.ai 한 곳 (Desktop · 웹 · Claude Code 공통)

1. claude.ai (또는 Claude Desktop) → **Customize › Plugins › Add › Add marketplace** → `nodemill-ai/hq-plugin` 입력 → 추가.
2. 목록에서 플러그인 **hq** 를 열고 **Add**.
3. 플러그인의 **Connectors** 탭 → `hq` 가 "Not added" 면 **추가**, 그 다음 **연결 (로그인)** → hq 의 Google 로그인 → **연결 허용** 화면에서 "돌아갈 주소" 가 `claude.ai` 인지 확인하고 **허용**.
4. 확인: 새 채팅에서 "오늘 뭐 해야 돼" → 브리핑.

같은 계정의 **Claude Code** 에는 다음 세션부터 `hq@synced` 로 자동 동기화된다 (`/reload-plugins` 또는 재시작). 처음 hq 도구를 부를 때 (또는 `/mcp` 에서 `plugin:hq:hq` 선택) 브라우저가 열리고 같은 Google 로그인 → 허용 화면 (돌아갈 주소 = `localhost`, 이 컴퓨터의 Claude Code 가 요청한 것) → connected · 도구 21개.

업데이트는 마켓플레이스에서 자동으로 온다 (플러그인 화면의 **Sync automatically** 를 켜 두면 됨). 연결을 끊으려면 Connectors 탭에서 로그아웃 (Code 는 `/mcp` › Clear authentication). hq 에서 구성원을 비활성화하면 그 사람의 연결은 다음 요청부터 바로 거부된다.

## 2. 하지 말 것 (중복 주의)

Claude Code 에 개발자용 `hq@nodemill-dev` (아래) 를 따로 설치하면 hq 서버가 **두 벌** 뜬다 (도구 42개). 구성원은 1 의 synced 만 쓴다.

## 개발자 메모

- 원본은 hq 레포 `plugin/` (이 README 포함). 공개 레포 `nodemill-ai/hq-plugin` 은 **복사본** — 직접 고치지 않는다. 배포: hq 레포 옆에 `git clone git@github.com:nodemill-ai/hq-plugin.git ../hq-plugin` 한 번 → 바꿀 때마다 `pnpm plugin:publish` (프런트매터 검사 · validate · 복사) → 출력에 나온 대로 commit · push.
- 로컬 검토: `claude --plugin-dir <hq 레포>/plugin`, 또는 hq 레포 자체를 마켓플레이스로 (`/plugin marketplace add <hq 레포 경로>` → `/plugin install hq@nodemill-dev`).
- 로컬 dev 서버 (`pnpm dev`) 에 붙이려면: `claude mcp add --transport http hq-local http://localhost:3000/api/mcp` → `/mcp` 로그인 (dev DB 구성원의 Google 계정 · OAuth). 스크립트 · curl 은 개인 키 (`pnpm mcp:issue-key <email>` → `Authorization: Bearer hq_…`) — 두 방식을 `/api/mcp` 가 모두 받는다.
- 스킬 프런트매터는 `name` · `description` (+ `license` · `compatibility` · `metadata` · `allowed-tools`) 만 — claude.ai 가 그 외 필드를 거부한다. `pnpm plugin:zip` · `pnpm plugin:publish` 가 검사한다.
- 검증: `claude plugin validate plugin` · `claude plugin validate .` · `pnpm plugin:zip` (ZIP 은 수동 업로드 검토용).
- 비공개 레포 (`jaewanLee/hq`) 를 마켓플레이스로 직접 추가하는 건 **추가하는 사람의 GitHub 계정에 그 레포 권한이 있을 때만** 된다 (Claude GitHub App 연결) — 그래서 공개 레포를 쓴다 (claude.com/docs/plugins/overview, 2026-10-30).
- OAuth 디스커버리 · 토큰 경로는 `hq/CLAUDE.md § 구조` (`/api/mcp` · `/.well-known/*` · `/consent`).
