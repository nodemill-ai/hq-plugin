---
name: task
description: hq 태스크 만들기 · 조회 · 수정 · 댓글 · 상태 변경. "태스크 만들어", "할 일 등록", "ERP 에 ~ 추가", "내 할 일 뭐 있어", "조성우 할 일 뭐 있어", "이번 주 마감", "광일 건 뭐 있어", "HQ-12 마감 금요일로", "HQ-12 에 댓글 달아", "HQ-12 끝났어" 라고 하면. 도구 — createTask · listTasks · getTaskByKey · updateTask · addComment · changeTaskStatus (+ listSilos · listMembers · listEpics · listCustomers).
---

# hq 태스크

사일로 → 로드맵 → 에픽 → 태스크 (`todo · doing · review · done`).

## 만들기
1. 말에서 뽑는다: 제목 · 사일로 · 담당 · 마감 (+ 에픽 · 고객사 · 시작일 · 설명 — 있을 때만). 세부 할 일 여럿은 설명에 `- ` 목록.
2. id 조회 (1회씩): `listSilos` · `listMembers { activeOnly: true }` (이름 또는 직책 `title` · 나 = `me: true` 행) · `listEpics` · 회사 이름이 나오면 `listCustomers` (표기 그대로 — "광일" → "광일금속" · 목록에 없으면 `customer` 를 넣지 않는다).
3. 빠진 값은 추천을 채운다: 사일로 = 말에 나온 영역 · 고객사 · 같은 주제 태스크의 사일로 / 담당 = 이름 · 직책이 나오면 그 사람, 아니면 본인 (`me` 행 — 누구냐고 묻지 않는다) / 마감 = 근거 있는 것 하나 — 말의 기간 계산 ("이번 주" = 금요일) · 관련 에픽 · 로드맵의 계획 끝 · 미팅 날짜 (다음 주간 미팅 전) · 태스크 크기 (잡일 · 연락 · 확인 = 1~3일 · 문서 · 개발 = 1~2주), 근거가 없으면 "마감 미정 (담당이 정함)" / 에픽 = 제목이 기존 에픽과 겹치면 그 에픽.
4. **확인 한 줄** — 실제 날짜로: "HQ 사일로 · 담당 조성우 · 마감 2026-11-10 (추천 · 다음 미팅 전) — 이대로 만들까요? (바꿀 것만 말해 주세요)". 추천한 값은 "(추천)" 표시 · 마감 추천은 "(추천 · 근거 한 단어)". 사용자가 마감을 말하지 않았으면 이 한 줄에서 반드시 묻는다. 사용자가 전부 말했어도 이 한 줄은 거치고, 값을 바꾸면 고친 한 줄을 다시 보인다. "다음 금요일" 처럼 두 날짜로 읽히면 확인 한 줄에 둘 다 적어 고르게 한다.
5. "ㅇㅇ · 좋아 · 그렇게" → `createTask { title, siloId, assigneeId, dueDate | duePending: true, epicId?, customer?, startDate?, description? }`.
6. 보고: `HQ-0042 — 제목 / 사일로 / 담당 / 마감` 한 줄.

## 조회 — "내 할 일 뭐 있어" · "조성우 할 일" · "이번 주 마감" · "광일 건 뭐 있어"
- `listTasks { mine?, assigneeIds?, dueWithinDays?, customer?, status? }` → 한 줄씩 `키 제목 (마감)`. 내 것 = `mine: true` · 다른 사람 · 여러 명 ("나랑 조성우") = `listMembers` 의 id 로 `assigneeIds`. 담당 이름은 `listMembers`.

## 수정 — "HQ-12 마감 다음 주 금요일로" · "담당 재완으로" · "제목 바꿔"
1. `getTaskByKey { key: "HQ-0012" }` → 바뀔 값 한 줄 확인 → `updateTask { taskId, <바꿀 필드만> }` (`null` = 비움 · 마감을 넣으면 마감 미정이 풀린다).

## 댓글 — "HQ-12 에 '…' 댓글 달아"
- `getTaskByKey` → `addComment { taskId, body }` (만든 사람 · 담당에게 알림).

## 상태 — "시작했어" · "검토 올렸어" · "끝났어"
- `changeTaskStatus` doing · review · done. 날짜는 상태가 맞춘다 — 따로 `updateTask` 하지 않는다.
- `closeEpic` 이 열린 태스크 키 목록과 INVALID 를 주면 목록을 보여 주고 확인 뒤 `force: true`.

## 예
"라인프렌즈 소개서 자료 모아 줘" → "제목 '라인프렌즈 소개서 자료 수집' · 영업 사일로 (추천) · 담당 나 (추천) · 마감 2026-11-06 (추천 · 자료 수집 1~3일) — 이대로 만들까요? (바꿀 것만 말해 주세요)"

## 규칙
- 확인 한 줄 없이 `createTask` · `updateTask` 하지 않는다.
- 같은 요청으로 두 번 만들지 않는다 — 실패 여부를 모르면 `search` 로 제목을 먼저 찾는다.
- `deleteTask` · `closeEpic` 은 사용자가 명시했을 때만, 키 · 제목 확인 뒤.
- 공통: id 는 조회로만 얻는다 · `FORBIDDEN` = admin 에게 요청 안내 · 401 · 연결 오류 = "hq 다시 로그인 (Code `/mcp` · claude.ai 플러그인 Connectors 탭)" 안내 후 멈춤 · 결과 JSON 을 붙이지 않는다.
