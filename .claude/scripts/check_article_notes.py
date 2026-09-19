#!/usr/bin/env python3
"""記事一覧の各項目の読みどころを検証する (#325, #342)。

2つを見る:

1. 読みどころがあるか (#325)。無い項目は、読者が見出しだけで「開くか」を
   判断することになり、そこだけ流し読みのリズムが止まる
2. 読みどころが見出しとソース名以上のことを言っているか (#342)。
   「原文で確認できる」「〜そのもの」のような出どころの紹介は、
   同じ行の (ソース名) で既に分かることしか渡しておらず、1 の検査は通るのに
   読者の「開くか決められない」は残る

投稿ファイルを作ったら commit 前に実行する。

使い方:
  python3 .claude/scripts/check_article_notes.py                     # 当日 (JST) の投稿
  python3 .claude/scripts/check_article_notes.py _posts/2026-09-18-news.md ...
  python3 .claude/scripts/check_article_notes.py --all               # 全投稿（棚卸し用）

2 の検査は、観測された出どころ紹介の文面を取り除いたうえで、見出しとソース名にも
無い中身がどれだけ残るかを見る。既知の型に対する回帰検査であって、
「中身があるか」の判定そのものではない。新しい言い回しの出どころ紹介は素通りしうるので、
観測されたら META_PHRASES に足す（GUARDRAILS.md「観測された失敗モードに対してのみ追記する」）。

終了コード 0 なら、検査した全項目に読みどころがあり、いずれも既知の型の
出どころ紹介だけで終わってはいない。番号付き項目に見えて ITEM_RE に一致しない行（太字リンク・
番号後の連続スペース・箇条書き等）は検査対象から漏れるため、警告として別途出力する
（exit code には影響しない）。
"""
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

JST = timezone(timedelta(hours=9))
ITEM_RE = re.compile(r"^\d+\. \[(?P<title>.*?)\]\((?P<url>[^)]*)\)(?P<rest>.*)$")
# ITEM_RE に一致しないが、番号付き/箇条書きリンク項目に見える行（検査漏れの検出用）
POSSIBLE_ITEM_RE = re.compile(r"^\s*(?:\d+[.)]|[-*])\s*\*{0,2}\[")
BR_RE = re.compile(r"(?i)<br\s*/?>")
LABEL_RE = re.compile(r"\((?P<label>[^()]*)\)\s*$")

# 出どころを述べるだけの言い回し。読みどころから取り除いて「残り」を見る。
# いずれも観測された文面から起こしたもので、網羅ではない（docstring 参照）。
# 節をまたいで削らないよう、範囲は読点・句点で止める。
# 「〜経由で叩く」「詳細は〜」のような普通の言い回しまで消してしまい、
# 中身のある読みどころを誤って NG にしていた
META_PHRASES = [
    r"原文で[^、。]*?(確認|読める|読む|追える)[^、。]*",
    r"一次情報で[^、。]*?確認[^、。]*",
    r"[^、。]{0,16}?(公式|自身)の[^、。]{0,16}?そのもの",
    r"[^、。]{0,16}?(公式|自身)の(発表|リリース|変更履歴|リリースノート|ブログ記事|告知)",
    r"[^、。]{0,16}?(経由|発)で話題になった\d*本",
    r"[^、。]{0,16}?で議論が伸びた\d*本",
    r"(Hacker News|HN|はてブ|Reddit)で\d+(ポイント|点)[^、。]*",
    r"\d+件のコメントを集めた[^、。]*",
    r"注目の\d*本",
    r"[^、。]{0,16}?の話題の\d*本",
    r"Show HN投稿",
    r"[^、。]{0,16}?欄(に掲載された|による)[^、。]*",
    r"[^、。]{0,16}?による(ニュース)?解説記事",
    r"[^、。]{0,16}?速報の一報",
    r"コメント欄も読みどころ",
    r"原論文",
]
# 媒体・記事の種類を指すだけの語。どの記事にも当てはまるので読者への新情報にならない
META_WORDS_RE = re.compile(
    "原文|一次情報|公式|発表|記事|解説|論文|速報|一報|経由|話題|確認|直接|詳細|全文"
    "|本文|投稿|レポート|紹介|概要|内容|ブログ|リンク|告知|新機能|変更点|お知らせ"
    "|まとめ|一覧|リリース")
WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9.+#-]{1,}")
NON_WORD_RE = re.compile(r"[^\w\u3040-\u30ff\u4e00-\u9fff]+")
# 「見出し・ソース名・出どころ語彙を取り除いた残り」がこの数に満たなければ、
# 出どころの紹介だけとみなす。9/14〜9/17 の投稿（読者から問題の報告が無かった日）で
# 誤検出が出ない範囲の上限は 17 で、18 から誤検出が出はじめる。
# 上限に張り付かせず 1 つ余裕を取って 16 にしている
MIN_RESIDUE = 16


def items_of(post: Path):
    """投稿本文の記事項目を (見出し, ソース表記, 読みどころ) で返す"""
    text = post.read_text(encoding="utf-8")
    body = text.split("---", 2)[2] if text.startswith("---") else text
    lines = body.split("\n")
    for i, line in enumerate(lines):
        m = ITEM_RE.match(line)
        if not m:
            continue
        note = ""
        if "<br>" in m.group("rest"):
            # <br> 以降（同じ行の残り + 続く字下げ行）が読みどころ
            tail = [m.group("rest").split("<br>", 1)[1]]
            for follow in lines[i + 1:]:
                if not follow.strip() or ITEM_RE.match(follow):
                    break
                tail.append(follow)
            # <br><br> や末尾の孤立した <br> はタグを除去してから判定する
            # (除去前は "<br>" という文字列自体が非空のため、空の読みどころを見逃す)
            note = BR_RE.sub("", "".join(tail)).strip()
        head = BR_RE.split(m.group("rest"))[0].strip()
        label = LABEL_RE.search(head)
        yield (m.group("title"),
               label.group("label").strip() if label else "",
               note)


def _fragments(text: str) -> set:
    """比較用の断片（CJK は 2 文字組、英数字は単語）にほぐす。

    日本語は分かち書きされないため、「創薬」と「創薬事業参入」のような
    区切りのずれを 2 文字組で吸収する。
    """
    squeezed = NON_WORD_RE.sub("", text)
    pieces = {squeezed[i:i + 2] for i in range(len(squeezed) - 1)}
    return pieces | {w.lower() for w in WORD_RE.findall(text)}


def residue_of(title: str, label: str, note: str) -> set:
    """読みどころから、見出し・ソース名・出どころ語彙を差し引いた残りを返す"""
    stripped = note
    for pattern in META_PHRASES:
        stripped = re.sub(pattern, "", stripped)
    stripped = META_WORDS_RE.sub("", stripped)
    return _fragments(stripped) - _fragments(title) - _fragments(label)


def malformed_lines_of(post: Path):
    """ITEM_RE に一致しない、番号付き/箇条書きリンクに見える行を返す"""
    text = post.read_text(encoding="utf-8")
    body = text.split("---", 2)[2] if text.startswith("---") else text
    for line in body.split("\n"):
        if not ITEM_RE.match(line) and POSSIBLE_ITEM_RE.match(line):
            yield line


def main(argv):
    if "--all" in argv:
        posts = sorted(Path("_posts").glob("*.md"))
    elif [a for a in argv if not a.startswith("--")]:
        posts = [Path(a) for a in argv if not a.startswith("--")]
    else:
        today = datetime.now(JST).strftime("%Y-%m-%d")
        posts = sorted(Path("_posts").glob(f"{today}-*.md"))
        if not posts:
            print(f"{today} の投稿がありません（_posts/{today}-*.md）", file=sys.stderr)
            return 1

    checked = missing = meta_only = warned = 0
    for post in posts:
        if not post.is_file():
            print(f"NG {post}: ファイルがありません")
            missing += 1
            continue
        for title, label, note in items_of(post):
            checked += 1
            if not note:
                print(f"NG {post.name}: 読みどころなし 「{title}」")
                missing += 1
                continue
            if len(residue_of(title, label, note)) < MIN_RESIDUE:
                print(f"NG {post.name}: 読みどころが出どころの紹介だけ "
                      f"「{title}」→「{note}」")
                meta_only += 1
        for line in malformed_lines_of(post):
            warned += 1
            print(f"WARN {post.name}: 番号付き項目に見えるが検査できない行 「{line.strip()}」")

    print(f"検査 {checked} 件 / 読みどころなし {missing} 件 / "
          f"出どころの紹介だけ {meta_only} 件 / 検査できない行 {warned} 件")
    return 1 if missing or meta_only or checked == 0 else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
