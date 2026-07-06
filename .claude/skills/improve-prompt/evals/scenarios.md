# 机上評価シナリオ

スキルを変更したら、[eval-guide.md](../references/eval-guide.md) の机上シミュレーションで以下を検証する。期待を満たさない変更は merge しない。

1. **MUST / CRITICAL の多い古いエージェントプロンプト**（Claude 4 前半世代の書き方）
   期待: 強調を理由つき通常表現へ変換し、model-notes.md を根拠に世代のズレを指摘する。全要素が対応表に載る
2. **600 行の SKILL.md、全情報インライン**
   期待: type-specific-guide.md のスキル節を読み、progressive disclosure（references への分離）と description の what + when を提案する
3. **「改善の効果を確かめたい」という依頼つきのスキル改善**
   期待: eval-guide.md の軽量ループ（baseline snapshot → fresh subagent で新旧並列 → blind 比較）を提案し、実行できる
4. **ラベル付き 100 例と exact-match metric がある分類パイプライン**
   期待: 手作業の書き換えで終えず、programmatic-optimization.md を読んで 3 条件の充足を確認し、DSPy (GEPA) を提案する
5. **元プロンプトにない技術仕様を補いたくなる対象**（regex フレーバー未指定等）
   期待: 推測で断定せず、条件付き表現で提案し、対応表で「追加」と明示する
6. **数行の rule 修正**
   期待: フルの workflow を回さず、釣り合った軽い提示（対応表は数行、eval 提案なし）
7. **発火境界**: 「このコードのエラーメッセージを改善して」のような、プロンプトでない文言改善の依頼
   期待: このスキルの対象外と判断する（description の発火判断にも使う near-miss）
