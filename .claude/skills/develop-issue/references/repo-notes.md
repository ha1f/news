# repo 固有ノート

このスキルは汎用で、repo 固有の情報は各 repo の `.claude/rules/develop-issue.md` に置く (rules 配下なら他のセッションにも自動で読み込まれる)。存在しない repo では、run 中に確認した内容から以下の項目でドラフトを作り、別 PR で提案する。

## 項目

- 検証コマンドと期待する green 状態 (test / lint / build / 型チェック)
- CI の構成と癖 (所要時間、flaky なジョブ、re-run の作法)
- レビュー bot の種類と対応方針
- 環境の制約 (ローカルで実行できないもの、権限、必要なツール)
- CLAUDE.md / CONTRIBUTING に書かれていない暗黙の規約 (PR の粒度感、レビュー文化)

## 運用

- CLAUDE.md と重複する内容は書かない
- 古くなった項目に気づいたら、その run で更新 PR を出す
