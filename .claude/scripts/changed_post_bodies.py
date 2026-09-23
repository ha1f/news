#!/usr/bin/env python3
"""2つの ref の間で、本文（front matter の外）が変わった `_posts/*.md` を列挙する。

記事の品質検査（`check_article_notes.py` / `check_source_hints.py`）が見るのは
本文の記事項目だけで、front matter だけが変わった投稿には何も言うことがない。
にもかかわらず CI は「変更された `_posts`」を丸ごと渡していたため、front matter
の一括更新をすると、その投稿が書かれた当時のルールで書かれた本文まで今の検査に
かかり、変更と無関係な既存の違反で red になる（実測 #401: title 行だけを直した
368件を渡すと、`check_source_hints.py` が 2,453 件の不一致を出す。同じ数が
main 側の同じファイルでも出るので、PR が持ち込んだものではない）。

本文が変わった投稿だけを渡せば、検査は PR が持ち込んだ内容に対して働く。

使い方:
  python3 .claude/scripts/changed_post_bodies.py <base-ref> <head-ref>
  python3 .claude/scripts/changed_post_bodies.py <base-ref>          # head は作業ツリー

該当する投稿のパスを1行1件で出力する（0件なら何も出力せず終了コード 0）。
"""
import subprocess
import sys


def body_of(text: str) -> str:
    """front matter を除いた本文。front matter が無ければ全体を本文とみなす。

    閉じの `---` は「その行がちょうど `---` である最初の行」で決める。本文中の
    水平線 `---` で切ってしまうと、そこから後ろの書き換えを見落とす。
    """
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return text
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return "\n".join(lines[i + 1:])
    return text  # 閉じが無い = front matter として成立していないので全体を本文とみなす


def changed_posts(base: str, head: str):
    """base..head で追加・変更された `_posts/*.md`（削除は除く）"""
    args = ["git", "diff", "--name-only", "--diff-filter=d", base]
    if head:
        args.append(head)
    args += ["--", "_posts/*.md"]
    out = subprocess.run(args, capture_output=True, text=True, check=True).stdout
    return [line for line in out.splitlines() if line]


def show(ref: str, path: str):
    """その ref の時点のファイル内容。無ければ None（= 新規追加）"""
    if ref is None:
        try:
            with open(path, encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return None
    r = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def body_changed(base: str, head: str, path: str) -> bool:
    before = show(base, path)
    if before is None:
        return True  # 新規追加は常に検査対象
    after = show(head, path)
    if after is None:
        return True  # 読めないものは検査に回して気づけるようにする
    return body_of(before) != body_of(after)


def main(argv):
    if not argv or len(argv) > 2:
        print(__doc__, file=sys.stderr)
        return 2
    base = argv[0]
    # 空文字は「省略」と同じ扱いに寄せる。そうしないと changed_posts は作業ツリー、
    # show は index (`git show :path`) を見て、一覧と内容の取得元が食い違う
    head = argv[1] if len(argv) > 1 and argv[1] else None
    for path in changed_posts(base, head):
        if body_changed(base, head, path):
            print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
