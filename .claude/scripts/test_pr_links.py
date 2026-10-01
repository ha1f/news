#!/usr/bin/env python3
"""pr_links.py のテスト。

守りたいのは2つで、どちらを落としても静かに壊れる:

- リンクキーワードを **データとして引用した** 箇所（コードフェンス内・インライン
  コード内）を linked issue に数えない。実測 (#473): PR #471 の body は、正規表現の
  挙動を説明する例と他 PR の引用だけで `[408, 421]` を生み、`#421`（週次上限で配信が
  欠落した issue）が合格時に誤って close されうる状態だった
- 実際に issue を進める散文中の `Closes #N` は取りこぼさない。取りこぼすと、
  PR が進める issue が backlog に残り続け、マージしても close されない
"""
import unittest

import pr_links


class ExtractLinkedIssues(unittest.TestCase):
    def test_prose_keywords_are_kept(self):
        """散文中のリンクキーワードは従来どおり拾う（表記ゆれを含む）"""
        self.assertEqual(pr_links.extract_linked_issues("Closes #123"), [123])
        self.assertEqual(
            pr_links.extract_linked_issues("Fixes #1, closed #2, RESOLVE #3, ref #4"),
            [1, 2, 3, 4])
        self.assertEqual(
            pr_links.extract_linked_issues("Refs #408 と Closes #421"), [408, 421])

    def test_non_keyword_mentions_are_ignored(self):
        """キーワードを伴わない言及は従来どおり拾わない"""
        self.assertEqual(pr_links.extract_linked_issues("この PR は #408 に着手して…"), [])
        self.assertEqual(pr_links.extract_linked_issues("関連: #408"), [])

    def test_fenced_code_is_not_a_link(self):
        body = "説明:\n\n```\n'Refs #408' -> ['408']\n'Closes #421' -> ['421']\n```\n"
        self.assertEqual(pr_links.extract_linked_issues(body), [])

    def test_fenced_code_with_info_string(self):
        body = "```python\nLINK_RE  # Closes #99\n```\n\n本文で Closes #7"
        self.assertEqual(pr_links.extract_linked_issues(body), [7])

    def test_tilde_fence(self):
        self.assertEqual(pr_links.extract_linked_issues("~~~\nRefs #5\n~~~"), [])

    def test_indented_fence_up_to_three_spaces(self):
        self.assertEqual(pr_links.extract_linked_issues("   ```\n   Closes #12\n   ```"), [])

    def test_strip_code_blocks_alone_removes_fenced_content(self):
        """フェンス処理を単体で固定する。

        extract_linked_issues 越しでは、``` のフェンスはインラインコードの処理が
        「同じ長さのバッククォート列で閉じるコードスパン」として巻き取ってしまうため、
        フェンス処理を落としても結果が変わらない変異がある。ここで直接当てる
        """
        self.assertNotIn("#12", pr_links.strip_code_blocks("   ```\n   Closes #12\n   ```"))
        self.assertNotIn("#5", pr_links.strip_code_blocks("~~~\nRefs #5\n~~~"))
        self.assertNotIn("#9", pr_links.strip_code_blocks("```\nCloses #9"))
        # フェンスの外は残す
        self.assertIn("Closes #7", pr_links.strip_code_blocks("```\nx\n```\nCloses #7"))
        # 4スペース以上のインデントはフェンスではない（リストの中のコード等と区別しない）
        self.assertIn("Closes #3", pr_links.strip_code_blocks("    ```\n    Closes #3"))

    def test_unclosed_fence_runs_to_the_end(self):
        """閉じフェンスが無い body は、そこから末尾までコード（レンダラと同じ）"""
        self.assertEqual(pr_links.extract_linked_issues("```\nCloses #9"), [])

    def test_longer_fence_is_not_closed_by_a_shorter_one(self):
        """```` で開いたフェンスは ``` では閉じない（閉じは開きと同じ長さ以上）"""
        self.assertEqual(
            pr_links.extract_linked_issues("````\n```\nCloses #1\n````"), [])

    def test_inline_code_is_not_a_link(self):
        self.assertEqual(pr_links.extract_linked_issues("`Closes #421` はコード引用"), [])
        self.assertEqual(pr_links.extract_linked_issues("他 PR の `Refs #408` を引用"), [])

    def test_inline_code_with_multiple_backticks(self):
        """``…`` の中にバッククォートを含む形でも、閉じは同じ長さの列"""
        self.assertEqual(pr_links.extract_linked_issues("``a ` b`` Refs #6"), [6])
        self.assertEqual(pr_links.extract_linked_issues("``Closes #8`` だけ"), [])

    def test_code_span_is_closed_only_by_an_equal_length_run(self):
        """`` で開いたコードスパンは、中の単独の ` では閉じない"""
        self.assertEqual(pr_links.extract_linked_issues("`` ` Closes #1 ``"), [])

    def test_lone_backtick_is_not_a_code_span(self):
        """閉じが無いバッククォートは、それ以降を飲み込まない"""
        self.assertEqual(pr_links.extract_linked_issues("バッククォート1個 ` だけ。Closes #11"),
                         [11])

    def test_fence_info_string_cannot_contain_a_backtick(self):
        """``` の行の後ろにバッククォートが続く行はフェンスではない（CommonMark）。

        フェンスと誤認すると、そこから下が丸ごとコード扱いになり、本物の
        `Closes #N` を取りこぼす
        """
        self.assertEqual(pr_links.extract_linked_issues("```a` の説明\nCloses #1"), [1])

    def test_backticks_mid_line_are_not_a_fence(self):
        """フェンスは行頭（インデント3まで）から。行中の ``` はコードスパン扱い"""
        self.assertEqual(pr_links.extract_linked_issues("文中の ``` の後\nCloses #9"), [9])

    def test_removal_does_not_create_a_new_hit(self):
        """落とした結果でキーワードと番号が隣接し、新しい偽ヒットを作らない。

        LINK_RE のキーワードと `#N` の間は `\\s+` なので、コードを空行・空白に
        置き換えると `Closes` と `#123` がつながって一致してしまう
        """
        self.assertEqual(pr_links.extract_linked_issues("Closes\n```\nx\n```\n#123"), [])
        self.assertEqual(pr_links.extract_linked_issues("Closes `x`\n#123"), [])
        self.assertEqual(pr_links.extract_linked_issues("Closes `x` #123"), [])

    def test_empty_body(self):
        self.assertEqual(pr_links.extract_linked_issues(None), [])
        self.assertEqual(pr_links.extract_linked_issues(""), [])

    def test_result_is_sorted_and_deduplicated(self):
        self.assertEqual(
            pr_links.extract_linked_issues("Refs #408 Refs #408 Closes #12"), [12, 408])

    def test_regression_pr_471_body(self):
        """PR #471 の body の実物（抜粋）。素の正規表現では [408, 421] を生んでいた。

        内訳は、正規表現の挙動表（コードフェンス内）と、他 PR の body の
        バッククォート引用。この PR 自身は「linked issue は無い」と宣言していた
        """
        body = (
            "## 観測された事実\n\n"
            "`classify_prs.py:30` と `select_issues.py:42` の `LINK_RE` に #471 自身の\n"
            "body を当てると:\n\n"
            "```\n"
            "'Refs #408' -> ['408']\n"
            "'refs #408' -> ['408']\n"
            "'Closes #421' -> ['421']\n"
            "```\n\n"
            "散文で他 PR の body を引用した箇所（`Refs #408` / `Refs #408`）も拾う。\n"
        )
        self.assertEqual(pr_links.extract_linked_issues(body), [])


if __name__ == "__main__":
    unittest.main()
