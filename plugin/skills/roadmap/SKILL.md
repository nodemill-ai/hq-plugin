---
name: roadmap
description: hq 로드맵 (몇 달짜리 계획) 짜기 · 에픽 배치 · 진행 보기 · 닫기. 사용자가 "로드맵 짜 줘", "ERP 로드맵 만들어", "3월까지 ~ 계획 세워 줘", "이 에픽 로드맵에 넣어", "에픽 기간 바꿔", "로드맵 진행 어때", "ERP 일정 어떻게 돼", "늦어지는 거 있어?" 라고 하면 hq MCP 로드맵 도구 (listRoadmaps · getRoadmap · createRoadmap · updateRoadmap · closeRoadmap) 와 createEpic · updateEpic 으로 처리한다.
---

# hq 로드맵

**id 는 추측하지 않는다** — `listSilos` · `listRoadmaps` · `listEpics` · `listMembers` 로 얻는다.

## 개념

사일로 (업무 영역) → **로드맵** (몇 달짜리 계획 — 목표 · 계획 기간) → 에픽 (태스크 묶음 · 계획 기간) → 태스크. 로드맵은 한 사일로에 속한다 (사일로를 넘는 로드맵 없음). 에픽 없는 태스크 · 로드맵 없는 에픽도 괜찮다 — 잡일마다 로드맵을 만들지 않는다.

- **계획** = 로드맵 · 에픽에 직접 적은 시작 · 끝 (`planned`). **실제** = 태스크의 시작 · 마감에서 계산 (`actual`). 둘은 다를 수 있고 그게 정보다.
- **지연** (`late`) = 열려 있는데 오늘 (한국 시간) 이 계획 끝을 지남.
- 진행률: 로드맵 = 닫힌 에픽 / 전체 에픽 · 끝난 태스크 / 전체 태스크. 에픽 = 끝난 태스크 / 전체.
- 웹 = hq **태스크 탭 › 로드맵** (트리 + 데스크톱 막대 타임라인 · 홈 "로드맵" 블록). 화면에서 보라고 안내할 때는 이 위치를 말한다.

## 로드맵 짜기 ("ERP 로드맵 짜 줘 — 3월까지 첫 납품")

1. 사용자 말에서 뽑는다: 사일로 · 로드맵 이름 · 목표 (한 문장) · 계획 기간 · 단계 (에픽 후보). 사일로가 애매하면 `listSilos` 후 묻는다. 기간 · 단계를 말하지 않았으면 묻는다 (지어내지 않는다).
2. `listRoadmaps { siloId, activeOnly: false }` · `listEpics { siloId }` 로 같은 이름이 이미 있는지 본다.
3. **만들기 전에 표로 보여 주고 확인받는다** — 상대 날짜는 실제 날짜로 (오늘 기준 · `YYYY-MM-DD`):

   | 에픽 | 계획 시작 | 계획 끝 | 첫 태스크 (선택) |
   |---|---|---|---|
   | 재고 모듈 | 2026-11-10 | 2026-12-15 | 입고 화면 |

   이미 있는 에픽은 "기존 — 이 로드맵으로 옮김" 으로 표시한다.
4. 확인되면: `createRoadmap { siloId, name, goal, startDate, endDate }` → 에픽마다 `createEpic { siloId, name, roadmapId, startDate, endDate }`.
   - `created: false` (같은 이름 기존 에픽) 이면 로드맵 · 기간이 **적용되지 않았다** → 표에서 확인받은 대로 `updateEpic { epicId, roadmapId, startDate, endDate }`.
   - 첫 태스크는 사용자가 원할 때만 `task` 스킬 규칙대로 `createTask { …, epicId }` (담당 · 마감은 묻거나 비운다).
5. 보고: 로드맵 이름 · 기간 → 에픽 한 줄씩 (이름 · 계획 기간). 결과 JSON 은 붙이지 않는다.

## 에픽을 로드맵에 넣기 · 빼기 · 기간 바꾸기

- "이 에픽 ERP 로드맵에 넣어" → `listRoadmaps` · `listEpics` 로 id → `updateEpic { epicId, roadmapId }`.
  - 같은 사일로의 로드맵만 된다 (다른 사일로 = INVALID — 사용자에게 사일로가 다르다고 말한다).
  - 닫힌 로드맵 = INVALID → "다시 열까요?" 라고 묻고, 원하면 `reopenRoadmap` 뒤 다시.
- 빼기 = `updateEpic { epicId, roadmapId: null }`. 기간 = `updateEpic { epicId, startDate, endDate }` (`null` = 비움).
- 로드맵 이름 · 목표 · 기간 = `updateRoadmap`. 에픽 계획이 로드맵 기간 밖이어도 된다 — 다만 보고에 "로드맵 끝 (3/31) 보다 늦다" 를 한 줄 짚는다.

## 진행 보기 ("로드맵 진행 어때", "ERP 일정 어떻게 돼")

1. `listRoadmaps` (특정 사일로면 `siloId`) → 로드맵마다 한 줄:
   `ERP 1.0 — 2026-11-10 ~ 2027-03-31 · 에픽 1/4 · 태스크 7/23` (+ 지연이면 "지연", 계획이 없으면 "계획 없음").
2. 지연 로드맵 · 사용자가 특정 로드맵을 물으면 `getRoadmap { roadmapId }` → 짚을 것만:
   - 지연 에픽 (`late`) — 이름 · 계획 끝 · 남은 태스크 수.
   - 실제가 계획보다 늦게 끝나는 에픽 (`actual.end` > `planned.end`).
   - 계획 기간이 없는 에픽 — "기간을 정할까요?" 제안.
3. 바로 할 수 있는 액션을 1~3개 제안한다 (기간 조정 · 태스크 상태 변경 · 담당 확인). 담당자 이름은 `listMembers` 로.

## 닫기 · 다시 열기

- 사용자가 명시적으로 "로드맵 닫아" 라고 했을 때만 `closeRoadmap { roadmapId }`.
- 열린 에픽이 있으면 INVALID 와 이름 목록이 온다 → 목록을 보여 주고 "에픽은 열린 채로 두고 로드맵만 닫을까요?" 확인 뒤 `force: true`. 에픽까지 닫으려면 에픽마다 `closeEpic` (태스크 규칙은 `task` 스킬).
- 되돌리기 = `reopenRoadmap`.

## 규칙

- 같은 요청으로 로드맵 · 에픽을 두 번 만들지 않는다 — 실패했는지 모르면 `listRoadmaps` · `listEpics` 로 먼저 찾는다.
- 삭제 도구는 없다 (닫기만). 사용자가 지우라고 하면 닫기를 제안한다.
- `FORBIDDEN` 이면 권한 문제 — 우회하지 말고 admin 에게 요청하라고 안내한다.
- 401 · 연결 오류면 "hq 연결이 끊겼다 — Claude Code 는 `/mcp` 에서, claude.ai 는 플러그인 Connectors 탭에서 hq 에 다시 로그인" 을 안내하고 멈춘다.
