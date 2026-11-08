---
name: parking
description: hq 보류함 — "언젠가" 일 넣기 · 보기 · 꺼내기. "보류함에 넣어", "언젠가 해야 하는데", "나중에 — 사무실 생기면", "HQ-0037 보류함으로", "보류함 보여 줘", "꺼낼 것 있어?", "보류함의 X 꺼내 줘", "꺼내서 로드맵으로 짜 줘" 라고 하면. 도구 — parkItem · listParkingItems · getParkingItem · updateParkingItem · takeOutParkingItem · deleteParkingItem (+ getTaskByKey · listSilos · listTasks · listEvents · createTask · createEpic · createRoadmap · linkResource).
---

# hq 보류함

지금은 못 하고 조건이 되면 할 일을 태스크가 아닌 **보류 항목** (제목 · 꺼낼 조건 · 개념 · 사일로 · 링크) 으로 둔다 — 보드 · 브리핑 · 캘린더에 안 나온다. 모양 (태스크 · 에픽 · 로드맵) 은 꺼낼 때 정한다. 웹 위치 = hq **태스크 탭 › 보류함**.

## 넣기 — "도메인 연락처 교체는 사무실 번호 생기면 — 보류함에 넣어" · "HQ-0037 보류함으로"
1. 새 일: 제목 · 꺼낼 조건 한 줄 · 개념 (말한 맥락) · 사일로 (분명할 때만 `listSilos` — 모르면 비움) 을 뽑는다. 조건이 없으면 한 줄을 제안한다.
2. 기존 태스크: `getTaskByKey` → 완료면 못 옮긴다고 알린다 · 아니면 "보드에서 빠지고 설명 · 댓글 · 링크 (+ 담당 · 에픽 · 마감 한 줄) 가 항목으로 가요" 를 함께 보인다.
3. 확인 한 줄 ("보류함 — 제목 · 꺼낼 때 '사무실 대표번호가 생기면' (추천) — 넣을까요?") 뒤 `parkItem { title, condition?, concept?, siloId? }` 또는 `parkItem { taskId, condition? }`. taskId 와 title · concept · siloId 를 같이 주지 않는다 (고칠 건 뒤에 `updateParkingItem`).
4. 보고: `보류함 — 제목 (꺼낼 때 · 조건)` 한 줄.

## 보기 — "보류함 보여 줘"
- `listParkingItems { q?, siloId? }` → 한 줄씩 `제목 — 꺼낼 때 · 조건 (원래 키)`. 꺼낸 것까지 = `status: "all"` · 꺼낸 것만 = `"taken_out"`.

## 꺼낼 것 있어? — "보류함에서 꺼낼 것 있어?"
1. `listParkingItems` (보류 중). 비면 "보류함이 비어 있어요".
2. 지금 상황을 모은다: 이 대화에서 사용자가 말한 사실 · 최근 태스크 (`listTasks { status: "done" }` · `"doing"`) · 일정 (`listEvents` 오늘 ~ 2주) — 조건과 이어질 만할 때만 부른다.
3. 항목마다 꺼낼 조건 ↔ 상황을 대조해 **후보만** 1~2줄: `제목 — 조건 '…' · 근거 (무엇이 언제) → 꺼낼 만해요 (추천 모양)`. 근거 없는 것은 "아직: 제목, 제목" 한 줄 · 조건 없는 것은 "조건 없음 N개 — 정할까요?".
4. 사용자가 고르면 아래 "꺼내기". 고르기 전에는 아무것도 만들지 않는다.

## 꺼내기 — "보류함의 X 꺼내 줘" · "꺼내서 로드맵으로 짜 줘"
1. `listParkingItems { q: "X" }` → `getParkingItem { itemId }` (개념 · 링크).
2. 모양을 추천 1개 + 근거로 정한다: 태스크 (한 사람 · 몇 주 안) · 에픽 (태스크 여럿) · 로드맵 (몇 달 · 에픽 여럿 → `roadmap` 스킬 "짜기" 절차). 사일로가 비었으면 이때 정한다.
3. 확인 뒤 만든다: `createTask` (`task` 스킬의 확인 한 줄 · `description` = 개념) · `createEpic` · `createRoadmap` (`goal` = 개념 요약 · 2000자 이하). `created: false` (같은 이름이 이미 있음) 면 그것을 기록할지 다른 이름으로 할지 묻는다.
4. `takeOutParkingItem { itemId, made: [{ kind: "task" | "epic" | "roadmap", id }, …] }` — 만든 것 전부 (1~20개).
5. 항목 링크는 자동으로 안 옮겨진다 — 태스크에 필요한 것만 `linkResource { taskId, kind, ref, title }`.
6. 보고: `꺼냄 — 제목 → HQ-0123 · 에픽 「…」` 한 줄.

## 고치기 · 삭제
- "도메인 건 조건을 '사무실 계약 뒤' 로 바꿔" → `updateParkingItem { itemId, condition }` (바꿀 필드만 · `null` = 비움). 꺼낸 항목은 INVALID.
- 삭제는 사용자가 "필요 없어졌어 · 지워" 라고 했을 때만, 제목 확인 뒤 `deleteParkingItem { itemId }` (만든 사람 · admin · 태스크에서 옮긴 항목 (`originTaskKey` 있음) 은 admin 만 — `FORBIDDEN` 이면 admin 에게 안내). 일을 시작하는 거면 삭제가 아니라 꺼내기.

## 예
"보류함에서 꺼낼 것 있어?" → "도메인 연락처 교체 — 조건 '사무실 대표번호가 생기면' · 어제 '대표번호 개통' 태스크가 완료됐어요 → 태스크로 꺼낼까요? / 아직: 개인정보처리방침 공개 (실제 배포 전)"

## 규칙
- "언젠가 · 조건이 되면" 일은 태스크로 만들지 않고 여기에 넣는다 — 마감 · 담당을 지어내지 않는다.
- 조건이 됐는지는 **제안만** 한다 — 확인 없이 꺼내거나 (`create*` · `takeOutParkingItem`) 태스크를 옮기지 (`parkItem { taskId }`) 않는다.
- 꺼낼 때 만든 것은 빠짐없이 `takeOutParkingItem` 에 기록한다 — 안 하면 항목이 보류 중으로 남아 두 번 꺼내게 된다.
- 같은 요청으로 두 번 넣지 않는다 — 실패 여부를 모르면 `listParkingItems { q }` 로 먼저 찾는다.
- 공통: id 는 조회로만 얻는다 · `FORBIDDEN` = admin 에게 요청 안내 · 401 · 연결 오류 = "hq 다시 로그인 (Code `/mcp` · claude.ai 플러그인 Connectors 탭)" 안내 후 멈춤 · 결과 JSON 을 붙이지 않는다.
