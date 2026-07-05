# モデルと体制のノート

一次情報 (skill に転記せず、必要なときここから参照する):

- [Prompting Claude Fable 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5)
- [Prompting Claude Sonnet 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5)
- [Claude Code system prompts](https://platform.claude.com/docs/en/release-notes/system-prompts) — harness の指示と重複させないための照合先
- [Getting started with loops](https://claude.com/blog/getting-started-with-loops) — 停止条件つきループの設計
- [Harness engineering (OpenAI)](https://openai.com/ja-JP/index/harness-engineering/) — ルールは機械的に検証できる形で環境側に置く
- [Building a C compiler with parallel Claudes (Anthropic)](https://www.anthropic.com/engineering/building-c-compiler) — 検証器の正確さと共有が土台。検証器を先に整備し、全 agent が同じ検査を再実行できるようにする

## 使い分け

orchestrator は session のモデル、実装 worker は sonnet、ログ解析・分類など機械的な作業は haiku を並列で。迷ったら指定しない。

team の形は 3 つ: 使い捨て subagent (独立作業)、会話を継続する teammate (設計判断の往復が要る大物)、fan-out + 検証 (独立視点が欲しいとき)。

## 癖

- Sonnet 5: 字義通りに解釈するので適用範囲を明示する。レビュー依頼は「確信が低くても全部報告、フィルタは別段階」。orchestrator を任せるなら計画コメントを checklist として更新させる
- Fable 5: 手順を書くほど品質が下がる。ゴールと制約だけ渡す。宣言だけして止まることが稀にあるので、return が実行を伴うか確認する
