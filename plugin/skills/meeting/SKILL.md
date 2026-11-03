---
name: meeting
description: 미팅 회의록 정리 · 올리기 · 찾기. 사용자가 "미팅 정리해 줘", "회의록 써 줘", "오늘 광일 미팅 정리", "지난 광일 미팅 뭐였지", "ERP 시연 때 뭐 정했지", "이 슬라이드 어제 미팅에 넣어" 라고 하면 hq MCP (listMeetings · getMeeting) 로 미팅 자리를 찾고, Google Drive 커넥터로 미팅 폴더 · 회의록.md · 자료를 올린 뒤 후속 태스크를 createTask · linkResource(kind=meeting) 로 만들어 미팅에 연결한다.
---

# 미팅

원본 = 회사 Google **공유 드라이브**. 미팅 1건 = 폴더 1개 — hq 는 읽기 전용 창 (`https://hq.nodemill.ai/meetings`) 이고, 폴더 · 파일 **쓰기는 Google Drive 커넥터** (사용자 본인 권한) 가 한다. hq 에 미팅을 만드는 도구는 없다.

## 자리 규칙

| 종류 | 자리 | 예 |
|---|---|---|
| 노드밀 (사내) | `운영/미팅/YYYY-MM-DD_주제/` | `운영/미팅/2026-11-03_hq-로드맵/` |
| 사외 | `고객사/<회사>/미팅/YYYY-MM-DD_주제/` | `고객사/광일금속/미팅/2026-11-03_ERP-1차-시연/` |

- 주제 = 낱말을 `-` 로 잇는다 (공백 없음). 같은 날 같은 주제가 이미 있으면 `_2`.
- 폴더 안: **`회의록.md`** (이름 고정 · 0~1개) + 자료 (슬라이드 · pdf · 이미지 — 이름은 `file` 스킬 규칙 `YYYYMMDD_주제_버전.확장자`, 사용자가 준 이름이 있으면 그대로).
- 종류 · 회사는 위치로 정해진다 — frontmatter 에 넣지 않는다.

## 정리 · 올리기 — "미팅 정리해 줘" (+ 메모 · 녹취 텍스트 · 슬라이드)

1. **자리 판정**: 사내 / 사외를 참석자 · 말에서 정한다 (외부 회사 사람이 있으면 사외). 애매하면 묻는다.
   - 사외: `listMeetings { kind: "external" }` 의 `companies` 에서 회사를 고른다.
     - `meetingsFolderId` 가 있으면 그 폴더가 부모.
     - 회사는 있는데 `meetingsFolderId` 가 null 이면 → 커넥터로 `고객사/<회사>/미팅` 폴더를 만든다 (규칙 고정 경로 — 승인 없이).
     - 회사가 없으면 → "`고객사/<회사>` 를 새로 만들까요?" 로 제안 · 승인 (`file` 스킬 규칙 — 승인 없이 회사 폴더를 만들지 않는다).
   - 노드밀: `listMeetings { kind: "internal" }` 결과가 비어 있어도 된다. `운영/미팅` 폴더 id 는 `searchDrive { q: "미팅" }` 의 `path` 가 `운영` 인 폴더 — 없으면 `운영` 아래에 커넥터로 `미팅` 을 만든다 (규칙 고정 경로 — 승인 없이 · 루트에는 만들지 않는다).
2. **회의록 작성**: `references/회의록.md` 템플릿 목차대로 — frontmatter (`title` · `date` · `attendees` · `tags`) · **일시 · 참석** · **안건** · **논의** · **결정 사항** · **후속 태스크** · **자료**. 메모에 없는 내용은 지어내지 않는다 (빈 절은 "없음"). 날짜는 한국 시간 `YYYY-MM-DD`.
3. **후속 태스크 후보**: 결정 사항 · 할 일에서 뽑는다 (담당 · 마감 포함). `task` 스킬 규칙대로 사일로 · 담당 id 를 조회해 둔다 (아직 만들지 않는다).
4. **한 줄 확인**: "`고객사/광일금속/미팅/2026-11-03_ERP-1차-시연/` 에 회의록 + 자료 2개 · 후속 태스크 3개 (① … ② … ③ …) — 올릴까요?" — 사용자가 빼거나 고친 것을 반영한다.
5. **올리기** (Google Drive 커넥터 `create_file`):
   1. 미팅 폴더 생성 (부모 = 1 의 미팅 폴더 id).
   2. `회의록.md` — `textContent` = 회의록 전문 · `contentMimeType: "text/markdown"` · **`disableConversionToGoogleType: true`** (안 그러면 Google 문서로 바뀌어 hq 가 본문을 못 그린다).
   3. 자료 — `base64Content` + `contentMimeType` (같은 옵션). 첨부 바이트를 넘길 수 없으면 회의록만 올리고 "자료는 Drive 앱 · hq 파일 화면에서 이 폴더로 올려 주세요" 로 폴더 링크를 준다.
6. **후속 태스크**: 확인받은 항목마다 `createTask` (사외 미팅이면 `customer` = 그 미팅의 회사 이름 — `listMeetings` 의 `company` 그대로) → `linkResource { taskId, kind: "meeting", ref: <미팅 폴더 id>, title: "<YYYY-MM-DD> <주제 (공백)>" }` → 만든 키를 회의록 "후속 태스크" 절에 채워 커넥터로 `회의록.md` 를 갱신한다.
7. **확인 · 보고**: `getMeeting { meetingId: <폴더 id> }` 로 회의록 (`minutes.status: ok`) · 자료가 보이는지 확인 → 미팅 제목 · 자리 · hq 링크 (`hqUrl` = `https://hq.nodemill.ai/meetings?m=<id>`) · 만든 태스크 키를 보고. 목록 화면에는 최대 5분 늦게 보일 수 있다 (링크는 바로 열린다).

## 찾기 · 회상 — "지난 광일 미팅 뭐였지" · "ERP 시연 때 뭐 정했지"

1. `listMeetings` — 회사면 `company`, 주제 · 내용이면 `q` (제목 부분 일치 + 회의록 · 자료 내용의 낱말 일치), 기간이면 `from` / `to`. `contentSearched: false` 면 내용 검색이 안 된 것 — 다른 낱말로 한 번 더.
2. 고른 미팅을 `getMeeting` → 결정 사항 · 후속 태스크 (`tasks` 의 키 · 상태) 를 요약하고 `hqUrl` 링크.
3. 회의록이 없는 미팅 (`minutes: null`) 은 자료 이름 · 링크를 준다. `minutes.status: unreadable` 이면 Drive 에서 열라고 안내.

## 덧붙이기 — "이 슬라이드 어제 광일 미팅에 넣어"

1. `listMeetings { company, from }` 로 미팅을 찾는다 (여럿이면 고르게 한다).
2. 파일 이름 · 미팅을 한 줄로 확인 → 커넥터로 그 미팅 폴더 (`id`) 에 업로드 (`disableConversionToGoogleType: true`).
3. 회의록이 있으면 "자료" 절에 파일 이름을 더할지 묻는다 (`getMeeting` 의 `minutes.fileId` 를 커넥터로 갱신).

## 규칙

- 회의록 고치기는 `getMeeting` 으로 지금 내용을 읽은 뒤 합쳐서 — 다른 사람이 Drive 에서 고친 내용을 덮어쓰지 않는다.
- 위키 회의록 템플릿 (`_templates/회의록.md`) · 위키 문서로 미팅을 쓰지 않는다 — 미팅은 이 스킬 (공유 드라이브).
- 미팅 위치 밖 폴더 id 는 hq 에서 `NOT_FOUND` — 자리 규칙대로 옮기자고 안내한다 (이동은 사용자가 말했을 때만).
- 비밀번호 · 키 · 개인정보가 든 메모는 올리기 전에 한 번 확인한다.
- `UNAVAILABLE` 이면 Drive 한도 · 장애 — 잠시 뒤 다시. 401 · 연결 오류면 "hq 연결이 끊겼다 — Claude Code 는 `/mcp` 에서, claude.ai 는 플러그인 Connectors 탭에서 hq 에 다시 로그인" 을 안내하고 멈춘다.
