---
name: roadmap
description: hq 로드맵 짜기 · 에픽 배치 · 진행 보기 · 닫기. "로드맵 짜 줘", "ERP 로드맵 만들어", "3월까지 ~ 계획 세워 줘", "이 에픽 로드맵에 넣어", "에픽 기간 바꿔", "로드맵 진행 어때", "늦어지는 거 있어?" 라고 하면. 도구 — listRoadmaps · getRoadmap · createRoadmap · updateRoadmap · closeRoadmap · reopenRoadmap · createEpic · updateEpic.
---

# hq 로드맵

사일로 1개 안의 몇 달짜리 계획 (목표 · 계획 기간) 과 그 아래 에픽을 만들고 진행을 본다. 계획 = 직접 적은 기간 (`planned`) · 실제 = 태스크에서 계산 (`actual`) · 지연 (`late`) = 열려 있는데 계획 끝이 지남. 웹 위치 = hq **태스크 탭 › 로드맵**.

## 짜기 — "ERP 로드맵 짜 줘 — 3월까지 첫 납품"
1. 뽑는다: 사일로 · 이름 · 목표 1문장 · 계획 기간 · 단계 (에픽 후보). 기간 · 단계가 없으면 묻는다.
2. `listRoadmaps { siloId, activeOnly: false }` · `listEpics { siloId }` 로 같은 이름이 있는지 본다.
3. 표로 확인받는다 (실제 날짜) — `| 에픽 | 계획 시작 | 계획 끝 | 첫 태스크 (선택) |` · 기존 에픽은 "기존 — 이 로드맵으로 옮김".
4. `createRoadmap { siloId, name, goal, startDate, endDate }` → 에픽마다 `createEpic { siloId, name, roadmapId, startDate, endDate }`. `created: false` 면 `updateEpic { epicId, roadmapId, startDate, endDate }`. 첫 태스크는 원할 때만 `task` 스킬로.
5. 보고: 로드맵 이름 · 기간 → 에픽 한 줄씩.

## 에픽 넣기 · 빼기 · 기간
- 넣기 `updateEpic { epicId, roadmapId }` · 빼기 `roadmapId: null` · 기간 `startDate` · `endDate` (`null` = 비움).
- 다른 사일로 = INVALID (그대로 알림) · 닫힌 로드맵 = INVALID → "다시 열까요?" 뒤 `reopenRoadmap`.
- 로드맵 자체 = `updateRoadmap`. 에픽이 로드맵 끝보다 늦으면 한 줄 짚는다.

## 진행 — "로드맵 진행 어때"
1. `listRoadmaps` → 한 줄씩 `ERP 1.0 — 2026-11-10 ~ 2027-03-31 · 에픽 1/4 · 태스크 7/23` (+ "지연" · "계획 없음").
2. 지연 · 특정 로드맵 → `getRoadmap { roadmapId }` → 지연 에픽 · 실제가 계획보다 늦는 에픽 · 기간 없는 에픽만 짚는다.
3. 액션 1~3개 제안 (기간 조정 · 상태 변경 · 담당 확인).

## 닫기
- 사용자가 "닫아" 했을 때만 `closeRoadmap`. 열린 에픽 INVALID → 목록을 보이고 확인 뒤 `force: true`. 되돌리기 = `reopenRoadmap`.

## 규칙
- 확인 전에 만들지 않는다 · 두 번 만들지 않는다 (모르면 `listRoadmaps` · `listEpics` 로 먼저 찾는다).
- 삭제 도구는 없다 — 지우라고 하면 닫기를 제안한다.
- 공통: id 는 조회로만 얻는다 · `FORBIDDEN` = admin 에게 요청 안내 · 401 · 연결 오류 = "hq 다시 로그인 (Code `/mcp` · claude.ai 플러그인 Connectors 탭)" 안내 후 멈춤 · 결과 JSON 을 붙이지 않는다.
