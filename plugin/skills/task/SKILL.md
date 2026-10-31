---
name: task
description: hq 태스크 작성. 사용자가 "태스크 만들어", "할 일 등록", "ERP 에 ~ 추가", "~ 를 대표 담당으로", "마감 다음 금요일" 처럼 새 업무를 자연어로 말하면 hq MCP 로 id 를 찾아 createTask 하고 키 · 제목으로 보고한다.
---

# hq 태스크 작성

자연어 → `createTask`. **id 는 추측하지 않는다** — 반드시 조회 도구로 얻는다.

## 개념

사일로 (업무 영역) → epic (태스크 묶음) → 태스크 (`todo · doing · review · done`). 구성원은 회사 → 팀 → 구성원이고, 각자 직책 (`title`, 자유 텍스트) 과 시스템 역할 (`role`: `admin · staff`) 을 가진다 — 역할은 권한 (삭제 · 구성원 · 사일로 관리 = admin) 이고 직책이 아니다.

## 절차

1. 사용자 말에서 뽑는다: 제목 · 사일로 · 담당자 · epic (있으면) · 시작일 · 마감일 · 설명 · 체크리스트.
2. id 를 찾는다 (필요한 것만, 각 1회):
   - 사일로 → `listSilos`. "ERP 쪽", "홈페이지 건" 같은 표현을 목록 이름에 맞춘다. 없는 영역이면 "사일로 '~' 가 없다 — 새로 만들까요?" 라고 묻고, 사용자가 원하면 `createSilo` (admin 만 — FORBIDDEN 이면 admin 에게 요청하라고 안내).
   - 담당자 → `listMembers` (`activeOnly: true`). 이름 또는 **직책** (`title` — 예 "대표" · "ceo" · "cto") 으로 찾는다. 담당자를 말하지 않았으면 **로그인한 구성원 (나)** 로 하되 보고에 명시한다.
   - epic → 사용자가 epic 을 언급했을 때만 `listEpics` 로 기존 것을 찾는다. 없으면 만들지 말고 "epic '~' 이 없다 — 새로 만들까요?" 라고 묻는다 (`createEpic` 은 같은 사일로여야 한다).
3. 날짜는 `YYYY-MM-DD` (한국 시간). "다음 금요일" · "이번 주 안에" 같은 상대 표현은 오늘 날짜 기준으로 계산해 **확인 문장에 실제 날짜를 적는다**.
4. **애매하면 묻는다** — 사일로를 알 수 없거나, 담당자가 둘 이상에 맞거나, 기간 표현이 두 가지로 읽히면 만들기 전에 한 번에 묻는다 (질문은 하나로 모아서).
5. `createTask` 호출: `title` · `siloId` · `assigneeId` 필수, `epicId` · `startDate` · `dueDate` · `description` · `checklist` 는 있을 때만.
6. 보고: `HQ-0001 — 제목` 형식으로 키 · 제목 · 사일로 · 담당 · 마감을 한 줄씩. 결과 JSON 은 붙이지 않는다.

## 상태 변경

- "시작했다" → `changeTaskStatus` doing · "확인해 줘 · 검토 올렸다" → review (태스크를 만든 사람에게 확인 요청 알림) · "끝났다" → done.
- epic 종료 (`closeEpic`) 에서 열린 태스크 때문에 INVALID 와 키 목록이 오면, 그 키들을 보여 주고 사용자가 확인한 뒤에만 `force: true` 로 다시 호출한다.

## 예

"ERP 사일로에 '인터뷰 패키지 발송' 태스크, 담당 대표, 마감 다음 금요일"
→ `listSilos` (ERP) · `listMembers` (title 이 "대표" 또는 "ceo" 인 구성원) → `createTask { title: "인터뷰 패키지 발송", siloId, assigneeId, dueDate: "2026-11-06" }` → "HQ-0042 — 인터뷰 패키지 발송 / ERP / 대표 / 마감 2026-11-06"

## 규칙

- 같은 요청으로 태스크를 두 번 만들지 않는다. 호출이 실패했는지 모르면 `search` 로 제목을 먼저 찾는다.
- 삭제 · 종료 같은 되돌리기 어려운 도구 (`deleteTask` — admin 만 · `closeEpic`) 는 사용자가 명시적으로 말했을 때만, 키 · 제목을 확인한 뒤.
- `FORBIDDEN` 이 오면 권한 (admin 전용) 문제다 — 우회하지 말고 admin 에게 요청하라고 안내한다.
- 401 · 연결 오류면 "hq 연결이 끊겼다 — Claude Code 는 `/mcp` 에서, claude.ai 는 플러그인 Connectors 탭에서 hq 에 다시 로그인" 을 안내하고 멈춘다.
