#!/usr/bin/env python3
"""run_unit_tests.py の純関数のユニットテスト。

回し方: cd .claude/scripts && python3 -m unittest discover -p 'test_*.py'
（このテスト自身も run_unit_tests.py の探索対象に入る。無限再帰にならないよう、
ここでは runner をプロセスとして呼ばず find_test_dirs だけを当てる）
"""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_unit_tests import find_test_dirs  # noqa: E402


class FindTestDirsTest(unittest.TestCase):
    def _tree(self, paths):
        root = Path(tempfile.mkdtemp())
        for rel in paths:
            target = root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("")
        return root

    def test_finds_nested_dirs_sorted(self):
        root = self._tree([
            "a/scripts/test_one.py",
            "a/scripts/one.py",
            "b/deep/scripts/test_two.py",
        ])
        self.assertEqual(find_test_dirs(root), ["a/scripts", "b/deep/scripts"])

    def test_dir_without_tests_is_not_listed(self):
        root = self._tree(["a/scripts/one.py", "b/test_two.py"])
        self.assertEqual(find_test_dirs(root), ["b"])

    def test_empty_tree_is_empty(self):
        self.assertEqual(find_test_dirs(self._tree([])), [])

    def test_skipped_dirs_are_not_searched(self):
        # 生成物・依存のツリーを拾うと、_site のビルド結果まで検査対象になる
        root = self._tree([
            "_site/test_generated.py",
            "node_modules/pkg/test_dep.py",
            ".git/test_hook.py",
            "cache/test_c.py",
            "output/test_o.py",
            "real/test_real.py",
        ])
        self.assertEqual(find_test_dirs(root), ["real"])

    def test_non_test_prefixed_file_is_ignored(self):
        root = self._tree(["a/tests_helper.py", "a/mytest_thing.py", "a/check_test.py"])
        self.assertEqual(find_test_dirs(root), [])

    def test_same_dir_with_several_tests_is_listed_once(self):
        root = self._tree(["a/test_one.py", "a/test_two.py"])
        self.assertEqual(find_test_dirs(root), ["a"])

    def test_this_repo_has_every_known_test_dir(self):
        # 列挙を yaml に焼き込まない形になっているかの歯止め。既知の置き場が
        # 1つでも落ちたら red になる（期待値はテスト側に直書きする）
        root = Path(__file__).resolve().parents[2]
        dirs = find_test_dirs(root)
        for expected in (
                ".claude/scripts",
                ".claude/skills/curate-news/scripts",
                ".claude/skills/evaluate-and-triage/scripts",
                ".claude/skills/remove-ai-tells/scripts",
                ".claude/skills/review-and-merge/scripts",
                ".claude/skills/select-and-develop/scripts",
        ):
            self.assertIn(expected, dirs)


if __name__ == "__main__":
    unittest.main()
