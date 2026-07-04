# モデルの使い分けと癖

一次情報は公式ガイド。ここには skill 運用に効く要点だけ置く:

- [Prompting Claude Fable 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5)
- [Prompting Claude Sonnet 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5)
- [Claude Code system prompts](https://platform.claude.com/docs/en/release-notes/system-prompts) — harness が既に与えている指示。skill や subagent prompt で重複させない
- [Getting started with loops](https://claude.com/blog/getting-started-with-loops) — 停止条件つきループの設計

## 使い分けの目安

- orchestrator (判断・検証・統合): session のモデルをそのまま使う
- 並列 worker (実装・探索): sonnet で十分なことが多い。Agent の model パラメータで指定
- 迷ったら指定しない (session のモデルを継承する)

## Sonnet 5

- 指示を字義通りに解釈する。適用範囲を明示する (「最初の 1 件だけでなく全 sub-plan に適用」等)
- レビューを依頼するときは「確信が低くても全部報告して。フィルタは別段階でやる」と伝えると recall が上がる

## Fable 5

- 手順を細かく書くほど品質が下がる。ゴール・制約・完了条件だけ渡す
- 長い run の終盤で「次に X をやります」と宣言したまま止まることが稀にある。subagent の return が宣言だけでなく実行を伴っているか確認する
