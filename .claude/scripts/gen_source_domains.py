#!/usr/bin/env python3
"""ソース表示名 → 記事ドメインの対応表 `_data/source_domains.json` を生成する (#183)。

記事ページ (`_layouts/post.html`) は、項目のラベル（例 `(HN・英語)`）が示す媒体と
リンク先のドメインが一致しない項目にだけ、遷移先のドメインを表示する。
アグリゲータ経由の項目では遷移先がラベルから読めず、媒体ラベルの項目では
ドメインを足すと二重表示になる (#294) ため。

一致の判定に使う「記事ドメイン」の正本はソース定義
(`.claude/skills/curate-news/references/sources/*.md`) にあるが、Jekyll は
ドットで始まるディレクトリを読まないので、ここで `_data/` に写す。
表示名のゆれ (`Hacker News` → `HN` 等) は check_source_hints.py の ALIASES を共有する。

使い方:
  python3 .claude/scripts/gen_source_domains.py           # _data/source_domains.json を書き出す
  python3 .claude/scripts/gen_source_domains.py --check   # 書き出し済みの内容が最新かだけ確かめる（古ければ exit 1）
"""
import json
import sys
from pathlib import Path

from check_source_hints import ALIASES, source_tables

OUT = Path("_data/source_domains.json")


def build():
    """{表示名: [記事ドメイン, ...]} を返す。ゆれの表記も同じドメインに引ける"""
    _, by_domain = source_tables()
    if by_domain is None:
        return None
    table = {}
    for domain, (_, display) in sorted(by_domain.items()):
        table.setdefault(display, []).append(domain)
    for alias, display in sorted(ALIASES.items()):
        if display in table:
            table[alias] = table[display]
    return dict(sorted(table.items()))


def render(table) -> str:
    return json.dumps(table, ensure_ascii=False, indent=2) + "\n"


def main(argv):
    table = build()
    if table is None:
        return 1
    text = render(table)
    if "--check" in argv:
        current = OUT.read_text(encoding="utf-8") if OUT.is_file() else ""
        if current != text:
            print(f"NG {OUT} がソース定義と一致しません。"
                  f"python3 .claude/scripts/gen_source_domains.py で書き直してください")
            return 1
        print(f"OK {OUT} はソース定義と一致しています（{len(table)} 件）")
        return 0
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(text, encoding="utf-8")
    print(f"{OUT} を書き出しました（{len(table)} 件）")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
