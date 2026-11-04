---
name: file
description: 회사 공유 드라이브 파일 올리기 · 찾기 · 태스크에 붙이기. "드라이브에 올려", "이 파일 저장해", "계약서 어디 있어", "~ 파일 찾아줘", "이 파일 태스크에 붙여" 라고 하면. 도구 — hq listDriveFolder · searchDrive · linkResource (조회 · 연결) · Google Drive 커넥터 create_file (업로드).
---

# 공유 드라이브 파일

공유 드라이브 (`운영` · `고객사` · `제품`) 기존 트리에 자리를 골라 올리고 찾는다. 조회는 hq, 업로드는 Drive 커넥터.

## 올리기 — "드라이브에 올려"
1. `listDriveFolder` (루트) → `folderId` 를 따라 내려간다 (계약서 → `운영/계약`). 이름을 알면 `searchDrive { q }` 의 `isFolder`.
2. 맞는 폴더가 없으면 경로 1개를 제안 · 승인 뒤 커넥터로 만든다 (루트 바로 아래는 만들지 않는다).
3. 이름 `YYYYMMDD_주제_버전.확장자` (`20261031_광일금속_견적_v1.pdf`) — 사용자가 준 이름이 있으면 그대로.
4. 경로 · 이름 한 줄 확인 → `create_file { parentId, title, disableConversionToGoogleType: true, textContent | base64Content + contentMimeType }`.
5. `listDriveFolder { folderId }` 로 보이는지 확인 → 이름 · 경로 · 링크 (`webViewLink` 또는 `https://hq.nodemill.ai/files?file=<id>`). 관련 태스크가 있으면 연결을 제안.

## 찾기 — "~ 파일 어디 있어"
1. `searchDrive { q }` (부분 일치) → 여럿이면 경로와 목록, 하나면 이름 · 경로 · 수정 시각 · 링크.
2. 못 찾으면 다른 낱말 (영문 · 약칭) 로 한 번 더 찾고 없다고 말한다.

## 태스크에 붙이기
- `getTaskByKey` → `linkResource { taskId, kind: "file", ref: <파일 id>, title: <파일 이름> }`.

## 예
"이 견적서 광일 폴더에 올려" → `searchDrive { q: "광일금속" }` → "`고객사/광일금속/견적` 에 `20261104_광일금속_견적_v1.pdf` 로 올릴까요?" → `create_file`

## 규칙
- 영수증은 `cost` 스킬 · 미팅 회의록 · 자료는 `meeting` 스킬.
- 승인 없이 폴더를 만들지 않는다 · 이동 · 이름 변경 · 삭제는 명시했을 때만 커넥터로.
- 비밀번호 · 키가 든 파일은 올리기 전 한 번 확인한다. 공유 드라이브 밖 파일 (`NOT_FOUND`) 은 옮기자고 안내한다.
- `UNAVAILABLE` = Drive 한도 · 장애 — 잠시 뒤 다시.
- 공통: id 는 조회로만 얻는다 · 401 · 연결 오류 = "hq 다시 로그인 (Code `/mcp` · claude.ai 플러그인 Connectors 탭)" 안내 후 멈춤 · 결과 JSON 을 붙이지 않는다.
