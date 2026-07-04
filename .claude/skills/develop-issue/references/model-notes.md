# モデルと体制のノート

一次情報は公式ガイド。ここには運用に効く要点だけ:

- [Prompting Claude Fable 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5)
- [Prompting Claude Sonnet 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5)
- [Claude Code system prompts](https://platform.claude.com/docs/en/release-notes/system-prompts) — harness が既に与えている指示。skill や subagent prompt で重複させない
- [Getting started with loops](https://claude.com/blog/getting-started-with-loops) — 停止条件つきループの設計
- [Harness engineering (OpenAI)](https://openai.com/ja-JP/index/harness-engineering/) — 指示で守らせるより、機械的に検証できるルールと自己完結した計画を先に整える。モデルを問わず再現性を上げる発想

## モデルの使い分け

- orchestrator (判断・検証・統合): session のモデルをそのまま使う
- 実装 worker: sonnet を並列で
- 機械的な作業 (ログ解析、大量ファイルの分類・要約、定型変換): haiku を並列数で稼ぐ
- 迷ったら指定しない (session のモデルを継承)

## team の形

- 使い捨て subagent: 自己完結した sub-plan を渡して返答を待つだけ。独立作業の基本形
- 会話を継続する teammate: 設計判断の往復が要る大きな sub-plan は、名前つき agent に任せて途中で追加指示・軌道修正する
- fan-out + 検証: 同じ対象に独立した視点が欲しいとき (観点を変えた複数レビュー、複数案の比較)

## Sonnet 5

- 指示を字義通りに解釈する。適用範囲を明示する (「最初の 1 件だけでなく全 sub-plan に適用」等)
- レビュー依頼は「確信が低くても全部報告して。フィルタは別段階でやる」と伝えると recall が上がる
- orchestrator を任せる場合は、issue の計画コメントを checklist として更新しながら進めると脱線しにくい

## Fable 5

- 手順を細かく書くほど品質が下がる。ゴール・制約・完了条件だけ渡す
- 長い run の終盤で「次に X をやります」と宣言したまま止まることが稀にある。subagent の return が宣言だけでなく実行を伴っているか確認する
