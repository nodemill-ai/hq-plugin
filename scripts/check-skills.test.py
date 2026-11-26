#!/usr/bin/env python3
"""check-skills.py 시험 — 규칙을 하나씩 어긴 작은 사본마다 exit 1 과 어긴 내용 한 줄, 지킨 사본은 exit 0.

돌리기: python3 scripts/check-skills.test.py  (임시 폴더는 TMPDIR 아래)
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

CHECK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "check-skills.py")

GOOD_DESC = '데모 일을 처리한다. "데모 해 줘", "데모 보여 줘", "데모 지워 줘" 라고 할 때.'
GOOD_PLUGIN = "데모 업무툴을 Claude 에서 쓴다."
GOOD_BODY = "\n# 데모\n\n데모를 한다.\n"


def skill(desc=GOOD_DESC, body=GOOD_BODY, name="demo", extra=""):
    return f"---\nname: {name}\ndescription: {desc}\n{extra}---\n{body}"


class CheckSkills(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="check-skills-")
        self.addCleanup(shutil.rmtree, self.root)
        self.write("plugin/skills/demo/SKILL.md", skill())
        self.write_manifests(GOOD_PLUGIN, GOOD_PLUGIN)

    def write(self, rel, text):
        path = os.path.join(self.root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)

    def write_manifests(self, plugin_desc, market_desc):
        self.write("plugin/.claude-plugin/plugin.json", json.dumps({"name": "hq", "version": "0.0.1", "description": plugin_desc}, ensure_ascii=False))
        self.write(".claude-plugin/marketplace.json", json.dumps(
            {"name": "nodemill", "owner": {"name": "nodemill"}, "plugins": [{"name": "hq", "source": "./plugin", "description": market_desc}]},
            ensure_ascii=False))

    def run_check(self):
        p = subprocess.run([sys.executable, CHECK, self.root], capture_output=True, text=True)
        return p.returncode, p.stdout + p.stderr

    def assert_fails(self, needle):
        code, out = self.run_check()
        self.assertEqual(code, 1, out)
        fails = [l for l in out.splitlines() if l.startswith("FAIL")]
        self.assertTrue(any(needle in l for l in fails), out)
        self.assertTrue(all("CLAUDE.md § 스킬 작성" in l for l in fails), out)

    # 지킨 사본
    def test_good_passes(self):
        code, out = self.run_check()
        self.assertEqual(code, 0, out)

    # AC-E1 — 글자 수는 바이트가 아니라 글자
    def test_140_hangul_passes(self):
        head = '가. "하나", "둘", "셋" 라고 할 때.'
        self.write("plugin/skills/demo/SKILL.md", skill(desc=head + "가" * (140 - len(head))))
        code, out = self.run_check()
        self.assertEqual(code, 0, out)

    def test_141_hangul_fails(self):
        head = '가. "하나", "둘", "셋" 라고 할 때.'
        self.write("plugin/skills/demo/SKILL.md", skill(desc=head + "가" * (141 - len(head))))
        self.assert_fails("141자")

    # AC3 — 문구 3~4개 · 도구 이름 없음 · 목적 문장이 먼저
    def test_two_phrases_fail(self):
        self.write("plugin/skills/demo/SKILL.md", skill(desc='데모를 한다. "하나", "둘" 라고 할 때.'))
        self.assert_fails("문구 2개")

    def test_five_phrases_fail(self):
        self.write("plugin/skills/demo/SKILL.md", skill(desc='데모를 한다. "가", "나", "다", "라", "마" 라고 할 때.'))
        self.assert_fails("문구 5개")

    def test_tool_name_fails(self):
        self.write("plugin/skills/demo/SKILL.md", skill(desc='데모를 listTasks 로 한다. "가", "나", "다" 라고 할 때.'))
        self.assert_fails("listTasks")

    def test_snake_tool_name_fails(self):
        self.write("plugin/skills/demo/SKILL.md", skill(desc='데모를 create_event 로 한다. "가", "나", "다" 라고 할 때.'))
        self.assert_fails("create_event")

    def test_no_purpose_sentence_fails(self):
        self.write("plugin/skills/demo/SKILL.md", skill(desc='데모 "가", "나", "다" 라고 하면 한다.'))
        self.assert_fails("목적")

    # AC-E2 — 한 줄 평문만
    def test_folded_description_fails(self):
        self.write("plugin/skills/demo/SKILL.md", skill(desc=">\n  데모를 한다. \"가\", \"나\", \"다\" 라고 할 때."))
        self.assert_fails("한 줄")

    def test_quoted_value_fails(self):
        self.write("plugin/skills/demo/SKILL.md", skill(desc="'데모를 한다. \"가\", \"나\", \"다\" 라고 할 때.'"))
        self.assert_fails("한 줄")

    # D12 — 본문 글자 수
    def test_body_over_limit_fails(self):
        self.write("plugin/skills/demo/SKILL.md", skill(body="\n" + "가" * 5501))
        self.assert_fails("본문")

    # AC2 — 플러그인 소개문
    def test_plugin_description_over_limit_fails(self):
        long = "가" * 101
        self.write_manifests(long, long)
        self.assert_fails("101자")

    def test_plugin_descriptions_differ_fail(self):
        self.write_manifests(GOOD_PLUGIN, GOOD_PLUGIN + " 더")
        self.assert_fails("marketplace.json")

    # 원래 검사 (프런트매터 키 · 이름)
    def test_disallowed_key_fails(self):
        self.write("plugin/skills/demo/SKILL.md", skill(extra="model: opus\n"))
        self.assert_fails("model")

    def test_name_mismatch_fails(self):
        self.write("plugin/skills/demo/SKILL.md", skill(name="other"))
        self.assert_fails("폴더")

    def test_missing_frontmatter_fails(self):
        self.write("plugin/skills/demo/SKILL.md", "# 데모\n")
        self.assert_fails("프런트매터")

    # AC9 — references 는 SKILL.md 가 직접 링크
    def test_unlinked_reference_fails(self):
        self.write("plugin/skills/demo/references/풀이.md", "# 풀이\n")
        self.assert_fails("references/풀이.md")

    def test_linked_reference_passes(self):
        self.write("plugin/skills/demo/references/풀이.md", "# 풀이\n")
        self.write("plugin/skills/demo/SKILL.md", skill(body=GOOD_BODY + "자세히는 `references/풀이.md`.\n"))
        code, out = self.run_check()
        self.assertEqual(code, 0, out)

    def test_missing_reference_target_fails(self):
        self.write("plugin/skills/demo/SKILL.md", skill(body=GOOD_BODY + "자세히는 `references/없음.md`.\n"))
        self.assert_fails("references/없음.md")


if __name__ == "__main__":
    unittest.main(verbosity=1)
