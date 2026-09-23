#!/usr/bin/env python3
"""changed_post_bodies.py のテスト。

要点は「front matter だけの変更を本文の変更と取り違えない」こと。
取り違えると #401 で観測した red（既存の本文が今の検査にかかる）に戻る。
逆に本文の変更を取りこぼすと、検査が効かなくなる方向に壊れる。
"""
import subprocess
import tempfile
import unittest
from pathlib import Path

import changed_post_bodies as m

POST = '---\nlayout: post\ntitle: "{title}"\ndate: 2026-09-21\n---\n\n{body}\n'


class TestBodyOf(unittest.TestCase):
    def test_strips_front_matter(self):
        self.assertEqual(m.body_of(POST.format(title="見出し", body="本文")), "\n本文\n")

    def test_same_body_different_title(self):
        a = m.body_of(POST.format(title="2026年9月21日", body="本文"))
        b = m.body_of(POST.format(title="AI大手の攻防", body="本文"))
        self.assertEqual(a, b)

    def test_different_body(self):
        a = m.body_of(POST.format(title="見出し", body="本文A"))
        b = m.body_of(POST.format(title="見出し", body="本文B"))
        self.assertNotEqual(a, b)

    def test_body_containing_hr(self):
        """本文中の水平線 `---` を front matter の終わりと取り違えない"""
        text = '---\ntitle: "見出し"\n---\n\n段落1\n\n---\n\n段落2\n'
        self.assertEqual(m.body_of(text), "\n段落1\n\n---\n\n段落2\n")

    def test_no_front_matter(self):
        self.assertEqual(m.body_of("front matter なし\n"), "front matter なし\n")


class TestAgainstGit(unittest.TestCase):
    """実際の git リポジトリを作って end-to-end で確かめる"""

    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.email", "t@example.com")
        self.git("config", "user.name", "t")
        (self.dir / "_posts").mkdir()
        self.write("2026-09-20-news.md", title="2026年9月20日", body="本文20")
        self.write("2026-09-21-news.md", title="2026年9月21日", body="本文21")
        self.git("add", "-A")
        self.git("commit", "-qm", "base")
        self.base = self.git("rev-parse", "HEAD").strip()

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.dir), *args],
                              capture_output=True, text=True, check=True).stdout

    def write(self, name, title, body):
        (self.dir / "_posts" / name).write_text(POST.format(title=title, body=body),
                                                encoding="utf-8")

    def run_helper(self, head=None):
        import os
        cwd = os.getcwd()
        os.chdir(self.dir)
        try:
            out = []
            for p in m.changed_posts(self.base, head):
                if m.body_changed(self.base, head, p):
                    out.append(p)
            return out
        finally:
            os.chdir(cwd)

    def test_title_only_change_is_not_listed(self):
        self.write("2026-09-21-news.md", title="AI大手の攻防", body="本文21")
        self.git("add", "-A"); self.git("commit", "-qm", "title only")
        self.assertEqual(self.run_helper(self.git("rev-parse", "HEAD").strip()), [])

    def test_body_change_is_listed(self):
        self.write("2026-09-21-news.md", title="2026年9月21日", body="本文21を書き換え")
        self.git("add", "-A"); self.git("commit", "-qm", "body")
        self.assertEqual(self.run_helper(self.git("rev-parse", "HEAD").strip()),
                         ["_posts/2026-09-21-news.md"])

    def test_new_post_is_listed(self):
        self.write("2026-09-22-news.md", title="新しい見出し", body="本文22")
        self.git("add", "-A"); self.git("commit", "-qm", "new")
        self.assertEqual(self.run_helper(self.git("rev-parse", "HEAD").strip()),
                         ["_posts/2026-09-22-news.md"])

    def test_mixed_change_lists_only_body_change(self):
        self.write("2026-09-20-news.md", title="見出し20", body="本文20")            # title だけ
        self.write("2026-09-21-news.md", title="見出し21", body="本文21を書き換え")  # 両方
        self.git("add", "-A"); self.git("commit", "-qm", "mixed")
        self.assertEqual(self.run_helper(self.git("rev-parse", "HEAD").strip()),
                         ["_posts/2026-09-21-news.md"])

    def test_deleted_post_is_not_listed(self):
        (self.dir / "_posts" / "2026-09-21-news.md").unlink()
        self.git("add", "-A"); self.git("commit", "-qm", "delete")
        self.assertEqual(self.run_helper(self.git("rev-parse", "HEAD").strip()), [])

    def test_working_tree_head(self):
        """head を省いたときは作業ツリーを見る"""
        self.write("2026-09-21-news.md", title="2026年9月21日", body="未コミットの書き換え")
        self.assertEqual(self.run_helper(None), ["_posts/2026-09-21-news.md"])


if __name__ == "__main__":
    unittest.main()
