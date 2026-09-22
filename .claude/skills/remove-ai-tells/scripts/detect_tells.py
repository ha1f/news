#!/usr/bin/env python3
"""文章から「AI が書いたように読める癖」の候補を機械的に拾い、JSON で出力する。

判定はしない。候補と文書全体の指標を返し、直すか残すかはスキル側で判断する。
語彙は references/common.md と references/<lang>.md の ```lexicon ブロックから読む。
```lexicon prose と書いたブロックは見出し行に当てない。

使い方:
  detect_tells.py <file> [--lang en|ja|ja,en] 候補を探す（日英が混ざる文章はカンマで両方指定する）
  detect_tells.py --stdin [--lang en|ja]      標準入力の文章から候補を探す
  detect_tells.py --compare <before> <after>  書き直しで消えた・増えた事実の要素を比べる

出力（scan）: lang, hits[{id, source, line, column, match, context}], counts{id: 総数},
  repeated_phrases[{phrase, count, lines}], metrics{words, chars, sentences, sentence_length_cv,
  commas_per_sentence, bullet_line_ratio, bold_count}, judgment_checks[{id, title}]
出力（compare）: lang, removed{numbers, urls, names, negations, hedges}, added{同じキー}
"""
import argparse
import json
import re
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

DEFAULT_REFS = Path(__file__).resolve().parent.parent / "references"

# ハーネスは長いツール出力を途中で切るので、同じ観点の一致は先頭だけ返す。総数は counts に残る
MAX_HITS_PER_ID = 20

# 繰り返しフレーズとして数える長さ。英語は単語数、日本語は文字数（英数字の並びは1つと数える）
NGRAM_RANGE = {"en": (3, 8), "ja": (6, 30)}

EN_STOPWORDS = set("""
a an and are as at be been but by can do for from had has have he her his i if in
into is it its me my no not of on or our she so than that the their them then there
these they this to too us was we were what when which who will with you your
""".split())

URL = re.compile(r"https?://[^\s)>\]]+")
INLINE_CODE = re.compile(r"`[^`]*`")
HEADING = re.compile(r"^\s*#")
BULLET = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s")
BOLD = re.compile(r"\*\*[^*\n]+\*\*")
SENTENCE_END = re.compile(r"[.!?。！？]+")

# --compare で比べる、意味を運ぶ要素
FACTS = {
    "en": {
        "negations": r"\b(?:not|no|never|none|nothing|neither|nor|without|cannot|"
                     r"can't|won't|don't|doesn't|didn't|isn't|aren't|wasn't|weren't|"
                     r"shouldn't|wouldn't|couldn't)\b",
        "hedges": r"\b(?:may|might|could|can|likely|unlikely|possibly|perhaps|"
                  r"probably|about|around|approximately|roughly|nearly|almost|some|"
                  r"several|often|usually|sometimes|mainly|mostly|partly|generally|"
                  r"typically|should|must)\b",
    },
    "ja": {
        "negations": r"ない|なかった|ません|ず(?=[、。にとも]|$)",
        # 「約」は「契約」などを拾わないよう数の直前に限る
        "hedges": r"約(?=[0-9０-９一二三四五六七八九十百千万数])|"
                  r"数(?:名|人|件|十|百|千|万|か月|ヶ月|日|年|回)|可能性|かもしれ|"
                  r"だろう|でしょう|と思(?:う|われ)|おそらく|たぶん|程度|ほど|など|"
                  r"主に|一部|ほぼ|およそ|必要|べき",
    },
}


def parse_lexicon(md: str) -> list:
    """Markdown 中の全 ```lexicon ブロックから (id, 正規表現, 適用範囲) を順に取り出す"""
    entries = []
    for info, block in re.findall(r"^```lexicon([^\n]*)\n(.*?)^```", md,
                                  re.S | re.M):
        scope = "prose" if info.strip() == "prose" else "all"
        for line in block.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if ": " not in line:
                raise ValueError(f"lexicon の行は「id: 正規表現」の形で書く: {line}")
            ident, pattern = line.split(": ", 1)
            entries.append((ident.strip(), pattern, scope))
    return entries


def _langs(lang: str) -> list:
    """「ja,en」のようなカンマ区切りの指定を言語のリストにする。先頭の言語で文や語を数える"""
    return [l.strip() for l in lang.split(",") if l.strip()] or ["en"]


def load_lexicon(refs: Path, lang: str) -> list:
    """common と対象言語の語彙を合わせてコンパイルする。id の重複と不正な正規表現はエラー"""
    if not (refs / "common.md").exists():
        raise FileNotFoundError(f"references が見つからない（common.md がない）: {refs}")
    entries, seen = [], set()
    for source in ["common"] + _langs(lang):
        path = refs / f"{source}.md"
        if not path.exists():
            continue
        for ident, pattern, scope in parse_lexicon(path.read_text(encoding="utf-8")):
            if ident in seen:
                raise ValueError(f"lexicon id が重複している: {ident}")
            seen.add(ident)
            try:
                regex = re.compile(pattern, re.IGNORECASE)
            except re.error as e:
                raise ValueError(f"lexicon {ident} の正規表現が不正: {e}") from e
            entries.append({"id": ident, "source": source, "regex": regex,
                            "scope": scope})
    return entries


def judgment_checks(refs: Path, lang: str) -> list:
    """references のうち種別が JUDGMENT の観点を (id, 見出し) で返す。正規表現では拾えず、全文を読んで確かめるもの"""
    checks = []
    for source in ["common"] + _langs(lang):
        path = refs / f"{source}.md"
        if not path.exists():
            continue
        items = re.split(r"^### ", path.read_text(encoding="utf-8"), flags=re.M)[1:]
        for item in items:
            head = re.match(r"([a-z0-9-]+): (.+)", item)
            if head and re.search(r"^- 種別:\s*JUDGMENT", item, re.M):
                checks.append({"id": head.group(1), "title": head.group(2).strip()})
    return checks


def detect_lang(text: str) -> str:
    """かな・漢字が文字の2割を超えれば日本語とみなす"""
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return "en"
    ja = sum(1 for c in letters
             if "\u3040" <= c <= "\u30ff" or "\u4e00" <= c <= "\u9fff")
    return "ja" if ja / len(letters) > 0.2 else "en"


def _blank(m: re.Match) -> str:
    return " " * len(m.group(0))


def checkable_lines(text: str) -> list:
    """検査する行を (行番号, 行, 見出しか) で返す。

    コードブロックと引用（他人の言葉）は飛ばし、インラインコードと URL は列位置を保ったまま空白にする。
    """
    lines, in_code = [], False
    for lineno, line in enumerate(text.splitlines(), 1):
        if line.lstrip().startswith("```"):
            in_code = not in_code
            continue
        if in_code or line.lstrip().startswith(">"):
            continue
        masked = URL.sub(_blank, INLINE_CODE.sub(_blank, line))
        lines.append((lineno, masked, bool(HEADING.match(line))))
    return lines


def detect(text: str, refs: Path, lang: str) -> dict:
    hits = []
    lexicon = load_lexicon(refs, lang)
    lines = checkable_lines(text)
    originals = text.splitlines()
    for lineno, line, is_heading in lines:
        for entry in lexicon:
            if is_heading and entry["scope"] == "prose":
                continue
            for m in entry["regex"].finditer(line):
                hits.append({"id": entry["id"], "source": entry["source"],
                             "line": lineno, "column": m.start() + 1,
                             "match": m.group(0),
                             "context": originals[lineno - 1].strip()})
    hits.sort(key=lambda h: (h["line"], h["column"]))
    counts, shown = defaultdict(int), []
    for h in hits:
        counts[h["id"]] += 1
        if counts[h["id"]] <= MAX_HITS_PER_ID:
            shown.append(h)
    primary = _langs(lang)[0]
    return {"lang": lang, "hits": shown, "counts": dict(counts),
            "repeated_phrases": repeated_phrases(text, primary),
            "metrics": metrics(text, primary),
            "judgment_checks": judgment_checks(refs, lang)}


def _units(line: str, lang: str) -> list:
    if lang == "ja":
        # 記号と空白は落とし、文字を単位にする。英数字の並びは途中で切らないよう1単位にまとめる
        return re.findall(r"[A-Za-z0-9][A-Za-z0-9'-]*|[^\W_]", line)
    return re.findall(r"[a-z0-9][a-z0-9'-]*", line.lower())


def _is_informative(gram: tuple, lang: str) -> bool:
    if lang == "ja":
        # 決まり文句は助詞や語尾をまたぐので、ひらがなを含み、カタカナか漢字が2字以上あるものを数える。
        # 日付や、用語・固有名詞だけの並びは繰り返して当然なので数えない
        if any(u[0].isdigit() for u in gram):
            return False
        chars = "".join(gram)
        has_kana = any("\u3040" <= c <= "\u309f" for c in chars)
        content = sum(1 for c in chars
                      if "\u30a0" <= c <= "\u30ff" or "\u4e00" <= c <= "\u9fff")
        return has_kana and content >= 2
    return any(w not in EN_STOPWORDS for w in gram)


def repeated_phrases(text: str, lang: str) -> list:
    """文書内で2回以上出るフレーズを、長いものを優先して返す。見出しは同じ形が並ぶのが当然なので数えない"""
    lo, hi = NGRAM_RANGE.get(lang, NGRAM_RANGE["en"])
    joiner = "" if lang == "ja" else " "
    lines = [(lineno, _units(line, lang))
             for lineno, line, is_heading in checkable_lines(text) if not is_heading]
    kept = []
    for n in range(hi, lo - 1, -1):
        where = defaultdict(list)
        for lineno, units in lines:
            for i in range(len(units) - n + 1):
                gram = tuple(units[i:i + n])
                if _is_informative(gram, lang):
                    where[gram].append(lineno)
        for gram, linenos in where.items():
            if len(linenos) < 2:
                continue
            phrase = joiner.join(gram)
            # より長い既出フレーズの一部で、出現回数も同じなら重複なので捨てる
            if any(phrase in k["phrase"] and k["count"] >= len(linenos)
                   for k in kept):
                continue
            kept.append({"phrase": phrase, "count": len(linenos),
                         "lines": sorted(set(linenos))})
    return kept


def metrics(text: str, lang: str) -> dict:
    """文書全体の量の指標。単独では判定に使わず、ほかの候補と合わせて読む"""
    body = [line for _, line, is_heading in checkable_lines(text)
            if line.strip() and not is_heading]
    sentences = []
    for line in body:
        line = BULLET.sub("", line)
        sentences += [s for s in SENTENCE_END.split(line) if s.strip()]
    if lang == "ja":
        lengths = [len(re.sub(r"\s", "", s)) for s in sentences]
        commas = sum(line.count("、") + line.count("，") for line in body)
    else:
        lengths = [len(s.split()) for s in sentences]
        commas = sum(line.count(",") for line in body)
    cv = (statistics.pstdev(lengths) / statistics.mean(lengths)
          if len(lengths) > 1 and statistics.mean(lengths) else 0.0)
    return {
        "words": sum(len(line.split()) for line in body),
        "chars": sum(len(re.sub(r"\s", "", line)) for line in body),
        "sentences": len(sentences),
        "sentence_length_cv": round(cv, 2),
        "commas_per_sentence": round(commas / len(sentences), 2) if sentences else 0.0,
        "bullet_line_ratio": round(sum(1 for l in body if BULLET.match(l)) / len(body), 2)
        if body else 0.0,
        "bold_count": sum(len(BOLD.findall(l)) for l in body),
    }


def _names(line: str, lang: str) -> list:
    if lang == "ja":
        return re.findall(r"[ァ-ヶー]{3,}|[A-Za-z][A-Za-z0-9.+#/-]*[A-Za-z0-9+#]", line)
    names, start, end = [], None, None
    text = BULLET.sub("", line)
    # 所有格の 's は名前に含めない（Example と Example's を同じ名前として比べるため）
    for m in re.finditer(r"[A-Za-z][A-Za-z0-9]*", text):
        word, before = m.group(0), text[:m.start()].rstrip()
        sentence_start = not before or before[-1] in ".!?:;"
        is_name = word != "I" and (any(c.isupper() for c in word[1:]) or (
            word[0].isupper() and not sentence_start))
        # 空白・スラッシュ・ハイフンでつながる名前（Cloud Pub/Sub など）は1つにまとめる
        if is_name and start is not None and re.fullmatch(r"[ /-]", text[end:m.start()]):
            end = m.end()
            continue
        if start is not None:
            names.append(text[start:end])
        start, end = (m.start(), m.end()) if is_name else (None, None)
    if start is not None:
        names.append(text[start:end])
    return names


def _facts(text: str, lang: str) -> dict:
    lang = _langs(lang)[0]
    lang = lang if lang in FACTS else "en"
    lines = [line for _, line, _ in checkable_lines(text)]
    return {
        "numbers": [m.group(0).rstrip(".,，．") for l in lines
                    for m in re.finditer(r"[0-9０-９][0-9０-９,，.．]*[%％]?", l)],
        "urls": [u.rstrip(".,") for l in text.splitlines() for u in URL.findall(l)],
        "names": [n for l in lines for n in _names(l, lang)],
        "negations": [m.group(0) for l in lines
                      for m in re.finditer(FACTS[lang]["negations"], l, re.I)],
        "hedges": [m.group(0) for l in lines
                   for m in re.finditer(FACTS[lang]["hedges"], l, re.I)],
    }


def _minus(a: list, b: list) -> list:
    """a にあって b にない要素を、a での出現順に（重複は個数ぶん）返す"""
    extra = Counter(a) - Counter(b)
    out = []
    for x in a:
        if extra[x] > 0:
            out.append(x)
            extra[x] -= 1
    return out


def compare(before: str, after: str, lang: str) -> dict:
    """書き直しで消えた要素（意味が変わった疑い）と増えた要素（捏造の疑い）を返す"""
    b, a = _facts(before, lang), _facts(after, lang)
    return {"lang": lang,
            "removed": {k: _minus(b[k], a[k]) for k in b},
            "added": {k: _minus(a[k], b[k]) for k in b}}


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    parser.add_argument("file", nargs="?")
    parser.add_argument("--stdin", action="store_true",
                        help="標準入力から読む（明示したときだけ）")
    parser.add_argument("--compare", nargs=2, metavar=("BEFORE", "AFTER"))
    parser.add_argument("--lang", help="en / ja / ja,en など。省略時は文字種から判定する")
    parser.add_argument("--refs", default=str(DEFAULT_REFS))
    args = parser.parse_args()

    if args.compare:
        before, after = (Path(p).read_text(encoding="utf-8") for p in args.compare)
        result = compare(before, after, args.lang or detect_lang(before))
    else:
        if args.stdin:
            text = sys.stdin.read()
        elif args.file:
            text = Path(args.file).read_text(encoding="utf-8")
        else:
            parser.error("ファイル、--stdin、--compare のどれかを指定する")
        try:
            result = detect(text, Path(args.refs), args.lang or detect_lang(text))
        except (FileNotFoundError, ValueError) as e:
            parser.error(str(e))
    json.dump(result, sys.stdout, ensure_ascii=False, indent=1)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
