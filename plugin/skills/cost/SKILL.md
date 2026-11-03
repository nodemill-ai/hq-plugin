---
name: cost
description: hq 비용 기록 · 조회 · 고정비. 사용자가 "영수증 등록", "법카 썼어", "11월 14일 회식 법카 12만 8천원", "법인카드로 결제했어", "AWS 지난달 얼마였지", "이거 얼마였지" (영수증 사진), "이번 달 고정비", "구독 추가", "Claude 구독 해지" 처럼 비용 · 영수증 · 법인카드 · 고정비를 말하면 hq MCP (createExpense · listExpenses · listCostItems · listPaymentCards · getCostSummary 등) 로 기록하고 찾는다. 증빙 파일은 올리지 않고 hq 웹 링크를 돌려준다.
---

# 비용 (영수증 · 법인카드 · 고정비)

## 개념

- **기록** (expense) = 한 장부. 영수증 · 법카 사용 · 구독 결제가 모두 같은 기록이다: 날짜 · 금액 · 통화 · 공급자 (가게 · 서비스) · 용도 · 결제수단 · (법인카드면) 카드.
- **고정비 항목** (cost item) = 반복 결제 (AWS · Vercel · Claude 구독 …). 분류 `infra` 인프라 · `ai` AI 도구 · `saas` 업무 도구 · `other` 기타, 주기 `monthly` · `yearly`. 고정비 결제 기록은 `costItemId` 로 항목에 묶는다.
- **법인카드** = 회사 카드는 전부 법인카드다. 결제수단이 `corporate_card` 일 때만 카드가 필수이고, 그 외 (`personal_card` 개인카드 = 환급 대상 · `transfer` 계좌이체 · `other`) 에는 카드를 넣지 않는다.
- **증빙** (영수증 사진 · PDF) 은 **hq 웹** (폰 PWA 포함) 에서 붙인다. Claude 는 기록만 만든다.

## 등록 — "11월 14일 회식 법카 12만 8천원"

사진 · PDF 를 붙였으면 **읽기만** 한다 (날짜 · 금액 · 공급자). 올리지 않는다.

1. **필드 모으기**: 사용자 말 + 첨부 이미지에서 `date` · `amount` · `currency` (KRW · USD) · `vendor` · `purpose` · `paymentMethod` · 카드. 사용자 말이 이미지보다 우선. 모자란 것은 **한 번에 묶어서** 묻는다. 날짜를 상대 표현 ("어제", "지난 금요일") 으로 말하면 한국 시간 기준 실제 날짜로 바꾼다. 오늘 이후 날짜는 등록할 수 없다.
2. **고정비면** `listCostItems` 로 항목을 찾아 `costItemId` 로 묶는다 ("AWS 결제", "Vercel 이번 달" 등). 맞는 항목이 없으면 묶지 않고, 매달 나가는 것이면 아래 고정비 항목 만들기를 제안한다.
3. **법인카드면** `listPaymentCards`:
   - 카드가 1장 → 그 카드.
   - 여러 장 → 사용자 말 ("신한", "1234", 쓰는 사람 이름) 로 `name` · `holderName` 과 맞춰 고른다. 애매하면 목록을 보여 주고 묻는다.
   - 목록에 없는 새 카드 → 이름을 사용자에게 확인받는다. 확인된 이름을 `createExpense` 의 `card` 에 넣으면 hq 가 카드를 만든다 (응답 `cardCreated: true`).
   - 카드 번호 전체는 받지도 쓰지도 않는다. 필요하면 끝 4자리만.
4. **중복 확인**: `listExpenses { from: <날짜>, to: <날짜>, vendor: <공급자> }` 로 같은 날짜 · 금액 · 공급자가 이미 있는지 본다. 있으면 "이미 같은 기록이 있습니다 (…) — 그래도 등록할까요?" 로 묻고 멈춘다.
5. **한 줄 확인**: 실제 날짜 · 금액 · 카드를 넣어 확인받는다 — "11/14 을지로고깃집 128,000원 · 법인카드(신한 1234) · 용도 팀 회식 — 등록할까요?". 확인 전에 `createExpense` 를 부르지 않는다.
6. **등록 · 보고**: `createExpense { date, amount, currency, vendor, purpose, paymentMethod, card?, costItemId? }` (증빙 없이). 보고 = 금액 · 날짜 · 카드 + **"영수증은 여기서 붙이세요: `<webUrl>`"** (응답의 `webUrl` 을 그대로). 카드를 새로 만들었으면 (`cardCreated`) 그 사실도 한 줄.

사용자가 "영수증은 이미 Drive 에 있어" 라고 하면 `searchDrive { q }` 로 파일을 찾아 (여럿이면 경로와 함께 보여 주고 고르게) `createExpense` 의 `receipts: [{ fileId }]` 로 붙인다. 이미 만든 기록에는 `updateExpense { expenseId, addReceipts: [{ fileId }] }`. 떼기는 `removeReceiptFileIds` (Drive 파일은 지워지지 않는다).

## 조회 — "AWS 지난달 얼마였지" · "이거 얼마였지"

1. `listExpenses` 에 필터를 건다: `vendor` (공급자) 또는 `q` (용도 · 공급자 · 메모) + `from` / `to`. 상대 날짜 ("지난달", "이번 주", "11월") 는 한국 시간 기준으로 실제 날짜 범위로 바꾸고, **답에 그 범위를 적는다** ("2026-10-01 ~ 2026-10-31"). 카드별은 `card`, 결제수단별은 `paymentMethod`, 고정비 항목별은 `costItemId`.
2. "이거 얼마였지" + 영수증 사진이면 사진에서 공급자 · 날짜를 읽어 같은 방식으로 찾는다. 사진의 금액은 참고만 — 답은 hq 기록 기준.
3. 답: 건별 **금액 · 날짜 · 공급자 · 용도 · 카드**, 증빙은 `receipts[].webViewLink` (Drive 링크) 또는 "증빙 없음" + 그 기록의 `webUrl`. 여러 건이면 `totals` (통화별 합계 — 환율 환산은 없다) 와 `missingReceipts` (증빙 없는 건수) 를 한 줄로.
4. 못 찾으면 기간을 넓히거나 `q` 로 바꿔 한 번 더 찾아본 뒤 없다고 말한다.

## 고정비

- **목록 · 이번 달 얼마**: `listCostItems { month? }` (기본 이번 달, `includeArchived: true` 면 해지 포함). 항목마다 `recordedAmount` (그 달 기록 합계) — **`null` 이면 아직 기록이 없고 `expectedAmount` 는 예상일 뿐**이라고 구분해서 말한다. `billingDate` · `nextBillingDate` 로 결제일.
- **AWS 이번 달 지금 얼마**: `listCostItems` 에서 `liveSource: "aws"` 항목의 `live` (`amount` · `asOf` = AWS 기준 시각 · `fetchedAt` = hq 가 가져온 시각) — 하루 1회 가져온 **현재까지 실제 지출 (표시용)** 이라 장부 금액 (`recordedAmount` · 합계) 과 다르다고 말한다. `live` 가 `null` 이면 아직 안 가져왔거나 연결된 항목이 없다 (`liveSources[].stale` = 36시간 넘게 갱신 안 됨). 항목에 붙이기 · 떼기 = `updateCostItem { costItemId, liveSource: "aws" | null }` (사용자가 말했을 때만). 월 확정 금액은 지금처럼 기록으로.
- **합계 · 추이**: `getCostSummary { month?, months? }` ("최근 6개월" → `months: 6`). 확인된 기록만 센다 — 예상은 섞이지 않고 환율 환산도 없다. 분류별 = `byCategory`, 반복 항목에 안 묶인 영수증 · 운영비 = `other`.
- **새 구독 · 고정비 항목**: 사용자가 등록하자고 했을 때만 `createCostItem { name, category, cycle, billingDay, billingMonth? (yearly 만), expectedAmount, currency, paymentMethod, card?, plan?, note? }`. 빠진 필드는 한 번에 묻는다. 법인카드면 위 등록 3 과 같은 카드 고르기.
- **해지 · 해지 취소**: `updateCostItem { costItemId, archived: true | false }` — 기록은 남고 목록 · 브리핑 "곧 결제" 에서만 빠진다. 해지는 사용자가 말했을 때만, 항목 이름을 확인한 뒤. 금액 · 결제일 · 카드 변경도 같은 도구 (바꿀 필드만).
- 결제 뒤 "이번 달 기록해줘" → 위 등록 흐름으로 `costItemId` 를 묶어 `createExpense` (금액은 사용자에게 확인 — 예상 금액과 다를 수 있다).

## 규칙

- 금액: KRW 는 정수, USD 는 소수 2자리 ("20.80"). "12만 8천원" → `128000`.
- 카드 번호 전체를 입력에 넣거나 답에 쓰지 않는다 — 끝 4자리까지만.
- 증빙 파일 바이트를 Drive 커넥터로 올리지 않는다 (한 번의 도구 호출에 담을 수 있는 크기를 넘는다). 사용자가 이유를 물으면 한 줄로만 설명하고 `webUrl` 로 안내한다.
- 수정 (`updateExpense`) · 삭제 (`deleteExpense`) 는 사용자가 명시적으로 말했을 때만. 삭제는 날짜 · 금액 · 공급자를 보여 주고 확인받은 뒤. 둘 다 **등록자와 admin** 만 가능하다 — `FORBIDDEN` 이면 그렇게 안내한다.
- `UNAVAILABLE` 이면 일시 장애 — 잠시 뒤 다시.
- 401 · 연결 오류면 "hq 연결이 끊겼다 — Claude Code 는 `/mcp` 에서, claude.ai 는 플러그인 Connectors 탭에서 hq 에 다시 로그인" 을 안내하고 멈춘다.
- 결과 JSON 을 그대로 붙이지 않는다. 요약만.
