---
name: schedule
description: 회사 캘린더 일정 잡기 · 옮기기 · 취소 · 조회. 사용자가 "일정 잡아 줘", "미팅 잡아", "목요일 3시 광일 미팅", "매주 월요일 10시 주간 회의", "내일 미팅 옮겨 줘", "워크숍 취소해 줘", "이번 주 일정", "휴가 등록" 이라고 하면 hq MCP listEvents 로 회사 캘린더 (nodemill) 를 보고, 쓰기는 Google 캘린더 커넥터 (create_event · update_event · delete_event) 로 회사 캘린더에만 한다.
---

# 일정 (회사 캘린더)

원본 = Google 회사 캘린더 **nodemill** 1개. hq 는 읽기 전용 창 (`https://hq.nodemill.ai/calendar` — 태스크 마감과 함께 보인다) 이고, 일정 **쓰기는 Google 캘린더 커넥터** (사용자 본인 권한) 가 한다. hq 에 일정을 만드는 도구는 없다. 개인 캘린더는 hq 에 안 보인다.

## 회사 캘린더 id

- `listEvents` 응답의 **`calendarId`** 를 커넥터의 `calendarId` 로 넘긴다. 없으면 (hq 장애) 커넥터 `list_calendars` 에서 이름 `nodemill` 을 고른다.
- **`calendarId` 를 생략하지 않는다** — 생략하면 사용자 개인 기본 캘린더에 들어가 hq 에 안 보인다.

## 제목 규칙

| 종류 | 제목 | 예 |
|---|---|---|
| 사외 (고객사) | `<고객사 이름> <주제>` — 이름은 `listCustomers` 표기 그대로 | `광일금속 ERP 1차 시연` |
| 사내 | 주제 | `주간 회의` · `hq 로드맵` |
| 개인 일정 (휴가 · 외근) | `<종류> — <이름>` | `휴가 — 재완` · `외근 — 재완` |

- 같은 날 미팅 폴더 주제가 이 제목과 같으면 hq 가 일정 ↔ 회의록을 자동으로 묶는다 (`meeting` 스킬이 같은 주제로 폴더를 만든다).

## 조회 — "이번 주 일정" · "내일 미팅 있어?"

1. `listEvents { from, to }` (`YYYY-MM-DD` · 한국 시간 · 포함 · 최대 62일). 오늘 = 브리핑의 `today` 기준.
2. 날짜별로 `시각 제목 (장소)` 한 줄 · 종일은 "종일". `meeting` 이 있으면 "회의록 있음" + `getMeeting` 으로 이어 볼 수 있다고 안내. 링크는 `hqUrl`.
3. 커넥터 `list_events` 는 쓰기 전 대상 찾기에만 쓴다 (조회 답은 hq — 미팅 연결이 붙는다).

## 만들기 — "목요일 3시 광일 미팅 잡아 줘"

1. 날짜 · 시각을 한국 시간으로 확정한다 ("목요일" = 다가오는 목요일). 끝 시각을 말하지 않았으면 1시간.
2. 고객사 이름이 나오면 `listCustomers` 로 표기를 맞춘다 ("광일" → "광일금속").
3. **한 줄 확인**: "11월 6일 (목) 15:00–16:00 · 광일금속 미팅 · 회사 캘린더 — 만들까요?" — 장소 · 설명을 말했으면 같이.
4. 커넥터 `create_event { calendarId, summary, startTime, endTime }` — 시각은 오프셋 없는 한국 시간 (`2026-11-06T15:00:00`). 종일은 `allDay: true`. 반복은 `recurrenceData` RRULE (`RRULE:FREQ=WEEKLY;BYDAY=MO`) — "매주 월요일 10시 주간 회의".
5. **참석자 (`attendees`) 는 기본으로 넣지 않는다** — 사용자가 이메일을 말한 사람 (사외 손님 등) 만. 대표 · CTO 는 회사 캘린더 구독으로 이미 본다.
6. 보고: 날짜 · 시각 · 제목 + hq 링크 `https://hq.nodemill.ai/calendar?month=YYYY-MM&day=YYYY-MM-DD` · "hq 에는 최대 1분 뒤 보여요".

## 옮기기 · 취소 — "내일 미팅 4시로" · "워크숍 취소해 줘"

1. 커넥터 `list_events { calendarId, timeMin, timeMax }` (그 날) 에서 제목으로 대상 1개를 확정한다. 여럿이면 고르게 한다.
2. 반복 일정이면 **"이번만 / 이후 전부"** 를 묻는다.
3. 한 줄 확인 ("11월 7일 (금) 워크숍 (종일) 을 취소할까요?") → `update_event` / `delete_event` (같은 `calendarId`).
4. 보고 + hq 링크.

## 커넥터가 없을 때 (Claude Code 등)

- 도구 목록에 Google 캘린더 커넥터가 없으면 만들 값 (제목 · 날짜 · 시각 · 반복 · 장소) 을 정리해 주고 "Google 캘린더 앱에서 **nodemill** 캘린더를 골라 만들어 주세요" 라고 안내한다. 조회는 hq `listEvents` 로 그대로 된다.

## 규칙

- 사용자가 확인하기 전에는 만들지 · 고치지 · 지우지 않는다.
- 회의록은 이 스킬이 아니라 `meeting` 스킬 (일정 제목과 같은 주제로 폴더).
- `listEvents` 가 `UNAVAILABLE` 이면 회사 캘린더 연결 안 됨 · 장애 — 커넥터로 쓰기는 할 수 있지만 hq 확인은 잠시 뒤. 401 · 연결 오류면 "hq 연결이 끊겼다 — Claude Code 는 `/mcp` 에서, claude.ai 는 플러그인 Connectors 탭에서 hq 에 다시 로그인" 을 안내한다.
