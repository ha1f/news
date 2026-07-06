---
name: improve-prompt
description: システムプロンプト・スキル・CLAUDE.md・ツール記述などのプロンプトを診断・改善する。「プロンプトを改善して」「このプロンプトをレビューして」「プロンプトを最適化して」で使う。プロンプトの書き方・評価 (eval)・自動最適化 (DSPy) についての質問や相談にも使う。
argument-hint: "対象のプロンプト（ファイルパスまたはテキスト）"
---

# improve-prompt

`$ARGUMENTS` のプロンプトを診断し、改善版・受け入れ判断の材料（対応表）・必要なら検証手段（eval）まで返す。原則の一次ソースは末尾の公式ドキュメントで、このスキルが持つのは適用の判断基準と手順。モデル世代固有の話は [references/model-notes.md](references/model-notes.md) に隔離してあり、本文は世代に依存しない。

## Step 0: 対象の理解と道具の選択

- 目的と種類を特定する: システムプロンプト / スキル / CLAUDE.md・rules / エージェント指示 / API 呼び出し / ツール記述。いずれにも該当しない文言（コード内のエラーメッセージ、UI テキスト等）はこのスキルの対象外と伝え、通常の作業として扱う
- エージェント向け・スキル・ツール記述・出力フォーマット制御・長文コンテキスト・API 呼び出しに該当したら [references/type-specific-guide.md](references/type-specific-guide.md) の該当節を読む
- モデル挙動や API 仕様に依存する記述、旧世代向けの徴候（MUST の連発、prefill、budget_tokens 等）があれば [references/model-notes.md](references/model-notes.md) を読む
- 対象が `.claude/rules/` / `.claude/skills/` 配下なら、同ディレクトリの既存ファイルを Read してスタイル（frontmatter、構造、表記慣習）を実物で確認する（コンテキストからの推測は改訂方針がブレる）
- 対象がコード化されたパイプライン（分類・抽出・RAG 等）で、metric を関数で書けて評価データが 20 例以上あるなら、手作業改善よりプログラマティック最適化が向く。[references/programmatic-optimization.md](references/programmatic-optimization.md) を読んで提案する。採用されたら以降の手作業は metric とシナリオの言語化（同ファイル末尾）に切り替える

## Step 1: 診断

改訂につながる発見だけを挙げる（網羅チェックではない）。深さは変更の規模に釣り合わせる:

- **矛盾** — 指示同士の衝突。解消に推論が浪費され、どちらにも従えない
- **曖昧さ・スコープ** — 同僚に渡して迷わず実行できるか。現行モデルは指示を literal に解釈するため、適用範囲（全部 / 最初だけ / 除外）を明示する
- **高度 (altitude)** — 条件分岐の羅列（brittle）でも精神論（曖昧）でもなく、判断基準（heuristics）を与えているか
- **動機の欠如** — 理由があると指示を汎化し、想定外のケースにも対応できる
- **否定形** — 「するな」だけの指示。理由つき肯定形か「Don't X — do Y instead」へ
- **過剰な強調** — MUST / CRITICAL / 絶対 は現行世代では overtriggering を招く。理由つきの通常表現で足りる
- **冗長さ** — 全 token が attention budget を消費する。「期待挙動を規定する最小集合」か。念のための記述・自己言及・空虚な激励を削る
- **構造** — 長いプロンプトは XML タグや見出しで指示・コンテキスト・入出力を分離。タグ内で Markdown 強調を多用しない（構造解釈が曖昧になる）
- **例の質** — examples は多様で典型的な 3〜5 個。edge case の詰め込みは汎化を壊す
- **手順の縛りすぎ** — エージェント向けは手順列挙よりゴールと成功条件。順序が重要なときだけ番号付きで

## Step 2: 改善

診断で挙げた問題を直す。代表例:

- Before: `NEVER use ellipses`
  After: `応答は読み上げエンジンで再生される。省略記号は発音できないため、文を完結させる`（否定形 → 理由つき肯定形）
- Before: `CRITICAL: You MUST use this tool when...`
  After: `Use this tool when...`（強調を外した通常表現で足りる。従わせたい理由があるなら直前に説明として置く）

1 行足すときは 1 行削れないか考える。改善は元の意図の保存が前提で、意図が不明な箇所は推測で断定せず、質問するか条件付き表現で提案する。

## Step 3: 情報保持の対応表

元プロンプトの全要素と改善版の対応を 1 つの表にまとめる。情報欠落の検証と差分提示を兼ねる。要素は意味の単位（見出し・箇条書き・文）で拾い、機械的な行単位にしない。

| 元プロンプトの要素 | 扱い | 説明 |
|---|---|---|
| `具体的な記述` | 保持 / 統合 / 変換 / 削除 / 追加 | 1 行 |

- **保持** — 文言は変えたが意図そのまま / **統合** — 別項目とまとめた（統合先を指す） / **変換** — 否定形→肯定形、強調→理由 など / **削除** — 自明・冗長・空虚 / **追加** — 改善版で新規に加えた（なぜ必要か）
- 「追加」は必ず明示する。新規の数値基準や推測した技術仕様を表に書き落とすと、ユーザーが元由来と提案を区別できない

## Step 4: 提示

改善版本体と対応表のみを提示する（変更サマリ等の別セクションは対応表と重複する）。メタ説明（診断 + 対応表）が改善版本体を超えないことを目安にし、超えるときは説明の短縮や行の統合で圧縮する（要素を落として満たさない）。数行の軽微な対象ではこの目安より対応表の完全性を優先し、表も数行でよい。

## Step 5: 検証の提案

繰り返し使われるプロンプト（スキル、システムプロンプト）への構造的な変更には、[references/eval-guide.md](references/eval-guide.md) の検証を提案する。手段は目的で選ぶ（必要なら両方）: 改善効果の判定は新旧を fresh context の subagent で並列実行する blind 比較、曖昧さ・矛盾の検出は机上シミュレーション。1 回の印象より複数 trial。効果が確認できたら、使ったシナリオを対象側の evals/ に残して回帰資産にする。

軽微な変更（数行の rule 修正等）には提案しない。

## 一次ソース

- Prompting best practices: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
- Context engineering: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- Skill authoring: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
- Evals: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
- モデル世代の差分: [references/model-notes.md](references/model-notes.md)（世代交代時はここだけ更新）
