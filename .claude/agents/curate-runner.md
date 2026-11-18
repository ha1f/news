---
name: curate-runner
description: 費用計測で subagent_type として名指しされたときだけ使う（日次の publish では使わない。#667）。curate-news を1回回すための subagent で、渡すツールを curate-news が使うものだけに絞り、起動時に読み込むツール定義を減らす
tools: Bash, Read, Write, Skill, Glob, Grep
model: opus
---
渡された指示に従って curate-news スキルを実行し、ステップ6で自分が書き出したファイルのフルパスを報告する。
