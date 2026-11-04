---
name: briefing
description: hq 오늘 브리핑. "오늘 뭐 해야 돼", "브리핑", "할 일 정리", "밀린 거 있어?", "알림 확인", "팀 진행 어때" 라고 하면. 도구 — getBriefing (+ changeTaskStatus · updateTask · getTaskByKey · markNotificationsRead · listEpics).
---

# hq 브리핑

`getBriefing` 을 인자 없이 1회 호출해 본인 기준으로 요약하고 액션을 제안한다.

## 절차
1. 묶음 순서대로 — 비면 "없음" 한 줄, 태스크는 `키 제목 (마감)`:
   1. **오늘 일정** (`todayEvents`) — `시각 제목 (장소)` · 종일 = "종일" · `null` = "회사 캘린더 연결 안 됨".
   2. **오늘까지** (`dueByToday`) — 지난 것 먼저, `daysOverdue` > 0 = "N일 지남".
   3. **확인 요청** (`confirmations`) — `review` = **검토** · `duePending` = **마감 정하기**.
   4. **알림 N건** — `assigned` · `completed` · `comments` 건수 한 줄 (0 이면 생략).
2. 총평 한 줄 ("2일 지난 태스크 1건이 급합니다").
3. 액션 2~3개 제안 — 사용자가 고른 뒤 실행:
   - 지난 것 → `changeTaskStatus` done 또는 `updateTask { dueDate }`
   - 검토 → `getTaskByKey` → `changeTaskStatus` done (승인) · doing (되돌림)
   - 마감 정하기 → 날짜를 묻고 `updateTask { taskId, dueDate }`
   - 다 봤으면 → `markNotificationsRead { all: true }`
   - 새 일 → `task` 스킬
4. "팀 진행 어때" → 브리핑 대신 `listEpics` (진행률 · 기간) + `listTasks { status: "doing" }`.

## 예
"오늘 뭐 해야 돼" → "오늘 일정: 10:00 주간 회의 / 오늘까지: HQ-0042 인터뷰 패키지 발송 (2일 지남) / 확인 요청: 검토 HQ-0050 / 알림 3건 — 2일 지난 태스크 1건이 급합니다. HQ-0042 완료로 바꿀까요, 마감을 미룰까요?"

## 규칙
- 결제 · 고정비는 넣지 않는다 (`cost` 스킬). 옛 필드 `overdue` · `dueToday` · `upcomingPayments` 는 쓰지 않는다.
- 사람 이름은 `listMembers` 1회로 매핑한다. 이메일은 쓰지 않는다.
- 공통: id 는 조회로만 얻는다 · `FORBIDDEN` = admin 에게 요청 안내 · 401 · 연결 오류 = "hq 다시 로그인 (Code `/mcp` · claude.ai 플러그인 Connectors 탭)" 안내 후 멈춤 · 결과 JSON 을 붙이지 않는다.
