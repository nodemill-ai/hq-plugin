#!/usr/bin/env bash
# 스킬 프런트매터 검사 → claude plugin validate (플러그인 · 마켓플레이스). push 전에 돌린다.
# 프런트매터 허용 키 = claude.ai 스킬 스펙 (name · description · license · compatibility · metadata · allowed-tools).
# 그 외 키 (argument-hint · model · disable-model-invocation 등 Code 전용) 가 있으면 exit 1 — claude.ai 업로드 · 마켓플레이스 동기화가 하드 에러를 내기 때문.
set -uo pipefail
root=$(cd "$(dirname "$0")/.." && pwd)
cd "$root" || exit 2
ALLOWED=" name description license compatibility metadata allowed-tools "
fail=0

for f in plugin/skills/*/SKILL.md; do
  [ -f "$f" ] || { echo "FAIL no skills under plugin/skills"; exit 1; }
  head -1 "$f" | grep -q '^---$' || { echo "FAIL $f: 프런트매터 없음"; fail=1; continue; }
  keys=$(awk 'NR==1{next} /^---$/{exit} /^[A-Za-z][A-Za-z0-9_-]*:/{sub(/:.*/,""); print}' "$f")
  bad=0
  for k in $keys; do
    case "$ALLOWED" in
      *" $k "*) ;;
      *) echo "FAIL $f: 허용되지 않은 프런트매터 키 '$k' (허용:$ALLOWED)"; bad=1 ;;
    esac
  done
  for req in name description; do
    printf '%s\n' "$keys" | grep -qx "$req" || { echo "FAIL $f: '$req' 없음"; bad=1; }
  done
  dir=$(basename "$(dirname "$f")")
  nm=$(awk 'NR==1{next} /^---$/{exit} /^name:/{sub(/^name:[ ]*/,""); print}' "$f")
  [ "$dir" = "$nm" ] || { echo "FAIL $f: name '$nm' ≠ 폴더 '$dir'"; bad=1; }
  if [ "$bad" = 0 ]; then echo "ok   $f ($(printf '%s' "$keys" | tr '\n' ' '))"; else fail=1; fi
done
[ "$fail" = 0 ] || exit 1

if command -v claude >/dev/null 2>&1; then
  claude plugin validate plugin || exit 1
  claude plugin validate . || exit 1
else
  echo "SKIP claude plugin validate (claude CLI 없음)"
fi
echo "CHECK OK"
