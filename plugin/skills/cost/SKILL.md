---
name: cost
description: hq 비용 기록 · 조회 · 고정비. "영수증 등록", "법카 썼어", "11월 14일 회식 법카 12만 8천원", "AWS 지난달 얼마였지", "이거 얼마였지" (영수증 사진), "이번 달 고정비", "구독 추가", "Claude 구독 해지" 라고 하면. 도구 — createExpense · updateExpense · deleteExpense · listExpenses · listCostItems · createCostItem · updateCostItem · listPaymentCards · getCostSummary (+ searchDrive).
---

# 비용 (영수증 · 법인카드 · 고정비)

비용을 기록 (expense) 으로 남기고 찾는다. 증빙 파일은 hq 웹에서 붙인다 — Claude 는 기록만. 고정비 · 금액 읽기 = [references/고정비.md](references/고정비.md).

## 등록 — "11월 14일 회식 법카 12만 8천원"
1. 말 + 첨부 사진 (읽기만) 에서 `date` · `amount` · `currency` · `vendor` · `purpose` · `paymentMethod` (`corporate_card` · `personal_card` · `transfer` · `other`) · 카드. 말이 사진보다 우선 · 빠진 건 한 번에 묻는다 · 상대 날짜는 실제 날짜로 · 미래 날짜 불가.
2. 고정비면 `listCostItems` 로 `costItemId` 를 묶는다.
3. 법인카드면 `listPaymentCards` — 1장이면 그것 · 여럿이면 `name` · `holderName` 으로 · 애매하면 묻는다 · 새 카드는 이름 확인 뒤 `card` 에 넣는다 (`cardCreated: true`).
4. `listExpenses { from, to, vendor }` 로 중복 확인 — 있으면 "그래도 등록할까요?" 후 멈춘다.
5. 한 줄 확인: "11/14 을지로고깃집 128,000원 · 법인카드(신한 1234) · 팀 회식 — 등록할까요?"
6. `createExpense { … }` → 금액 · 날짜 · 카드 + "영수증은 여기서 붙이세요: `<webUrl>`".
- 영수증이 이미 Drive 에 있으면 `searchDrive` → `receipts: [{ fileId }]` (기존 기록은 `updateExpense { expenseId, addReceipts }`).

## 조회 — "AWS 지난달 얼마였지"
1. `listExpenses { vendor | q, from, to, card?, paymentMethod?, costItemId? }` — 상대 기간은 실제 범위로 바꿔 답에 적는다.
2. 건별 금액 · 날짜 · 공급자 · 용도 · 카드 · 증빙 (`receipts[].webViewLink` 또는 "증빙 없음" + `webUrl`). 여러 건이면 `totals` · `missingReceipts` 한 줄.
3. 못 찾으면 기간을 넓히거나 `q` 로 한 번 더.

## 예
"AWS 지난달 얼마였지" → `listExpenses { vendor: "AWS", from: "2026-10-01", to: "2026-10-31" }` → "2026-10-01 ~ 2026-10-31 · AWS 412,300원 (11/02 법인카드) · 증빙 없음 → <webUrl>"

## 규칙
- 금액: KRW 정수 · USD 소수 2자리 ("12만 8천원" → `128000`). 카드 번호는 끝 4자리까지만.
- 확인 전에 `createExpense` 하지 않는다. 수정 · 삭제는 명시했을 때만 (등록자 · admin — `FORBIDDEN` 이면 그렇게 안내).
- 증빙 파일을 Drive 커넥터로 올리지 않는다 — `webUrl` 로 안내.
- `UNAVAILABLE` = 일시 장애 — 잠시 뒤 다시.
- 공통: id 는 조회로만 얻는다 · 401 · 연결 오류 = "hq 다시 로그인 (Code `/mcp` · claude.ai 플러그인 Connectors 탭)" 안내 후 멈춤 · 결과 JSON 을 붙이지 않는다.
