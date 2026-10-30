# hq-plugin

nodemill hq 업무툴의 Claude 플러그인 **원본** 이자 공개 마켓플레이스 (`nodemill-ai/hq-plugin`, PUBLIC). 구성원은 claude.ai `Add marketplace` 로 이 레포를 추가한다 — 비밀 · 키 · 구성원 정보를 절대 넣지 않는다 (서버는 OAuth 로그인한 구성원에게만 응답).

## 구조
- `.claude-plugin/marketplace.json` (이름 `nodemill`, 플러그인 `hq` → `./plugin`) · `plugin/` (`.claude-plugin/plugin.json` · `.mcp.json` · `skills/<name>/SKILL.md` · `README.md` = 사용자 설치 문서).
- `.mcp.json` 은 프로덕션 `https://hq-psi-indol.vercel.app/api/mcp` 만, 헤더 없음 (OAuth). 로컬 dev 서버 연결은 `plugin/README.md § 개발자 메모`.

## 검증
- `scripts/check.sh` = 스킬 프런트매터 검사 (`name` · `description` · `license` · `compatibility` · `metadata` · `allowed-tools` 만 — claude.ai 가 그 외 키를 거부) → `claude plugin validate plugin` → `claude plugin validate .`. push 전에 돌린다.
- 로컬 검토: `claude --plugin-dir ./plugin` 또는 `/plugin marketplace add <이 레포 경로>` → `/plugin install hq@nodemill`. 구성원 계정에 `hq@synced` 가 있으면 둘이 중복된다 (도구 42개) — 하나만.

## 규칙
- 스킬이 부르는 MCP 도구 이름 · 인자는 hq 레포 `server/mcp/server.ts` (`MCP_TOOL_NAMES`, 21개) 가 원본 — hq 에서 도구를 바꾸면 여기 스킬도 같이 고친다.
- 버전은 `plugin/.claude-plugin/plugin.json` 의 `version` — 사용자에게 보이는 변경마다 올린다. main 에 push 하면 "Sync automatically" 켠 계정에 자동 반영.
- 커밋 메시지 `type: 설명` 50자 이하. Claude 관련 문구 금지.
