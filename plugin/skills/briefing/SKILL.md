---
name: briefing
description: hq 오늘 브리핑. 사용자가 "오늘 뭐 해야 돼", "브리핑", "할 일 정리", "밀린 거 있어?", "알림 확인" 처럼 오늘의 업무 상태를 물으면 hq MCP 의 getBriefing 으로 요약하고 바로 할 수 있는 액션을 제안한다.
---

# hq 브리핑

hq MCP 서버 (`hq`) 의 `getBriefing` 을 **인자 없이** 한 번 호출한다. 결과는 호출자 (hq 에 로그인한 구성원 본인) 기준이다.

## 요약 형식

**브리핑** (오늘 할 일 — 상태에서 파생 · 읽음 없음) 3묶음을 먼저, 그 뒤 **알림** (누가 나에게 한 일) 을 짧게. 비어 있는 묶음은 "없음" 한 줄로. 각 태스크는 `키 제목 (마감)` 한 줄.

1. **오늘 일정** (`todayEvents`) — 회사 캘린더. `시각 제목 (장소)` (종일은 "종일"). 빈 배열이면 생략 · `null` 이면 "회사 캘린더 연결 안 됨" 한 줄 (브리핑은 계속). 일정 잡기 · 옮기기는 `schedule` 스킬.
2. **오늘까지** (`dueByToday`) — 마감이 오늘이거나 지난 내 미완료 태스크 (`review` 도 미완료). 지난 것이 먼저 · `daysOverdue` > 0 이면 "N일 지남" 으로 가장 눈에 띄게, 0 이면 "오늘".
3. **확인 요청** (`confirmations`) — 종류를 앞에 붙인다:
   - `kind: review` = **검토** — 내가 만든 태스크를 담당자가 검토로 올렸다. 완료로 바꾸거나 되돌린다.
   - `kind: duePending` = **마감 정하기** — 내가 맡은 마감 미정 태스크. 날짜를 정하면 풀린다.
4. **알림 N건** — 안 읽은 `assigned` (새로 배정) · `completed` (내가 맡긴 태스크 완료) · `comments` (새 댓글) 건수 한 줄 (예: "알림 3건 — 새로 배정 1 · 새 댓글 2"). 0 이면 생략 · 사용자가 물으면 줄마다.

곧 결제 (고정비) 는 브리핑에 넣지 않는다 — 물으면 `cost` 스킬 (`listCostItems`). 옛 필드 `overdue` · `dueToday` · `upcomingPayments` 는 쓰지 않는다 (호환용).

마지막에 한 줄 총평 (예: "2일 지난 태스크 1건이 급합니다").

## 액션 제안

요약 뒤에 바로 실행 가능한 것을 2~3개까지 제안한다. 실행은 사용자가 고른 뒤에만:

- 오늘까지 (지난 것) → `changeTaskStatus` (done) 또는 `updateTask` 로 `dueDate` 연장 (`YYYY-MM-DD`, 한국 시간)
- 검토 → 태스크를 `getTaskByKey` 로 보고 `changeTaskStatus` done (승인) 또는 doing (되돌림)
- 마감 정하기 → 사용자에게 날짜를 묻고 `updateTask { taskId, dueDate }` (넣으면 마감 미정이 저절로 풀린다)
- 태스크 상세가 필요하면 → `getTaskByKey` (키로) — 조회만이라 알림은 그대로 남는다
- 알림을 다 봤으면 → `markNotificationsRead` (`all: true`, 또는 처리한 항목의 id 들)
- 새로 만들 일이 나오면 → `task` 스킬의 절차로

"팀 진행 상황 · 프로젝트 어디까지 됐어" 처럼 **팀** 을 물으면 브리핑 대신 `listEpics` (에픽별 진행률 · 기간) + 필요하면 `listTasks { status: "doing" }` · 고객사별은 `listCustomers` (열린 태스크 수) 로 답한다 — 웹 홈 (`/`) 에 같은 내용이 있다.

## 규칙

- 담당자 · 작성자 id 를 사람 이름으로 바꿔야 하면 `listMembers` 를 한 번 호출해 매핑한다 (이름 · 직책 `title`). 이메일은 쓰지 않는다.
- `getBriefing` 이 401 · 연결 오류면 "hq 연결이 끊겼다 — Claude Code 는 `/mcp` 에서, claude.ai 는 플러그인 Connectors 탭에서 hq 에 다시 로그인. 구성원이 비활성이면 로그인도 거부된다" 를 안내하고 멈춘다.
- 결과 JSON 을 그대로 붙이지 않는다. 요약만.
