---
name: curate-runner
description: curate-news スキルを1回回すための subagent。渡すツールを curate-news が使うものだけに絞り、起動時に読み込むツール定義を減らす（費用計測用、#667）
tools: Bash, Read, Write, Skill, Glob, Grep
model: opus
---
渡された指示に従って curate-news スキルを実行し、ステップ6で自分が書き出したファイルのフルパスを報告する。
