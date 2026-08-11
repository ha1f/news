#!/usr/bin/env python3
"""既存の Jekyll 投稿にトピックタグを付与する。

キーワードベースでタグを判定し、frontmatter に tags: を追加する。
既に tags: がある投稿はスキップする。

使い方:
  python3 scripts/tag_posts.py              # dry-run (変更なし)
  python3 scripts/tag_posts.py --apply      # 実際に書き込む
"""
import re
import sys
from pathlib import Path

TOPICS = {
    "AI": [
        "AI", "LLM", "機械学習", "深層学習", "ニューラル", "GPT", "Claude",
        "OpenAI", "Anthropic", "生成AI", "エージェント", "agent", "モデル",
        "推論", "ファインチューン", "RAG", "プロンプト", "Gemini", "Llama",
        "transformer", "diffusion", "Copilot", "chatbot", "チャットボット",
        "AGI", "超知能", "alignment",
    ],
    "開発": [
        "開発", "プログラミング", "フレームワーク", "ライブラリ", "SDK", "API",
        "Git", "CI/CD", "DevOps", "Rust", "Python", "JavaScript", "TypeScript",
        "React", "Node", "コンパイラ", "IDE", "エディタ", "テスト", "リファクタ",
        "オープンソース", "OSS", "npm", "パッケージ", "CLI", "ターミナル",
        "Kubernetes", "Docker", "コンテナ", "マイクロサービス", "WebAssembly",
        "Wasm", "Swift", "Kotlin", "Go言語", "Zig",
    ],
    "セキュリティ": [
        "セキュリティ", "脆弱性", "攻撃", "認証", "暗号", "プライバシー",
        "データ保護", "漏洩", "hack", "ハック", "CVE", "ゼロデイ",
        "ランサムウェア", "フィッシング", "マルウェア", "サイバー",
        "パスワード", "多要素", "SSO",
    ],
    "ビジネス": [
        "スタートアップ", "資金調達", "買収", "上場", "IPO", "M&A",
        "投資", "VC", "ユニコーン", "起業", "経営", "CEO",
        "Product Hunt",
    ],
    "科学": [
        "研究", "論文", "Nature", "Science", "学術", "発見", "実験",
        "物理", "化学", "生物", "医療", "ゲノム", "量子", "宇宙",
        "NASA", "天文", "素粒子",
    ],
    "デザイン": [
        "デザイン", "UI", "UX", "フォント", "タイポグラフィ", "Figma",
        "Dribbble", "ビジュアル", "アクセシビリティ",
    ],
    "経済": [
        "経済", "金融", "株", "為替", "GDP", "インフレ", "日銀", "FRB",
        "市場", "金利", "決算", "景気", "財政",
    ],
    "ハードウェア": [
        "半導体", "チップ", "GPU", "CPU", "NVIDIA", "TSMC", "Intel", "AMD",
        "プロセッサ", "センサー", "データセンター", "サーバー", "回路",
        "ロボット", "ドローン", "EV", "自動運転",
    ],
    "社会": [
        "規制", "法律", "政策", "社会", "教育", "雇用", "著作権",
        "独禁法", "反トラスト", "GDPR", "倫理", "バイアス",
        "ディープフェイク", "フェイクニュース", "選挙",
    ],
}

FRONTMATTER_RE = re.compile(r"^---\n(.*?\n)---\n", re.S)


def classify(content: str) -> list[str]:
    lower = content.lower()
    tags = []
    for topic, keywords in TOPICS.items():
        for kw in keywords:
            if kw.lower() in lower:
                tags.append(topic)
                break
    return sorted(tags)


def process_post(path: Path, apply: bool) -> tuple[str, list[str]]:
    text = path.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(text)
    if not m:
        return "skip-no-frontmatter", []
    fm = m.group(1)
    if "tags:" in fm:
        return "skip-has-tags", []

    body = text[m.end():]
    tags = classify(body)
    if not tags:
        return "skip-no-tags", []

    tags_line = "tags: [" + ", ".join(tags) + "]\n"
    new_fm = fm + tags_line
    new_text = "---\n" + new_fm + "---\n" + body

    if apply:
        path.write_text(new_text, encoding="utf-8")
    return "tagged", tags


def main():
    apply = "--apply" in sys.argv
    posts_dir = Path(__file__).resolve().parent.parent / "_posts"
    posts = sorted(posts_dir.glob("*.md"))
    stats = {"tagged": 0, "skip-has-tags": 0, "skip-no-tags": 0, "skip-no-frontmatter": 0}

    for p in posts:
        status, tags = process_post(p, apply)
        stats[status] += 1
        if status == "tagged":
            print(f"  {'WRITE' if apply else 'DRY'} {p.name}: {tags}")

    mode = "APPLIED" if apply else "DRY-RUN"
    print(f"\n{mode}: tagged={stats['tagged']}, "
          f"already-tagged={stats['skip-has-tags']}, "
          f"no-match={stats['skip-no-tags']}, "
          f"no-frontmatter={stats['skip-no-frontmatter']}")


if __name__ == "__main__":
    main()
