# 英語の観点

英語の文章に出る AI の癖のうち、英語の語彙や文型に依存するもの（多用される語、定型句、", highlighting ..." のような分詞の付け足し、"not just X, but Y" の言い回し、英語のチャットの残骸）と、英語で残すべきジャンルの慣習をまとめる。否定の対比や三点セットのように言語をまたぐ構造の説明と直し方の原則は common.md にあり、ここには英語での現れ方と検出パターンだけを書く。どの項目も 1 回の出現はたいてい偶然で、直す対象になるのは「兆候になる条件」を満たすときだけ。直すときは語を同義語に替えず、原文にある具体的な事実を前に出す。

## 目次

- 語彙: en-ai-vocabulary, en-common-marker-density, en-promotional-words, en-self-evaluation-phrases
- 定型句: en-significance-phrases, en-signposting, en-generic-opener, en-summary-opener, en-vague-attribution, en-change-summary
- 文の形: en-participial-significance, en-negative-parallelism, en-copula-and-stiff-verbs, en-abstract-triad, en-reveal-label
- 残骸と定型文: en-chat-leftovers, en-author-instructions, en-email-stock-phrases
- 英語で残すもの
- 時期で変わる傾向（確認日: 2026-09）

## 語彙

### en-ai-vocabulary: LLM が多用する語と慣用句

```lexicon
en-ai-vocabulary: \b(?:delv(?:e|es|ed|ing)|showcas(?:e|es|ed|ing)|tapestry|interplay|intricac(?:y|ies)|intricate(?:ly)?|meticulous(?:ly)?|garner(?:s|ed|ing)?|bolster(?:s|ed|ing)?|multifaceted|unwavering|camaraderie|palpable|amidst|commendable|noteworthy|elucidat(?:e|es|ed|ing)|pivotal)\b
en-ai-vocabulary-2: \bunderscor(?:e|es|ed|ing)\s+(?:the|a|an|how|that|its|their|this|these|our|what|why)\b|\b(?:in|into|within) the realm of\b|\bresonat(?:e|es|ed|ing) (?:with|deeply)\b|\bnavigat(?:e|es|ed|ing) (?:the )?(?:complexities|intricacies|challenges|landscape)\b|\bembark(?:s|ed|ing)? on\b|\bunlock(?:s|ed|ing)? (?:the |its |their )?(?:full )?(?:potential|power)\b|\bharness(?:es|ed|ing)? the power\b|\ba beacon of\b
```

- 種別: LEXICAL
- 兆候になる条件: 1 語なら偶然のことが多い。1 段落に 2 語以上、または文書全体で何度も出るとき。どれも具体的なことを言わずに文を重要そうに見せる語なので、その文から語を抜いて中身が残るかで判断する。小説では普通に使う語もあり、ジャンルに合わない所に出たときが兆候
- 残す場合: 引用、固有名詞（Realm というデータベースなど）、"underscore" が記号 `_` を指す場合、機械の軸を指す "pivot"、その語でしか言えない専門的な用法
- 直し方: 同義語に替えない（delve を explore にしても文の空疎さは残る）。語が飾っている具体的なことを主語と動詞で言う。具体的なことが原文になければ、文ごと削るか書き手に聞く
- 例: Before "The report delves into the intricate interplay between pricing and churn across the two plans." → After "The report compares churn across the two plans."
- 出典: 強。Kobak et al. 2025 https://www.science.org/doi/10.1126/sciadv.adt3813 / Juzek & Ward 2025 https://arxiv.org/abs/2412.11385 / Reinhart et al. 2025 https://www.pnas.org/doi/10.1073/pnas.2422455122 / Liang et al. 2024 https://arxiv.org/abs/2403.07183 / https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing

### en-common-marker-density: 普通の語の偏り

```lexicon
en-common-marker-density: \b(?:additionally|crucial(?:ly)?|comprehensive|enhanc(?:e|es|ed|ing|ement)|notably|robust|seamless(?:ly)?|leverag(?:e|es|ed|ing)|foster(?:s|ed|ing)?|valuable|vital|innovative|streamlin(?:e|es|ed|ing)|align(?:s|ed)? with)\b
```

- 種別: METRIC
- 兆候になる条件: 個々のヒットは直さない。見るのはスクリプトの counts にあるこの id の件数で、metrics の words（本文の語数）に対して 1,000 語あたり 2 件を超えるとき（人が書いた技術文書と百科事典の記事で測ると 0.5 件以下だった）、または en-ai-vocabulary と同じ段落に集まるときだけ
- 残す場合: 学術論文や査読の "robust" "comprehensive"、統計や工学の用語としての "robust"、金融の "leverage"、単独の "Additionally"、固有名詞（社名や製品名）。固有名詞の一致は件数から引いて密度を見る
- 直し方: 件数が多いときは、評価の語（crucial, valuable, robust）を削って残る事実で文が成り立つかを見る。接続詞を全部消すと文がぶつ切りになるので、つなぎの語は残してよい
- 例: Before "Additionally, the robust new pipeline seamlessly enhances data quality by dropping rows with missing IDs." → After "The new pipeline drops rows with missing IDs."
- 出典: 中（語ごとには弱い）。Kobak et al. 2025 https://www.science.org/doi/10.1126/sciadv.adt3813 / Liang et al. 2024 https://arxiv.org/abs/2403.07183 / https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing

### en-promotional-words: 宣伝や旅行案内の語

```lexicon
en-promotional-words: \bboast(?:s|ed|ing)?\b|\bnestled\b|\bin the heart of\b|\bbreathtaking\b|\bstunning\b|\bvibrant\b|\brenowned\b|\bgroundbreaking\b|\bcaptivat(?:e|es|ed|ing)\b|\bexemplif(?:y|ies|ied)\b|\brich (?:history|heritage|cultural heritage)\b|\bnatural beauty\b|\bdiverse (?:array|range) of\b|\bcommitment to (?:excellence|quality|innovation)\b
```

- 種別: LEXICAL
- 兆候になる条件: 宣伝が目的でない文章（経歴、技術文書、記事の地の文）に出るとき。話題が変わっても同じ語が出るとき。新しいモデルは露骨な最上級を避け、平凡な事実を控えめに持ち上げるので、語がなくても common.md の宣伝調の項目で全体の口調を見る
- 残す場合: 広告コピーや観光案内など、宣伝がジャンルの役割である文章。書き手自身の評価として書かれた感想
- 直し方: 形容詞を、確かめられる事実（場所や数など）に替えるか削る
- 例: Before "Nestled in the heart of the old town, the library boasts a stunning reading room with a glass roof." → After "The library is in the old town. Its reading room has a glass roof."
- 出典: 中。https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing / Reinhart et al. 2025 https://www.pnas.org/doi/10.1073/pnas.2422455122

### en-self-evaluation-phrases: 自己評価の決まり文句と抽象名詞

```lexicon
en-self-evaluation-phrases: \b(?:results|detail)[- ](?:driven|oriented)\b|\bself[- ]starter\b|\bgo[- ]getter\b|\bteam player\b|\bproven track record\b|\bpassionate about\b|\bthink outside the box\b|\bhit the ground running\b|\bfast[- ]paced environment\b|\bhands[- ]on (?:senior|leader|engineer|manager|developer)\b|\b(?:hold|holds|held|holding|set|sets|setting) (?:a |the )?high bar\b
en-self-evaluation-phrases-2: \bat scale\b|\bend[- ]to[- ]end\b(?!\s*(?:test|encrypt|latenc|delay))|\b(?:built|build|builds|building|laid|lay|laying|established|establishing) (?:the |a |its |their |our |my )?(?:[\w-]+ ){0,3}foundations?\b|\bsingle source of truth\b
```

- 種別: LEXICAL
- 兆候になる条件: レジュメやカバーレターで、仕事をどう評価すべきかを言うだけで何をしたかを言わないとき。すぐ隣に具体的な事実（規模の数字、作ったものの名前）があるのに抽象名詞で前置きしているときは特に強い。同じ語（foundation、end to end など）が文書内で繰り返されるときは common.md の繰り返しの項目と合わせて見る
- 残す場合: 求人票の必須キーワードとして求められている語。"end-to-end tests" のような技術用語。規模の数字を言い換えずに添えている "at scale"
- 直し方: 抽象名詞や決まり文句を消し、隣にある具体的な項目を先頭に出す。具体的な項目がなければ作らずに書き手に聞く
- 例: Before "Results-driven engineer who built the team's testing foundation: contract tests for 30 services." → After "Added contract tests to 30 services."
- 出典: 弱（作成時に行った実文書（非公開）の監査で観測）。Homegardner, Forbes 2025 https://www.forbes.com/councils/forbescoachescouncil/2025/08/07/how-recruiters-can-tell-you-used-ai-on-your-resume-and-why-it-matters/ / Belcher 2025 https://wendybelcher.com/writing-advice/10-ways-ai-is-ruining-your-students-writing/

## 定型句

### en-significance-phrases: 意義・転換点・遺産を言う定型句

```lexicon
en-significance-phrases: \b(?:a|an)\s+(?:crucial|vital|key|significant|critical|instrumental|central)\s+(?:role|moment|milestone|turning point)\b|\btestament to\b|\bindelible mark\b|\bdeeply rooted\b|\b(?:set|sets|setting) the stage for\b|\bpav(?:e|es|ed|ing) the way for\b|\bmark(?:s|ed|ing)? a (?:pivotal|significant|major|key) (?:moment|shift|step|milestone|turning point)\b|\breflect(?:s|ed|ing)? (?:a |the )?broader\b|\b(?:ever-?evolving|rapidly evolving|evolving|changing) landscape\b
en-significance-phrases-2: \b(?:this|these|which) (?:highlights|underlines|speaks to) (?:the (?:importance|need|value|role|significance|potential|power)|how|why|its|their|a (?:broader|growing|deeper))\b|\bserves as a (?:reminder|testament)\b
en-significance-phrases-3: \bdespite (?:these|its|their|this|such) (?:challenges|setbacks|limitations|obstacles)\b|\bfac(?:e|es|ed|ing) (?:several|numerous|many|various|significant) challenges\b|\bfuture (?:outlook|prospects)\b|\bchallenges and (?:future|opportunities|legacy)\b
```

- 種別: LEXICAL
- 兆候になる条件: 平凡な事実のあとに、出典のない意義づけが付くとき（common.md の意義の強調の項目）。"This highlights ..." のように人ではなく文章やデータを主語にして意義を言う形も同じ仲間。-3 は「困難に直面するが、それでも」と展望で締める記事の型で、課題に触れること自体は兆候ではない
- 残す場合: 意義を論じることが目的の文章で、誰がどう評価したかの出典があるとき。論文の "these results highlight" のように分野の慣習になっている言い方
- 直し方: 意義づけを削って事実だけを残す。意義を言う必要があれば、評価した人と根拠を書く
- 例: Before "The bridge opened in spring, a testament to the town's resolve, and it set the stage for the two bus routes that now cross it." → After "The bridge opened in spring, and two bus routes now cross it."
- 出典: 中。https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing / Russell et al. 2025 https://arxiv.org/abs/2501.15654 / Belcher 2025 https://wendybelcher.com/writing-advice/10-ways-ai-is-ruining-your-students-writing/

### en-signposting: 注意書きと前置きの定型句

```lexicon
en-signposting: \b(?:important|crucial|essential|worth|vital) (?:to note|noting|to remember|to mention|mentioning|to keep in mind|to highlight|highlighting)\b
en-signposting-2: \blet(?:'s|’s| us) (?:dive|delve) (?:in|into|deeper)\b
```

- 種別: LEXICAL
- 兆候になる条件: 中身の前に「注意すべきことに」と予告を置き、その後の内容が注意書きでなくても成り立つとき。短い文章に複数あるとき
- 残す場合: 前置きを外すと警告だと伝わらない箇所（データが消える操作の前の注意など）。長いマニュアルの冒頭の案内
- 直し方: 前置きを削って中身から書く。中身がなければ文ごと削る
- 例: Before "It's worth noting that the cache is cleared on every deploy." → After "The cache is cleared on every deploy."
- 出典: 中。https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing / Russell et al. 2025 https://arxiv.org/abs/2501.15654 / Pangram Labs https://www.pangram.com/signs-of-ai-writing

### en-generic-opener: 時代を語る書き出し

```lexicon
en-generic-opener: \bin today(?:'s|’s) (?:fast-paced|digital|ever-changing|rapidly (?:changing|evolving)|modern|competitive|interconnected)(?: [\w-]+)? (?:world|age|landscape|era|environment|market)\b|\bin (?:an|the) (?:era|age) (?:of|where|when)\b|\bin an increasingly \w+ world\b
```

- 種別: LEXICAL
- 兆候になる条件: 文書や段落の書き出しにあり、続く内容がどの時代にも当てはまるとき。書き出しを消しても後ろの文が困らないなら兆候
- 残す場合: 時代の変化そのものが主題で、その変化を具体的に述べている文章
- 直し方: 書き出しを削り、2 文目以降の具体的な話から始める
- 例: Before "In today's fast-paced digital world, teams need faster feedback. Our CLI runs the test suite in parallel." → After "Our CLI runs the test suite in parallel."
- 出典: 中。Pangram Labs https://www.pangram.com/signs-of-ai-writing / Russell et al. 2025 https://arxiv.org/abs/2501.15654

### en-summary-opener: まとめの書き出し

```lexicon
en-summary-opener: (?:^\s*(?:[-*]\s+)?|[.!?]\s+)(?:in (?:summary|conclusion|essence)|overall|ultimately|all in all|to sum up)\s*[,:]
```

- 種別: LEXICAL
- 兆候になる条件: 短い文章の最後の段落や、bullet の最後の文がこの句で始まり、前に書いたことを言い直すとき（common.md のまとめの言い直しの項目）。すべての節の終わりにあるとき
- 残す場合: 報告書の executive summary、論文の conclusion など、要約が役割の箇所。前の内容を踏まえて新しい判断を述べる "Overall, we recommend ..."
- 直し方: 言い直しの文を削り、最後の具体的な事実か次の行動で終える
- 例: Before "Incidents fell from nine to two after the migration. Overall, the migration was a success that improved reliability." → After "Incidents fell from nine to two after the migration."
- 出典: 中。https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing / Russell et al. 2025 https://arxiv.org/abs/2501.15654

### en-vague-attribution: 名前のない権威

```lexicon
en-vague-attribution: \b(?:experts|observers|critics|analysts|commentators|industry (?:experts|observers|reports|insiders))\s+(?:argue|say|note|have noted|suggest|believe|point out|agree|contend)\b|\b(?:is|are|was|were|remains?) widely (?:regarded|considered|recognized|recognised|seen|viewed|acknowledged) as\b|\bsome (?:critics|experts|observers|scholars) (?:argue|say|note|suggest|contend)\b
```

- 種別: LEXICAL
- 兆候になる条件: 誰の意見かを特定できない書き方で主張に重みを付けているとき。出典が 1 つしかないのに "experts" と複数にしているとき
- 残す場合: 直後に具体的な出典が続くとき。報道で匿名の情報源を明示して扱う場合
- 直し方: 出典があれば名前と何を示したかを書く。なければ主張ごと削る。出典を作らない
- 例: Before "Experts argue the new layout is easier to read, as a usability study of the help center found." → After "A usability study of the help center found the new layout easier to read."
- 出典: 中。https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing

### en-change-summary: 変更内容を言わない変更の説明

```lexicon
en-change-summary: \b(?:improv|enhanc|refin|streamlin)(?:e|ed|es|ing)\s+(?:the\s+)?(?:overall\s+)?(?:clarity|readability|flow|consistency|maintainability|quality|structure)\b|\bwhile (?:preserving|retaining|maintaining|keeping)\s+(?:the\s+)?(?:original|existing|core|overall)\b|\bensur(?:e|ed|es|ing)\s+(?:that\s+)?(?:consistency|clarity|compliance|robustness|accuracy)\b|\bfor (?:better|improved|enhanced|greater) (?:clarity|readability|maintainability|consistency)\b
```

- 種別: LEXICAL
- 兆候になる条件: コミットメッセージ、PR 説明、「何を直したか」のメモで、具体的な変更の代わりに「読みやすくした」「一貫性を保った」と書くとき。変えていないものにわざわざ触れるとき。説明にある変更が diff にないときは癖ではなく誤りなので、diff と突き合わせて確かめる
- 残す場合: 挙動を変えないことが変更の目的で、それを読み手が知る必要があるとき（リファクタリングの "no behavior change"）
- 直し方: 何をどう変えたかを具体的に並べる。形容詞と "while preserving" の節は、保持が目的でない限り削る
- 例: Before "Refactored the parser by splitting parse() into tokenize() and build_tree(), improving readability while preserving the original behavior." → After "Split parse() into tokenize() and build_tree(). No behavior change."
- 出典: 中。https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing / Gong et al. 2026 https://arxiv.org/abs/2601.04886

## 文の形

### en-participial-significance: 文末の分詞による意義の付け足し

```lexicon
en-participial-significance: ,\s+(?:thereby\s+|further\s+|ultimately\s+|thus\s+)?(?:highlighting|underscoring|emphasi[sz]ing|showcasing|reflecting|symboli[sz]ing|ensuring|fostering|cultivating|enhancing|contributing to|solidifying|reinforcing|cementing|paving the way|setting the stage|marking|signall?ing|embodying|demonstrating|illustrating|underlining)\b
en-participial-significance-2: ,\s+(?:resulting in|leading to)\b
```

- 種別: LEXICAL
- 兆候になる条件: 事実の文の後ろに ", ensuring ..." ", highlighting ..." を付けて、測っていない効果や意義を主張するとき（common.md の文末の意義の付け足しの項目）。-2 の ", resulting in ..." は 1 回なら普通の英語で、隣り合う bullet が同じ形で終わるときに兆候になる
- 残す場合: 分詞句が情報を運んでいるとき（", covering sign-up, billing and refunds"）。小説の描写。効果が本当に測られていて数字が続く ", resulting in a 40% drop in timeouts"
- 直し方: 付け足しを削る。原文の別の箇所に測った効果があれば、分詞ではなく独立した文か節で書く。効果の数字を作らない
- 例: Before "Moved the job queue to a managed service, ensuring reliability and fostering developer productivity." → After "Moved the job queue to a managed service."
- 出典: 強。Reinhart et al. 2025 https://www.pnas.org/doi/10.1073/pnas.2422455122 / https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing / Kobak et al. 2025 https://www.science.org/doi/10.1126/sciadv.adt3813

### en-negative-parallelism: 英語の否定の対比

```lexicon
en-negative-parallelism: (?:\bnot|n't|n’t)\s+(?:just|only|merely|simply)\b[^.;:!?]{1,80}?(?:\bbut\b(?!\s+also\b)|[,;\u2013\u2014]\s*(?:it|they|this|that)(?:'s|’s|\s+is|\s+are|'re|’re)\b)
en-negative-parallelism-2: (?<!\bif )(?<!\bwhen )(?<!\bunless )\b(?:it|this|that)(?:'s|’s|\s+is|\s+was)\s+not\b[^.;!?]{1,60}?[;,.\u2013\u2014]\s*(?:it|this|that)(?:'s|’s|\s+is|\s+was)\b|\b(?:it|this|that) (?:isn't|isn’t|wasn't|wasn’t)\b[^.;!?]{1,60}?[;,.\u2013\u2014]\s*(?:it|this|that)(?:'s|’s|\s+is|\s+was)\b
en-negative-parallelism-3: \bno\s+\w+(?:\s+\w+)?,\s+no\s+\w+(?:\s+\w+)?,?\s+(?:just|only)\b|\bnot about\b[^.]{1,60}?\b(?:it's|it’s|it is)\s+about\b|\bless about\b[^.]{1,60}?\bmore about\b
```

- 種別: LEXICAL
- 兆候になる条件: 誰も主張していない X を立てて打ち消し、Y を持ち上げるとき（common.md の否定の対比の項目）。"not only X but also Y" は普通の英語なので検出しない。"Y rather than X" も同じ型だが、普通の比較で頻繁に使うので検出はせず、読むときに判断する
- 残す場合: 読み手が実際に X だと思っている誤解を正す文。技術文書の指示（"use a lock rather than a retry loop"）。トラブルシュートで原因を切り分ける文
- 直し方: X を消して Y を具体的に言う。対比を自問自答やコロンの種明かしに言い換えない（別の癖になる）
- 例: Before "The checklist is not just a document, but a script that runs before every release." → After "The checklist is a script that runs before every release."
- 出典: 強。Paech et al. 2025 https://arxiv.org/abs/2510.15061 / Merrill et al., Washington Post 2025 https://www.washingtonpost.com/technology/interactive/2025/how-detect-chatgpt-em-dash/ / https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing / Russell et al. 2025 https://arxiv.org/abs/2501.15654

### en-copula-and-stiff-verbs: is/has と平易な動詞の言い換え

```lexicon
en-copula-and-stiff-verbs: \b(?:serves|stands) as (?:a|an|the|our|its|their|his|her|one of)\b
en-copula-and-stiff-verbs-2: \butili[sz](?:e|es|ed|ing|ation)\b|\bcommenc(?:e|es|ed|ing)\b|\bendeavou?r(?:s|ed|ing)?\b
```

- 種別: LEXICAL
- 兆候になる条件: is/has で足りる所に "serves as" "stands as" を使うとき、use / start / try で足りる所に utilize / commence / endeavor を使うとき。1 文書に何度も出るとき。LLM に推敲させると is が serves as に替わりやすいので、書き換え後の文章にも出ていないか見る
- 残す場合: 過去の役職（"served as chair"）、法律や学術の文体、機能を表す技術文書の "serves as the entry point" のように役割を説明する必要がある文
- 直し方: is/has と平易な動詞に戻す
- 例: Before "The dashboard serves as the team's main view and utilizes cached queries." → After "The dashboard is the team's main view and uses cached queries."
- 出典: 中。https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing / Geng & Trotta 2024 https://arxiv.org/abs/2404.08627

### en-abstract-triad: 抽象語の三点セット

```lexicon
en-abstract-triad: \b[a-z]+(?:ity|ness|tion|sion|ment|ance|ence|ancy|ency|ship)s?,\s+[a-z]+(?:ity|ness|tion|sion|ment|ance|ence|ancy|ency|ship)s?,?\s+(?:and|or)\s+[a-z]+(?:ity|ness|tion|sion|ment|ance|ence|ancy|ency|ship)s?\b
en-abstract-triad-2: \b[a-z]+(?:ive|ful|ous|able|ible|ient|ent|ant)(?:ly)?,\s+[a-z]+(?:ive|ful|ous|able|ible|ient|ent|ant)(?:ly)?,?\s+(?:and|or)\s+[a-z-]+(?:ive|ful|ous|able|ible|ient|ent|ant|oriented|driven)(?:ly)?\b
```

- 種別: LEXICAL
- 兆候になる条件: 抽象名詞や評価の形容詞をちょうど 3 つ並べ、網羅的に見せているとき（common.md の三点セットの項目）。1 文や 1 bullet に三つ組が複数あるとき、文書中の多くの列挙がちょうど 3 項のときに強くなる。このパターンは語尾で抽象語を拾うので、具体的な列挙に当たることもある
- 残す場合: 実在する項目の列挙（機能名やツール名）と、本当に 3 つある事柄。スピーチや広告の修辞
- 直し方: 実際に言える項目だけ残す。原文にある具体的な事実が 1 つあれば、それで三つ組を置き換える。4 項に増やして型を崩すことはしない
- 例: Before "The redesign focused on scalability, reliability, and maintainability by moving uploads to a queue." → After "The redesign moved uploads to a queue."
- 出典: 中（作成時に行った実文書（非公開）の監査で抽象語の三つ組を観測）。https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing / Reinhart et al. 2025 https://www.pnas.org/doi/10.1073/pnas.2422455122 / Russell et al. 2025 https://arxiv.org/abs/2501.15654

### en-reveal-label: 種明かしのラベル

```lexicon
en-reveal-label: (?:^\s*(?:[-*]\s+)?|[.!?]\s+)(?:the (?:result|upshot|catch|kicker|bottom line|takeaway|secret|twist|payoff)|here(?:'s|’s| is) the (?:thing|kicker|catch|deal|twist))\s*[:?]
```

- 種別: LEXICAL
- 兆候になる条件: "The result:" "Here's the kicker:" のように、事実の前に短いラベルとコロン（または疑問符）を置いて盛り上げるとき。文書内の多くの bullet や文が「主張: 種明かし」の形で並ぶときは common.md のコロン構文の項目と合わせて見る
- 残す場合: 実験手順や FAQ の決まった見出し（"Result:" の欄）。広告や UI 文言の自問自答
- 直し方: ラベルを削り、原因と結果を 1 文でつなぐ
- 例: Before "We cached the lookups. The result: page loads dropped from 900 ms to 300 ms." → After "Caching the lookups cut page loads from 900 ms to 300 ms."
- 出典: 弱（作成時に行った実文書（非公開）の監査で、本文の約半分の bullet がコロンの種明かしの形だった）。tropes.fyi https://tropes.fyi/directory

## 残骸と定型文

### en-chat-leftovers: チャットの応答の残骸

```lexicon
en-chat-leftovers: ^\s*(?:certainly|absolutely|of course|sure thing)!
en-chat-leftovers-2: \bhere(?:'s|’s| is) (?:a|an|the|your) (?:revised|polished|updated|improved|refined|rewritten|edited|tightened|cleaner|shorter|more \w+) (?:version|draft|rewrite)\b
en-chat-leftovers-3: \b(?:i hope (?:this|that) helps|let me know if you(?:'d|’d| would) like (?:me to|any|a|another)|would you like me to|is there anything else (?:i can|you(?:'d|’d| would) like))\b
en-chat-leftovers-4: \bas an ai(?: language model| assistant)?,|\bas of my (?:last|latest) (?:knowledge|training) (?:update|cutoff)\b|\bmy (?:knowledge|training) cutoff\b|\byou(?:'re|’re| are) absolutely (?:right|correct)\b|\bgreat question\b|\bbased on the (?:information|details|text) (?:you(?:'ve|’ve| have)? )?provided\b
```

- 種別: LEXICAL
- 兆候になる条件: 成果物（メール、レジュメ、文書、PR 説明）の中に、依頼者に向けたチャットの言葉が残っているとき。成果物の冒頭と末尾に多い。ほぼ確実な兆候
- 残す場合: 本物の返信の中の "Sure," や、メールの相手に実際に申し出る "Would you like me to send the slides?"。チャットの会話そのものを記録した文章
- 直し方: 残骸を削る。削った後の文章が成り立つかだけ確かめる
- 例: Before "Certainly! Here's a polished version of your email: Hi Dana, thanks for the notes on the draft." → After "Hi Dana, thanks for the notes on the draft."
- 出典: 強。https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing / Pangram Labs https://www.pangram.com/signs-of-ai-writing / anthropics/claude-code issue #3382 https://github.com/anthropics/claude-code/issues/3382

### en-author-instructions: 書き手への指示と別案の残骸

```lexicon
en-author-instructions: \b(?:feel free to|be sure to|make sure to|don't forget to|don’t forget to) (?:customi[sz]e|tailor|adjust|tweak|personali[sz]e|replace|fill in|add your)\b|\byou (?:can|may|might want to) (?:customi[sz]e|tailor|tweak|personali[sz]e) (?:this|it|the)\b
en-author-instructions-2: ^\s*(?:[-*]\s+|\d+[.)]\s+)?(?:\*{2})?(?:more (?:formal|casual|concise|detailed)(?: version| option)?|shorter version|alternative (?:version|option))(?:\*{2})?\s*[:(]
```

- 種別: LEXICAL
- 兆候になる条件: 成果物の中に、書き手に向けた助言（「自分の数字に差し替えて」「送る前にこの節を消して」）や、同じ文の別案（"More formal:" "Shorter version:"）が並んで残っているとき
- 残す場合: テンプレートとして配ることが目的の文書。読み手が自分で調整する手順書
- 直し方: 助言を削り、別案は 1 つに決めて残す。どれを残すか決められなければ書き手に聞く
- 例: Before "Led the billing rewrite. (Feel free to tailor this bullet to the job description.)" → After "Led the billing rewrite."
- 出典: 中。https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing

### en-email-stock-phrases: メールとカバーレターの決まり文句

```lexicon
en-email-stock-phrases: \bi hope (?:this|my|the) (?:email|message|note) finds you well\b|\bi(?:'m|’m| am) writing to (?:express|inquire|apply)\b|\bi(?:'m|’m| am) (?:excited|thrilled|delighted) to (?:apply|submit)\b|\b(?:caught|captured) my (?:attention|eye|interest)\b
```

- 種別: LEXICAL
- 兆候になる条件: 短いメールで、定型の前置きが中身の前に来るとき。本文の最初と最後を同じ型の丁寧句（"I'd be glad to ..." と "I'd be happy to ..."）で挟むとき。LLM 以前からある決まり文句なので、AI の証拠ではなく、読み手が読み飛ばす文として扱う
- 残す場合: 相手や業界の慣習として求められる書き出し。挨拶の 1 文（"Thanks for reaching out."）
- 直し方: 前置きを削り、用件から書く。何に惹かれたかを言うなら、その具体的な点を書く
- 例: Before "I hope this email finds you well. I am writing to express my interest in the data engineer role." → After "I'm interested in the data engineer role."
- 出典: 中（"caught my attention" は弱、作成時に行った実文書（非公開）の監査で観測）。https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing / Homegardner, Forbes 2025 https://www.forbes.com/councils/forbescoachescouncil/2025/08/07/how-recruiters-can-tell-you-used-ai-on-your-resume-and-why-it-matters/

## 英語で残すもの

次のものは人の文章の特徴か、ジャンルの慣習なので、候補に挙がっても直さない。

- レジュメ: 主語（I）を省いて動詞で始める bullet、形式の揃った bullet、成果の数字（Harvard のレジュメガイド https://careerservices.fas.harvard.edu/resources/create-a-strong-resume/ ）。Skills 欄の太字のカテゴリ名、求人票のキーワードの繰り返し（ATS で照合されるため）、見出しの "Company — Title" の区切り、日付範囲の en dash も慣習
- メール: "Thanks for reaching out." などの挨拶、"Best," などの結び、実際に質問を受け付ける "Let me know if you have any questions."
- 技術文書: 並列の構文のリスト（Google developer documentation style guide https://developers.google.com/style/lists ）、"Note:" の注記、命令形の手順。同じ概念に同じ語を使い続けるのも規則で、同義語に言い換えると別のものに見える（Federal Plain Language Guidelines https://webarchive.library.unt.edu/web/20120915090140mp_/http:/www.plainlanguage.gov/howto/guidelines/FederalPLGuidelines/writeTermUse.cfm ）
- 学術文: may / suggest / appear to などの限定表現、主語のない受動態、名詞化、"In this paper, we ..." の予告、"robust" や "findings" などの分野の語
- 句読点: AP スタイルの前後にスペースを入れる em dash と、Chicago スタイルのスペースなしの em dash はどちらも正しい。英国式の前後にスペースを入れた en dash も挿入句のダッシュとして使う（https://apvschicago.com/2011/05/em-dashes-and-ellipses-closed-or-spaced.html ）。曲がった引用符は OS やワープロが自動で入れる。Oxford comma の有無は書き手の流儀
- 人の文章に多いもの: 飾らない is/has、wrote / used / tried などの平易な動詞、事実としての最上級（"was the first"）、very / perhaps / tends to などの限定と強調、"in order to" のような冗長な句、くだけた文章の短縮形。これらを「強い」語や言い切りに替えると AI の文体に近づく（https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing ）
- 非ネイティブの書き手の、少し変わっているが正しい言い回し。流暢で一般的な英語に均すと書き手の声が消える。AI 判定ツールは非ネイティブの英文を AI と誤判定しやすい（Liang et al. 2023 https://arxiv.org/abs/2304.02819 ）

英語で直すときの注意:

- em dash を消すとき、セミコロンに替えない。LLM はセミコロンを人より使わないので、置き換え先としては句点、カンマ、括弧の方が人の文章に近い（The Economist 2026 の二次情報）
- 受動態を機械的に能動態にしない。GPT-4o は主語のない受動態を人の約半分しか使わない（Reinhart et al. 2025）

## 時期で変わる傾向（確認日: 2026-09）

どの語や記号が多用されるかはモデルと時期で入れ替わる。上の項目の語彙が見つからないことは、AI の関与がない証拠にならない。

- 語彙の入れ替わり: Wikipedia は時期別の語を挙げている。2023 年〜2024 年中頃（GPT-4 期）は delve, tapestry, testament, intricate, meticulous, pivotal, underscore, boasts など。2024 年中頃〜2025 年中頃（GPT-4o 期）は align with, fostering, highlighting, showcasing, enhance, vibrant など。2025 年中頃以降（GPT-5 期）は emphasizing, enhance, highlighting, showcasing と、報道で取り上げられたことを強調する言い回し。delve は 2025 年に大きく減った。Grok は 2026 年も underscore を使い、"Y rather than X" の形を好む。このページ自体が最新モデルへの更新を要すると 2026-08 に注記されている（https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing ）
- ChatGPT（2025-07 時点）: 共有された会話 328,744 件の分析で、delve は約 1,000 件に 1 件まで減り、core が 5 倍に増え、modern は 8% 超のメッセージに出た。"not just X, but Y" 系は会話の 6%、絵文字は 70% のメッセージにあり、ensure, various, crucial, significant, approach は減った。em dash を含む応答は 2024 年の 1 割未満から 2025 年夏に半数超へ増えた（Merrill et al., Washington Post 2025-11 https://www.washingtonpost.com/technology/interactive/2025/how-detect-chatgpt-em-dash/ ）
- em dash: OpenAI は GPT-5.1 で em dash を抑えた。The Economist（2026-07、55,940 文）では、プロの書き手より em dash が多いのは Claude だけで、ChatGPT はどの書き手よりも少なかった（有料記事のため二次情報 https://daringfireball.net/linked/2026/08/11/economist-ai-writing ）。同じ調査で ChatGPT と Claude は "not X but Y" と三つ組も人より多かった。Wikipedia は 2026-09 に em dash を過去の兆候の一覧へ移すか検討している。一般の人の文章と比べると今も約 10 倍という検出器ベンダーの測定もある（Pangram Labs https://www.pangram.com/signs-of-ai-writing ）。基準にする人の文章で結論が変わるので、em dash は Claude の下書きと、くだけたメールで特に見る
- 引用符: ChatGPT（2025 年中頃から）と DeepSeek は曲がった引用符を使い、Gemini と Claude は通常使わない（Wikipedia）
- Claude: 語レベルのコーパス調査は見つからなかった。測られているのは em dash、否定の対比、三つ組の多さ（The Economist）で、"You're absolutely right" の多用は利用者の報告（https://github.com/anthropics/claude-code/issues/3382 ）
