# 言語によらない観点

言語に依存しない AI の文章の癖（書式と記号、文のリズムと形、修辞と内容、チャットやツールの残骸、自分の言い回しの使い回し）をまとめる。決まった語彙や言い回しの一覧は en.md と ja.md にある。否定の対比や意義の付け足しのように、考え方は共通でも候補の拾い方が言語ごとに違う観点は、ここには判断の基準だけを書き、正規表現は言語別ファイルに置く。種別の LEXICAL は lexicon ブロックの正規表現で `scripts/detect_tells.py` が候補を拾うもの、METRIC はスクリプトが文書全体の値を出すもの、JUDGMENT は全文を読んで判断するもの。どの種別でも 1 回の出現はたいてい偶然で、兆候になるのは密度、位置、ほかの癖との重なり。lexicon の id は一度付けたら変えない。

## 目次

- 書式と記号: common-bold-label-bullet, common-emoji-marker, common-bold-overuse, common-list-for-prose, common-em-dash, common-colon-reveal
- リズムと形: common-uniform-rhythm, common-same-shape, common-rule-of-three, common-self-echo
- 修辞と内容: common-generic-claim, common-inflated-significance, common-negative-parallelism, common-tagline-ending, common-summary-restatement, common-vague-attribution
- チャットとツールの残骸: common-tool-residue, common-chat-leftover
- ジャンル別の例外
- 直しすぎの兆候
- スクリプト出力の読み方
- 時期で変わる傾向（確認日: 2026-09）

## 書式と記号

### common-bold-label-bullet: 太字のラベルで始まる箇条書き

```lexicon
common-bold-label-bullet: ^[ \t]*(?:[-*+\u2022\u30fb]|\d+[.)\uff0e])[ \t]*\*\*[ \t]*[^*\s][^*\n]{0,39}?(?:[:\uff1a][ \t]*\*\*|\*\*[ \t]*(?:[:\uff1a]|[-\u2013\u2014][ \t]))(?=[ \t]*\S)
```

- 種別: LEXICAL
- 兆候になる条件: 説明や経緯を書く箇条書きの大半が「太字の見出し語、コロンかダッシュ、説明」の形になっている。ラベルが後ろの説明を短く言い直しているだけのことが多い。
- 残す場合: 用語集、API のパラメータ一覧、設定項目や操作の一覧、レジュメのスキル欄のカテゴリ名のように、読み手がラベルを拾い読みする一覧。README の手順や機能紹介でも使われる形なので、一覧の性格で判断する。ラベルがインラインコードだけの行（``**`src/`**: ...`` のようなファイルや引数の一覧）と、ラベルのあとに説明のない行（下の階層の一覧やリンクが続く形）は拾わない。
- 直し方: ラベルを消して説明の文だけ残す。項目どうしに因果や順序があるなら段落に戻す（common-list-for-prose）。
- 例: Before `- **高速化:** ビルドキャッシュを入れ、CI の所要時間を 12 分から 4 分にした` → After `- ビルドキャッシュを入れ、CI の所要時間を 12 分から 4 分にした`
- 出典: [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)、[Russell et al. 2025](https://arxiv.org/abs/2501.15654)、[textlint-rule-preset-ai-writing](https://github.com/textlint-ja/textlint-rule-preset-ai-writing)。証拠の強さ: 中

### common-emoji-marker: 行頭や見出しの絵文字

```lexicon
common-emoji-marker: ^[ \t]*(?:(?:[-*+\u2022\u30fb]|\d+[.)])[ \t]*|#{1,6}[ \t]+)?(?:[\U0001F300-\U0001FAFF\u2600-\u2604\u2607-\u260f\u2613-\u2775\u2794-\u27bf\u2b50\u2b55]|[0-9#*]\ufe0f?\u20e3)
```

- 種別: LEXICAL
- 兆候になる条件: 見出しや箇条書きの頭に ✅ 🚀 💡 などを飾りとして置く。文書、記事、レジュメ、メールで出ると目立つ。
- 残す場合: チャットや Slack の投稿、チェックリストの完了・未完了の印、その書き手やリポジトリの既存の文書が見出しに絵文字を使っている場合（LLM 以前の OSS のテンプレートや技術ブログにもあった形）。評価の ★☆、チェックボックスの ☐☒、丸数字の ❶、文中の矢印は拾わない。
- 直し方: 削る。状態を表しているなら「完了」のような語にする。
- 例: Before `## 🚀 変更点` → After `## 変更点`
- 出典: [Washington Post 2025](https://www.washingtonpost.com/technology/interactive/2025/how-detect-chatgpt-em-dash/)、[Pangram](https://www.pangram.com/signs-of-ai-writing)、[Qiita の記事の前後比較](https://nyosegawa.com/posts/qiita-writing-before-after-ai/)。証拠の強さ: 中

### common-bold-overuse: 本文の太字の多用

- 種別: METRIC
- 兆候になる条件: `metrics.bold_count` が段落の数に比べて多い。文中の句を強調のために太字にする、同じ用語を出てくるたびに太字にする、という使い方。メールやフォームのように太字が描画されない場所では記号が見えたまま残るので、1 つでも貼り付けの跡になる。
- 残す場合: 技術文書で UI のボタン名を示す慣例、レジュメのセクション名やカテゴリ名、論理の要所の 1〜2 か所。
- 直し方: 強調がなくても要点が分かる語順と文にする。本当に必要な 1 か所だけ残す。
- 例: Before（メール本文）`**明日の 10 時**に伺います。` → After「明日の 10 時に伺います。」
- 出典: [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)、[Pangram](https://www.pangram.com/signs-of-ai-writing)、[Qiita の記事の前後比較](https://nyosegawa.com/posts/qiita-writing-before-after-ai/)。証拠の強さ: 中

### common-list-for-prose: 散文で足りる内容の箇条書きと見出し

- 種別: METRIC
- 兆候になる条件: `metrics.bullet_line_ratio` が高く、しかも項目の間に因果や順序がある。短いメールやチャットの返事に見出しや箇条書きがある。中身がなく次の見出しだけを持つ見出し、節ごとの水平線、1 文で言える内容の小さな表も同じ癖。
- 残す場合: レジュメ、手順書、仕様、リファレンス、チェックリスト。項目が並列で互いに独立していれば箇条書きでよい。
- 直し方: つながりのある項目は接続の語を補って段落に戻す。見出しは、読み手が節を探す必要のある長さの文書にだけ付ける。
- 例: Before「確認しました。/ - 結論: 明日リリースできます / - 理由: テストがすべて通りました / - 次のステップ: 17 時にタグを打ちます」→ After「確認しました。テストがすべて通ったので、明日リリースできます。17 時にタグを打ちます。」
- 出典: [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)、[Anthropic: Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)、[Qiita の記事の前後比較](https://nyosegawa.com/posts/qiita-writing-before-after-ai/)、[Google developer documentation style guide: Lists](https://developers.google.com/style/lists)。証拠の強さ: 中

### common-em-dash: em dash の多用

```lexicon prose
common-em-dash: (?<![\u3000-\u30ff\u4e00-\u9fff\uff00-\uffef\u2014\u2015])(?<![\u3000-\u30ff\u4e00-\u9fff\uff00-\uffef][ \t])\u2014(?![ \t]?[\u3000-\u30ff\u4e00-\u9fff\uff00-\uffef\u2014\u2015])(?![^\[\]\n]*\]\()
```

- 種別: LEXICAL
- 兆候になる条件: em dash が段落ごとに出る。カンマや括弧で足りる挿入や、一言の強調に使っている。カジュアルなメールやチャットで出ると特に目立つ。どのモデルで多いかは時期で変わる（末尾の節）。
- 残す場合: 見出しの区切り（社名と肩書など。見出し行は検出しない）、一覧の太字ラベルと説明の区切り（その行は common-bold-label-bullet にも当たるので、1 つの問題として判断する）、ニュース記事や編集を経たエッセイ（人の書き手も 1 記事に何度も使う。AP は前後に空白を入れる）。日付範囲などの en dash と、リンクの文字列（引用したページのタイトル）の中のダッシュは拾わない。日本語の文中のダッシュは ja.md が扱い、このパターンは日本語に直接または空白 1 つを挟んで隣接するダッシュを拾わない。
- 直し方: 前後の関係に合わせて句点、カンマ、括弧に置き換える。全部をコロンやセミコロンにすると別の癖（common-colon-reveal）が増える。
- 例: Before "Thanks for the update — I'll review the draft on Thursday." → After "Thanks for the update. I'll review the draft on Thursday."
- 出典: [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)、[Washington Post 2025](https://www.washingtonpost.com/technology/interactive/2025/how-detect-chatgpt-em-dash/)、[AP vs. Chicago](https://apvschicago.com/2011/05/em-dashes-and-ellipses-closed-or-spaced.html)。証拠の強さ: 中（モデルと時期で向きが変わる）

### common-colon-reveal: 前置きの主張とコロンのあとの種明かし

- 種別: JUDGMENT
- 兆候になる条件: 本文の箇条書きや文の多くが「前置きの主張、コロン、言い直しか決め台詞」の形になっている。1 か所ずつなら人のエッセイや技術文書にも普通にある形なので、同じ形が続く割合で見る。前置きが評価（"had grown messy"）や自分の方法へのラベルのときに強い。短いラベルで盛り上げる形（"The result:"）は en.md、述語のあとのコロンは ja.md の正規表現で拾えるが、長い主張のあとのコロンは人の文章と区別できる正規表現がないので、読んで数える。
- 残す場合: コロンのあとがリストや定義で、前置きに評価が入っていない場合。「項目: 説明」の一覧や、行末のコロンでリストやコードに続ける形。
- 直し方: コロンの前が評価の前置き（"had grown messy"）なら削って事実から始める。後ろが決め台詞なら削る（common-tagline-ending）。
- 例: Before "- Reworked how the sync service handles failures: retries now back off and stop after five attempts." → After "- Made the sync service back off on retries and stop after five attempts."
- 出典: [tropes.fyi](https://tropes.fyi/directory)、このスキルの作成時に行った実文書（非公開）の監査。証拠の強さ: 弱（研究はないが、実文書の監査で最も目立った構造上の癖だった）

## リズムと形

### common-uniform-rhythm: 文の長さが揃っている

- 種別: METRIC
- 兆候になる条件: `metrics.sentence_length_cv` が、同じ書き手の過去の文章や同じジャンルの人間の文章より低い。公開された閾値はない。文が少ない文書では値がぶれるので `metrics.sentences` も見る。
- 残す場合: 手順書、API リファレンス、定型の報告書。揃っているのが正しい。
- 直し方: 長さそのものは動かさず、揃っている原因を探して直す。同じ構文の繰り返し（common-same-shape）や、どの文も同じ長さの複文になっている箇所が多い。短い断片をわざと挟まない。
- 例: Before「検索条件を保存できるようにした。保存した条件は一覧から選び直せるようにした。条件ごとに新着の通知も受け取れるようにした。」→ After「検索条件を保存し、一覧から選び直せるようにした。条件ごとに新着の通知も受け取れる。」
- 出典: [Russell et al. 2025](https://arxiv.org/abs/2501.15654)、[Muñoz-Ortiz et al. 2024](https://arxiv.org/abs/2308.09067)、[Chakrabarty et al. 2025](https://arxiv.org/abs/2510.13939)、[Qiita の記事の前後比較](https://nyosegawa.com/posts/qiita-writing-before-after-ai/)。証拠の強さ: 中（逆向きの報告もある。末尾の節）

### common-same-shape: 隣り合う箇条書きや文が同じ骨格

- 種別: JUDGMENT
- 兆候になる条件: 隣り合う 3 本以上の箇条書きや文が同じ骨格で書かれている。目印は後半の揃い方で、"..., resulting in X% improvement in Y" や「〜し、〜を実現」のように成果を述べる部分まで同じ形になる。1 文の中で、同じ長さと調子の節をセミコロンで 4 つも並べる形も同じ癖。
- 残す場合: レジュメの箇条書きが過去形の動詞で始まること、手順、API のパラメータ説明、法令の号。前半を揃えるのはジャンルの規則。
- 直し方: 内容の違いを形に出す。大事な項目は理由や背景まで書き、自明な項目は短くする。足りない事実は作らず書き手に聞く。
- 例: Before「- 決済処理をキューに移し、タイムアウトの削減を実現 / - 取引先 API に契約テストを追加し、品質の向上を実現 / - 検索インデックスの更新処理を作り直し、速度の改善を実現」→ After「- 決済処理をキューに移し、タイムアウトを減らした / - 取引先 API に契約テストを追加した / - 検索インデックスの更新処理を作り直した（[要確認: 更新にかかる時間がどれだけ変わったか]）」
- 出典: [Shaib et al. 2024](https://aclanthology.org/2024.emnlp-main.368/)、[Chakrabarty, Laban, Wu 2025](https://arxiv.org/abs/2409.14509)、[Google developer documentation style guide: Lists](https://developers.google.com/style/lists)。証拠の強さ: 中

### common-rule-of-three: 形だけの三つ組

- 種別: JUDGMENT
- 兆候になる条件: 形容詞や短い句がちょうど 3 つ並ぶ箇所が何度も出て、どれかが他の言い換えになっている。1 文や 1 項目の中に三つ組が重なると強い。英語は en.md の en-abstract-triad が、-ity や -ive のような語尾を持つ抽象語の三つ組だけを拾う（下の例の "fast" のような語は拾わない）。それ以外の三つ組と日本語は、読んで判断する。
- 残す場合: ツール名や製品名のように具体的な名前がちょうど 3 つある場合、本当に聞きたい質問が 3 つある場合。スピーチや広告の三つ組は修辞として正当。
- 直し方: 実際の数に合わせる。抽象語の三つ組は、根拠のある 1 つに絞るか全部削る。2 つや 4 つに揃え直さない。
- 例: Before "Designed a fast, reliable, and scalable sync engine that handles 2 million events a day." → After "Designed a sync engine that handles 2 million events a day."
- 出典: [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)、[Russell et al. 2025](https://arxiv.org/abs/2501.15654)、[Reinhart et al. 2025](https://www.pnas.org/doi/10.1073/pnas.2422455122)。証拠の強さ: 中

### common-self-echo: 同じ評価の言い回しの使い回し

- 種別: METRIC
- 兆候になる条件: `repeated_phrases` に評価や決め台詞の言い回しが 2 回以上出ている。要約と本文のように別々の場所に同じ句があると、一方からもう一方を生成した跡に見える。レジュメと添えるメールのように文書をまたぐ繰り返しは、両方を 1 つのファイルにまとめてスクリプトにかけると出る。
- 残す場合: 用語、製品名、定義した語、求人票の必須キーワード。同じ概念には同じ語を使うのが正しい。
- 直し方: 評価の言い回しは 1 か所だけ残すか、それぞれの場所の具体的な事実に置き換える。同義語に言い換えない（直しすぎの兆候）。
- 例: Before「（要約）現場の声に寄り添う開発を続けてきた。/（職歴）現場の声に寄り添い、問い合わせの多かった通知設定の画面を作り直した。」→ After「（要約の一文は削る）/（職歴）問い合わせの多かった通知設定の画面を作り直した。」
- 出典: [Shaib et al. 2024](https://aclanthology.org/2024.emnlp-main.368/)、[Shaib et al. 2026](https://arxiv.org/abs/2509.19163)、[tropes.fyi](https://tropes.fyi/directory)、このスキルの作成時に行った実文書（非公開）の監査。証拠の強さ: 弱（構文の繰り返しは研究で確かめられているが、句の繰り返しは実文書での観察だけ）

## 修辞と内容

### common-generic-claim: 具体的な事実の代わりに置いた抽象的な評価

- 種別: JUDGMENT
- 兆候になる条件: どの人やどの製品にも当てはまる評価（"at scale"、"deep expertise"、「高い品質」「幅広い経験」）が、何をしたかの代わりに置かれている。すぐ近くに具体的な事実があるのに、評価が先に来ている形が多い。その文を別の人のレジュメや別の会社の文書に移しても通じるなら、中身がない。
- 残す場合: 要約欄や概要の節が、本文にある具体的な事実を短くまとめている場合。評価の語だけで中身を言わない自己評価は、要約欄でも直す。学術文の名詞化は正当。
- 直し方: 評価を消し、同じ文書にある事実を前に出す。使える事実がなければ作らず、`[要確認: 何をどれだけ]` の形で書き手に聞く。半端な数字や変わった具体は人が書いた証拠なので、整えて消さない。
- 例: Before "Brings deep expertise in building performant apps at scale, having shipped a video player used by 3 million people." → After "Shipped a video player used by 3 million people."
- 出典: [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)、[Russell et al. 2025](https://arxiv.org/abs/2501.15654)、[Chakrabarty, Laban, Wu 2025](https://arxiv.org/abs/2409.14509)、[Shaib et al. 2026](https://arxiv.org/abs/2509.19163)。証拠の強さ: 強

### common-inflated-significance: 意義の誇張と宣伝調

- 種別: JUDGMENT
- 兆候になる条件: 事実を述べたあとに、裏付けのない意義や影響を付け足す（英語の ", ensuring ..." や ", highlighting ..."、日本語の「〜につながった」「〜を実現」）。平凡な事実を「転換点」「大きな流れを映す」と持ち上げる。形容が肯定一辺倒で、旅行ガイドや広告のように読める。候補を拾う語句は言語別ファイルにある。
- 残す場合: 付け足しの句が情報を持つ場合（対象範囲を並べる "covering A and B" など）。広告コピーや製品紹介の宣伝調はジャンルの形。
- 直し方: 測れる結果が原文にあればそれに置き換え、なければ削る。形容詞は比較の対象や数字に置き換える。書き換えたあとも同じ観点で見直す（宣伝調を消したつもりで持ち込む例がある）。
- 例: Before「社内向けの監視ダッシュボードを作り、チーム全体の開発体験を大きく向上させる転換点となった。」→ After「社内向けの監視ダッシュボードを作った。」
- 出典: [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)、[Reinhart et al. 2025](https://www.pnas.org/doi/10.1073/pnas.2422455122)、[Muñoz-Ortiz et al. 2024](https://arxiv.org/abs/2308.09067)。証拠の強さ: 強

### common-negative-parallelism: 誰も言っていない見方を打ち消す対比

- 種別: JUDGMENT
- 兆候になる条件: 誰も主張していない見方を立てて打ち消し、そのあとで本題を言う（"not just X, but Y"、"It's not X, it's Y"、"Y rather than X"、「単なる A ではなく B」）。1 文書に何度も出るときや、段落の締めに出るときに強い。英語は en.md の en-negative-parallelism が候補を拾う。日本語は ja.md の ja-negative-contrast で、読んで判断する。
- 残す場合: 読み手が実際に持っている誤解や、相手の発言を正す文。トラブルシュートの「原因は A でなく B」や、技術文書の「A でなく B を使う」という指示。
- 直し方: 打ち消す側を消し、本題を具体的に言う。
- 例: Before "This isn't just a job change for me; it's a chance to keep working on the payment systems I've built for four years." → After "I want to keep working on payment systems, which I've built for four years."
- 出典: [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)、[Paech et al. 2026 (Antislop)](https://arxiv.org/abs/2510.15061)、[Washington Post 2025](https://www.washingtonpost.com/technology/interactive/2025/how-detect-chatgpt-em-dash/)、[Russell et al. 2025](https://arxiv.org/abs/2501.15654)。証拠の強さ: 強

### common-tagline-ending: 決め台詞で締める

- 種別: JUDGMENT
- 兆候になる条件: 段落や箇条書きの最後に、事実を足さない格言、自分の方法に付けたラベル、読み手を励ます一言を置く。削っても意味が変わらない締めが複数の段落で続く。コロンのあとに置く形（common-colon-reveal）と重なりやすい。
- 残す場合: スピーチ、広告コピー、エッセイの結び。
- 直し方: 削る。締めが要るなら、最後の具体的な事実か次の行動（日程の候補など）で終える。
- 例: Before "- Set up contract tests that run against every partner build: quality, built in from day one." → After "- Set up contract tests that run against every partner build."
- 出典: [Russell et al. 2025](https://arxiv.org/abs/2501.15654)、[tropes.fyi](https://tropes.fyi/directory)、このスキルの作成時に行った実文書（非公開）の監査。証拠の強さ: 中

### common-summary-restatement: まとめの言い直しで終わる

- 種別: JUDGMENT
- 兆候になる条件: 文書や節の最後の段落が、前に書いたことの言い直しになっている。最後の段落に新しい数字、固有名詞、次の行動がなく、前の段落と同じ語が多い。どの節の最後にも小さなまとめがある。
- 残す場合: 論文の abstract と結論、報告書の executive summary、ニュースのリード、長い文書の要約の節。
- 直し方: 削る。終え方が要るなら、次の行動、未解決の点、判断を仰ぐ事項のような本文にない情報で終える。その情報は原文から取り、作らない。
- 例: Before「（最後の段落）以上のように、今回の移行で運用の負担が減り、開発の速度も上がった。今後もこの取り組みを続けていきたい。」→ After「（最後の段落を削り、その前の段落の『旧サーバーは来月の保守日に止める』で終える）」
- 出典: [Russell et al. 2025](https://arxiv.org/abs/2501.15654)、[Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)、[tropes.fyi](https://tropes.fyi/directory)。証拠の強さ: 中

### common-vague-attribution: 誰の意見か分からない帰属

- 種別: JUDGMENT
- 兆候になる条件: "Experts say"、"Industry reports suggest"、「専門家によると」のように、誰が言ったかを特定しない帰属。出典が 1 つなのに「多くの」と書く。英語の語句は en.md の en-vague-attribution が拾う。日本語（「専門家によると」「一般に言われている」など）は読んで判断する。
- 残す場合: 直後に具体的な出典がある場合。
- 直し方: 原文や会話に出典があれば特定する。なければ主張ごと削るか、`[要確認: 誰の調査か]` を付けて書き手に聞く。出典を作らない。
- 例: Before "Experts agree that offline-first apps keep users longer." → After "Offline-first apps keep users longer [要確認: 誰の調査か]."
- 出典: [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)。証拠の強さ: 中

## チャットとツールの残骸

### common-tool-residue: 生成ツールの出典トークンの残り

```lexicon
common-tool-residue: contentReference\[oaicite:\d+\]|\boaicite\b|\boai_citation\b|(?:\bcite|\b)turn\d+(?:search|news|file|image|view|fetch)\d+\b|\u3010\d+(?::\d+)?\u2020[^\u3011\n]*\u3011|\[cite(?:_start|_end|:[ \t]*\d+(?:[ \t]*,[ \t]*\d+)*)\]|\[span_\d+\]\((?:start|end)_span\)|\bgrok_(?:card|render_citation_card_json)\b|\[(?:attached_file|web):\d+\]
```

- 種別: LEXICAL
- 兆候になる条件: 1 つでも出れば、チャットの出力を貼り付けた跡としてほぼ確実。スクリプトは URL を伏せてから検査するので、リンクに付いた `utm_source=chatgpt.com` のようなパラメータは目で確かめる。
- 残す場合: これらのトークンそのものを説明する文章（インラインコードに入れれば検出されない）。
- 直し方: 削る。出典が必要なら、元の出典を書き手に確かめて通常の形で書く。
- 例: Before "The v1 API was retired in 2023.:contentReference[oaicite:2]{index=2}" → After "The v1 API was retired in 2023."
- 出典: [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)。証拠の強さ: 強

### common-chat-leftover: 依頼した人に向けた文の残り

- 種別: JUDGMENT
- 兆候になる条件: 読み手でなく、生成を頼んだ人に向けた文が成果物に残っている。依頼への返事の前置き、前の版を見ていない読み手に向けた「修正版」「変更点」の枠付け、「案 1 / 案 2」のような複数案、書き手への助言（「提出前にこの節を消してください」）、埋め忘れのプレースホルダ、メールやフォームのように描画されない場所の Markdown 記号。決まった言い回し（"Certainly!"、「いかがでしたか」）は言語別ファイルにある。
- 残す場合: テンプレートとして配る文書のプレースホルダ。README や PR 説明のように Markdown が描画される場所の記号。
- 直し方: 削る。プレースホルダは推測で埋めず、書き手に聞く。
- 例: Before "Here's a more concise version: Hi Dana, thanks for the note. I can meet on Tuesday." → After "Hi Dana, thanks for the note. I can meet on Tuesday."
- 出典: [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)、[Pangram](https://www.pangram.com/signs-of-ai-writing)。証拠の強さ: 強

## ジャンル別の例外

同じ形でも、ジャンルによっては慣例として正しい。ジャンルが分からないときは em dash、並列、三つ組を兆候として弱めに扱う。ユーザーや組織のスタイルガイドがあればそちらに従う。

| ジャンル | 兆候に見えるが慣例のもの | それでも直すもの |
|---|---|---|
| レジュメ | 動詞で始まる箇条書き、主語の省略、形式の一貫性、成果の数字、スキル欄のカテゴリ名の太字、日付範囲の en dash、見出しの区切りのダッシュ、求人票のキーワードの繰り返し | 抽象的な自己評価（common-generic-claim）、評価の言い回しの使い回し（common-self-echo）、成果の部分まで揃った骨格（common-same-shape）、意義の付け足し、求人に合わせて盛った肩書や経歴（事実を書き手に確かめる） |
| メール | 定型の挨拶と結び（「お世話になっております」、"Thanks for reaching out"）、短い段落 | 見出し、太字、箇条書き（common-list-for-prose）、依頼した人向けの前置き（common-chat-leftover）、カジュアルな文の em dash、レジュメなど別の文書からの言い回しの流用 |
| 技術文書・README | 見出し、表、並列構文の箇条書き、同じ用語の繰り返し、手順の揃った形、Note などのラベル、Markdown | 宣伝調（common-inflated-significance）、既存の文書にない見出しの絵文字、1 項目だけの箇条書き、中身のない見出し、節の最後の言い直し |
| 記事・ブログ | 論旨としての対比や意義づけ、スタイルガイドに従う em dash、ニュースの要約のリード | ほぼすべての観点。特に曖昧な帰属、どれも同じ口調の引用、まとめの言い直し |
| PR 説明・コミットメッセージ | Markdown、組織の PR テンプレート（概要やテスト計画の節）、チェックリストの完了印 | 差分にない変更を書いた説明（差分と突き合わせる）、「改善した」だけの説明、飾りの絵文字、形だけの三つ組 |
| コードコメント | 短い断片、主語の省略、命令形、TODO | コードの言い換え、変更の経緯（「以前は〜だった」）、意義の主張、依頼した人向けの文 |
| UI 文言・マーケティング | 断片、自問自答（"Ready to start? Create an account."）、動詞で始める文、三つ組、極端な短さ | 読み手に関係ない誇張、チャットの残骸 |

出典: [Harvard College Guide to Creating a Strong Resume](https://careerservices.fas.harvard.edu/resources/create-a-strong-resume/)、[Google developer documentation style guide: Lists](https://developers.google.com/style/lists)、[Microsoft Writing Style Guide](https://learn.microsoft.com/en-us/style-guide/top-10-tips-style-voice)、[Best practices for writing code comments](https://stackoverflow.blog/2021/12/23/best-practices-for-writing-code-comments/)、[Gong et al. 2026（エージェントが書いた PR の説明と差分の食い違い）](https://arxiv.org/abs/2601.04886)、[AP vs. Chicago](https://apvschicago.com/2011/05/em-dashes-and-ellipses-closed-or-spaced.html)

## 直しすぎの兆候

書き換えは文章を悪くすることがある。書き換えたあとにスクリプトをもう一度かけ、次の形が増えていないか確かめる。

- 同義語の言い換え（synonym cycling）: 繰り返しを避けて用語や主語を別の語に替えると、読み手は別のものを指すのかと迷う。契約書や仕様では解釈の争いの種になる。用語は同じ語で繰り返し、評価の言い回しの繰り返しは具体的な事実で直す。
- ぶつ切りの文: 長い文を一律に分けると短い断片が並ぶ。分けるのは、1 文が本当に 2 つのことを言っている場合だけにする。
- 限定表現（hedge）や精度の脱落: 「約」「may」「〜の可能性がある」は書き手の確度を表す。削ると主張が強くなり、意味が変わる。数字の丸めや、条件や範囲の省略も同じ。削ってよいのは、どの主張にも付く中身のない断り書きだけ。
- わざとくだけさせる: 口語、スラング、誤字、文体の混在を足しても文章は良くならず、レジュメやビジネスメールでは信用を落とす。目指すのは、そのジャンルの人間が書く文。
- 別の揃った型: 三つ組を二つ組に揃える、箇条書きを全部同じ長さにする、em dash を全部コロンに替える。形の均一さが残る。
- 事実の追加: 具体的にするために数字、名前、体験を補うのは捏造。`[要確認: ...]` で書き手に聞く。
- 人らしい具体の消去: 半端な数字、変わった出来事、非母語話者らしいが正しい言い回しは、人が書いた証拠。整えて一般的な文にしない。

文法の正しさ、硬い語や凝った語彙そのもの、中立的な口調、単独の接続詞、曲がった引用符（OS やワープロが自動で変える）、AI 判定ツールのスコアは、兆候として扱わない。どれも人の文章に普通にあり、単独で直す理由にならない。

出典: [Masrour et al. 2025（humanizer の監査。検出器ベンダーによる研究）](https://arxiv.org/abs/2501.03437)、[Federal Plain Language Guidelines](https://webarchive.library.unt.edu/web/20120915090140mp_/http:/www.plainlanguage.gov/howto/guidelines/FederalPLGuidelines/writeTermUse.cfm)、[Adams on Contract Drafting](https://www.adamsdrafting.com/more-industry-wide-elegant-variation-amendments-in-writing/)、[Hyland 1996](https://academic.oup.com/applij/article-abstract/17/4/433/198756)、[Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)、[Russell et al. 2025](https://arxiv.org/abs/2501.15654)、[Liang et al. 2023](https://arxiv.org/abs/2304.02819)

## スクリプト出力の読み方

`detect_tells.py <file>` は次のキーを持つ JSON を返す。コードブロックと引用行（`>` で始まる行）は検査せず、インラインコードと URL は伏せてから検査する。文中の「」や "" で囲んだ引用は伏せないので、その中の候補は引用として残す。どの値も候補で、直すかどうかは各項目の「兆候になる条件」で決める。

- `lang`: 使った言語。指定がなければ文字種から判定する。日英が混ざる文章は `--lang ja,en` のように両方を指定すると、両方のパターンが当たる（文と語は先頭の言語で数える）。
- `hits`: 一致ごとに `id`、`source`（`common` か言語）、`line`、`column`（1 始まり）、`match`（一致した文字列）、`context`（その行全体）。lexicon prose の観点は見出し行に当てない。同じ id の一致は先頭の一部だけ返る。
- `counts`: id ごとの一致の総数。1 件はたいてい偶然。件数を文書の長さ（`metrics.words`、`metrics.chars`）と比べて読む。
- `repeated_phrases`: 2 回以上出る言い回しの `phrase`、`count`、`lines`。評価や決め台詞の繰り返しは兆候（common-self-echo）で、用語、製品名、固有名詞の繰り返しは必要なもの。見出し行は数えない。英語は 3 語未満の句と機能語（the、of など）だけの句、日本語は 6 文字未満の句、数字を含む句、英数字だけの句を数えないので、リストが空でも短い決め台詞の繰り返しはありうる。
- `metrics`: 文書全体の値。単独では判定せず、ほかの候補と合わせて読む。
  - `words`、`chars`: 見出しとコードを除いた本文の語数と、空白を除いた文字数。`counts` の件数を 1,000 語（日本語は 1,000 字）あたりに直すときに使う。
  - `sentences`: 数えた文の数。行と句読点で区切るので、箇条書きは 1 項目が 1 文になる。少ないとほかの値がぶれる。
  - `sentence_length_cv`: 文の長さ（英語は語数、日本語は空白を除いた文字数）の標準偏差を平均で割った値。低いほど長さが揃っている（common-uniform-rhythm）。閾値はないので、同じ書き手や同じジャンルの人間の文章と比べる。
  - `commas_per_sentence`: 1 文あたりのカンマ（日本語は読点）の数。AI の文章で多いか少ないかの向きが言語で違うので、読み方は言語別ファイルに従う。
  - `bullet_line_ratio`: 見出しを除く本文の行のうち、箇条書きの行（`-` `*` `+` か番号で始まる行。「・」は数えない）の割合（common-list-for-prose）。
  - `bold_count`: 本文の太字の数（common-bold-overuse）。
- `judgment_checks`: common と対象の言語で、種別が JUDGMENT の観点の `id` と見出し。正規表現では拾えないので、各項目を読んで全文から探す。

`detect_tells.py --compare <before> <after>` は、書き換えで消えた要素を `removed`、増えた要素を `added` に、それぞれ `numbers`、`urls`、`names`、`negations`、`hedges` に分けて返す。次の順に見る。

1. `added.numbers`: 増えた数字は捏造の疑いとして最初に確かめる。原文か会話にない数字は消すか、`[要確認]` にして書き手に聞く。増えた `names` と `urls` も同じ。
2. `removed.negations` と `removed.hedges`: 否定や限定表現が消えたら意味が変わっている。書き手が同意していなければ戻す。英語の `hedges` には may のほか can、should、must、some なども入り、日本語は「約」「数名」「可能性」「かもしれない」「主に」などを拾う。
3. `removed.numbers`、`removed.names`、`removed.urls`: 言い直しの重複を削ったなど、意図した削除かを確かめ、対応表に理由を書く。

`names` は大文字や文字種から推定するので、ふつうの語も混ざる。数えるのは要素の個数なので、同じ語が文の中で位置を変えただけの変化は出ない。

## 時期で変わる傾向（確認日: 2026-09）

どの語や記号が多用されるかはモデルと時期で入れ替わる。以下は確認日時点の観察で、項目の判断はこれに頼りすぎない。

- em dash: ChatGPT の応答で em dash を含むものは 2024 年に 1 割未満、2025 年夏に半分超だった（[Washington Post 2025-11](https://www.washingtonpost.com/technology/interactive/2025/how-detect-chatgpt-em-dash/)）。OpenAI は GPT-5.1 で抑えた。2026-07 の The Economist の分析では、プロの書き手より多く使うのは Claude だけで、ChatGPT はどの書き手より少なかった（有料記事のため [Daring Fireball](https://daringfireball.net/linked/2026/08/11/economist-ai-writing) と Wikipedia 経由の二次情報）。Wikipedia は 2026-09 時点でこの兆候を過去の兆候に移すか検討している（[Wikipedia](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)）。今は Claude の下書きと、このスキル自身の書き換えで特に確かめる。
- 絵文字: 2025-07 の ChatGPT の応答の 70% に絵文字が 1 つ以上あり、✅ は人の 11 倍だった（Washington Post）。Wikipedia によると記事の中では減っている。
- 太字、箇条書き、Markdown: 検出器ベンダーの計測（日付の記載なし）で、太字は人の約 43 倍、Markdown 全体で約 12 倍、箇条書きは約 9 倍（[Pangram](https://www.pangram.com/signs-of-ai-writing)）。Qiita の技術記事を 2019〜2022 年の平均と 2026-08 で比べた計測では、1,000 字あたりの太字が 1.26 から 3.83、箇条書きの行の割合が 8.9% から 16.4%、ダッシュが 0.043 から 0.426 に増えた（[逆瀬川 2026-09](https://nyosegawa.com/posts/qiita-writing-before-after-ai/)。増えた理由を AI と特定してはいない）。
- 文の長さ: 同じ Qiita の計測で文長の変動係数は 0.609 から 0.535 に下がった（揃う方向）。一方 The Economist（2026-07）は、AI の文章では長い文が続いて短い文で区切られることが少ないと報告しており、短い断片を連ねる癖を挙げる実務者の観察（[tropes.fyi](https://tropes.fyi/directory)）とは向きが違う。
- カンマと読点: 日本語の技術記事では 1 文あたりの読点が 0.63 から 0.95 に増えた（Qiita の計測）。英語では LLM の方がカンマやセミコロンが少ないという報告がある（The Economist、二次情報）。
- 否定の対比: 2025-07 の ChatGPT の会話の 6% に "not just X, but Y" の形があった（Washington Post）。一部のモデルでは "It's not X, it's Y" の形が人の 6.3 倍だった（[Antislop](https://arxiv.org/abs/2510.15061)）。Grok は "Y rather than X" の形に偏る（Wikipedia）。
- まとめ: "In conclusion" のような明示の締めは、Wikipedia では古いモデルの兆候に移った。言い直しで終える癖そのものは、2025 年のモデルの文章でも専門家が手がかりにしている（[Russell et al. 2025](https://arxiv.org/abs/2501.15654)）。
- 同義語の言い換え: 古いモデルの repetition penalty から来た過去の兆候とされる（Wikipedia）。2025 年にも大学教員の観察がある（[Belcher 2025](https://wendybelcher.com/writing-advice/10-ways-ai-is-ruining-your-students-writing/)）。2026 年の Claude で下書きした実文書の監査では、逆に同じ言い回しの使い回しが目立った。
- モデルの差: ChatGPT と Grok は意義や大きな流れを語りがちで、Gemini と Claude は簡潔寄り（Wikipedia）。
