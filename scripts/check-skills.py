#!/usr/bin/env python3
"""스킬 · 플러그인 소개문 검사 — check.sh (pre-push) 가 부른다. 규칙 원문 = CLAUDE.md § 스킬 작성.

python3 scripts/check-skills.py [레포 루트]   → 어긴 것마다 FAIL 한 줄 · 하나라도 있으면 exit 1
글자 수는 유니코드 글자로 센다 (BSD awk length 는 한글을 바이트로 센다).
"""
import glob
import json
import os
import re
import sys

# claude.ai 스킬 스펙이 받는 프런트매터 키 — 그 외 키는 업로드 · 동기화가 하드 에러를 낸다
ALLOWED_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
DESC_MAX = 140          # 스킬 소개문 — 10개 × 140 = 1,400 (지금 합계 3,031 의 절반 아래)
PHRASES = (3, 4)        # 사용자가 할 말 (따옴표 문구) 개수
BODY_MAX = 5500         # SKILL.md 본문 — compaction 뒤 스킬당 앞 5,000 토큰만 남는다 (약 0.86 토큰/자)
PLUGIN_DESC_MAX = 100   # plugin.json · marketplace.json 플러그인 소개문
RULE = " — 작성 규칙 = CLAUDE.md § 스킬 작성"

# listTasks · create_event — 경계는 ASCII 로 본다 (\b 는 한글도 글자로 쳐서 'getBriefing으로' 를 놓친다)
TOOL_NAME = re.compile(r"(?<![A-Za-z0-9_])(?:[a-z]+[A-Z][A-Za-z0-9]*|[a-z0-9]+_[a-z0-9_]+)(?![A-Za-z0-9_])")
PHRASE = re.compile(r'"[^"]+"')
REF_LINK = re.compile(r"references/([^\s`)\]]+?\.md)")


def split_frontmatter(text):
    """(프런트매터 줄 목록, 본문) — 없으면 (None, text)."""
    lines = text.split("\n")
    if not lines or lines[0] != "---":
        return None, text
    for i in range(1, len(lines)):
        if lines[i] == "---":
            return lines[1:i], "\n".join(lines[i + 1:])
    return None, text


def check_description(desc, fail):
    if desc == "" or desc[0] in ">|'\"":
        fail("description 은 한 줄 평문으로 쓴다 (여러 줄 · 따옴표로 감싼 값 금지)")
        return
    n = len(desc)
    if n > DESC_MAX:
        fail(f"description {n}자 (한도 {DESC_MAX}자)")
    k = len(PHRASE.findall(desc))
    if not PHRASES[0] <= k <= PHRASES[1]:
        fail(f"description 의 사용자가 할 말 (따옴표 문구) 문구 {k}개 (허용 {PHRASES[0]}~{PHRASES[1]}개)")
    tools = sorted(set(TOOL_NAME.findall(desc)))
    if tools:
        fail(f"description 에 도구 이름 {', '.join(tools)} — 도구 · 절차는 본문에만")
    q = desc.find('"')
    if q <= 0 or not desc[:q].rstrip().endswith("."):
        fail("description 은 무엇을 하는지 목적 한 문장 (마침표) 으로 시작하고 그 뒤에 할 말을 둔다")
    return n, k


def check_skill(root, path, fails):
    rel = os.path.relpath(path, root)
    before = len(fails)

    def fail(msg):
        fails.append(f"FAIL {rel}: {msg}{RULE}")

    with open(path, encoding="utf-8") as f:
        text = f.read()
    front, body = split_frontmatter(text)
    if front is None:
        fail("프런트매터 없음 (첫 줄 --- 부터 다음 --- 까지)")
        return None
    fields = {}
    cont = {}
    last = None
    for line in front:
        m = re.match(r"^([A-Za-z][A-Za-z0-9_-]*):[ ]?(.*)$", line)
        if m:
            last = m.group(1)
            fields[last] = m.group(2)
        elif line.strip() and last:
            cont[last] = True
    for k in fields:
        if k not in ALLOWED_KEYS:
            fail(f"허용되지 않은 프런트매터 키 '{k}' (허용: {' '.join(sorted(ALLOWED_KEYS))})")
    for req in ("name", "description"):
        if req not in fields:
            fail(f"'{req}' 없음")
    folder = os.path.basename(os.path.dirname(path))
    if "name" in fields and fields["name"].strip() != folder:
        fail(f"name '{fields['name'].strip()}' ≠ 폴더 '{folder}'")
    stats = None
    if "description" in fields:
        if cont.get("description"):
            fail("description 은 한 줄 평문으로 쓴다 (여러 줄 · 따옴표로 감싼 값 금지)")
        else:
            stats = check_description(fields["description"].strip(), fail)
    if len(body) > BODY_MAX:
        fail(f"본문 {len(body)}자 (한도 {BODY_MAX}자) — 갈래 · 긴 절은 references/ 로 옮긴다")
    # references 는 한 단계 — SKILL.md 가 폴더의 모든 파일을 직접 링크하고, 링크는 있는 파일만
    skill_dir = os.path.dirname(path)
    have = {os.path.basename(p) for p in glob.glob(os.path.join(skill_dir, "references", "*.md"))}
    linked = set(REF_LINK.findall(body))
    for name in sorted(have - linked):
        fail(f"references/{name} 를 SKILL.md 가 링크하지 않는다")
    for name in sorted(linked - have):
        fail(f"SKILL.md 가 없는 파일 references/{name} 를 링크한다")
    if len(fails) == before and stats:
        print(f"ok   {rel} (소개 {stats[0]}자 · 문구 {stats[1]} · 본문 {len(body)}자)")
    return stats


def check_plugin(root, fails):
    def load(rel):
        with open(os.path.join(root, rel), encoding="utf-8") as f:
            return json.load(f)

    pj = ".claude-plugin/plugin.json" if not os.path.exists(os.path.join(root, "plugin/.claude-plugin/plugin.json")) else "plugin/.claude-plugin/plugin.json"
    plugin = load(pj)
    desc = plugin.get("description", "")
    if len(desc) > PLUGIN_DESC_MAX:
        fails.append(f"FAIL {pj}: description {len(desc)}자 (한도 {PLUGIN_DESC_MAX}자) — 스킬 · 도구를 나열하지 않는다{RULE}")
    market = load(".claude-plugin/marketplace.json")
    entry = next((p for p in market.get("plugins", []) if p.get("name") == plugin.get("name")), None)
    if entry is None:
        fails.append(f"FAIL .claude-plugin/marketplace.json: 플러그인 '{plugin.get('name')}' 항목 없음{RULE}")
    elif entry.get("description", "") != desc:
        fails.append(f"FAIL .claude-plugin/marketplace.json: 플러그인 description 이 {pj} 와 다르다 (같은 글로 맞춘다){RULE}")
    return len(desc)


def main():
    root = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    skills = sorted(glob.glob(os.path.join(root, "plugin", "skills", "*", "SKILL.md")))
    if not skills:
        print("FAIL plugin/skills 아래 스킬 없음")
        return 1
    fails = []
    total = 0
    for path in skills:
        s = check_skill(root, path, fails)
        if s:
            total += s[0]
    plugin_len = check_plugin(root, fails)
    for line in fails:
        print(line)
    print(f"소개문 합계 {total}자 (스킬 {len(skills)}개) · 플러그인 {plugin_len}자")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
