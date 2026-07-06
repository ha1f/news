# プログラマティック最適化 (DSPy / GEPA)

手で書き直す代わりに、optimizer がプロンプトを自動改善するアプローチ。手作業改善（このスキル本体）と排他ではなく、条件が揃う対象ではこちらの方が確実に効く。

## いつ提案するか

3 条件が揃ったら手作業でなくこちらを提案する:

1. **パイプラインがコード化されている**（または容易にできる）: 分類・抽出・RAG・要約など入出力が定まった反復タスク
2. **metric が関数で書ける**: exact match、スコア関数、または「期待 X に対し実際 Y」というテキストフィードバック
3. **評価データがある**: 20 例〜（optimizer により 10〜200+。ラベルは入力のみでも可）

不向きなもの: 対話エージェントのシステムプロンプト（タスク分布が広く trainset を切り出せない）、主観的品質（「良い文章」）、多目的の同時最適（品質×コスト等）。これらは手作業改善 + eval の領分。

参考: https://dspy.ai / https://github.com/stanfordnlp/dspy （2026-05 時点 v3.2.1）

## Optimizer の選び方

| Optimizer | 向く条件 |
|---|---|
| BootstrapFewShot | 例が ~10 件。few-shot 例の自動生成 |
| BootstrapFewShotWithRandomSearch | 例が 50 件以上 |
| MIPROv2 | 指示文 + few-shot の同時最適化。200 例以上推奨（overfit 防止） |
| GEPA | 実行トレースへの reflection で指示文を進化。テキストフィードバックを活かせ、少データ（数十例）から大規模まで動く |
| SIMBA | カスタムフィードバックから学ぶ。agentic / long-horizon 向き |

迷ったら GEPA（現在の主推奨。公式 docs も主経路として案内）。データ件数は目安であり、行を選ぶ基準はタスクの形（few-shot が効くか、指示文を進化させたいか）。

GEPA は実行トレース（推論・tool call・エラー）を LM が自然言語で reflect して指示文を書き換え、Pareto frontier から変異元を選んで局所解を回避する（論文: https://arxiv.org/abs/2507.19457, ICLR 2026）。camera-ready 版の数値では RL (GRPO) を平均 +6%・最大 +20% 上回り、rollout 数は最大 1/35、MIPROv2 を 10% 超上回る。**二次記事によくある「+10%」は v1 の数値なので引用時は注意。** DSPy に統合済み（`dspy.GEPA`）。standalone 版 https://github.com/gepa-ai/gepa は DSPy なしで生のシステムプロンプトも最適化できる（要 evaluation セット）。

## Claude で使う

実行系（program）は安いモデル、reflection（GEPA の指示文生成）は賢いモデルを使う。metric は score とテキスト feedback を返す（GEPA はテキストで学ぶ）:

```python
opt = dspy.GEPA(metric=metric, auto="light",
                reflection_lm=dspy.LM("anthropic/claude-opus-4-8"))
optimized = opt.compile(program, trainset=trainset[:20], valset=trainset[20:])
```

## 限界と運用

- 最適化自体が大量の LM 呼び出し。light 設定でも 30〜90 分の報告あり。コストと時間を見積もってから
- 「なぜ良くなったか」は最終スコアからは分からない。コンパイル済みプロンプトを読んで理解する
- metric が悪いと metric に overfit する。Signature / Module 設計と metric 定義は人間が固めてから optimizer に回す — この前工程（metric とシナリオの言語化）が improve-prompt の手作業の出番で、eval-guide.md のシナリオ設計とそのまま接続する
