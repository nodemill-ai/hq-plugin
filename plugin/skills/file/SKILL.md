---
name: file
description: 회사 공유 드라이브에 파일 올리기 · 찾기. 사용자가 "드라이브에 올려", "이 파일 저장해", "계약서 어디 있어", "~ 파일 찾아줘", "이 파일 태스크에 붙여" 라고 하면 hq MCP (listDriveFolder · searchDrive) 로 기존 폴더 트리에서 자리를 고르고 Google Drive 커넥터로 업로드한 뒤 필요하면 linkResource 로 태스크에 연결한다.
---

# 공유 드라이브 파일

원본 = 회사 Google **공유 드라이브** (`운영` · `고객사` · `제품` 아래 기존 트리). hq 는 읽기 전용 창이다 — 폴더 조회 · 검색은 hq MCP, **업로드는 Google Drive 커넥터** (사용자 본인 권한) 가 한다.

## 올리기 — "드라이브에 올려"

1. **자리 찾기**: `listDriveFolder` (루트) → 내용에 맞는 폴더로 `folderId` 를 따라 내려간다 (예 계약서 → `운영/계약`). 이름으로 바로 찾을 수 있으면 `searchDrive { q: <폴더 이름> }` 의 `isFolder` 항목. **미팅 회의록 · 미팅 자료는 이 스킬이 아니라 `meeting` 스킬** (미팅 폴더 규칙 · 회의록 · 후속 태스크).
2. **맞는 폴더가 없으면 새 폴더를 제안하고 승인받는다** — "`고객사/케이녹스/계약` 폴더를 새로 만들어 넣을까요?" 처럼 경로 1개. 승인 뒤 Drive 커넥터로 폴더를 만든다 (부모 = 기존 폴더 id). 승인 없이 폴더를 만들지 않는다. 루트 (공유 드라이브 바로 아래) 에는 새 폴더를 만들지 않는다.
3. **파일 이름**: `YYYYMMDD_주제_버전.확장자` (예 `20261031_광일금속_견적_v1.pdf`). 사용자가 준 이름이 있으면 그대로.
4. **업로드**: 경로 · 파일 이름을 한 줄로 확인받은 뒤 Google Drive 커넥터 `create_file` — `parentId` = 1~2 에서 고른 폴더 id, **`disableConversionToGoogleType: true`** (안 그러면 텍스트 · 오피스 파일이 Google 문서로 바뀐다), `title` = 3 의 이름, 내용은 `textContent` (텍스트) 또는 `base64Content` + `contentMimeType`.
5. **확인 · 보고**: `listDriveFolder { folderId: <그 폴더> }` 로 파일이 보이는지 확인 → 이름 · 경로 · 링크 (`webViewLink` 또는 hq 의 파일 화면 `https://hq.nodemill.ai/files?file=<id>`) 를 보고.
6. 태스크와 관련 있으면 연결을 제안한다 (아래).

## 찾기 — "~ 파일 어디 있어"

1. `searchDrive { q }` — 이름의 일부면 된다 (대소문자 무시 · 부분 일치). 결과에 폴더 경로 (`path`) 가 붙는다.
2. 여럿이면 경로와 함께 목록, 하나면 이름 · 경로 · 수정 시각 · 링크. 폴더를 둘러보자고 하면 `listDriveFolder`.
3. 못 찾으면 다른 낱말 (영문 · 약칭) 로 한 번 더 찾아본 뒤 없다고 말한다.

## 태스크와 연결

"이 파일 HQ-0042 에 붙여" → `getTaskByKey` 로 taskId → `linkResource { taskId, kind: "file", ref: <Drive 파일 id>, title: <파일 이름> }` (title 을 넣어야 태스크 패널에 이름이 보인다).

## 규칙

- 영수증 · 비용 증빙은 이 스킬이 아니라 `cost` 스킬 (기록 + hq 웹에서 증빙 붙이기). 미팅 회의록 · 자료는 `meeting` 스킬.
- 파일 내용은 hq 가 읽지 않는다 — 미리보기는 hq 파일 화면 (`https://hq.nodemill.ai/files?file=<id>`) 이나 Drive 에서.
- 공유 드라이브 밖 (내 드라이브 · 다른 드라이브) 파일은 hq 에서 `NOT_FOUND` — 공유 드라이브로 옮기자고 안내한다.
- 이동 · 이름 변경 · 삭제는 사용자가 명시적으로 말했을 때만, Drive 커넥터로 (hq 도구 없음).
- 비밀번호 · 키가 든 파일은 올리기 전에 한 번 확인한다.
- `UNAVAILABLE` 이면 Drive 한도 · 장애 — 잠시 뒤 다시. 401 · 연결 오류면 "hq 연결이 끊겼다 — Claude Code 는 `/mcp` 에서, claude.ai 는 플러그인 Connectors 탭에서 hq 에 다시 로그인" 을 안내하고 멈춘다.
