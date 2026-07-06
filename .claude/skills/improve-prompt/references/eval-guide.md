# プロンプト eval ガイド

プロンプト・スキル変更の効果を「動くはず」でなく観察で確かめるための軽量ループ。

## いつ・どれだけやるか

- 数行の rule 修正 → eval 不要。対応表チェックで足りる
- 繰り返し使うスキル・システムプロンプトへの構造的変更 → 軽量ループ（下記）
- 成熟したスキル・失敗が高コストなプロンプト → 回帰シナリオ集を育てて変更のたびに流す

公式の目安: 実利用を代表する ~20 クエリで変化は検出できる（大きな eval セットを作るまで待たない）。実際の失敗から採った 20〜50 のシンプルなタスクが great start。

## 軽量ループ

1. **baseline を確保**: 旧版を snapshot する（`cp -r` で別ディレクトリへ）
2. **シナリオを 2〜3 個**書く（新規時）。形式: 入力プロンプト + 期待挙動の検証可能な assertion 列挙（pass/fail、部分点なし）。「発火すべき」だけでなく「発火すべきでない near-miss」（キーワードは共有するが対象外の依頼）も入れる
3. **fresh context の subagent で新旧を並列実行**する。subagent には snapshot / 新版それぞれのパスだけを渡し「このファイル群だけを頼りに実行し、事前知識で欠落を補完しない」と指示する。作者コンテキストを持った自分で試すのは甘い検証になる
4. **採点して transcript も読む**。集計値だけ見ない（hallucination や迷いは transcript にしか出ない）
5. 見つけた失敗をシナリオ化して evals/ に追加し、次回の回帰チェックに使う

### 机上シミュレーション（スキル向け・最軽量）

fresh context の agent に「SKILL.md と references だけを頼りに各シナリオを模擬実行し、行動が決定できない点・失敗しうる点を報告」させる。実行なしで曖昧さ・矛盾を検出できる。字義通りに解釈する軽量モデルを想定した読みも含めると堅牢。

### blind 比較（改善効果の判定）

新旧の出力を A/B ラベルだけで独立の judge agent に渡す（どちらが新版かは知らせない）。position bias 対策に順序を入れ替えて 2 回。tie は稀のはず — 毎回 tie ならシナリオに判別力がない。

## grader の使い分けと設計

安く速い順に使う: code-based（exact match / regex）→ LLM-as-judge（先に人間の判定と較正）→ human（gold standard だが遅い。spot-check と較正に限定）。

LLM-as-judge を使うときの規律:

- rubric は検証可能に書く（「第 1 文で X に言及。なければ incorrect」）。「良い文章か」のような純定性的評価はスケールしない
- 判定は binary か 1〜5 スケール。理由を考えさせてから判定させ、理由は捨てる
- **process でなく outcome を採点する**（どの経路を通ったかでなく、正しい最終状態に到達したか）
- escape hatch を与える（判定に足る情報がなければ "Unknown"）。**迷ったら FAIL** — 弱い assertion での pass は false confidence を生み、無いより悪い
- 独立した評価次元（正確さ・引用・網羅性など）は別々の judge コールに分ける
- 生成と判定は別モデルにする（self-preference bias の報告あり）
- verbosity bias（長い出力の過大評価）と position bias（提示順で勝率が動く）を前提に設計する

## 非決定性

- 1 回の pass/fail はノイズ。シナリオごとに複数 trial（3 回目安）で平均と分散を見る
- pass@k（k 回中 1 回成功）と pass^k（k 回全部成功）は別物 — per-trial 75% でも 3 連続成功は ~42%
- 高分散（例: 50% ± 40%）は flaky の兆候。プロンプトでなくシナリオや環境を先に疑う
- 新旧どちらでも常に pass する assertion は判別力がない。剪定するか難化する。全シナリオ 100% になったら回帰検出専用に格下げし、新しい難しいシナリオを足す

## ツール

- Anthropic Console evaluation tool: `{{variable}}` でテストセット作成、side-by-side 比較、5 段階採点。https://platform.claude.com/docs/en/test-and-evaluate/eval-tool
- skill-creator プラグイン: スキルの with/without 並列実行・blind 比較・variance 分析の参考実装
- promptfoo: YAML 宣言で assertion と CI 統合。https://www.promptfoo.dev

## 一次ソース

- https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents （task 設計・grader 3 分類・pass@k/pass^k・落とし穴）
- https://platform.claude.com/docs/en/build-with-claude/develop-tests （成功条件の定義と grading の使い分け）
- https://www.anthropic.com/engineering/multi-agent-research-system （~20 クエリで始める、end-state 評価、manual testing の重要性）
