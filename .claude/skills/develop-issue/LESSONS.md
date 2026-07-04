# LESSONS

実行から得た教訓。1 教訓 1 行 (理由が必要ならカッコで)。repo や git 履歴から分かることは書かない。固有名詞は抽象化する。解消したら消す。

- worktree 環境では diff の base に local branch でなく `origin/<base>` を使う (local が古いと他人の commit が diff に混入する)
- ユーザ指示で質問をスキップして進むときも、スキップした判断と想定した回答を記録する (issue コメントで人間が後から検証できるように)
- プロンプトに外部サービスの固有名 (bot 名等) をハードコードしない (GitHub API の `user.type == "Bot"` のような型レベルの判定で足りる)
