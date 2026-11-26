# hq-plugin

nodemill hq 업무툴의 Claude 플러그인 **원본** 이자 공개 마켓플레이스 (`nodemill-ai/hq-plugin`, PUBLIC). 구성원은 claude.ai `Add marketplace` 로 이 레포를 추가한다 — 비밀 · 키 · 구성원 정보를 절대 넣지 않는다 (서버는 OAuth 로그인한 구성원에게만 응답).

## 구조
- `.claude-plugin/marketplace.json` (이름 `nodemill`, 플러그인 `hq` → `./plugin`) · `plugin/` (`.claude-plugin/plugin.json` · `.mcp.json` · `skills/<name>/SKILL.md` · `README.md` = 사용자 설치 문서).
- `.mcp.json` 은 프로덕션 `https://hq.nodemill.ai/api/mcp` 만, 헤더 없음 (OAuth). 로컬 dev 서버 연결은 `plugin/README.md § 개발자 메모`.

## 검증
- `scripts/check.sh` = 소개문 · 본문 · 프런트매터 검사 (`scripts/check-skills.py` — § 스킬 작성의 한도 · 프런트매터 키는 `name` · `description` · `license` · `compatibility` · `metadata` · `allowed-tools` 만 (claude.ai 가 그 외 키를 거부)) → `claude plugin validate plugin` → `claude plugin validate .`. push 하면 `.githooks/pre-push` 가 돌리고 실패하면 push 를 막는다 — clone 마다 한 번 `git config core.hooksPath .githooks` (worktree 는 따로 필요 없다). 검사 자체의 시험 = `python3 scripts/check-skills.test.py`.
- 발동 시험 (소개문을 바꾸는 커밋 전에 손으로 · Opus 1회 = 구독 사용량 · 정가 환산 약 3.5달러): `claude plugin eval . --trust-plugin --no-publish --ablation none --runs 1 -j 4 --model claude-opus-5-5 --threshold 0 --json <결과 파일>` → `aggregates.overallScore` 가 1 (46/46) 이어야 한다 (`casesPassed` 는 `--threshold 0` 이면 늘 46 이라 보지 않는다). 떨어진 케이스만 `--case <이름> --runs 3` 으로 다시. 케이스 = `evals/<이름>/` (켜져야 할 말 40 · 안 켜져야 할 말 6) · hq 도구는 이름만 모의 (`evals/mocks/hq/_server.md` — 실제 도구 설명은 고객사 이름이 들어 있어 올리지 않는다) · 케이스 문구에도 실제 고객사 · 구성원 이름을 쓰지 않는다. 결과 폴더 `evals/results/` 는 커밋하지 않는다.
- 로컬 검토: `claude --plugin-dir ./plugin`. 로컬 경로를 마켓플레이스로 추가하지 않는다 (이 Mac 의 `hq@nodemill` 이 그 폴더를 가리키게 바뀐다 · 되돌리기는 `plugin/README.md § 개발자 메모`). 계정의 `hq@synced` 와 겹치는 것 같으면 Claude Code 에서만 하나를 끈다.

## 규칙
- 스킬이 부르는 MCP 도구 이름 · 인자는 hq 레포 `server/mcp/server.ts` (`MCP_TOOL_NAMES`, 60개) 가 원본 — hq 에서 도구를 바꾸면 여기 스킬도 같이 고친다.
- 버전은 `plugin/.claude-plugin/plugin.json` 의 `version` — 사용자에게 보이는 변경마다 올린다. main 에 push 하면 "Sync automatically" 켠 계정에 자동 반영 (꺼진 계정은 claude.ai 에서 수동 업데이트). Claude Code 세션의 스킬 목록은 시작 때 스냅샷 — 올린 뒤 새 세션에서 확인한다 (nodemill 하네스가 이 스킬 절차에 기댄다).
- 커밋 메시지 `type: 설명` 50자 이하. Claude 관련 문구 금지.
- **스킬 작성** (스킬 = Claude 가 읽는 지시문 · 어기면 `scripts/check.sh` 가 push 를 막는다):
  - `description` = 무엇을 하는지 목적 한 문장 (마침표) + 사용자가 할 말 3~4개 (`"…"`) + `라고 할 때.` — 한 줄 평문 · 140자 이하. 도구 이름 · 절차 · 범위 나열은 쓰지 않고 본문에만 둔다 (소개문에 절차를 요약하면 본문을 안 읽고 요약을 따른다). 기능을 더해도 소개문을 늘리지 않고 할 말을 바꾼다. 소개문은 매 세션 목록에 실린다.
  - 플러그인 소개문 (`plugin.json` · `marketplace.json` — 같은 글) = 한두 문장 · 100자 이하 · 스킬 · 도구를 나열하지 않는다.
  - 본문: 목적 1줄 → 절차 (번호) → 예 1개 → 규칙 ≤ 5 ("한다 / 하지 않는다" 형). 5,500자 이하 (compaction 뒤 스킬당 앞 5,000 토큰만 남는다) — 갈래가 여러 개면 갈래를 `references/` 파일로 나누고 본문 맨 앞에 「요청 → 읽을 파일」 표를 둔다 (`meeting`). 배경 · 이유 · 예외 사례 · 실측 기록도 `references/` 로 빼고 본문엔 링크 1줄. `references/` 파일은 모두 `SKILL.md` 가 직접 링크한다 (한 단계).
  - 공통 규칙 (id 조회로만 · FORBIDDEN · 401 재로그인 · JSON 안 붙이기) 은 각 스킬 규칙 끝 "공통:" 1줄로 복사한다 — 스킬은 claude.ai 에서 폴더 단위로 올라가 다른 스킬 폴더의 파일을 읽는다는 보장이 없다.
