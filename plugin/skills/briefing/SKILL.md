---
name: briefing
description: hq 오늘 브리핑. "오늘 뭐 해야 돼", "브리핑", "할 일 정리", "밀린 거 있어?", "알림 확인", "팀 진행 어때" 라고 하면. 도구 — getBriefing (+ changeTaskStatus · updateTask · acknowledgeRequest · getTaskByKey · markNotificationsRead · listEpics).
---

# hq 브리핑

`getBriefing` 을 인자 없이 1회 호출해 본인 기준으로 **해야 할 것만 간략히** 요약하고 액션을 제안한다 (업무 전체는 hq 홈).

## 절차
1. 묶음 순서대로 — 비면 "없음" 한 줄, 태스크는 `키 제목 (마감)`:
   1. **오늘 일정** (`todayEvents`) — `시각 제목 (장소)` · 종일 = "종일" · `null` = "회사 캘린더 연결 안 됨".
   2. **지난 일** (`overdue`) — 오래 지난 것 먼저 · "N일 지남" (`daysOverdue`) · 상태가 `review` 면 "(검토 중)".
   3. **오늘 마감** (`dueToday`).
   4. **확인 요청** (`requests` — 나에게 온 것) — `보낸 사람: "요청 앞부분" — 키 제목 (N일 전)`.
   5. **날짜 미정** (`undated` — 마감 없는 내 태스크) — 5개까지 + "N개 더".
   6. **알림 N건** (`alerts` — 안 읽은 것) — 종류별 건수 한 줄: `assigned` 새 배정 · `status_changed` 상태 변경 (`status` = 바뀐 상태) · `comment` 새 댓글 · `request_done` 확인함 (0 이면 생략 · `comment_request` 는 4번과 겹치니 세지 않는다).
2. 총평 한 줄 — `todayCount` = 지난 일 + 오늘 마감 + 확인 요청 ("오늘 볼 것 4건 — 6일 지난 계약서 보완이 가장 급합니다").
3. 액션 2~3개 제안 — 사용자가 고른 뒤 실행:
   - 지난 일 · 오늘 마감 → `changeTaskStatus` done 또는 `updateTask { dueDate }`
   - 확인 요청 → 내용을 보여 주고 "확인했음" = `acknowledgeRequest { commentId }` · 답을 달면 `acknowledgeRequest { commentId, reply }` (`reply` = 따옴표로 준 문장은 그대로 바로 · 요지만 말했으면 「공통 (글)」 대로 풀어 쓴 답을 보이고 확인 뒤)
   - 날짜 미정 → 날짜를 묻고 `updateTask { taskId, dueDate }`
   - 다 봤으면 → `markNotificationsRead { all: true }`
   - 새 일 · 확인 요청 보내기 → `task` 스킬
4. "팀 진행 어때" → 브리핑 대신 `listEpics` (진행률 · 기간) + `listTasks { status: "doing" }`.

## 예
"오늘 뭐 해야 돼" → "오늘 일정: 10:00 주간 회의 / 지난 일: HQ-0042 계약서 보완 (6일 지남) / 오늘 마감: HQ-0051 장비 셋팅 / 확인 요청: 대표 "단가 표 이걸로 맞나요?" — HQ-0050 견적서 보내기 (어제) / 날짜 미정 2 / 알림 3건 (상태 변경 2 · 새 댓글 1) — 오늘 볼 것 3건, 6일 지난 계약서 보완이 가장 급합니다. 단가 표 확인 요청에 답할까요?"

## 규칙
- 다가오는 것 · 내가 보낸 요청 · 로드맵 · 최근 활동 · 결제는 넣지 않는다 (홈 · `task` · `cost` 스킬). 옛 필드 `dueByToday` · `assigned` · `completed` · `comments` 는 쓰지 않는다 (`alerts` 로).
- **검토** 상태는 확인 요청이 아니다 — 확인 요청은 `requests` 뿐이다.
- 사람 이름은 `listMembers` 1회로 매핑한다. 이메일은 쓰지 않는다.
- 공통 (글): hq 에 쓰는 글 (설명, 댓글, 확인 요청, 답) 은 처음 읽는 사람이 회의록이나 대화 없이 그 글만 읽고 이해하게 풀어 쓴다. 해요체 문장으로 쓰고 명사로 끝내지 않는다. 어디서 나온 일인지, 왜 하는지, 지금 상태, 무엇을 하면 끝인지, 언제까지인지 (안 정했으면 그렇다고), 다음에 누가 무엇을 하는지 (남은 일이 없으면 없다고) 를 넣는다. 기호 (`·` `→` `=` `/` `—`) 로 낱말을 이어 붙이지 않고 말로 잇는다 (늘어놓을 때는 쉼표나 `와`, `과`). 처음 읽는 사람이 모를 수 있는 번호, 키, 파일, 화면, 도구 이름, 내부 용어는 무엇인지, 어디인지 함께 쓴다. 일에 대한 사실 (날짜, 금액, 이름, 결정, 이유) 은 원문에 있는 것만 쓴다. 길이는 필요한 만큼 쓴다.
- 공통: id 는 조회로만 얻는다 · `FORBIDDEN` = admin 에게 요청 안내 · 401 · 연결 오류 = "hq 다시 로그인 (Code `/mcp` · claude.ai 플러그인 Connectors 탭)" 안내 후 멈춤 · 결과 JSON 을 붙이지 않는다.
