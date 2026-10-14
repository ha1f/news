# モデルと体制のノート

一次情報 (skill に転記せず、必要なときここから参照する):

- [Prompting Claude Fable 5.1](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1) — 5.1 固有の癖（バッチ指示・targeted edit）。5 共通の goal-oriented パターンは [Prompting Claude Fable 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5)
- [Prompting Claude Sonnet 5.5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5) — 現行の Sonnet。同ページが「Claude Sonnet 5 向けのプロンプトはそのままでよく、[Prompting Claude Sonnet 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5) のパターンも出発点として有効」と書いているので、5 側も併読してよい
- [Claude Code system prompts](https://platform.claude.com/docs/en/release-notes/system-prompts) — harness の指示と重複させないための照合先
- [Getting started with loops](https://claude.com/blog/getting-started-with-loops) — 停止条件つきループの設計
- [Harness engineering (OpenAI)](https://openai.com/ja-JP/index/harness-engineering/) — ルールは機械的に検証できる形で環境側に置く
- [Building a C compiler with parallel Claudes (Anthropic)](https://www.anthropic.com/engineering/building-c-compiler) — 検証器の正確さと共有が土台。検証器を先に整備し、全 agent が同じ検査を再実行できるようにする

## 使い分け

orchestrator は session のモデル（trigger の指定に従う。現行世代は live docs の models/overview、指定の方針は README の trigger 定義）、実装 worker は現行の Sonnet（2026-10-02 時点は Sonnet 5.5）、ログ解析・分類など機械的な作業は現行の Haiku（2026-10-11 時点は Haiku 5.5）を並列で。迷ったら指定しない。

team の形は 3 つ: 使い捨て subagent (独立作業)、会話を継続する teammate (設計判断の往復が要る大物)、fan-out + 検証 (独立視点が欲しいとき)。

## 癖

- Sonnet 5.5: 字義通りに解釈するので適用範囲を明示する（Sonnet 5 からの持ち越し。公式も 5 向けのパターンを出発点として挙げている）。レビュー依頼は「確信が低くても全部報告、フィルタは別段階」。orchestrator を任せるなら、計画コメントを投稿する run では checklist として更新させる
  - **effort の目安が変わった**: 既定は `high`。agentic coding は well-specified なら `medium`、難しい・長いものは `high` から。レベルの体感は Sonnet 5 と同じではないので、5 の設定をそのまま持ち越さない
  - **`low` / `medium` では途中で確認に戻ることがある**（完走させたい worker には effort を上げるか、「頼まれたことが全部終わるまで続け、ユーザなしでは進めないときと危険な操作の前だけ聞く」を指示に入れる）
  - **頼んでいないテスト・ドキュメント・補助ファイルを足す傾向**がどの effort でも出る（diff を最小に保ちたいタスクでは「終わって検証できたら止まる。頼まれていない追加はしない」を添える）
- Fable 5.1: 手順を書くほど品質が下がる。ゴールと制約だけ渡す。宣言だけして止まることが稀にあるので、return が実行を伴うか確認する。並列ツール呼び出しが減る傾向あり（1文のバッチ指示で戻る）
