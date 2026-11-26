#!/usr/bin/env bash
# 올리기 전 검사 — 스킬 · 플러그인 소개문 검사 (scripts/check-skills.py) → claude plugin validate (플러그인 · 마켓플레이스).
# pre-push 훅이 돌린다. 규칙 원문 = CLAUDE.md § 스킬 작성.
set -uo pipefail
here="${BASH_SOURCE[0]%/*}"
[ "$here" = "${BASH_SOURCE[0]}" ] && here=.
root=$(cd "$here/.." && pwd)
cd "$root" || exit 2

command -v python3 >/dev/null 2>&1 || { echo "FAIL python3 없음 — 소개문 검사를 건너뛰지 않는다 (macOS: xcode-select --install)"; exit 1; }
python3 scripts/check-skills.py "$root" || exit 1

if command -v claude >/dev/null 2>&1; then
  claude plugin validate plugin || exit 1
  claude plugin validate . || exit 1
else
  echo "SKIP claude plugin validate (claude CLI 없음)"
fi
echo "CHECK OK"
