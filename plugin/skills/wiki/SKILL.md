---
name: wiki
description: hq 위키 (회사 문서) 쓰기 · 수정 · 삭제 · 찾기. "위키에 올려", "이거 위키에 정리해", "결정 기록으로 저장", "위키 고쳐", "위키 지워", "위키에서 ~ 찾아봐", "~ 가이드 어디 있어", "계정 어딨지", "~ 비밀번호 뭐야" 라고 하면. 도구 — listWikiTree · getWikiPage · writeWikiPage · deleteWikiPage · linkResource.
---

# hq 위키

회사 Markdown 위키를 hq 가 대신 커밋한다 (커밋에 내 이름). 본문 작성 기준 = [references/작성-규칙.md](references/작성-규칙.md).

## 쓰기 — "위키에 올려"
1. 올릴 내용이 초안이면 작성 규칙대로 줄여 "이대로 올릴까요?" 확인.
2. `listWikiTree` 1회 → 맞는 기존 폴더를 고른다. 같은 주제 문서가 있으면 수정 흐름으로. 맞는 폴더가 없으면 경로 1개를 제안해 승인받는다.
3. 맞는 템플릿 (`templates`) 을 `getWikiPage` 로 읽어 목차를 따르고 frontmatter 를 채운다.
4. 경로 · 제목 한 줄 확인 → `writeWikiPage { path, body, message }` (새 파일은 `baseSha` 없이).
5. 보고: 제목 · 경로 · `hqUrl`.

## 수정 — "위키 고쳐"
1. 찾기 → `getWikiPage` 로 `content` · `sha` → 변경을 합친 전체 본문 (frontmatter 유지) → 바뀌는 부분 요약 확인.
2. `writeWikiPage { path, body, message, baseSha: sha }`. `INVALID` + "current sha" 면 다시 읽어 합쳐 1회만 재시도.

## 삭제 — "위키 지워"
1. 사용자가 명시했을 때만 → `getWikiPage` → "이 문서를 지울까요? (되살리기는 GitHub 이력에서만)" 확인.
2. `deleteWikiPage { path, baseSha: sha }` (`baseSha` 필수). `INVALID` = 다시 읽어 다시 확인 (자동 재시도 없음). 루트 `README.md` · `_templates/` · `assets/` 는 못 지운다.
3. 이동 · 이름 변경 = 새 경로 `writeWikiPage` → 옛 문서 `deleteWikiPage` (둘 다 확인 뒤).

## 찾기 — "위키에서 ~ 찾아봐"
1. `listWikiTree` → 경로 · 파일명으로 후보 (본문 검색 없음). 여럿이면 고르게, 하나면 `getWikiPage`.
2. 답 = 필요한 부분 요약 + `hqUrl`. 없으면 "위키에 '~' 문서가 없다" 후 새로 만들지 묻는다.
3. 태스크에 붙이기 = `getTaskByKey` → `linkResource { taskId, kind: "wiki", ref: <path>, title }`.

## 예
"이 결정 위키에 올려" → `listWikiTree` → `getWikiPage _templates/결정-기록.md` → "`제품/2026-11-04-로드맵-단위.md` 로 올릴까요?" → `writeWikiPage`

## 규칙
- 회사 계정 · 비밀번호는 위키 · 드라이브를 뒤지지 않고 Bitwarden (`https://vault.bitwarden.com` · hq 사이드바 "계정") 으로 한 줄 안내한다.
- 승인 없이 새 폴더를 만들지 않는다 · `_templates/` 는 읽기만.
- 본문에 비밀번호 · 키 · 개인 연락처를 넣지 않는다.
- `UNAVAILABLE` = GitHub 한도 · 장애 — 재시도를 반복하지 않는다.
- 공통: id 는 조회로만 얻는다 · `FORBIDDEN` = admin 에게 요청 안내 · 401 · 연결 오류 = "hq 다시 로그인 (Code `/mcp` · claude.ai 플러그인 Connectors 탭)" 안내 후 멈춤 · 결과 JSON 을 붙이지 않는다.
