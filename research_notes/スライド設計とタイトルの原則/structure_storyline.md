# デッキ全体の構成・ストーリーラインの原則（何を・どの順で・どう下書きするか）

調査日: 2026-11-15。対象はデッキ単位の構成と下書き工程。スライドタイトルの文言と視覚・チャート設計は他の調査者の担当なので、ここでは構成に関わる範囲だけ触れる。

各原則は「原則（一文）／手順・チェック項目／良い例・悪い例／出典／根拠の種類／適用範囲・反対意見」の形で書く。原則番号 P1〜P27 は全体の通し番号。根拠の種類は「実証研究」「組織規範」「個人の経験則」の3つで分類した。今回集めた中に、デッキ構成を対象にした実証研究は見つからなかった（各 Gaps 参照）。

一次資料かどうかの表記:
- 【一次】著者本人の文章・配布資料・出版社ページ・本人執筆の記事
- 【準一次】元当事者の手記
- 【二次】要約・解説記事。原典は未確認

---

## Q1. ピラミッド原則（Minto）・SCQA・空雨傘・答えファーストの具体ルールとデッキへの適用

### Takeaway
答えを最初に置き、その下に根拠をグループ化する。縦方向は「なぜ？／だから何？」でつなぎ、横方向は MECE でそろえる。導入は SCQA（または空・雨・傘）で聞き手の頭に問いを立ててから答えを出す。デッキでは、冒頭のエグゼクティブサマリーがピラミッドの頂点にあたり、各セクションが第2階層、各スライドのタイトルがキーラインになる。Minto の原著は今回直接確認できず、ルールの細部は二次資料経由になる。

### Cited Findings

#### P1. 結論を頂点に置き、根拠をその下にグループ化する（ピラミッド構造）
- **原則**: 主張（答え）を最上位に置き、それを支える根拠を下位に並べる。「データや感想より先に結論を話す」。
- **手順・チェック**:
  - 縦の論理: 下位の項目群に「だから何？（so what?）」と問うと上位の主張が出てくる。上位の主張に「なぜ？」と問うと下位の項目が答える。この往復が成り立つか確認する — [ModelThinkers: Pyramid Principle](https://modelthinkers.com/mental-model/225)【二次】, [Product Mindset: McKinsey's Pyramid Principle](https://productmindset.substack.com/p/mckinseys-pyramid-principle)【二次】
  - 横の論理: 同じ階層の項目は、まとめて上位の問いに答える。重なりも漏れもない（MECE）。並べ方は帰納（同種の根拠を並べる）か演繹（前提→前提→結論）。演繹は論証が隙なく組めるときに限る — 同上【二次】
  - 話す型は「これが結論です」→「理由は A で、B で、C だからです」→相手の了解 — [伊藤羊一, PRESIDENT Online 2018-05-29](https://president.jp/articles/-/25226)【一次: 著者本人の記事】
- **良い例／悪い例**: 悪い例は伊藤の言う「てっぺんのないピラミッド」。「A さんもいいと言っていました」「実際に数字も上がっています」で話が終わり、聞き手は「で？」となる。事例やデータを重ねても、何を読み取ればよいかが伝わらない — [伊藤羊一, PRESIDENT Online 2018](https://president.jp/articles/-/25226)
- **出典**: Barbara Minto『The Pyramid Principle』（元マッキンゼー。原著は今回未確認）。伊藤羊一（武蔵野大学アントレプレナーシップ学部 学部長）『1分で話せ』SB クリエイティブ, 2018 / PRESIDENT Online 抜粋 2018-05-29。
- **根拠の種類**: 組織規範（マッキンゼー由来）と個人の経験則。
- **適用範囲・反対意見**: 意思決定者向けの報告・提案に向く。根拠の数について、伊藤の抜粋記事には「根拠は3つ」という固定ルールはなく、「根拠は複数あることが多い」とだけある — [PRESIDENT Online 2018](https://president.jp/articles/-/25226)。MECE の考案者を Minto とする資料が多いが、出典によって記述が割れている — [検索結果の要約群, 例: Product Mindset](https://productmindset.substack.com/p/mckinseys-pyramid-principle)。

#### P2. 導入は SCQA で書き、聞き手がすでに抱いている問いに答えとして主張を出す
- **原則**: Situation（誰もが同意する前提）→ Complication（安定を崩した変化・問題）→ Question（そこから自然に出る問い）→ Answer（統括メッセージ）の順に導入を組む。
- **手順・チェック**:
  - S は「誰もが同意できる」内容か（新情報を入れない）
  - C は「聞き手の問いが1つに絞れる」ほど具体的か
  - Q は C の論理的な延長か
  - A は1文で、大胆かつ具体的か
  — [Enterprise Spectator: The Key to Compelling Communication](https://enterprisespectator.substack.com/p/the-key-to-compelling-communication)【二次】, [Think Insights: SCQA Logic](https://thinkinsights.net/index.php/strategy/scqa-logic)【二次】
- **デッキへの適用**: 本文の各キーライン（＝各セクションや各スライドの主張）は、上位から出る「なぜ？」「どうやって？」に答える。どの問いにも答えていないスライドはストーリーラインから外れている。キーラインは単語ではなく「文（主張）」で書く — 同上【二次】
- **良い例**: S「本日の打ち合わせで顧客が目的を共有した」→ C「顧客のニーズが当社の通常の提供範囲と合わない」→ Q「どうすれば顧客ニーズに応えられるか」 — [Enterprise Spectator](https://enterprisespectator.substack.com/p/the-key-to-compelling-communication)【二次】
- **出典**: Barbara Minto（SCQA はピラミッド原則の導入部の型として説明されることが多い）。
- **根拠の種類**: 組織規範・個人の経験則。
- **適用範囲・反対意見**: 導入部（1〜2枚目、エグゼクティブサマリー）の型として使う。本文全体の並びは P1 のピラミッドが決める。

#### P3. 空・雨・傘（＋HTD）で「事実・解釈・行動」をそろえる
- **原則**: 空（事実・状況）、雨（解釈）、傘（取るべき行動 = What to do）の3つをそろえる。そのうえで HTD（How to do = どう実行するか）まで考える。
- **手順・チェック**:
  - ストーリーは自由に広げ、脇道も考える
  - 複数のストーリーを想定し、よりよいものを選んでから HTD を作り込む
  - 空・雨・傘だけ作って他人に丸投げしても人は動かない
  — [PRESIDENT Online 2011-09-26（相馬留美, 中川邦夫氏の見解）](https://president.jp/articles/-/2425)【二次: 取材記事】
- **良い例／悪い例**: 記事の公開部分には具体例がない。
- **出典**: 中川邦夫（A-10 代表取締役、元マッキンゼー）。1982年に中川氏が入社した当時、マッキンゼー東京事務所にはすでにこの概念があったという — [PRESIDENT Online 2011](https://president.jp/articles/-/2425)。マッキンゼー公式の資料は見つからなかった。
- **根拠の種類**: 組織規範（コンサル内の慣用）。
- **適用範囲・反対意見**: スライド順に「事実→解釈→打ち手」を並べるときの点検に使える。同じ「空・雨・傘サイクル」という名前を、総務省統計局の手引きはデータ分析計画という別の文脈で使っている — [統計局 ガイドブック](https://www.stat.go.jp/dstart/point/guidebook/pdf/guide2025-6.pdf)。

#### P4. 各スライドは上位の問いに答える1つの仕事を持ち、答えファースト（答え→理由→証拠→示唆）で組む
- **原則**: どのスライドも、1つの問いに答えるか、1つの結論を支える。そうでないスライドは削除・統合・アペンディックス送りにする。
- **手順・チェック**: 各論点を「答え→理由→証拠→示唆・行動」の順に組んでいるか確認する（answer-first check）。ストーリーラインが事実から診断へ、診断から提言へと切り替わる箇所にはセクション区切りを入れる — [Umbrex, The Consulting Career Guide Vol.4 Ch.4.2 "Storylining and Deck Structure"](https://umbrex.com/resources/the-consulting-career-guide/storylining-and-deck-structure/)【準一次: 元コンサルのネットワークによるキャリアガイド。著者名と日付の記載なし】
- **良い例／悪い例**:
  - 観察止まり:「中小企業顧客の解約が増えた」
  - 示唆まで:「解約増の大半を占め、法人顧客より維持コストが低い中小企業顧客を、維持施策の優先対象にすべきだ」
  — [Umbrex](https://umbrex.com/resources/the-consulting-career-guide/storylining-and-deck-structure/)
- **根拠の種類**: 組織規範（コンサル業界の慣行）。
- **適用範囲・反対意見**: 意思決定のためのデッキに向く。学術発表の慣行（Q6 参照）とは結論の位置が異なる。

### Inferences
- デッキの構成要素はピラミッドに対応づけられる。頂点はエグゼクティブサマリーの統括メッセージ（SCQA の A）、第2階層は各セクションの主張、第3階層は各スライドのタイトル、最下層はスライド本文の証拠。AI に作らせるときは、まずこのピラミッドをテキストで出させ、それからスライドに割り付ける順序が妥当と考えられる。
- 空・雨・傘は、各スライドが「事実」「解釈」「行動」のどれを担うかのタグ付けに使える。タグが「空」ばかりのデッキは示唆が欠けている（P4 の「観察止まり」）。

### Gaps
- Minto の原著（ルールの正確な文言、序論の書き方、デッキへの具体的な適用）は、今回は二次資料経由でしか確認できていない。Scribd などにある非公式コピーは使っていない。
- 「根拠は3つ」という数字を一次資料では確認できなかった（伊藤の抜粋記事にもない）。

---

## Q2. ゴーストデッキ／ストーリーボード／ドットダッシュ／水平・垂直ロジック：下書きの工程とチェック

### Takeaway
コンサル流の工程は次の順番になる。
1. ドットダッシュ（箇条書きのストーリーライン）
2. 関係者の合意
3. ゴーストデッキ（約20%完成。タイトルと図の手描きスケッチだけ）
4. 不足データの洗い出し
5. 本作成

点検の中心は2つ。タイトルだけ通読して話が通るか（水平ロジック）と、各スライドの中身がタイトルを支えているか（垂直ロジック）。プレゼン専門家側（Knaflic、Reynolds、Atkinson、前田鎌利）も、ソフトを開く前に紙や付箋で構成を決めるという点で一致している。

### Cited Findings

#### P5. ドットダッシュでストーリーラインを先に書き、スライドを作る前に関係者のフィードバックをもらう
- **原則**: デッキの骨組みは、スライドや図を作る前に箇条書きのアウトラインで固める。
- **手順・チェック**:
  - 第1階層の「ドット」にはストーリーを動かす主要な主張を書く
  - 第2階層の「ダッシュ」には、それを支える論点・事実・図を書く
  - アウトライン段階でキーとなる関係者の早期フィードバックを得る。ストーリーラインが間違っていた場合、フルデッキやゴーストデッキを作り直す無駄を避けられる
  — [Working with McKinsey blog, "McKinsey storyline: dot-dash", 2013-07-07](https://workingwithmckinsey.blogspot.com/2013/07/McKinsey-storyline-dot-dash.html?m=0)【準一次: 元マッキンゼーのコンサルタントによる匿名ブログ】
- **定義**: ストーリーラインとは「聞き手の現在の考えから、望む結果への旅路」で、デッキはその乗り物 — 同上
- **良い例／悪い例**: 記事に実例はない。
- **根拠の種類**: 組織規範（マッキンゼーの慣行を元社員が記述）。
- **適用範囲・反対意見**: ドットをどうスライドに割り当てるかの明示ルールは、この記事にはない。二次資料には「ドットがアクションタイトル、ダッシュがスライド上のデータと図になる」とする説明があるが、一次資料では確認できていない — [検索結果の要約（thinkinsights など）](https://thinkinsights.net/consulting/storyboard)【二次】

#### P6. ストーリーライン合意後に「ゴーストデッキ」を作り、4つの問いで点検する
- **原則**: 約20%完成の下書きデッキを作る。労力は主にリード（タイトル）と見出しに割き、ほかのページは空白か手描きの図スケッチにとどめる。
- **手順・チェック**:
  - 作るのは、チーム・上位者（パートナー）・場合によっては顧客がストーリーラインに合意した**後**
  - 4つの問いで点検する: ①ストーリーラインを変えたいか ②それを支える中身は何か ③すでに何があり、どう見せるか ④何が足りず、どう手に入れるか
  - 各ページに「手元にあるデータ」と「まだ入手が必要なもの」を付箋（sticker）で貼る
  - 先にこれを作ると、ストーリーラインの穴が「埋まらないページ」として見える。手戻りが少ないうちに直せるし、顧客や第三者へのデータ依頼を絞り込める（「海を沸かす」ような全方位調査を避ける）
  - 他社では shell や skeleton とも呼ぶ
  — [Working with McKinsey blog, "McKinsey presentations: ghost decks", 2013-07-06](https://workingwithmckinsey.blogspot.com/2013/07/McKinsey-presentations-ghost-decks.html?m=1)【準一次】
- **良い例**: 空白ページに図のラフと「データ: 顧客から入手予定」といったメモが付いている状態 — 同上
- **根拠の種類**: 組織規範。
- **適用範囲・反対意見**: 分析を伴う案件で、データ収集がボトルネックになる場面に特に効く。日本語の「紙芝居」はコンサル界隈でゴーストデッキとほぼ同じ意味で使われることがある。一方で「語り手がいないと伝わらない、図ばかりの資料」という悪い意味でも使われる — [EnterpriseZine](https://enterprisezine.jp/article/detail/911)【二次】。日本語でゴーストデッキ相当の工程を一次資料で裏付けるものは見つからなかった。

#### P7. 水平ロジック：タイトルだけを順に読んで、話全体が通るか確かめる
- **原則**: 各スライドのタイトルを要点（アクションタイトル）にし、タイトルだけを通読して全体のストーリーが伝わるかを確かめる。説明的なタイトルではこの検査が働かない。
- **手順・チェック**:
  1. 全スライドにアクションタイトルを付ける
  2. タイトルだけを順に読む
  3. 意図した話になっているか確認する
  4. 冒頭にエグゼクティブサマリーを置き、後続スライド1枚につき1項目の箇条書きにして、タイトルの順番とそろえる
  — [Cole Nussbaumer Knaflic, storytelling with data blog "horizontal logic", 2013-12（URL より）](https://www.storytellingwithdata.com/blog/2013/12/horizontal-logic)【一次】
  - タイトルが論証を運んでいるか。「市場動向」のようなトピック名のタイトルは、デッキがまだ記述にとどまっている兆候 — [Umbrex](https://umbrex.com/resources/the-consulting-career-guide/storylining-and-deck-structure/)【準一次】
- **良い例／悪い例**:
  - 弱い:「コストベンチマーク」 → 強い:「コスト差の大半は労働生産性で説明できる」
  - 弱い:「顧客インタビュー」 → 強い:「顧客は低価格より信頼性を重視している」
  — [Umbrex](https://umbrex.com/resources/the-consulting-career-guide/storylining-and-deck-structure/)
- **根拠の種類**: 組織規範・個人の経験則。
- **適用範囲・反対意見**: 読まれる資料と、意思決定のためのプレゼンに強く効く。Reynolds や高橋メソッドのような「スライドは話を補助するだけ」という流派ではタイトルに主張を書かないので、この検査は使えない（Q5 参照）。

#### P8. 垂直ロジック：各スライドの中身がタイトルを支え、タイトルと関係しない要素は削る
- **原則**: スライド本文（図・データ・箇条書き）はタイトルの主張を裏付けるものだけにする。
- **手順・チェック**:
  - 各図表がタイトルを支えているか確認する — [Umbrex](https://umbrex.com/resources/the-consulting-career-guide/storylining-and-deck-structure/)【準一次】
  - 要素ごとにタイトルとのつながりを問い、つながらなければ削る
  - 1枚の内容を1つのアクションタイトルで言えるか試す。2つの考えを「と（and）」でつなぐ必要があるなら、スライドを分ける — [Deckary: How to Make Consulting Slides](https://deckary.com/blog/consulting-quality-slides)【二次: ベンダーのブログ】
  - Doumont の「下位論点ごとに1枚」（P15）も同じ方向の規則。
- **根拠の種類**: 組織規範・個人の経験則。
- **適用範囲・反対意見**: Knaflic の "vertical logic" の記事（2013-12）は今回取得していない（Gaps）。

#### P9. ソフトを開く前に、紙・付箋・ホワイトボードで構成を組み、並べ替えを試す
- **原則**: ストーリーボードは低技術の道具で作る。スライド作成ソフトから始めると、構成が固まる前にスライドを作り込み始め、それに執着してしまう。
- **手順・チェック**（Knaflic）:
  1. 先に「誰が聞き手で、何を知る／するべきか」を決める
  2. メッセージの要素を付箋に書き、構造（アウトライン）に並べる
  3. 順序を入れ替えていくつかの流れを試す
  4. Big Idea を冒頭に置くことを検討する（聞き手が要点を見逃さないため）
  5. 細部が固まるにつれて構造を直す
  6. 可能ならこの段階で顧客やステークホルダーの承認を得て、後の手戻りを減らす
  — [Knaflic, "storyboarding", storytelling with data, 2014-02-10](https://www.storytellingwithdata.com/blog/2014/02/storyboarding)【一次】
- **同じ趣旨の他の専門家**:
  - Reynolds: 準備の初期段階はコンピュータから離れて行う（ホワイトボード・付箋・紙）。デザイン前に全体像と中核メッセージを特定する — [Presentation Zen, Ch.3 "Planning Analog"（O'Reilly 目次）](https://www.oreilly.com/library/view/presentation-zen-simple/9780132901529/ch03.html)、内容は [SuperSummary 要約](https://www.supersummary.com/presentation-zen/summary/)【二次】
  - Atkinson: 5原則の第1は "Nail down the story before the slides"、第5は "Think like a storyboard" — [Microsoft Press Store 抜粋, Beyond Bullet Points 4th ed., 2018-11-22](https://www.microsoftpressstore.com/articles/article.aspx?p=2916274)【一次: 出版社の抜粋】
  - 前田鎌利: 「まず全体のラフを作り、それぞれのスライドにタイトルをつけてから1枚の中身に入っていかないとなかなかゴールにたどり着かない」 — [ニュースイッチ 2020-01-03](https://newswitch.jp/p/20564)【一次: 本人インタビュー】
- **良い例**: Knaflic の夏季理科学習プログラムの例では、当初 Big Idea が最後にあったストーリーボードを、冒頭に移すよう提案している — [storyboarding](https://www.storytellingwithdata.com/blog/2014/02/storyboarding)
- **根拠の種類**: 個人の経験則（複数の専門家で一致）。
- **適用範囲・反対意見**: AI 生成では「紙」はテキストのアウトラインに置き換わる。並べ替えを試す工程を明示的に入れないと、最初に出た順序がそのまま残りやすい（推論）。

#### P10. 逆ストーリーボード：できたデッキから各ページの要点を書き出し、アウトラインとして読めるか見る
- **原則**: 完成した（または他人の）デッキを読み、各ページの要点を1行ずつ書き出す。そのリストがストーリーボードやアウトラインのように読めれば、構成は通っている。
- **手順・チェック**: 内容を読む → 各ページの要点を書く → 一覧がストーリーボードの形になっているか確認する — [storytelling with data オンライン講座 Week 4 "low-tech planning"](https://www.storytellingwithdata.com/onlinecourse-week4)【一次。ただし検索スニペットでの確認のみ】
- **根拠の種類**: 個人の経験則。
- **適用範囲**: AI が生成したデッキの自己点検にそのまま使える。

### Inferences
- 一次・準一次資料から組み立てたデッキ下書きの標準工程（AI スキル向けの手順案）:
  1. 聞き手・目的・1文の中核メッセージを決める（Q4）
  2. ドットダッシュ形式のアウトラインを書く。ドットは主張文、ダッシュは根拠と必要データ
  3. ドット（主張）の並べ替えを2〜3通り試し、1つ選ぶ
  4. ゴーストデッキとして全スライドのタイトルと「本文に置く証拠のメモ（手元にあるか、まだ必要か）」だけを作る
  5. タイトル通読（水平）と、タイトル対本文（垂直）で点検する
  6. 本文を作る
  7. 逆ストーリーボードで最終確認する
- ゴーストデッキの「付箋（必要データ）」は、AI 生成では「根拠が手元にない主張」の可視化に読み替えられる。根拠のない主張をもっともらしい数字で埋める（捏造）のを防ぐ点検項目になり得る。

### Gaps
- McKinsey・BCG・Bain の公式資料でゴーストデッキやドットダッシュを説明したものは見つからなかった。いずれも元社員ブログと業界ガイド経由。
- Knaflic の「vertical logic」記事（[URL](https://www.storytellingwithdata.com/blog/2013/12/vertical-logic)）は未取得。

---

## Q3. プレゼン専門家の原則（Duarte / Reynolds / Atkinson / Doumont / Knaflic / Heath / 高橋メソッド / 伊藤羊一 / 前田鎌利 / 山口周）

### Takeaway
専門家に共通するのは次の3点。①スライドの前に1文の中核メッセージを決める（Big Idea、3分ストーリー、エレベーターテスト、1分で話せ）②スライド作成前に構成を紙で決める ③1枚1メッセージ。違いは、スライドを単独で読めるものにするか（Doumont・コンサル）、話の補助にとどめるか（Reynolds・高橋メソッド）。最も手順が具体的だったのは Doumont の配布資料で、導入から結論までの型と、プレビューの論点数（理想3、最大5）を明示している。

### Cited Findings

#### P11. Big Idea：中核メッセージを「独自の視点＋何が懸かっているか」を含む完全な1文にする（Duarte → Knaflic）
- **原則**: Big Idea は ①独自の視点を示し ②何が懸かっているか（stakes）を伝え ③完全な文である。
- **手順・チェック**: 3分ストーリーを1文に凝縮する。視点・懸かっているもの・求める行動が入っているか確認する。各スライドにも小さな Big Idea を持たせ、全体を貫く Big Idea を1つ置く — [Knaflic, "what's the Big Idea?", 2014-02-06](https://www.storytellingwithdata.com/blog/2014/02/whats-big-idea)【一次】。視点は「経験から得た、具体的で反論の余地のある立場」、stakes は「聞き手が採用した／しなかった場合に何が起きるか」 — [Duarte: Business Storytelling](https://www.duarte.com/resources/storytelling-framework/)【一次: Duarte 社サイト】
- **良い例**: 「生徒の理科への認識を改善するパイロットプログラムは成功したので、継続を推奨し、予算承認をお願いしたい」 — [Knaflic 2014](https://www.storytellingwithdata.com/blog/2014/02/whats-big-idea)
- **出典**: Nancy Duarte『Resonate』Wiley, 2010。Knaflic『Storytelling with Data』（Wiley）。
- **根拠の種類**: 個人の経験則（Duarte 社のコンサル実務に基づく）。
- **適用範囲**: 説得・意思決定を求める場面全般。純粋な情報共有では stakes が弱くなりがち。

#### P12. 3分ストーリー／エレベーターテスト／1分版：スライドなしで短く話せるかで、メッセージの明確さを試す
- **原則**: スライドに頼らずに短時間で要点を言えなければ、メッセージはまだ固まっていない。
- **手順・チェック**:
  - Knaflic: 聞き手に伝えるべきことを3分で言えるか。上司に聞かれたときや、持ち時間を削られたときにもこの版で対応する — [Knaflic, "the 3-minute story", 2014-02-04](https://www.storytellingwithdata.com/blog/2014/02/the-3-minute-story)【一次】
  - Reynolds: 中核メッセージを30〜45秒で伝えられるか（エレベーターテスト）。「聞き手が1つだけ覚えて帰るなら何か」「だから何？」を問う — [SuperSummary: Presentation Zen](https://www.supersummary.com/presentation-zen/summary/)【二次】
  - 前田鎌利:「『1分バージョン』も用意しておく」 — [ダイヤモンド社 書籍ページ『【完全版】社内プレゼンの資料作成術』2022-03](https://www.diamond.co.jp/book/9784478115152.html)【一次】
  - 伊藤羊一: 長く話さず1分程度でまとめる — [PRESIDENT Online 2018](https://president.jp/articles/-/25226)【一次】
- **数値の相違**: 3分（Knaflic）、30〜45秒（Reynolds、二次資料経由）、1分（前田・伊藤）。用途はどれも「メッセージの明確さの検査」で一致している。
- **根拠の種類**: 個人の経験則。

#### P13. グランステスト：各スライドの要点が3秒で伝わるか
- **原則**: 聞き手はスライドを見ながら話も聞かなければならない。要点は3秒以内に把握できるべきだ。
- **チェック項目**（Duarte 公式）:
  - 3秒で意味が取れるか
  - 1つの明確な要点に絞れているか
  - 要素の配置がメッセージを支えているか
  - コントラストと余白で重要情報を強調しているか
  - 統一感と流れがあるか
  - 各要素が理解を助けているか
  - 視覚ノイズを減らしているか
  — [Duarte: The Glance Test](https://www.duarte.com/resources/guides-tools/the-glance-test/)【一次。ページに日付なし】
- **由来**: Duarte が HBR（2012年）で提唱 — [Small Wars Journal 転載, 2012-10-22](https://smallwarsjournal.com/2012/10/22/do-your-slides-pass-the-glance-test/)【二次】。KLA-Tencor の Glenn Hughes と共同開発し、信号対雑音比で採点する — 同【二次】
- **根拠の種類**: 個人の経験則（採点ツールはあるが、検証研究は見当たらない）。
- **適用範囲・反対意見**: 投影して話すプレゼン向け。戦略や業務の提案で、役員が3秒見ただけで経理機能の統合を承認することはない、という批判がある — [Think Insights: Designing Effective Slides](https://thinkinsights.net/index.php/insights/designing-effective-slides)【二次】。読む資料には当てはまりにくい。スライド単位の規則なので、詳細は視覚設計の担当に譲る。

#### P14. スパークライン：「現状（what is）」と「ありうる未来（what could be）」を繰り返し対比して勢いをつくる（Duarte）
- **原則**: 説得型プレゼンは、現状と、より良い未来とを行き来することで推進力を生む。
- **事例**: Duarte はキング牧師「I Have a Dream」、ジョブズの iPhone 発表などを分析している — [Duarte blog: Creating moments of impact using Sparklines](https://www.duarte.com/blog/creating-moments-of-impact-using-sparklines-for-strategic-conversations/)【一次】, [library-d7m: Duarte Sparkline 要約](https://library-d7m.pages.dev/communication-framework/storytelling-and-presentation/duarte-sparkline)【二次】
- **根拠の種類**: 個人の経験則（著名スピーチの事後分析）。
- **適用範囲・反対意見**: ビジョンや変革の訴求に向く。定例報告やデータ報告では過剰になりうる（推論）。始まりと終わりの具体的な型（"new bliss" など）は、今回は一次資料で確認していない。

#### P15. Doumont：計画の5つの問い → 導入〜結論の型 → 1スライド1メッセージ
- **原則**: 「1. 計画（考えをまとめる）→ 2. 設計（構造を決める）→ 3. スライド作成（メッセージを伝える）→ 4. 実演 → 5. 質疑」の順に進め、スライドは最後に作る。スライドは必須ではない（"Slides are optional; first plan, design… and rehearse."）。
- **手順・チェック**（Doumont 本人の配布資料より）:
  - **計画の5つの問い**: Why（目的）/ Who（聞き手）/ What（内容）/ When（時間の制約）/ Where（場所の制約）
  - **構成の型**:
    - 導入は聞き手に焦点を当てる: Attention getter（聞き手を「ニーズ」へ効率よく導く）→ Need（現状と望ましい状態の差）→ Task（そのニーズに対して自分が何を決めた／頼まれたか）→ Main message（聞き手に覚えてほしい1文）→ Preview（本論の地図。**理想は3点、最大5点**）
    - 本論: Point 1 → Transition → Point 2 → Transition → …
    - 結論は再び聞き手に焦点を戻す: Review（本論の要約。結論への橋渡し）→ Conclusion（以上が聞き手にとって最終的に何を意味するか）→ Close（明確かつ優雅に終える）
  - **スライド**: 1枚で1メッセージだけを伝える。メッセージはまず言葉で述べ、次に視覚で展開する。主メッセージ → 主論点 → 下位論点の階層で、下位論点ごとに1枚。スライドはそれ単体で意味が通るようにし、話す内容と「効果的に冗長」にする。言葉でも視覚でも簡潔に
  - **3法則**: 聞き手に合わせる／信号対雑音比を最大化する／効果的な冗長性を使う
  - **What と So what**: 情報（what）に解釈を加えてメッセージ（so what）にする
  — [Jean-luc Doumont, "Effective oral presentations" 配布資料, © 2009 Principiae（チリ大学のコースページに掲載）](https://users.dcc.uchile.cl/~cgutierr/cursos/INV/presentaciones1.pdf)【一次: 本人作成の配布資料。原典は『Trees, Maps, and Theorems』Principiae, 2009】
- **良い例**: 同配布資料では、睡眠時間の円グラフに説明的タイトル（「成人の睡眠時間の分布」）を付けた版と、メッセージタイトル（「推奨の8時間眠る成人は28%だけ」）を付けた版を並べている — 同上
- **根拠の種類**: 個人の経験則（科学技術コミュニケーションの講師としての実務に基づく）。
- **適用範囲・反対意見**: 口頭発表全般。スライドを単独で意味が通るものにするという点は、Reynolds の「スライドと配布資料を分ける」立場と緊張関係にある（Q5）。

#### P16. Beyond Bullet Points（Atkinson）：ストーリーテンプレートでデッキ全体を1〜2ページに収めてから、スライドを作る
- **原則**:
  - 5原則: ①スライドより先にストーリーを固める ②情報を Yes/No の意思決定向けに組み直す ③「No」から始めて「Yes」に至る ④常に終わりを意識する ⑤ストーリーボードのように考える
  - 10の構成要素: Hook、Relevance、Challenge、Desire、Map、Anchors、Explanation、Headlines、Visuals、Flow
- **手順・チェック**:
  - ストーリーテンプレート（Word 文書）を中心の整理道具にし、個々のスライドに視覚・言語要素を足す前に、ストーリー全体を1〜2ページで見えるようにする
  - 章立ては「最初の5枚をスケッチ → 残りのスライドをスケッチ → 最初の5枚に図を入れる → 残りに図を入れる」の順で、冒頭5枚を先に作り込む構成になっている
  — [Microsoft Press Store: Beyond Bullet Points 4th ed. 第1章抜粋, 2018-11-22](https://www.microsoftpressstore.com/articles/article.aspx?p=2916274)【一次】
- **補足**: 旧版のテンプレートは3幕構成（冒頭・中盤・結末）と紹介されている。第1幕は舞台設定の5要素、第3幕は危機・解決・クライマックス・決着の4要素とする書評がある — [Goodman Center "Free Range" 2005-06 書評](https://www.thegoodmancenter.com/wp-content/uploads/2013/07/free_range_2005_06.pdf)【二次。検索スニペットのみ】
- **根拠の種類**: 個人の経験則。
- **適用範囲・反対意見**: 版によってテンプレートの名称や構成が違う。最新の第4版の各要素の詳細と、見出しの3つの規則は未確認。

#### P17. 前田鎌利：社内の意思決定プレゼンを「5〜9枚」「3分」で、決裁者の判断材料に絞る
- **原則**: 社内プレゼンはシンプルかつロジカルにし、決裁者が意思決定に必要とする情報だけを載せる。
- **手順・チェック**:
  - 3分を目標にし、5〜9枚にまとめる
  - スライド作成の前に準備する（「A3 1枚」に整理する、報告型・依頼型など目的別の型を使う）
  - 「事実を伝えるだけでは『報告』ではない」
  - 「『2案』を提案して、採択率を上げる」
  - 「依頼プレゼンは『＋1』で構成する」
  - アペンディックスと想定問答（FAQ）を用意する
  - 「1分バージョン」も用意する
  — [ダイヤモンド社 書籍ページ, 2022-03](https://www.diamond.co.jp/book/9784478115152.html)【一次】
  - 全体ラフ → タイトル → 中身の順に作る。1枚は15分以内で作る、といった時間ルールを決める。1枚の理解に20秒以上かかると聞き手の思考が止まる。説明用資料はシンプルにし、どんな質問にも答えられるようアペンディックスを充実させる — [ニュースイッチ 2020-01-03](https://newswitch.jp/p/20564)【一次: 本人インタビュー】
- **出典**: 前田鎌利（ソフトバンク系で17年、2010年にソフトバンクアカデミア1期生。2018年に一般社団法人プレゼンテーション協会を設立）。
- **根拠の種類**: 個人の経験則（社内決裁プレゼンの実務経験）。
- **適用範囲・反対意見**: 日本企業の社内決裁向け。13字のキーメッセージ、70〜100pt の文字、色の規則などはタイトルと視覚設計の範囲なので他の担当に譲る。コンサルの読む資料（1枚に多くの情報）とは設計思想が逆。

#### P18. 高橋メソッド：巨大な文字で1〜2語のスライドを、多数・短時間ずつ見せる
- **原則**: 図表や写真を使わず、1枚に1〜2語程度の短い言葉だけを巨大な文字で置く。その分、枚数は多くなり、1枚あたりの表示時間は短くなる — [Takahashi method（Wikipedia 転載）](https://wiki.krisyotam.com/content/wikipedia_en_all_nopic_2026-03/Takahashi_method)【二次】。発表者はスライドの文字をほぼそのまま読み上げる使い方が標準とされる — [ITmedia オルタナティブ・ブログ 2011-09](https://blogs.itmedia.co.jp/magic/2011/09/post-2c75.html)【二次】
- **出典**: 高橋征義。考案の経緯と年代、本人の解説ページは今回未確認。
- **根拠の種類**: 個人の経験則。
- **適用範囲・反対意見**: LT や技術講演など、語りとリズムで聞かせる場に向く。配布資料や読む資料には使えない。枚数を時間から逆算する一般的な目安（Q6）はこの方式には当てはまらない。

#### P19. Heath 兄弟『Made to Stick』：核心を見つけ（Commander's Intent）、知識の呪いを外部の人で検査する
- **原則**: 最も重要な1点を決め、それを埋もれさせない（find the core）。軍の「指揮官の意図」のように、計画が崩れても判断の指針になる短い目標の言明を持つ。専門家は「知らない状態」を想像できなくなる（知識の呪い）。専門用語は知識の呪いの兆候なので、部外者に伝わるかを試す — [Shortform: Commander's Intent](https://www.shortform.com/blog/?p=45730)【二次】
- **良い例**: サウスウエスト航空の「THE low-fare airline」 — 同上【二次】
- **出典**: Chip Heath & Dan Heath『Made to Stick』Random House, 2007。
- **根拠の種類**: 個人の経験則。本書は心理学研究も引くが、今回は二次資料のみで確認。
- **適用範囲**: 中核メッセージの絞り込み（P11、P12）を補う。

#### P20. 山口周：構成 → 文章化 → デザイン化の3段階（参考程度）
- **内容**: 外資系コンサル向けの解説では、資料作成を「構成」「文章化」「デザイン化」の3段階に分け、最初に伝えたいメッセージを最適な順序で整理してストーリー全体の骨組みを作るとしている — [外資就活ドットコム コラム](https://gaishishukatsu.com/archives/124107)【二次】。山口周『外資系コンサルのスライド作成術』（東洋経済新報社。電子版は2013年10月配信）の書誌は確認したが、本文の手順は未確認 — [NDL サーチ](https://ndlsearch.ndl.go.jp/en/books/R100000002-I026256956)
- **根拠の種類**: 組織規範（二次）。
- **適用範囲**: 山口本人の手順として扱わないこと。

### Inferences
- 「1文のメッセージ → 構成を紙で → スライド」という順序は、Duarte、Knaflic、Reynolds、Atkinson、Doumont、前田、伊藤で一致している。AI スキルの工程として最も裏付けが厚い。
- Doumont の型（Need → Task → Main message → Preview → Points → Review → Conclusion）は、SCQA（S + C ≒ Need、Q ≒ Task、A ≒ Main message）とほぼ対応する。違いは Preview と Review を明示する点で、口頭発表の冗長性を設計に組み込んでいる。

### Gaps
- Duarte『Resonate』のスパークラインの始まり・終わりの型と、『slide:ology』の構成関連の規則は、一次資料で確認できていない。
- 高橋征義本人の解説（目安の枚数や考案の経緯）、山口周の著作本文、伊藤羊一の書籍本文（ピラミッドの「3つの箱」の詳細）は未確認。
- Reynolds の本文（エレベーターテストの秒数、分析的計画の手順）は、O'Reilly で 403 が返り未取得。二次要約のみ。

---

## Q4. スライドを作る前に聞き手とゴールを定義する（最初に答えるべき問い）

### Takeaway
どの流派も、スライド作成の前に「誰が聞き手か」「聞いた後に何を知り、何をしてほしいか」「その中核を1文で言うと何か」を決めている。最も網羅的なのは Doumont の5問（Why / Who / What / When / Where）。コンサル側（Umbrex）はさらに「デッキの種類（運営委員会向けか、作業チーム向けか、など）」と「目的の種類（事実の合意・診断・選択肢比較・推奨・実行準備）」を先に決めるよう求めている。

### Cited Findings

#### P21. 作る前に「聞き手・目的・中核メッセージ・制約」を書き出す
- **原則**: デッキの内容と順序は、聞き手と目的から逆算して決める。
- **手順・チェック**:
  - 5つの問い（Why 目的 / Who 聞き手 / What 内容 / When 時間の制約 / Where 場所の制約）に答え、そのうえで聞き手に覚えてほしい1文（Main message）を決める — [Doumont 配布資料 2009](https://users.dcc.uchile.cl/~cgutierr/cursos/INV/presentaciones1.pdf)【一次】
  - ストーリーボードの前に「聞き手は誰か、何を知る／するべきか」を決める — [Knaflic, storyboarding 2014](https://www.storytellingwithdata.com/blog/2014/02/storyboarding)【一次】
  - 誰がデッキを使うかを特定する（運営委員会、作業チーム、パートナーレビュー、提案書、最終報告で必要な詳細度が違う）。目的が「事実の合意」「診断」「選択肢の比較」「推奨」「実行準備」のどれかを決める — [Umbrex](https://umbrex.com/resources/the-consulting-career-guide/storylining-and-deck-structure/)【準一次】
  - 情報を Yes/No の意思決定向けに組み直す — [Atkinson 2018](https://www.microsoftpressstore.com/articles/article.aspx?p=2916274)【一次】
  - 相手の立場に立ち、意思決定に必要なデータを選ぶ — [前田鎌利, ニュースイッチ 2020](https://newswitch.jp/p/20564)【一次】
  - ストーリーラインとは「聞き手の現在の考えから、望む結果への旅路」 — [Working with McKinsey 2013](https://workingwithmckinsey.blogspot.com/2013/07/McKinsey-storyline-dot-dash.html?m=0)【準一次】
- **良い例／悪い例**:
  - 悪い例:「本デッキでは市場動向、顧客調査、価格、次のステップを説明します」（目次の読み上げ）
  - 良い例:「市場は魅力的だが、利益率が最も高く実行リスクが管理可能な2つの重点セグメントに絞って参入すべきだ」
  — [Umbrex](https://umbrex.com/resources/the-consulting-career-guide/storylining-and-deck-structure/)
- **根拠の種類**: 個人の経験則と組織規範（流派をまたいで一致）。
- **適用範囲・反対意見**: 反対意見は見当たらない。

### Inferences
- AI スキルの入力として、スライド生成の前に次の項目を必須で埋めさせるのが妥当と考えられる。
  - 聞き手（役職と前提知識）
  - 聞いた後の行動・判断（Yes/No にできるか）
  - 目的の種類（Umbrex の5分類）
  - 1文の中核メッセージ（視点・懸かっているもの・求める行動）
  - 持ち時間と媒体（投影か、事前に読む資料か）
- 「聞き手の現在の考え」をあらかじめ書かせると、SCQA の S（誰もが同意する前提）を選びやすくなる（推論）。

### Gaps
- 聞き手分析の手法（ペルソナ化や反論の予測など）について、デッキ作成に特化した一次資料は Umbrex の「懐疑的な顧客なら何を問うか」以外に見つからなかった。

---

## Q5. 投影用スライドと読む資料（スライデュメント／配布資料／Amazon 6ページメモ）の区別

### Takeaway
3つの立場がある。
- **分離派**: 投影スライドは話の補助にとどめ、詳細は別の配布資料に書く（Reynolds、Duarte の Slidedocs、高橋メソッド）。
- **単独で読めるスライド派**: 各スライドが単体で意味をなすよう主張タイトルを付ける（Doumont、コンサル）。
- **スライド否定派**: 意思決定や技術的議論には文章を使う（Amazon、Tufte）。

AI スキルでは、最初に「投影して話すのか／事前に読ませるのか／後で配るのか」を決め、それに応じて文字の密度と構成の規則を切り替える必要がある。

### Cited Findings

#### P22. スライドと配布資料は別物として作る（スライデュメントを避ける）
- **原則**: スライドと文書の中間物（slideument）は、スライドとしても配布資料としても機能しない。投影用スライドと、詳細を書いた別の文書を用意する。
- **手順・チェック**:
  - Reynolds が「slideument」という語を作ったとされる — [Martin Fowler, bliki "Slideument"](https://martinfowler.com/bliki/Slideument.html)【二次: 著名エンジニアの解説】
  - 印刷を前提にスライドへ文字を詰め込むと、どちらつかずになる。スライドとは別に、主要な図を添えた文章の要約を配る — [SuperSummary: Presentation Zen](https://www.supersummary.com/presentation-zen/summary/)【二次】
  - 発表者ノートにはさらに多くのデータを、配布資料にはそれ以上のデータと詳細を載せる — [Notre Dame: Presentation Zen 解説](https://learning.nd.edu/resource-library/presentation-zen)【二次】
  - Duarte 社は、発表者なしで情報を伝える「Slidedocs（視覚的文書）」を別のジャンルとして定義し、事前に読む資料（pre-read）や後に残す資料（leave-behind）に使うとしている。プレゼンは強力な説得の手段だが、情報を届ける手段として常に適切とは限らない — [Duarte: Slidedocs](https://www.duarte.com/resources/books/slidedocs/)【一次】
- **根拠の種類**: 個人の経験則。
- **適用範囲・反対意見**: Doumont は「スライドは単体で意味が通るように」作り、話と「効果的に冗長」にせよと言う — [Doumont 2009](https://users.dcc.uchile.cl/~cgutierr/cursos/INV/presentaciones1.pdf)。コンサルのデッキは、主張タイトルと根拠を1枚に収め、読まれることを前提にした混成物（P7、P8）。日本の「紙芝居」批判は、語り手なしでは伝わらない図だけの資料を問題にしている — [EnterpriseZine](https://enterprisezine.jp/article/detail/911)【二次】。つまり、スライドを単独で読めるようにするかどうかで流派が分かれる。

#### P23. 議論と意思決定には、スライドではなく物語形式の文章を使う（Amazon）
- **原則**: 箇条書きのスライドでは情報量が少なく、何が何より重要か、物事がどうつながるかが見えない。物語形式で構造化したメモを書き、会議の冒頭で全員が黙読する。
- **手順・チェック**:
  - 2004年6月9日付の Bezos のメールで、S チーム会議での PowerPoint の使用をやめ、「よく構造化された物語形式の文章」を求めた — [Slab: How Jeff Bezos Turned Narrative into Amazon's Competitive Advantage](https://slab.com/blog/jeff-bezos-writing-management-strategy)【二次】
  - 会議は6ページのメモから始め、最大30分ほど黙読してから議論する。読み手は、自分の質問がメモの中で答えられるまで待てる。補足データはアペンディックスに置く — [Shawn Callahan, Anecdote 2018-05-08](https://www.anecdote.com/2018/05/amazons-six-page-narrative-structure/)【二次】
  - Bezos は株主書簡でも、スライド型のプレゼンはせず、物語形式の6ページメモを書くと述べた — [Researchscape: Bezos on narratives](https://researchscape.com/blog/bezos-on-narratives)【二次。書簡本文は未取得】
  - スライドは「発表者には楽だが、聞き手には難しい」。従来型の PPT だと役員が途中で割り込む（Brad Porter による Bezos の引用） — [Anecdote 2018](https://www.anecdote.com/2018/05/amazons-six-page-narrative-structure/)
- **数値の相違**: 2004年のメールは「4ページ」とする資料と、後の書簡の「6ページ」とする資料があり、「4〜6ページ」とする資料もある — [Slab](https://slab.com/blog/jeff-bezos-writing-management-strategy), [Quartz](https://qz.com/work/1256645/for-meetings-amazon-makes-its-employees-write-anonymous-six-page-stories-instead-of-powerpoints-or-slides)【二次】
- **構造について**: Amazon 公式の章立ては見つからなかった。Callahan の4拍子（「以前はこうだった」→「そこで何かが起きた」→「だから今こうすべきだ」→「すると未来はこうなる」）は本人の提案であり、Amazon の規範ではない — [Anecdote 2018](https://www.anecdote.com/2018/05/amazons-six-page-narrative-structure/)
- **根拠の種類**: 組織規範（Amazon）。
- **適用範囲・反対意見**: 黙読の時間を取れる社内の意思決定会議に向く。

#### P24. 技術的な情報伝達では、スライドより短い文書を配る（Tufte）
- **原則**: 技術的な場では、参加者全員が読める短い書面の報告を配るのが最も効果的。スライドは推論を断片化する。
- **根拠**: Tufte『The Cognitive Style of PowerPoint』（2003年、28ページの小冊子）。コロンビア号事故調査委員会の報告書は、NASA が技術文書の代わりに PowerPoint のブリーフィングスライドを常用していることを問題として指摘し、Tufte の分析を引いた。改訂版には同委員会の分析が加わった — [Edward Tufte: The Columbia evidence](https://www.edwardtufte.com/notebook/the-columbia-evidence/)【一次】, [New edition of The Cognitive Style of PowerPoint](https://www.edwardtufte.com/notebook/new-edition-of-the-cognitive-style-of-powerpoint/)【一次】
- **根拠の種類**: 事例分析（事故調査）と個人の主張。統制された実証研究ではない。
- **適用範囲・反対意見**: 技術レビュー、安全性判断、複雑なデータの議論に向く。説得や講演には向かない。

### Inferences
- AI スキルでは、最初に「モード」を決めさせるのが妥当と考えられる。
  - **投影モード**: 話が主役。1枚1メッセージ、少ない文字、グランステスト、補足は発表者ノートと別の資料
  - **読む資料モード**: 単独で読める。主張タイトル＋根拠、タイトル通読で論が通る。コンサル式・Slidedocs
  - **文章モード**: 議論の材料として文章を書く。Amazon・Tufte
- 同じデッキを投影にも配布にも使う場合は、スライデュメントになりやすい。投影用の本編と、読む用のアペンディックスや別資料に分けるのが、Reynolds・前田（アペンディックスの充実）・Amazon（データはアペンディックス）に共通する解決策と読める。

### Gaps
- スライドと文書の理解度や意思決定の質を比べた実証研究は、今回は探しきれていない。Tufte もコロンビア号の件も事例分析にとどまる。
- Bezos の2004年メールと株主書簡の原文は、今回直接確認していない。

---

## Q6. 実践的ヒューリスティクス（枚数と時間、結論の位置、アジェンダ・まとめ、つなぎ、アペンディックス）

### Takeaway
枚数の目安は出典ごとに大きく違い、用途で使い分けるしかない。
- 学術発表: 1分1枚（30秒〜1分）
- VC へのピッチ: 10枚・20分（Kawasaki）
- 社内決裁: 5〜9枚（前田）
- 高橋メソッド: 大量

結論の位置は、ビジネス（冒頭）、学術（末尾）、Doumont（冒頭と末尾の両方）で分かれる。アジェンダやまとめは、目次の羅列ではなく「後続の主張の要約」にする点で各流派が一致している。

### Cited Findings

#### P25. 枚数は持ち時間と用途から逆算する（目安は出典ごとに違うため、すべて併記する）
| 出典 | 目安 | 用途・前提 | 根拠の種類 |
|---|---|---|---|
| Guy Kawasaki「10/20/30ルール」 | 10枚・20分・30pt 以上 | VC 向けピッチ（1時間枠のうち40分を議論に残す）。「人は1回の会議で10を超える概念を理解できない」 | 個人の経験則。初出は2004年の書籍、2005年や2006年のブログなど諸説あり — [guykawasaki.com](https://guykawasaki.com/the_102030_rule/)（403 で本文未取得）, [CBS News](https://www.cbsnews.com/news/improve-your-powerpoint-presentations-with-guy-kawasakis-10-20-30-rule/)【二次】 |
| 前田鎌利 | 5〜9枚、3分目標 | 日本企業の社内決裁プレゼン | 個人の経験則 — [ダイヤモンド社 2022](https://www.diamond.co.jp/book/9784478115152.html), [ニュースイッチ 2020](https://newswitch.jp/p/20564) |
| 東北大学 発表資料チェックリスト | 1分で1枚 | 研究発表（工学系研究室） | 組織規範（教育機関） — [東北大 checklist_presen（2026-03 掲載）](https://web.tohoku.ac.jp/yusa/wp-content/uploads/2026/03/checklist_presen_0204.docx)【一次】 |
| 神奈川県理学療法士会 | 1枚30秒〜1分、発表時間の1.5〜2倍の枚数 | 学会発表 | 組織規範 — [pt-kanagawa.or.jp PDF](https://pt-kanagawa.or.jp/wpt/wp-content/uploads/2025/06/96d283cdb3e909b4341b958edf2175dd.pdf)【検索スニペットのみ。本文は 503 で未取得】 |
| 名古屋大学 | 1分1枚換算 | 学術発表 | 組織規範 — [名大 DesignPresentation.pdf, 2018](https://web.cshe.nagoya-u.ac.jp/asg/designpresentation/DesignPresentation.pdf)【検索スニペットのみ。PDF のテキスト抽出は失敗】 |
| 新潟大学 | 合計15枚ほど、各1分 | 学術発表 | 組織規範 — [新潟大 PDF](https://niigata-u.repo.nii.ac.jp/record/32162/files/20181108-3.pdf)【検索スニペットのみ】 |
| 高橋メソッド | 通常より大幅に多く、1枚の表示は短い | LT・技術講演 | 個人の経験則 — [Takahashi method](https://wiki.krisyotam.com/content/wikipedia_en_all_nopic_2026-03/Takahashi_method)【二次】 |
| Umbrex | 枚数の目標はない。10枚のデッキなら論理をおよそ10文で説明できるはず | コンサルのデッキ | 組織規範 — [Umbrex](https://umbrex.com/resources/the-consulting-career-guide/storylining-and-deck-structure/) |

- **注意**: 1枚あたりの時間で比べると、Kawasaki は約2分、学術は30秒〜1分、高橋メソッドは数秒で、桁が違う。前田の「1枚の理解に20秒以上かかると思考が止まる」は、1枚の情報量の上限についての経験則で、表示時間の目安ではない — [ニュースイッチ 2020](https://newswitch.jp/p/20564)

#### P26. 結論の位置・アジェンダ・まとめ・つなぎ・アペンディックス
- **結論を冒頭に置く（ビジネス）**:
  - エグゼクティブサマリーは、プロジェクトの背景ではなく、役員が下すべき判断から始める。各セクションを順に要約するのではなく、発見・重要性・推奨・残るリスク・次の一手を、つながった少数のメッセージに統合する。「so what」と「now what」の両方を入れる — [Umbrex](https://umbrex.com/resources/the-consulting-career-guide/storylining-and-deck-structure/)
  - Big Idea を冒頭に置くことを検討する — [Knaflic, storyboarding](https://www.storytellingwithdata.com/blog/2014/02/storyboarding)
  - まず結論を話す — [伊藤羊一](https://president.jp/articles/-/25226)
- **結論を末尾に置く（学術）**:
  - 構成は「1枚目は背景、2枚目は目的、3枚目以降は適切な構成」。結論が「目的」と対応しているかを確認する — [東北大チェックリスト](https://web.tohoku.ac.jp/yusa/wp-content/uploads/2026/03/checklist_presen_0204.docx)
  - 表紙 → 背景 → 課題 → 目的 → 本論 → 結論 → 今後の課題 → 参考文献、という流れを示す大学資料もある（南山大学の資料として検索スニペットで確認）
- **両方に置く（Doumont）**: 導入で Main message を述べ、末尾で Review → Conclusion（聞き手にとっての意味）を述べる。冗長性を意図的に設計する — [Doumont 2009](https://users.dcc.uchile.cl/~cgutierr/cursos/INV/presentaciones1.pdf)
- **アジェンダ・プレビュー**:
  - 本論の地図を示す。論点は理想3、最大5 — [Doumont 2009](https://users.dcc.uchile.cl/~cgutierr/cursos/INV/presentaciones1.pdf)
  - 冒頭のエグゼクティブサマリーに後続スライド1枚につき1項目を書き、タイトル順と一致させる — [Knaflic, horizontal logic](https://www.storytellingwithdata.com/blog/2013/12/horizontal-logic)
  - Atkinson の構成要素にも "The Map" がある — [Atkinson 2018](https://www.microsoftpressstore.com/articles/article.aspx?p=2916274)
  - 悪い例は、エグゼクティブサマリーが目次のように読めること — [Umbrex](https://umbrex.com/resources/the-consulting-career-guide/storylining-and-deck-structure/)
- **つなぎ（トランジション）**:
  - 本論の各論点の間に Transition を入れる。Review で本論を振り返ってから結論に入る — [Doumont 2009](https://users.dcc.uchile.cl/~cgutierr/cursos/INV/presentaciones1.pdf)
  - ストーリーラインが事実 → 診断 → 提言と切り替わる箇所にセクション区切りを入れる — [Umbrex](https://umbrex.com/resources/the-consulting-career-guide/storylining-and-deck-structure/)
- **アペンディックス**:
  - 明確な仕事を持たないスライドはアペンディックスに移す — [Umbrex](https://umbrex.com/resources/the-consulting-career-guide/storylining-and-deck-structure/)
  - 説明用資料はシンプルにし、どんな質問にも答えられるようアペンディックスと FAQ を充実させる — [前田, ニュースイッチ 2020](https://newswitch.jp/p/20564), [ダイヤモンド社 2022](https://www.diamond.co.jp/book/9784478115152.html)
  - Amazon のメモでも補足データはアペンディックスに置く — [Anecdote 2018](https://www.anecdote.com/2018/05/amazons-six-page-narrative-structure/)
- **選択肢の提示**: 「2案」を提案して採択率を上げる — [前田, ダイヤモンド社 2022](https://www.diamond.co.jp/book/9784478115152.html)【個人の経験則。採択率の数値データは示されていない】
- **根拠の種類**: 組織規範と個人の経験則。実証研究なし。

### Inferences
- 結論の位置は「聞き手が意思決定者か（冒頭）、学術的な検証を追う聞き手か（末尾）」で切り替えるのが妥当と考えられる。迷う場合は Doumont 式に冒頭と末尾の両方に置くと、どちらの規範とも衝突しにくい。
- AI スキルの具体的な規則の候補:
  1. エグゼクティブサマリーの項目数と順序を、本論のセクション（またはスライドタイトル）と1対1で対応させる
  2. アジェンダは3〜5項目に収める（Doumont）
  3. タイトル通読で役割がないと判定したスライドは、削除ではなくまずアペンディックスに移す

### Gaps
- 「1分1枚」のような枚数の目安を検証した実証研究は見つからなかった。いずれも経験則か教育機関の規範。
- Kawasaki の原文（初出年と原文の表現）は 403 で未確認。
- アジェンダのスライドを置かないという立場（短いプレゼンでは不要とする意見など）の一次資料は見つからなかった。

---

## Q7. 推敲・レビューの工程（タイトル通読、"so what?" テスト、懐疑的な聞き手の視点、事前根回し）

### Takeaway
レビューは「構造の検査」が先で、「見た目の検査」が後。構造の検査は次の4つ。
- タイトルだけの通読（水平ロジック）
- 各スライドが1つの仕事を持ち、タイトルと中身が対応しているか（垂直ロジック）
- 観察だけで終わらず、示唆と行動まで書けているか（so what / now what）
- 懐疑的な聞き手なら何を突くか

ゴーストデッキの段階で上位者がレビューすることと、本番前に意思決定者へ個別に根回しする pre-wiring も、コンサルの標準的な工程として記録されている。「レッドチーム」という名前でのデッキレビューは一次資料で確認できなかった。

### Cited Findings

#### P27. 構造レビューの手順：タイトル通読 → 1枚1仕事 → so what / now what → 懐疑的な聞き手 → エグゼクティブサマリー単独テスト
- **原則**: デッキはまず論証として検査し、細部の作り込みはその後にする。
- **手順・チェック**:
  1. **タイトル通読**: タイトルだけを読み、筋の通った物語になっているか — [Umbrex](https://umbrex.com/resources/the-consulting-career-guide/storylining-and-deck-structure/), [Knaflic, horizontal logic](https://www.storytellingwithdata.com/blog/2013/12/horizontal-logic)。パートナーは顧客ミーティングの前にこの方法でデッキを確認する。上級役員がタイトルと出典行だけを読んでも推奨が分かるべきだ — [Deckary: Consulting Slide Standards](https://deckary.com/blog/consulting-slide-standards)【二次: ベンダーの経験則】
  2. **各図表がタイトルを支えているか** — [Umbrex](https://umbrex.com/resources/the-consulting-career-guide/storylining-and-deck-structure/)
  3. **so what テスト**: 何が重要か、なぜ重要か、次に何をすべきかが読み手に分かるか。観察から示唆へ移り、特定の判断や行動に結び付けているか — 同上。Reynolds の「だから何？」も同趣旨 — [SuperSummary](https://www.supersummary.com/presentation-zen/summary/)【二次】
  4. **論理の負荷試験**: 別の説明の可能性を検討し、前提を明示し、確信度を誇張していないか。懐疑的な顧客なら何に異議を唱え、何を誤解し、次に何を求めるか — [Umbrex](https://umbrex.com/resources/the-consulting-career-guide/storylining-and-deck-structure/)
  5. **エグゼクティブサマリー単独テスト**: 忙しいリーダーがサマリーだけを読んで、状況・結論・理由・推奨・求められる判断を把握できるか。目次のように読めたら書き直す — 同上
  6. **繰り返し**: 問いを研ぎ、ストーリーラインを強め、証拠を足し、構造を簡素にし、メッセージを磨く — 同上
- **ゴーストデッキ段階での上位者レビュー**: チームと上位者（パートナー）、場合によっては顧客が、ストーリーラインはまだ成り立つか、どの図表にデータの裏付けがあるか、何が足りないかを確認する — [Working with McKinsey 2013-07-06](https://workingwithmckinsey.blogspot.com/2013/07/McKinsey-presentations-ghost-decks.html?m=1)【準一次】
- **事前の根回し（pre-wiring）**: グループでの発表の前に、主要な意思決定者に個別に発見と推奨を説明し、当日に驚きがないようにする。発表や進捗レビューの前に、関係者全員を個別に案内する — [RightAttitudes 2008-05-27（Rasiel『The McKinsey Way』の要約）](https://www.rightattitudes.com/2008/05/27/pre-wiring-presentations-for-buy-in/)【二次】, [Goodreads 抜粋](https://www.goodreads.com/notes/6664932-the-mckinsey-way/11920478-jason/4ce50912-e309-4c7c-a616-825049424f9f)【二次】。反対意見として、時間がかかり、口を出す人が増えすぎるという実務家の指摘がある — [Unwritten Business Guide](https://unwrittenbusinessguide.substack.com/p/pre-wiring-the-art-of-getting-stakeholder)【二次】
- **その他の点検**:
  - 逆ストーリーボード（P10）
  - 3分ストーリーとエレベーターテストによるメッセージの明確さの検査（P12）
  - グランステスト（P13。投影用のみ）
  - 結論が目的と対応しているか — [東北大チェックリスト](https://web.tohoku.ac.jp/yusa/wp-content/uploads/2026/03/checklist_presen_0204.docx)
  - 1枚の作成時間を15分以内と決める（作り込みすぎの防止） — [前田, ニュースイッチ 2020](https://newswitch.jp/p/20564)
- **根拠の種類**: 組織規範（コンサル）と個人の経験則。
- **適用範囲・反対意見**: 時間が限られる場合は、手順1、3、5を優先する（推論）。

### Inferences
- AI が自己レビューする手順の案:
  1. タイトルだけを抜き出して通読し、1段落に要約できるか確かめる
  2. 各スライドについて「答えている問い」を1行で書き、書けないものはアペンディックス候補にする
  3. 「and」が必要なタイトルは分割する
  4. 観察だけのタイトルに so what を足す
  5. 懐疑的な役員になりきって反論を3つ挙げ、本文かアペンディックスで答える
  6. エグゼクティブサマリーだけで判断できるか確かめる
  7. 逆ストーリーボードで最初のドットダッシュと一致するか照合する
- 手順5は、レッドチームレビューに相当する工程を一人（または1つの AI）で行う方法として位置づけられる（推論。一次資料の裏付けは Umbrex の「懐疑的な顧客」のみ）。

### Gaps
- 「レッドチーム」と名付けたデッキレビューの手順を記録した一次資料は見つからなかった。
- コンサル会社の公式トレーニング資料（パートナーレビューの実際のチェックリスト）は公開資料では確認できなかった。Deckary などベンダーのブログの記述は、経験則として扱うべき。
- 推敲の工程がデッキの効果（理解度や採択率）に与える影響を測った実証研究は見つからなかった。
