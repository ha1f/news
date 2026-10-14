---
name: audit-and-adopt
description: "ループ自身の資産（スキル・ルール・ワークフロー・ドキュメント）を監査し、エコシステムの新機能やベストプラクティスを取り込む。daily-loop の週次ステージ（日曜11時）。「環境を監査して」でも使う。"
---

# audit-and-adopt

プロダクトでなく「ループ自身の環境」を改善対象にする週次ステージ。オーナーの指摘を待たずに、外部視点の批評とエコシステム追従を自動で回す。状態の持ち方と status issue コメントの形式は [.claude/GUARDRAILS.md](../../GUARDRAILS.md) に従う（stage は `audit`）。

日次の reflect-and-improve が拾うのは「その会話で観測された摩擦」。会話の外にある劣化 — マージ済み資産の陳腐化・エコシステムとの乖離・手順の形骸化 — はどのステージも見ていないため、ここが受け持つ。オーナーが指摘するはずだった水準の発見を人間なしで毎週出せていれば成功。

## 手順

5つのレンズを fresh context の subagent で回し、自分は PdM として取捨する。前提として、status issue（番号は check_state.py の `status_issue`）の直近の記録（前回監査の end レコードと今週の各ステージのレコード）は `gh api "repos/{owner}/{repo}/issues/<status issue>/comments?since=<8日前のUTC 例 2026-10-03T00:00:00Z>&per_page=100" --jq '.[] | [.created_at, (.body | split("\n")[0])] | @tsv'` の1回で取る（1行目 JSON だけ抜けば 1 週間分が約 36KB で入る。生出力は約 370KB、MCP の `get_comments` は 1 ページ 80〜200KB で、実測 2026-10-11 は 8 ページ分を退避ファイルから結合する羽目になった。100 件を超えたら `&page=2` を足す。`--paginate` は 403）。前回の記録が「修正 PR で解消」と書いている件は、`gh api repos/{owner}/{repo}/pulls/<n> --jq '{merged,state,labels:[.labels[].name]}'` でマージ状態を確かめてから subagent に渡す（`gh pr view` は GraphQL で 403。実測 2026-10-11: hold 中の #501 を「マージ済み」として渡し、subagent が前提を訂正した）:

1. **資産批評** — `.claude/` 配下と VISION.md / DESIGN.md / README.md から今週の対象を1〜2個選ぶ（前回監査の status 記録を見てローテーション、最終更新が古いものを優先）。外部の専門家として批評させる: 正確性・肥大化・日付つき事実の失効・pin したバージョンの乖離・公式ベストプラクティスとの差分。並行して Claude Code 組み込みの `claude -p '/doctor prompt-audit' --max-turns 60 --output-format text` を1回走らせ、CLAUDE.md・rules・全スキルを横断した失効パス・矛盾の報告を得る（実測 2026-10-11: `--max-turns 10` では完走しない。約 10 分。CLAUDE.md の存在しないパス参照を初回で検出した）。報告の各項目は主張として扱い、現物で裏取りできたものだけ採用する
2. **エコシステム** — Claude Code の changelog（https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md）・公式 docs（https://code.claude.com/docs/）・公式スキル集（https://github.com/anthropics/skills）を確認させ、この repo が使っていない有用な新機能・取り込む価値のある外部スキルを採用判断つきで報告させる。Claude Code の外も対象にする: ループが今やっている作業や人間に残っている作業を肩代わりできるツール（GitHub App・Action・外部サービス。依存更新の Renovate が先例）があれば、導入の issue として提案する。判断の物差しは GUARDRAILS の設計原則と DESIGN.md（目新しさより整合を優先）。毎回必ず見るのはループ自身が動くモデルの世代で、[README.md](../../../README.md) の trigger 定義にあるモデル指定の方針と、各 trigger の実際の指定を突き合わせる（現行世代の正は live docs の `https://platform.claude.com/docs/en/models/overview` と `https://code.claude.com/docs/en/model-config` を直接読む。claude-api スキルの Current Models はキャッシュで1世代遅れうる（2026-09-27 実測: cached 2026-06-24 の表が Opus 5.5 を「launching」と書いていた）。記憶で判断しない）。trigger は repo 外にあり人間しか編集できないため、乖離していれば trigger ごとの新旧モデル ID を添えて issue にする（直接は直せない）
3. **プロセス監査** — 直近1週間のマージ済み PR が無ければ subagent を起動せず「該当なし」とする（早期終了の原則）。あれば、それらと status issue の記録を、各スキルが定める手順の痕跡（UI PR のスクショ確認コメント、複数案の検討記録、reflect の実施、issue の受け入れ条件との突合コメント）と照合させ、手順が守られなかった事例を挙げさせる。違反には「なぜ守られなかったか」の仮説（手順が重い・曖昧・知られていない）まで付けさせる
4. **プロダクト監査** — [audit スキル](../audit/SKILL.md)を引数なしで実行する。該当監査の選定（再監査トリガーと履歴の突合）・実行・記録はスキル側が担い、該当が無ければ「該当なし」で戻る。対象はループ環境でなくプロダクト・事業側（法務・収益化準備など）で、環境しか見ないレンズ1〜3の死角をここで受け持つ
5. **PR 在庫** — `python3 .claude/skills/audit-and-adopt/scripts/pr_stock.py` の分類に従って、溜まった open PR を動かす。どのカテゴリも空なら subagent を起動せず「該当なし」とする。このレンズの出力は close・ready 化・DM・修正 PR のいずれかにし、下の取捨の基準にある cap 超過時の見送りは当てはめない（記録だけに終わると、在庫は誰にも動かされない。2026-10-12 実測: open PR 15件のうち13件がオーナー待ちか担当なしだった）
   - `superseded` → 後継へのリンクをコメントして close する
   - `stale_drafts` → 中身が今の main に対しても正しく完成していれば ready 化して review に渡す。そうでなければ、PR が残そうとした事実や未完の作業を issue に残してから、理由をコメントして close する（学びを残す起票は GUARDRAILS の保全分なので、cap 超過でも行う）
   - `hold` → PR ごとに subagent へ、今の main に対する推奨（merge / close / 直してから merge）と根拠を調べさせる。同じ head SHA に一次レビューのコメントがあれば判定はそれを使い、調べるのはその後に変わったこと（main との conflict、前提の失効）だけにする。同じファイルを触る PR のマージ順も付けた判断リストにまとめ、status の end コメントに載せ、Slack が使えればオーナーに DM で1通送る。hold PR 自体には触れない
   - `stalled` → 本来動かしているはずのステージ（ready なら review、linked issue が open な draft なら develop）が拾わなかった原因を調べ、手順の不備が原因なら直す PR を出す
   - `summary` を status の end コメントに載せ、前回の audit の記録と比べる。open PR 数や最古の日数が増えていれば、その原因も `stalled` と同じく調べる

取捨の基準: 観測された問題・確実な失効だけ拾い、推測的な改善は捨てる。軽微で確実な修正（バージョン更新・失効した記述の訂正）は直接 DRAFT PR にして ready 化する。修正先が保護パスで、同じファイルを保護パス由来の `hold` で待つ open PR があれば、自分の PR にそれらの diff を取り込んで本文に番号を書き、人間のマージ判断を1回にまとめる（hold PR 自体には commit を積まない。要修正判定が付いたものは指摘を反映して取り込む。人間が理由を書いて止めた hold は対象外。保護パスは人間のマージ判断が律速で、PR を増やすほど滞留する。2026-10-04 実測: review-and-merge/SKILL.md を待つ hold PR が3件・最長8日並び、その間に同ファイルの手順が実環境と乖離した。#501）。判断が要るものは issue にする（書式・上限は evaluate-and-triage の新規 issue と同じ。上限は日単位で evaluate と共有なので、当日の作成済み件数を差し引く。cap 超過時は見送り、status 記録に残す）。ビジョン・フェーズに関わる提案は VISION.md の更新 PR。該当なしのレンズは無理に絞り出さず「該当なし」でよい。

PR を作成したら `python3 .claude/scripts/check_protected_paths.py --diff origin/main` で保護パスへの該当を確認し、該当する場合は該当ファイルと理由を PR にコメントする。`hold` ラベルは付けず、マージもしない (保護パスは review が毎 run diff から機械判定して自分で付ける。先回りすると review はそれを「人間が止めた PR」として素通りし、review の一次レビューもオーナーへの通知も無いまま人間待ちになる。実測 #396)

## 完了条件

- 5レンズの結果がそれぞれ issue / PR / close / DM / status 記録の「該当なし」のいずれかに落ちている
- status issue に開始と終了の各1コメント（1行目 JSON、stage は `audit`。選んだ監査対象と結果の要約を summary に）
- 最後に reflect-and-improve を実行し、作成した改善 PR を ready 化する（次の review run のレビュー対象になる）
