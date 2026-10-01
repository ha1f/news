#!/usr/bin/env python3
"""PR body から linked issue 番号を取り出す正本 (#473)。

review-and-merge の `classify_prs.py` と select-and-develop の `select_issues.py` が
同じ正規表現を別々に持っていたため、両方が同じ欠陥を抱えていた: body を素のまま
走査するので、**リンクキーワードをデータとして引用した箇所**（コードフェンス内・
インラインコード内・他 PR の body の引用）まで linked issue に数える。

実測 (PR #471 の body): 6ヒットのうち4件は正規表現の挙動表そのもの
(`'Refs #408' -> ['408']` 等)、2件は他 PR の body のバッククォート引用で、
`[408, 421]` という偽のリンクができていた。その PR は「linked issue は無い」と
宣言していたのに、である。

これは散文の規律（「この単語を打つな」）では塞げない。リンクの抽出は
GUARDRAILS.md の設計原則の第1項が言う「決定的な処理」なので、スクリプト側で
Markdown のコード部分を落としてから正規表現を当てる。

正本を1つにしているのは、2箇所に写した正規表現が実際に同じ欠陥を2箇所に
生んだため。片方だけ直すと、同じ body を見ている2つのステージが違う結論を出す。
"""
import re

# `Closes #123` / `Refs #45` 等。両スクリプトが持っていたものと同一
LINK_RE = re.compile(r"(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?|refs?)\s+#(\d+)", re.I)

# コードフェンスの開始/終了。CommonMark に合わせ、インデントは3スペースまで、
# フェンスはバッククォートかチルダ3つ以上
_FENCE_RE = re.compile(r"^ {0,3}(?P<fence>`{3,}|~{3,})(?P<info>.*)$")


PLACEHOLDER = "[code]"


def strip_code_blocks(text):
    """コードフェンスの中身を落とし、1行ずつ PLACEHOLDER に置き換える。

    空行でなく PLACEHOLDER を置くのは、落とした結果で前後がつながり **新しい**
    偽ヒットが生まれるのを防ぐため。LINK_RE のキーワードと `#123` の間は `\\s+`
    なので、空行を挟んでも `Closes` と `#123` は一致してしまう（改行は空白）。
    キーワードにも数字にもならない文字列を挟めば、そこで必ず切れる。
    閉じフェンスが無いまま body が終わる場合は、そこから末尾までコードとして扱う
    （Markdown のレンダラと同じ挙動）。
    """
    out = []
    fence_char = None
    fence_len = 0
    for line in (text or "").split("\n"):
        m = _FENCE_RE.match(line)
        if fence_char is None:
            # ``` のフェンスでは info 文字列にバッククォートを含められない
            if m and not (m.group("fence")[0] == "`" and "`" in m.group("info")):
                fence_char = m.group("fence")[0]
                fence_len = len(m.group("fence"))
                out.append(PLACEHOLDER)
                continue
            out.append(line)
        else:
            closing = (m and m.group("fence")[0] == fence_char
                       and len(m.group("fence")) >= fence_len
                       and not m.group("info").strip())
            out.append(PLACEHOLDER)
            if closing:
                fence_char = None
    return "\n".join(out)


def strip_inline_code(text):
    """インラインコード（バッククォートで囲まれた範囲）を落とす。

    CommonMark のコードスパンと同じく、開始のバッククォート列と**同じ長さ**の
    列で閉じる。閉じが無い列はコードスパンではないのでそのまま残す。
    正規表現1本で書くと「同じ長さで閉じる」が表しにくいので素直に走査する。
    """
    text = text or ""
    out = []
    i = 0
    n = len(text)
    while i < n:
        if text[i] != "`":
            out.append(text[i])
            i += 1
            continue
        start = i
        while i < n and text[i] == "`":
            i += 1
        run = i - start
        # 同じ長さのバッククォート列を探す（それより長い列は閉じにならない）
        j = i
        close = -1
        while j < n:
            if text[j] == "`":
                k = j
                while k < n and text[k] == "`":
                    k += 1
                if k - j == run:
                    close = j
                    break
                j = k
            else:
                j += 1
        if close == -1:
            out.append(text[start:i])  # 閉じが無い = ただのバッククォート
            continue
        # コードスパンを落とす。strip_code_blocks と同じ理由で、空白でなく
        # PLACEHOLDER を挟んで前後が新しいヒットを作らないようにする
        out.append(PLACEHOLDER)
        i = close + run
    return "".join(out)


def strip_code(text):
    """コードフェンスとインラインコードの両方を落とす。"""
    return strip_inline_code(strip_code_blocks(text))


def extract_linked_issues(body):
    """PR body が実際に進める issue の番号を昇順で返す（純関数）。

    コード部分を落としてから LINK_RE を当てるので、`Closes #N` を
    コードとして引用しただけの body は空リストになる。
    """
    return sorted({int(m.group(1)) for m in LINK_RE.finditer(strip_code(body))})
