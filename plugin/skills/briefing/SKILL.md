---
name: briefing
description: hq 오늘 브리핑. 사용자가 "오늘 뭐 해야 돼", "브리핑", "할 일 정리", "밀린 거 있어?", "알림 확인" 처럼 오늘의 업무 상태를 물으면 hq MCP 의 getBriefing 으로 요약하고 바로 할 수 있는 액션을 제안한다.
---

# hq 브리핑

hq MCP 서버 (`hq`) 의 `getBriefing` 을 **인자 없이** 한 번 호출한다. 결과는 호출자 (hq 에 로그인한 구성원 본인) 기준이다.

## 요약 형식

섹션 순서대로, 비어 있는 섹션은 "없음" 한 줄로. 각 태스크는 `키 제목 (마감)` 한 줄.

1. **기한 지남** (`overdue`) — 마감이 `today` 보다 이른 미완료 태스크 (`review` 도 미완료). 가장 먼저, 가장 눈에 띄게.
2. **오늘 마감** (`dueToday`)
3. **확인 요청** (`reviews`) — 내가 만든 태스크를 담당자가 `review` 로 올렸다. 완료로 바꾸거나 되돌린다.
4. **새로 배정됨** (`assigned`) — 다른 사람이 나에게 맡긴 태스크 알림
5. **내가 맡긴 태스크 완료** (`completed`)
6. **새 댓글** (`comments`)

마지막에 한 줄 총평 (예: "기한 지남 2건이 급합니다").

## 액션 제안

요약 뒤에 바로 실행 가능한 것을 2~3개까지 제안한다. 실행은 사용자가 고른 뒤에만:

- 기한 지남 태스크 → `changeTaskStatus` (done) 또는 `updateTask` 로 `dueDate` 연장 (`YYYY-MM-DD`, 한국 시간)
- 확인 요청 → 태스크를 `getTaskByKey` 로 보고 `changeTaskStatus` done (승인) 또는 doing (되돌림)
- 태스크 상세가 필요하면 → `getTaskByKey` (키로) — 조회만이라 알림은 그대로 남는다
- 알림을 다 봤으면 → `markNotificationsRead` (`all: true`, 또는 처리한 항목의 id 들)
- 새로 만들 일이 나오면 → `task` 스킬의 절차로

## 규칙

- 담당자 · 작성자 id 를 사람 이름으로 바꿔야 하면 `listMembers` 를 한 번 호출해 매핑한다 (이름 · 직책 `title`). 이메일은 쓰지 않는다.
- `getBriefing` 이 401 · 연결 오류면 "hq 연결이 끊겼다 — Claude Code 는 `/mcp` 에서, claude.ai 는 플러그인 Connectors 탭에서 hq 에 다시 로그인. 구성원이 비활성이면 로그인도 거부된다" 를 안내하고 멈춘다.
- 결과 JSON 을 그대로 붙이지 않는다. 요약만.
