---
name: schedule
description: 회사 캘린더 일정 잡기 · 옮기기 · 취소 · 조회. "일정 잡아 줘", "목요일 3시 광일 미팅", "매주 월요일 10시 주간 회의", "내일 미팅 옮겨 줘", "워크숍 취소해 줘", "이번 주 일정", "휴가 등록" 이라고 하면. 도구 — hq listEvents (조회) · Google 캘린더 커넥터 create_event · update_event · delete_event · list_events (쓰기).
---

# 일정 (회사 캘린더 nodemill)

조회는 hq `listEvents`, 쓰기는 Google 캘린더 커넥터로 회사 캘린더에만 한다.

## 조회 — "이번 주 일정"
1. `listEvents { from, to }` (`YYYY-MM-DD` · 최대 62일) → 날짜별 `시각 제목 (장소)` · 종일 = "종일" · `meeting` 이 있으면 "회의록 있음".

## 만들기 — "목요일 3시 광일 미팅 잡아 줘"
1. 날짜 · 시각 확정 (다가오는 요일 · 끝 시각 없으면 1시간). 고객사는 `listCustomers` 표기로.
2. 제목: 사외 `<고객사> <주제>` (`광일금속 ERP 1차 시연`) · 사내 `<주제>` · 개인 `<휴가|외근> — <이름>`.
3. 한 줄 확인: "11월 6일 (목) 15:00–16:00 · 광일금속 미팅 · 회사 캘린더 — 만들까요?"
4. `create_event { calendarId, summary, startTime: "2026-11-06T15:00:00", endTime }` — 종일 `allDay: true` · 반복 `recurrenceData: "RRULE:FREQ=WEEKLY;BYDAY=MO"`.
5. 보고 + `https://hq.nodemill.ai/calendar?month=YYYY-MM&day=YYYY-MM-DD` · "hq 에는 최대 1분 뒤 보여요".

## 옮기기 · 취소
1. 커넥터 `list_events { calendarId, timeMin, timeMax }` 로 대상 1개 확정 (여럿이면 고르게).
2. 반복 일정이면 "이번만 / 이후 전부" 를 묻는다 → 한 줄 확인 → `update_event` / `delete_event`.

## 예
"내일 미팅 4시로" → `list_events` (11-05) → "11월 5일 (목) 광일금속 미팅 15:00 → 16:00–17:00 로 옮길까요?" → `update_event`

## 규칙
- `calendarId` 는 `listEvents` 응답의 값 (없으면 `list_calendars` 의 `nodemill`) — 생략하지 않는다 (개인 캘린더에 들어간다).
- 확인 전에 만들지 · 고치지 · 지우지 않는다. `attendees` 는 사용자가 이메일을 말한 사람만.
- 커넥터가 없으면 값을 정리해 주고 "Google 캘린더 앱에서 nodemill 캘린더로 만들어 주세요" 로 안내한다.
- 회의록은 `meeting` 스킬. `listEvents` `UNAVAILABLE` = 캘린더 연결 장애 (쓰기는 가능).
- 공통: id 는 조회로만 얻는다 · 401 · 연결 오류 = "hq 다시 로그인 (Code `/mcp` · claude.ai 플러그인 Connectors 탭)" 안내 후 멈춤 · 결과 JSON 을 붙이지 않는다.
