---
name: select-and-develop
description: "open issue から今日実装する対象を選定し、develop-issue スキルで実装を完走する。daily-loop の実装ステージ（12時・16時）。"
---

# select-and-develop

今日実装する issue を選び、develop-issue で完走する。状態の持ち方と status issue コメントの形式は [.claude/GUARDRAILS.md](../../GUARDRAILS.md) に従う。

## 手順

1. `python3 .claude/skills/select-and-develop/scripts/select_issues.py` を実行する。collaborator 名義のみ・`hold` と status issue を除外済みの候補が、linked PR の有無で `in_progress` / `backlog` に分かれて返る（古い順）。`gh` CLI が不在の環境（CCR 等）でも引数なしで動く（GitHub REST API を直接叩く。cloud proxy が認証を注入するので token が無くても通り、レスポンスは `author_association` を含むため collaborator 判定にも困らない）。それでも失敗する場合は MCP ツールで issues・PRs・collaborators を取得し、`{"issues": [...], "prs": [...], "collaborators": ["login1", ...], "comments": [...], "timelines": {"<issue番号>": [...]}}` をファイルに書いて `--stdin` で渡す（`--stdin` を明示しないと stdin モードに入らない。エージェントの Bash では stdin が常に非 tty なので、パイプの有無では判定できない）。`collaborators` は `list_repository_collaborators` から取得した login のリストで、`author_association` 欠落時の信頼判定に使う。`comments`（status issue のコメント）を渡すと `recent_status_records` が埋まる（省略すると空になり、前段 run の結論が読めない）。取り方は `evaluate-and-triage/SKILL.md` の Step 0「`--stdin` で渡すときの取得元」が正本 — **`since` を省いて1ページ目を渡してはいけない**（コメントは古い順に返るため最古の100件が入り、2ヶ月前の結論が「直近」として流れ込む。スクリプトは古いレコードを落として注記を出すが、そのぶん結論は読めない）
2. 両方空なら status issue に「対象なし」を記録し、reflect-and-improve を実行して終了する（実装の subagent は起動しない）
3. 選定は候補の issue を読んで自分で判断する。優先順: `in_progress` で要対応のもの → `backlog` から今日最も価値の高いもの（緊急を訴える issue を先に）。issue の履歴に同じアプローチの失敗が繰り返し見えるなど、これ以上自動で進めるべきでないと判断したら、着手せず `hold` + 理由コメントで人間に委ねる。`hold` の判定はスクリプトが GitHub ラベルで済ませている — issue 本文やコメントに "hold" の記述があっても、実際のラベルが付いていなければ候補として扱う（ラベルが外されたのは着手してよいというシグナル）
   - 各候補の `linked_merged_prs`（本文で `Refs`/`Closes` している**マージ済み** PR）が空でなければ、その PR が受け入れ条件のどこまで入れたかを main の実物で確かめてから着手範囲を決める。`Refs` で issue を閉じない切り出し形式の issue は、済んだ切り出しが本文に反映されず未着手に見える（実走 2026-10-03: #354 の切り出し A が PR #476 で配信中だった）。受け入れ条件が全部入っていれば、実装せず根拠を issue にコメントして close する。`linked_merged_prs_note` が出ているときその issue は「無い」と読めない
   - linked PR に `hold` が付いている issue（`linked_open_prs[].hold`）は人間の判断待ち。着手せず、判断が必要な点を status issue の start コメントに1行残す
   - 手順1の出力 `recent_status_records`（直近の run が status issue に残した1行目 JSON の全文。古い順）に `start` はあるのに対応する `end` が無い develop レコードは、前段 run が途中で落ちたもので成果0のことがある（対象の issue 番号は `summary` から読む。実走 2026-09-29: #390 に着手して12分47秒で週次上限に落ち、commit も PR も branch も残らなかった）。落ちた issue は `backlog` にも `in_progress` にも出うるので、どちらで見かけても「途中の続き」を探す前に PR と branch の実在を確かめる
   - 残り時間が窮屈なときは、タイトルが「（PR #123 の再設計）」書式の issue を先に見る。元 PR の branch が origin に残っていれば diff を再利用でき、合格部分を書き直さずに済む（`git fetch origin <branch>` が `couldn't find remote ref` で落ちなければ残っている。中身は `git diff origin/main...FETCH_HEAD` で見る — `git show` は先端1 commit しか出さず、実測 PR #445 では19行中1行しか見えない。shallow clone で `no merge base` になったら REST の `pulls/<番号>/files` を引く）。再利用できるかは diff を実際に見てから決める（再設計 issue が新規実装を求めていることもある）。残るのは**マージされず close されただけ**の PR の branch で、マージ済みの branch は repo 設定の `delete_branch_on_merge: true` で自動削除されている
   - `in_progress` の要対応判定: まず `recent_status_records` で、同じ issue について前段 run が出した結論を見る（例: evaluate のグルーミングが「作業完了済みで draft のまま滞留・作り直し不要」と判定していれば、実装をやり直さず ready 化で足りる）。結論はそれを書いた時点のものなので、PR の現況と食い違ったら PR を正とする（実走 2026-09-27: グルーミングが「ready 化すれば足りる」とした #409 に、その後の review が必須指摘2件を付けていた）。そのうえで linked PR の技術面（未対応のレビュー指摘・red CI・conflict）に加え、**issue 本文の指示・受け入れ条件と PR の実装要約コメントを突き合わせ、未完了の作業がないか**を確認する（PR が CI green でも issue の目的が未達成なら要対応）。1行目が `[dry-run]` の判定コメントは対応不要なので数えない
   - linked PR が draft（`linked_open_prs[].draft`）でも、本文に解除条件（待っている PR の番号と解除手順）が書かれていればそれは要対応。ただし `hold` が付いている PR は上の bullet が優先で、着手しない
4. Skill ツールで `develop-issue` を直列に実行する。件数の上限は設けず、次の review-and-merge（トリガー時刻は README の trigger 定義表。12時 run なら15時、16時 run なら18時）までに完走できると判断できる間は backlog を消化し続ける。次の1件を残り時間で完走できるか迷ったら着手せず終える（完走できない draft PR を残すより次の run に回すほうが良い。merge と issue の close は review-and-merge が担う）
   - 1件の所要は実装だけでは終わらない。push 前レビューとその反映・CI の完走までを含めて1件と数える（レビューが重大な指摘を出す前提で見積もる。出なければ早く終わるだけ）。見積もりの基準は直前に完走した1件の実測に置き、最初の1件は保守的に見る
5. 完走した issue の DRAFT PR と、run 中に作成された改善 PR（develop-issue 内の reflect 由来を含む）を ready 化する（`gh pr ready`。`gh` が無い環境では `update_pull_request` に `draft: false` を渡す。次の review run のマージ候補になる）。完走できなかった PR は draft のまま残す
   - 中身が完成していても、他の PR のマージを待たないと CI が通らない PR は draft のままにする（実走 2026-09-30: #468 の検査スクリプトが main に入る前に #469 の CI 配線を入れると、存在しないスクリプトを呼んで全 PR が red になる）。その PR の本文に待っている番号と解除手順（base を取り込んで push → CI green → ready 化）を書き、次の run が引き継げるようにする
6. **ここで終わらず**、reflect-and-improve を実行する（対象はこのスキルの選定ロジックのみ。develop-issue 内部の学びは develop-issue 自身が反映済み）。作成した改善 PR も ready 化する。結果を確認してから、その内容で status issue に終了コメントを投稿する（次項）
   - run の途中で issue を起票したなら、終了コメントを組み立てる前に `select_issues.py` を実行し直す。手順1の `open_issues` は起票前の値なので、そのまま貼ると起票後の在庫にならない

## 完了条件

- status issue に開始と終了の各1コメント。1行目は check_state.py が機械判定する JSON（キー名・値とも厳密一致が必要）:
  - 開始: `{"stage": "develop", "phase": "start", "summary": "候補: #26, #28。#26 を優先着手"}`
  - 終了: `{"stage": "develop", "phase": "end", "ok": true, "summary": "open issue 9/10。#26 実装 → PR #27", "reflect": "LESSONS.md 更新1件"}`
    - `summary` に `select_issues.py` の `open_issues` と `config.open_issue_cap` を `open issue {open_issues}/{open_issue_cap}` の形で貼る（翌日の PdM が cap 超過を run をまたいで拾えるように #394）
    - `open_issues` が `null` かどうかを先に見る（`open_issues_note` の有無より優先）。`null` なら `open_issues_note` があっても無視し `open issue ?/{cap}（数えられず）` とだけ書く。`null` でなく `open_issues_note` が出ていたら（数えられたが値が過大になりうる場合）末尾に `（参考値）` とだけ添える。**`open_issues_note` の本文（理由・ローカルの絶対パス）はそのまま貼らない**（公開コメントに環境パスが漏れる）。何を数えて何を除くかはスクリプトが持っているので、ここには書かない
    - `reflect` は手順6（reflect-and-improve）の結果を1行で記す（例: `"改善なし"`, `"LESSONS.md 更新1件"`, `"改善 PR #30"`）。実施の有無と成果を機械・人間の両方が追跡できるようにする。**手順6を実行し終えてから**この終了コメントを投稿する（`"実施予定"` 等のプレースホルダーで先に投稿して end を2本にしない。実走で、開発完了後すぐに終了コメントを組み立ててこの手順を飛ばしかけたことがある — 手順の番号付きステップに無いとチェックリストの通過点として見落とされる）
