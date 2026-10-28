#!/usr/bin/env bash
# PR の CI（jekyll-build-check.yml の「Check article quality」）で回す検査の正本。
# workflow は保護パス（人間のマージが要る）なので、検査を足す・外すのはここで行う。
#
# 使い方: ci_article_checks.sh <base SHA> <head SHA>
#   repo ルートで、_site をビルドした後に実行する
set -e
base="${1:?PR の base SHA を渡す}"
head="${2:?PR の head SHA を渡す}"

python3 .claude/scripts/check_article_anchors.py _site
# 全投稿に当てる。ツール呼び出し構文の混入は間欠的に起きるので
# 「この PR が触った投稿」だけを見ると、別の PR で入った分を素通り
# させる。誤検知は持たない（#408 で全 408 本に当てて0件）
python3 .claude/scripts/check_tool_artifacts.py
# 本文が変わった投稿だけを渡す。この2つの検査が見るのは本文の記事項目
# だけなので、front matter を一括更新した PR に全件を渡すと、その投稿が
# 書かれた当時のルールで書かれた既存の本文まで今の検査にかかり、PR が
# 持ち込んでいない違反で red になる（#401 で実測: title 行だけを直した
# 368件を渡すと 2,453 件の不一致。同じ数が main 側の同じファイルでも出る）
changed=$(python3 .claude/scripts/changed_post_bodies.py "$base" "$head")
if [ -n "$changed" ]; then
  echo "$changed"
  python3 .claude/scripts/check_article_notes.py $changed
  python3 .claude/scripts/check_source_hints.py $changed
else
  echo "この PR は _posts の本文を変更していないためスキップ"
fi
