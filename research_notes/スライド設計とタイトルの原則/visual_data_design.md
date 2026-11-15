# スライドの視覚設計・図・データ表現の原則（調査ノート）

調査日: 2026-11-15。対象はスライドに何をどう載せるか（文字量・レイアウト・タイポグラフィ・色・グラフ・強調・図とメッセージの対応）。タイトルの言い回しとデッキ構成は他の担当者の範囲なので、ここでは「タイトルと図が一致しているか」という視覚側の論点だけを扱う。

凡例:
- 原則は P1〜P26 の番号付きカードで記録した。各カードの項目は「原則 / 手順・チェック項目 / 良い例・悪い例 / 出典 / 根拠の種類 / 適用範囲・反対意見」。
- 根拠の種類は「実証研究」「組織規範」「個人の経験則」「根拠なし」で分けた。
- 「（本文未確認）」は、検索結果の抜粋や二次要約でしか確認できず、一次資料の本文を読めなかったもの。
- 効果量 d は Cohen's d（または同等の標準化平均差）。

---

## 1. 認知科学：Mayer のマルチメディア学習原則と認知負荷理論はスライドについて何を示しているか（箇条書き対図、文字密度、読みながら聞くこと）

### Takeaway
最も安定して支持されているのは、要らない要素を削ること（一貫性、効果量の中央値 0.86）と、説明文を図の該当箇所の近くに置くこと（空間的近接、0.82〜1.10）の二つ。話す内容をそのまま画面に書くことの害（冗長性）は、Mayer 自身の推定で 0.86 から 0.10 に下がっており、2〜3語の短いラベルならむしろ記憶を助けるという結果もある。したがって、規則は「文字を一律に禁じる」ではなく、「話す内容の全文を載せず、短いキーワードを図に添える」と書くのがよい。

### Cited Findings

#### P1 一貫性（coherence）：メッセージに必要のない文字・画像・装飾を入れない
- **原則**: メッセージの理解に要らない素材（面白いだけの写真、背景の飾り、細かすぎる補足）は入れない。
- **手順・チェック項目**: スライド上の要素を一つずつ取り除いてみて、それでアサーション（主張）の理解が損なわれないなら削る。補足の詳細は口頭か配布資料に回す。
- **良い例・悪い例**: 良い例は、主張を裏づける図と最小限のラベルだけのスライド。悪い例は、既定のテキストボックスに細かい情報を詰め込んで要点が埋もれたスライドで、事前知識の少ない学習者ほど要点と周辺情報を区別しにくくなる — [Garner & Alley 2013, IJEE](https://www.ijee.ie/articles/Vol29-6/23_ijee2791ns.pdf)
- **出典と数値**:
  - Mayer（UCSB 心理学教授）の 2014 年版 Cambridge Handbook の章では 23 件中 23 件で支持され、効果量の中央値は 0.86 — [Cambridge（検索抜粋、本文未確認）](https://www.cambridge.org/core/services/aop-cambridge-core/content/view/CD5B7AE1279A9AB81F8EEBB53DBEC86E)
  - Mayer 2021 のメタ分析を載せた UNH の配布資料では 19 件中 18 件、0.86 — [UNH 配布資料（取得は 503 エラー、検索抜粋のみ）](https://www.unh.edu/teaching-learning-resource-hub/sites/default/files/media/2023-06/itow-research-based-principles-for-designing-multimedia-instruction-mayer.pdf)
  - Mayer 2017（Journal of Computer Assisted Learning）のレビューでは 0.70 — [Zendy 抄録](https://zendy.io/title/10.1111/jcal.12197)
- **根拠の種類**: 実証研究（実験の集積とメタ分析）
- **適用範囲・反対意見**: 原則によっては、事前知識の多い学習者より少ない学習者で効果が強いという境界条件がある — [Mayer 2017](https://zendy.io/title/10.1111/jcal.12197)。グラフの装飾を巡っては、装飾があっても正確さは落ちず、2〜3週間後の想起はむしろ良かったという反証がある（P12 を参照）。

#### P2 信号化（signaling）：見出し・強調・矢印で構造と要点を示す
- **原則**: 何が重要か、要素同士がどうつながるかを、見出し・色・矢印・太字などの手がかりで明示する。
- **手順・チェック項目**: 各スライドに、要点を示す手がかりが一つあるか確認する（例: 主張文の見出し、注目する系列だけ色を付ける、矢印）。手がかりが複数あって互いに競合していないかも確認する。
- **良い例・悪い例**: 悪い例はトピック見出しと箇条書きの組み合わせ。Garner & Alley は、これが信号化に反する点を三つ挙げている。(1) 見出しはトピックを示すだけで、他のトピックとの関係や全体の中での位置を示さない。(2) 箇条書きは項目どうしの関係を表せず、一度に一種類の関係しか表現できない。(3) 箇条書きは情報同士のつながりを隠してしまう — [Garner & Alley 2013](https://www.ijee.ie/articles/Vol29-6/23_ijee2791ns.pdf)
- **出典と数値**: 効果量の推定は版によって幅がある。2014 年版は 28 件中 24 件、中央値 0.41 — [Cambridge（検索抜粋）](https://www.cambridge.org/core/services/aop-cambridge-core/content/view/CD5B7AE1279A9AB81F8EEBB53DBEC86E)。2021 年版は 28 件中 26 件、0.70 — [UNH 配布資料（検索抜粋）](https://www.unh.edu/teaching-learning-resource-hub/sites/default/files/media/2023-06/itow-research-based-principles-for-designing-multimedia-instruction-mayer.pdf)。2017 年レビューでは 0.46 — [Zendy](https://zendy.io/title/10.1111/jcal.12197)。
- **根拠の種類**: 実証研究
- **適用範囲・反対意見**: データ可視化の分野では、強調（focus）を加えると主結論を捉える確率が約 2.5 倍になったという独立の実験がある（P9 を参照）。

#### P3 空間的近接（spatial contiguity）：説明の文字は図の該当箇所の近くに置く
- **原則**: ラベルや説明文は、それが指す図の部位のすぐ隣に置く。凡例や別枠の説明に目を往復させない。
- **手順・チェック項目**: グラフは凡例をやめて系列の端に名前を直接書く。図解では引き出し線で部位に名前を付ける。説明文の段落を図から離れた位置に置かない。
- **良い例・悪い例**: 良い例は、折れ線の右端に項目名を書いたグラフ。悪い例は、凡例が枠外にあって色で照合させるグラフ — [伝わるデザイン「配色（バリアフリー）」](https://tsutawarudesign.com/universal1.html)、[Storytelling with Data（直接ラベル）](https://www.storytellingwithdata.com/blog/2019/5/13/declutter-and-question-defaults)
- **出典と数値**: 2014 年版は 22 件中 22 件、効果量の中央値 1.10 で、扱った 4 原則の中で最大 — [Cambridge（検索抜粋）](https://www.cambridge.org/core/services/aop-cambridge-core/content/view/CD5B7AE1279A9AB81F8EEBB53DBEC86E)。2021 年版は 9 件中 9 件、0.82 — [UNH 配布資料（検索抜粋）](https://www.unh.edu/teaching-learning-resource-hub/sites/default/files/media/2023-06/itow-research-based-principles-for-designing-multimedia-instruction-mayer.pdf)。2017 年レビューでは 0.79 — [Zendy](https://zendy.io/title/10.1111/jcal.12197)。
- **根拠の種類**: 実証研究
- **適用範囲・反対意見**: 反対する実証結果は見つからなかった。

#### P4 冗長性（redundancy）：話す内容の全文をスライドに書かない。ただし短いキーワードのラベルは有効
- **原則**: 発表者が話す文章をそのまま画面に載せない。画面の文字は、図に添える 2〜3 語の要点ラベルにとどめる。
- **手順・チェック項目**: 画面の文字と台本を照合し、同じ文が連続して現れたら削る。残す文字は図の部位に付ける短いキーワードにする。
- **良い例・悪い例**: 悪い例は、既定のテキストボックスに文章を書き、それを読み上げる発表。PowerPoint の既定のテキストボックスは文字を増やすほどフォントを自動で縮めるため、冗長になりやすい — [Garner & Alley 2013](https://www.ijee.ie/articles/Vol29-6/23_ijee2791ns.pdf)
- **出典と数値（版によって大きく食い違う点に注意）**:
  - 2014 年版: 16 件中 16 件、0.86 — [Cambridge（検索抜粋）](https://www.cambridge.org/core/services/aop-cambridge-core/content/view/CD5B7AE1279A9AB81F8EEBB53DBEC86E)
  - 2017 年レビュー: 0.87 — [Zendy](https://zendy.io/title/10.1111/jcal.12197)
  - 2021 年メタ分析: 12 件中 8 件、0.10 — [UNH 配布資料（検索抜粋）](https://www.unh.edu/teaching-learning-resource-hub/sites/default/files/media/2023-06/itow-research-based-principles-for-designing-multimedia-instruction-mayer.pdf)
  - Adesope & Nesbit 2012（Journal of Educational Psychology 104 巻 250–263 頁）のメタ分析: 音声と文字を併用した場合と文字だけの場合に差はなく、併用は音声だけより成績が良かった。効果は事前知識、提示の速さ（システム制御か学習者制御か）、図やアニメーションの有無で変わった。冗長な文字が役立ったのは、事前知識が少なく、システムが速さを決め、図を同時に示さない条件だった — [WSU リポジトリ](https://rex.libraries.wsu.edu/esploro/outputs/journalArticle/Verbal-Redundancy-in-Multimedia-Learning-Environments/99900601157101842)、[Adesope 博士論文（SFU、効果量 48 件・報告 32 本）](https://summit.sfu.ca/item/9947)
  - Mayer & Johnson 2008（JEP 100 巻 380–386 頁）: 雷の発生を説明する教材で、ナレーションから取った 2〜3 語のラベルを画面に出すと、保持テストの成績は上がったが転移テストは変わらなかった。Yue, Bjork & Bjork 2013 は、ナレーションと完全に同じ文を出すと学習が損なわれ、要点の語句を強調すると想起が改善したと報告している — [Yue, Bjork & Bjork 2013（UCLA）](https://sites.lifesci.ucla.edu/psych-bjorklab/wp-content/uploads/sites/13/2016/07/YueBjorkBjork2013_redundancy.pdf)
- **根拠の種類**: 実証研究（ただし効果量は不安定）
- **適用範囲・反対意見**: 聴衆が文字だけで読める資料（発表者がいない資料）は対象外で、P14 を参照。

#### P5 時間的近接・段階提示：図の部分は、それを話すタイミングで出す
- **原則**: 図や文字を一度に全部見せず、説明に合わせて部分ごとに表示する。
- **手順・チェック項目**: 複雑な図は、説明の順番に合わせて分けて表示する（アニメーションのビルドを使う）。装飾目的のアニメーションは使わない。
- **良い例・悪い例**: Garner & Alley の実験では、アサーション・エビデンス条件の 11 枚のうち 8 枚で、従来条件では最初から見えている図の一部を、台本で触れたときに表示していた — [Garner & Alley 2013](https://www.ijee.ie/articles/Vol29-6/23_ijee2791ns.pdf)。Gene Zelazny（コンサルティング会社の元ビジュアルコミュニケーション部門ディレクター）は「要点を示す助けにならないならアニメーションは使うな」と述べている — [Atkinson「Five Experts Dispute Edward Tufte」](https://www.robertgaskins.com/files/five-experts-dispute-edward-tufte-on-powerpoint-sociable-media-cliff-atkinson.htm)
- **出典と数値**: 時間的近接は 8 件中 8 件、効果量の中央値 1.31（Mayer 2021） — [UNH 配布資料（検索抜粋）](https://www.unh.edu/teaching-learning-resource-hub/sites/default/files/media/2023-06/itow-research-based-principles-for-designing-multimedia-instruction-mayer.pdf)
- **根拠の種類**: 実証研究。アニメーションの節度は個人の経験則。
- **適用範囲・反対意見**: 配布やオンライン閲覧用の静的な資料ではビルドが再現されないので、最終状態だけで意味が通る必要がある（推論）。

### Inferences
- 一貫性と空間的近接は、どの版でも効果量が大きく安定しているので、スキルのチェック項目として優先度が最も高い。冗長性は版によって 0.86〜0.10 と揺れるので、「文字禁止」ではなく「話す文の全文転載禁止、キーワードのラベルは可」という条件付きの規則にするのが根拠に合う。
- 多くの原則は事前知識の少ない聴衆ほど効果が大きいので、専門外の聴衆向けのスライドほど厳しく適用する価値がある。
- Mayer の実験は主に教材（説明的なマルチメディア）で行われており、ビジネスの説得型プレゼンにそのまま当てはまるかは直接検証されていない。

### Gaps
- Mayer 2021 のメタ分析の原典（Multimedia Learning 第 3 版）と UNH 配布資料の本文は取得できなかった（503 エラー）。数値は検索結果の抜粋から得たもの。分節化（segmenting）原則の効果量も確認できなかった。
- Sweller（認知負荷理論）の一次文献でスライドを直接扱ったものは確認できなかった。検索結果の中に Kalyuga & Sweller 2014 が「冗長な素材の追加は学習に有害」と結論したとする二次言及があったが、出典ページを特定できなかった。
- 箇条書きと視覚表現を比べた研究で、工学教育以外の分野（ビジネス、一般聴衆）のものは見つからなかった。

---

## 2. Michael Alley のアサーション・エビデンス：視覚的根拠として何が良く、箇条書きをどう避けるか

### Takeaway
アサーション・エビデンス方式（主張を文で書いた 2 行以内の見出しと、それを裏づける視覚的根拠）は、工学部生 110 人の実験で理解（d=0.81）、遅延テスト（d=0.89）、誤概念の少なさ（d=0.47）、主観的な負荷の低さのいずれでも従来型を上回った。一方で、比較対象の従来型スライドの質が低い、単純な事実の想起では差がない、効果は控えめ、といった批判もある。「本文は図で示す」は強い既定にしつつ、絶対の規則にはしないのが妥当。

### Cited Findings

#### P6 本文は箇条書きではなく視覚的根拠で組む
- **原則**: スライドの本文は、見出しの主張を裏づける視覚的根拠（写真、グラフ、表、図、視覚的に配置した語）で構成し、箇条書きの羅列にしない。
- **手順・チェック項目**:
  - 見出しは主張の文にし、2 行以内に収める。
  - 本文に、関連する図を必ず一つ置く。
  - 本文の語数はできるだけ少なくする。
  - これらは Garner & Alley の実験で使われた作成基準 — [Garner & Alley 2013](https://www.ijee.ie/articles/Vol29-6/23_ijee2791ns.pdf)
- **良い例・悪い例**: 実験で使った 1 枚あたりの平均語数（英語）は、アサーション・エビデンス条件が 21.2 語（全スライドに関連図あり）、従来条件が 41.5 語（関連図があるのは 64%） — [Garner & Alley 2013](https://www.ijee.ie/articles/Vol29-6/23_ijee2791ns.pdf)
- **出典と数値**: Garner（Old Dominion 大学）と Alley（Penn State 工学部）、International Journal of Engineering Education 29 巻 6 号、2013 年、MRI の仕組みの解説。被験者は 110 人（従来 51、AE 59）で、台本は両条件とも同じ 1000 語。結果は次のとおり — [Garner & Alley 2013](https://www.ijee.ie/articles/Vol29-6/23_ijee2791ns.pdf)
  - 記述式テストの総合点: t(93.43)=3.67、p<0.001、d=0.81
  - 1 週間後の遅延テスト: t(93)=4.34、p<0.001、d=0.89
  - 誤概念の総数（従来 1.54、AE 0.98）: F(1,108)=9.84、p<0.01、d=0.47
  - 主観的な心的努力（7 段階）: 従来 3.61、AE 3.01、d=−0.50
  - 事実・統計の想起を問う多肢選択問題では差がなかった。
- **関連研究**:
  - 2011 年の ASEE 論文: 複雑な概念の理解ではアサーション・エビデンスが上回った — [ASEE 2011](https://peer.asee.org/assertion-evidence-slides-appear-to-lead-to-better-comprehension-and-recall-of-more-complex-concepts.pdf)
  - 同じ系統の研究: 単純な統計の短期想起では従来型が上回り、要点の長期想起ではアサーション・エビデンスが上回った — [Penn State 研究ページ](https://writing.engr.psu.edu/research.html)
  - Wolfe, Alley & Garner 2012: 有意差なし（傾向のみ）。著者らは、従来型スライドの図の質が結果を左右した可能性に触れている — [Penn State Pure](https://pure.psu.edu/en/publications/high-quality-visual-evidence-on-presentation-slides-may-offset-th-2/)
  - Aippersbach, Alley & Garner 2013: アサーション・エビデンスでスライドを作った発表者のほうが内容をよく理解していた — [ASEE](https://peer.asee.org/how-slide-design-affects-a-student-presenter-s-understanding-of-the-content)
- **根拠の種類**: 実証研究（小規模、工学教育）
- **適用範囲・反対意見**:
  - 2013 年の実験では、AE 群の自己評価の事前知識が有意に高かった（2.87 対 2.24）。ただし学習成果とは相関しなかった — [Garner & Alley 2013](https://www.ijee.ie/articles/Vol29-6/23_ijee2791ns.pdf)
  - David Farkas（ワシントン大学）は 2010 年 3 月の非公式文書で次のように批判している — [Farkas 2010](https://faculty.washington.edu/farkas/dfpubs/Farkas-Assessment%20Of%20Alleys%20Slide%20Design.pdf)
    - 比較に使った従来型スライドが特に出来の悪い例で、統計的には有意でも効果は意外に控えめ。
    - 発表者の役割を無視している。
    - すべての主張に図を求めると役に立たない図が増え、図が小さくなる。
    - 短く練られた箇条書きはそれ自体有害ではない。
    - ただし、文の形のスライドタイトルには利点があると認めている。

#### P7 図は「説明する」ものだけを使い、飾りや本文の重複には使わない
- **原則**: 視覚的根拠は、主張を説明・整理・解釈する図に限る。雰囲気づくりの写真や、本文の内容を絵に置き換えただけの図は根拠にならない。
- **手順・チェック項目**: 図ごとに「この図を消すと主張の裏づけが弱くなるか」を確認し、弱くならないなら削る。視覚的根拠には写真、グラフ、表、図、視覚的に配置した語が含まれる — [Garner & Alley 2013](https://www.ijee.ie/articles/Vol29-6/23_ijee2791ns.pdf)
- **良い例・悪い例**: 先行研究では、トピックと箇条書きのスライドのうち図があるのは 40〜60% だった。さらに、大学の心理学教科書の付属スライドで「説明的な図」の基準を満たしたのは 10% ほどにとどまった。多くの図は状況的な興味や見た目の楽しさを足すだけで、図とスライドの目的が切り離されていた — [Garner & Alley 2013](https://www.ijee.ie/articles/Vol29-6/23_ijee2791ns.pdf)。Farkas も、技術発表には装飾的・半装飾的な（テーマ的な）画像が多すぎると指摘している — [Farkas 2010](https://faculty.washington.edu/farkas/dfpubs/Farkas-Assessment%20Of%20Alleys%20Slide%20Design.pdf)
- **根拠の種類**: 実証研究（記述的な調査と一貫性原則）
- **適用範囲・反対意見**: Farkas は、技術的でないマーケティング向けの発表では Garr Reynolds や Nancy Duarte 流の印象重視のグラフィックを支持している — [Farkas 2010](https://faculty.washington.edu/farkas/dfpubs/Farkas-Assessment%20Of%20Alleys%20Slide%20Design.pdf)。

### Inferences
- AI が生成するスライドでは、「トピック見出しと箇条書き」が既定の失敗パターンになりやすい（PowerPoint の既定がそうなっているため）。スキルでは「本文に関連図が一つ以上あるか」「本文の文字が箇条書きの羅列だけになっていないか」を検査項目にするとよい。ただし Farkas の批判を踏まえ、図にできない内容（手順、定義、引用）まで無理に図にさせない例外を設けるべき。
- 単純な事実を覚えさせる場面では従来型と差がないので、「図が必須」の規則が効くのは概念・プロセス・因果を説明するスライドに限られる。

### Gaps
- 2011 年 ASEE 論文と 2012 年 Wolfe らの論文の効果量は確認していない。
- assertion-evidence.com のトップページには、視覚的根拠の具体的な基準（図の大きさ、本文語数の上限など）は載っていなかった。詳細はチュートリアル（craftscicom.org）にあるとされるが未取得。

---

## 3. スライド向けのデータ可視化：Knaflic、Tufte とその批判、Few、そしてグラフとタイトルの一致

### Takeaway
実験で最も効果がはっきりしているのは「強調（focus）」で、伝えたい系列だけを対比色にし、結論を述べる見出しを付けると、主結論を捉える確率が約 2.5 倍になった。一方、「デクラッター」（枠線やグリッド線を消す）は専門的に見えるようになるだけで、理解は改善しなかった。Tufte の最小主義（データインク）には、装飾されたグラフのほうが長期記憶に残るという反証があり、発表でのデータ密度を巡っては専門家の意見が割れている。

### Cited Findings

#### P8 グラフの種類は、見せたい関係（時系列、順位、構成比など）で選ぶ
- **原則**: まず、見せたいのが時系列、順位、構成比、偏差、分布、相関のどれかを決め、それに合った表現を選ぶ。
- **手順・チェック項目**: 時系列の傾向は折れ線、個々の値の比較や順位は棒（時系列で個々の値を見せたい場合は縦棒）を使う。角度（円グラフの扇形）で値を読ませるのは避ける。
- **良い例・悪い例**: Few（Perceptual Edge 主宰）は、点・線・棒・箱という表現手段と、時系列・順位・部分と全体などの関係を組み合わせた一枚の表（Graph Selection Matrix）で、各組み合わせを「よく使う／時々使う／使わない」に分類している — [Few, Graph Selection Matrix（2004–2018）](https://eda.seas.gwu.edu/2024-Fall/content/graph-selection-matrix.pdf)。Few は、棒は個々の値を強調するのに使い、折れ線は全体の変化のパターンを見て比べやすくすると書いている。また、値を表す視覚属性のうち角度（円グラフの扇形）を含め、うまく機能するものは少ないとしている — [Few 2004, Perceptual Edge](https://online225.psych.wisc.edu/wp-content/uploads/225-Master/225-UnitPages/Unit-12/Few_PerceptualEdge_2004.pdf)
- **根拠の種類**: 個人の経験則に、知覚研究に基づく組織的な指針が加わったもの（Few の書籍は知覚研究を引いているが、この表自体の効果は検証されていない）
- **適用範囲・反対意見**: Few は Andrew Abela のグラフ選択チャートを単純化しすぎで誤解を招くと批判しており、選択ガイドの間でも意見が分かれている — [Perceptual Edge ブログ](https://www.perceptualedge.com/blog/?p=2080)。円グラフについての Few の明示的な評価は、今回取得した抜粋には含まれていなかった。

#### P9 強調（focus）は一か所に絞り、他はグレーで後ろに下げる
- **原則**: 色・大きさ・位置といった前注意属性は控えめに使い、聴衆に見てほしい一点だけに当てる。
- **手順・チェック項目**: 既定ではすべての系列をグレーにし、主張に関わる系列や点だけを強調色にする。強調色は一色にし、デッキ全体で同じ意味に使う。
- **良い例・悪い例**: Storytelling with Data（Knaflic 主宰）は、大きさ・色・ページ上の位置を「控えめに使えば」注意を誘導できると説明している — [SWD「where are your eyes drawn?」](https://www.storytellingwithdata.com/blog/whereareyoureyesdrawn)。SWD の Mike Cisneros は「色はもっと控えめに、しかし意図的に使い、重要な要素を目立たせる」と書いている — [SWD「use color to focus or to compete for attention」（3 月 14 日付、2024 年頃）](https://www.storytellingwithdata.com/blog/use-color-to-focus-or-to-compete-for-attention)。『伝わるデザイン』も、注目するデータ以外はグレーにする、色相を変えずに明度・彩度で差を付ける、と勧めている — [伝わるデザイン「配色（バリアフリー）」](https://tsutawarudesign.com/universal1.html)
- **出典と数値**: Ajani, Lee, Xiong, Nussbaumer Knaflic, Kemper, Franconeri「Declutter and Focus」（IEEE TVCG, 2021）。6 種類のグラフをそれぞれ「雑然」「デクラッター済み（グレーと黒のみ）」「デクラッター＋強調（主要な傾向を対比色にし、見出しかキャプションを付けたもの）」の 3 版で用意し、24 人に 1 枚 10 秒ずつ見せた後、手で描き直して結論を書かせた。強調版では、デクラッターだけの版より主結論を捉える確率が約 2.5 倍になり、主要な傾向の描き直しも正確だった。一部の被験者は、強調版を「意図を押し付けている」と感じて信頼性を低く評価した — [Kellogg Insight（2021-12-09、Roberta Kwok）](https://insight.kellogg.northwestern.edu/article/do-people-understand-your-data-visualizations)、[論文 PDF（NSF PAR）](https://par.nsf.gov/servlets/purl/10350268)
- **根拠の種類**: 実証研究（小標本）と、実務家の経験則
- **適用範囲・反対意見**: SNS のように関与度の低い場では、色をもっと大胆に使わないと気づかれないこともある — [SWD Cisneros](https://www.storytellingwithdata.com/blog/use-color-to-focus-or-to-compete-for-attention)。

#### P10 見出しの主張と、強調しているデータ・色・ラベルを一致させる
- **原則**: タイトル（見出し）が述べている結論と、グラフで強調している系列・点が同じものを指しているようにする。文字・凡例・グラフで色の意味を揃える。
- **手順・チェック項目**: (1) 見出しに出てくる対象（例: 「A 社の売上が 2024 年に逆転」）がグラフ上で強調色になっているか。(2) 見出しや本文でその対象に触れるときの色が、グラフの系列の色と同じか。(3) 強調色が、見出しで触れていない系列に使われていないか。
- **良い例・悪い例**: Ajani らの「強調」条件は、対比色と見出し（またはキャプション）を組み合わせたもの — [Kellogg Insight](https://insight.kellogg.northwestern.edu/article/do-people-understand-your-data-visualizations)。Cisneros は「文字・凡例・グラフで色を統一する」ことを勧め、データの近くに置く選択的なラベルを評価している — [SWD Cisneros](https://www.storytellingwithdata.com/blog/use-color-to-focus-or-to-compete-for-attention)。『伝わるデザイン』は、同じ対象には「きちんと同じ色」を使い、違う色で混乱させないよう求めている — [伝わるデザイン「配色」](https://tsutawarudesign.com/miyasuku5.html)。Garner & Alley は、文の見出しが本文の情報を解釈する「錨」になると説明している — [Garner & Alley 2013](https://www.ijee.ie/articles/Vol29-6/23_ijee2791ns.pdf)
- **根拠の種類**: 実証研究（Ajani らの、見出しと強調をまとめた介入）と組織・実務の規範
- **適用範囲・反対意見**: Ajani らの研究は見出しと色の強調を一体の介入として扱っており、それぞれ単独の効果は分けて測っていない（検索結果の要約による）。

#### P11 デクラッター（枠線・グリッド線・マーカーを消し、軸を整理し、直接ラベルを付ける）は「見た目の信頼感」のためと位置づける
- **原則**: データを伝えない線や記号は取り除く。ただし、それで理解が上がるとは限らない。
- **手順・チェック項目**: Knaflic『Storytelling with Data』（2015）が挙げる 6 段階 — [二次要約（Medium）](https://medium.com/analytics-vidhya/six-important-lessons-from-storytelling-with-data-by-nussbaumer-knaflic-part-2-737d8478bc0b)
  1. グラフの枠線を消す
  2. グリッド線を消す
  3. データマーカーを消す
  4. 軸ラベルを整理する
  5. データに直接ラベルを付ける
  6. 色を一貫させる

  枠線は余白で置き換え、グリッド線は聴衆が正確な値を読む必要がある場合以外は消す。その場合も、必要な点に直接値を書くほうがよい — [SWD「declutter! (and question defaults)」2019-05-13](https://www.storytellingwithdata.com/blog/2019/5/13/declutter-and-question-defaults)
- **良い例・悪い例**: 悪い例はツールの既定のまま出したグラフ（枠線、濃いグリッド線、凡例、全点のマーカー付き）。
- **出典と数値**: Ajani ら 2021 では、デクラッター版は専門的に見えると評価されたが、描き直しや結論の記述は雑然版と有意に変わらなかった。Franconeri は「予測された認知的な利点は見つからなかった」と述べている — [Kellogg Insight](https://insight.kellogg.northwestern.edu/article/do-people-understand-your-data-visualizations)
- **根拠の種類**: 実務家の経験則。理解への効果は実証研究で否定的、見た目の評価への効果は肯定的。
- **適用範囲・反対意見**: 「理解のため」という理由づけは弱い。信頼感・専門性という印象のための整形として扱うのが妥当。

#### P12 データインクの最大化と装飾の扱い：データを邪魔する装飾は禁止、記憶を助ける装飾は条件付きで許容
- **原則**: データの読み取りを邪魔する装飾（グラフの背後の画像、立体化など）は入れない。一方、データと関係のある図像的な装飾は、理解を損なわずに記憶を助けることがある。
- **手順・チェック項目**: グラフの背景に写真やテクスチャを敷かない。装飾を加える場合は、データの外側に置き、データの意味と関係するものに限る。
- **良い例・悪い例**: Bateman, Mandryk, Gutwin ら「Useful Junk?」（CHI 2010, pp. 2573–2582）は、Nigel Holmes の装飾的なグラフと最小限のグラフを比べた。読み取りの正確さは同等で、直後の想起も同等だったが、2〜3 週間後の想起は装飾版が有意に良かった。ただし、装飾の位置と機能によって結果は変わり、背景画像は解釈を難しくした — [Bateman et al. 2010 PDF](https://vis.csail.mit.edu/classes/6.859/readings/pdfs/Bateman-UsefulJunk.pdf)
- **出典（Tufte 側）**: Edward Tufte『The Cognitive Style of PowerPoint』は 2003 年に Graphics Press から 27 頁の小冊子として出版され、2006 年に改訂されて『Beautiful Evidence』に収録された — [edwardtufte.com「new edition」](https://www.edwardtufte.com/notebook/new-edition-of-the-cognitive-style-of-powerpoint/)。主張の中心は、PowerPoint の認知スタイルが思考と伝達を損なうこと、PowerPoint で示す図は紙の配布資料より情報が少ないことにある — [Farkas「Toward a Better Understanding of PowerPoint」（検索抜粋）](https://faculty.washington.edu/farkas/dfpubs/Farkas-Toward%20A%20Better%20Understanding%20of%20PowerPoint.pdf)
- **根拠の種類**: Tufte は個人の経験則と事例分析、Bateman らは実証研究
- **適用範囲・反対意見**: Bateman ら自身、すべてのグラフをこの様式で作ることを勧めるのには慎重で、最小主義の前提の一部に疑問を投げたにとどまる — [Bateman et al. 2010](https://vis.csail.mit.edu/classes/6.859/readings/pdfs/Bateman-UsefulJunk.pdf)。後の論評には、装飾されたグラフをよく覚えていても、メッセージが伝わらなければ意味がないという懐疑もある — [検索結果の論評（Medium）](https://medium.com/@jopuga/useful-junk-the-effects-of-visual-embellishment-on-comprehension-and-memorability-of-charts-cf9b7539dae0)。

#### P13 発表用スライドのデータ密度は低く、詳細は配布資料に分ける
- **原則**: 口頭発表のスライドには、一目で取れる量の情報だけを載せる。精読用のデータは別の文書や配布資料にする。
- **手順・チェック項目**: 1 枚のグラフで系列や注記が多すぎて、読み上げずには説明できない場合は、分割するか配布資料に回す。
- **良い例・悪い例**: Tufte の中心事例は、2003 年のコロンビア号事故に関する NASA のスライドで、19 行の文字、6 段階の階層、11 の文が載っていたと紹介されている — [Farkas（検索抜粋）](https://faculty.washington.edu/farkas/dfpubs/Farkas-Toward%20A%20Better%20Understanding%20of%20PowerPoint.pdf)、[edwardtufte.com「the Columbia evidence」](https://www.edwardtufte.com/notebook/the-columbia-evidence/)
- **出典（意見の対立）**: Cliff Atkinson がまとめた反論（2004 年）が主な材料 — [Atkinson「Five Experts Dispute Edward Tufte on PowerPoint」](https://www.robertgaskins.com/files/five-experts-dispute-edward-tufte-on-powerpoint-sociable-media-cliff-atkinson.htm)
  - Don Norman（Nielsen Norman Group 共同創業者）: 「発表が論文ほど多くの情報を示すことは決してできない」「Tufte は発表の聴衆を、吸収しきれないほどのデータで圧倒してしまう」
  - Seth Godin: 「一目で情報を伝えられれば勝ちだ」
  - Richard Mayer: PowerPoint は「方法」ではなく「媒体」で、本と同じく使い方次第だ
  - Bob Horn（スタンフォード大学）: 箇条書きで因果関係を示しにくいという点は Tufte に同意しつつ、問題はツールではなく技能の不足だとする
  - Jean-luc Doumont も小冊子ほどの長さの反論を書いており、Tufte の主張を支える統計的証拠が乏しいと指摘している — [Doumont の反論（Scribd）](https://www.scribd.com/document/680475144/doumont-responds-to-tufte)
- **根拠の種類**: 個人の経験則同士の対立（実証研究はない）
- **適用範囲・反対意見**: Farkas は、注意深く言葉を選べば、発表用のデッキが単独で読む資料としてもある程度機能すると述べている — [Farkas 2010](https://faculty.washington.edu/farkas/dfpubs/Farkas-Assessment%20Of%20Alleys%20Slide%20Design.pdf)。

### Inferences
- スライド生成スキルで最も効果が見込めるのは、「見出しが述べる対象を一色で強調し、残りをグレーにする」という強調の規則（P9・P10）。デクラッターは見た目の印象を上げる作業として、優先度を一段下げてよい。
- Tufte の高密度の主張と Norman・Godin の一目の主張は、媒体が違うことで両立する。発表スライドでは一目で読めることを優先し、詳細は配布資料に回す。スキルには「発表用か、読む資料か」を最初に判定する分岐を入れるべき。
- 装飾の扱いは、「データの背後や上に重ねない」「データの意味と無関係な絵を入れない」という二つの禁止に絞ると、Bateman らの結果とも矛盾しない。

### Gaps
- Tufte の本文（Cognitive Style of PowerPoint）を直接読めなかった（edwardtufte.com の該当ページは 404）。「スライド 1 枚あたりの語数」に関する Tufte の数値は確認できなかった。
- Knaflic の書籍本文は未確認で、6 段階は二次要約から得た。
- Ajani らの論文本文は未取得で、オッズ比や検定値は確認していない。
- Few の円グラフに関する明示的な評価（『Save the Pies for Dessert』など）は取得していない。

---

## 4. 日本語スライドのデザイン実務：書体、行間、ジャンプ率、揃え、余白、色数、装飾の回避

### Takeaway
日本語の実務指針は主に『伝わるデザインの基本』（高橋佑磨・片山なつ、公式サイト tsutawarudesign.com）に依拠している。主な数値は、行間は文字サイズの約 70%、字間は 5%、色は 4 色まで、揃えは左揃えが基本、MS ゴシック・HG ゴシック・MS 明朝は避けて太字に対応したモダンなゴシック体を使う、というもの。いずれも著者の経験に基づく規範で、日本語スライドを対象とした実証研究は見つからなかった。ジャンプ率に数値で裏づけられた基準はない。

### Cited Findings

#### P14 和文書体は、太字に対応したモダンなゴシック体を使い、欧文はサンセリフで揃える
- **原則**: スライドの本文と見出しには、複数のウェイトを持つゴシック体を使う。古い字形のシステムフォントや擬似ボールドは使わない。
- **手順・チェック項目**:
  - 推奨: メイリオ、游ゴシック（Windows）、ヒラギノ角ゴシック（Mac）、BIZ UD ゴシック、Noto Sans CJK JP（無料）
  - 避ける: MS ゴシック、HG ゴシック、MS 明朝
  - 太字は、太字に対応した書体で付ける（擬似ボールドにしない）。
  - 日本語は斜体にしない。
  - 欧文はゴシック体に Segoe UI や Arial などのサンセリフを合わせ、見た目の大きさと太さを揃える。メイリオに Calibri を合わせると欧文が小さく見えるので、Segoe UI か Tahoma にする。
  - 出典: [伝わるデザイン「フォントの選び方」](https://tsutawarudesign.com/yomiyasuku2.html)
- **良い例・悪い例**: 悪い例は、MS ゴシックに太字を指定したもの（擬似ボールド）。『伝わるデザイン』は、擬似ボールドは不格好で十分に太くならず可読性も下がると説明している。MS ゴシックを避ける理由として、字形が直線的で雑なこと、文字ごとに太さがばらつくこと、太字に対応していないこと、非 ClearType で画面上の輪郭がガタつくことを挙げている — [伝わるデザイン「フォントの選び方」](https://tsutawarudesign.com/yomiyasuku2.html)。文字を縦や横に伸ばして縦横比を変えると、読み間違いが起きやすい — [伝わるデザイン「文字組み」](https://tsutawarudesign.com/yomiyasuku4.html)
- **根拠の種類**: 個人の経験則（著者らの書籍と公式サイト）
- **適用範囲・反対意見**: 明朝体は、文章量の多い Word 文書などには向くとされる（游明朝、ヒラギノ明朝、BIZ UD 明朝、Noto Serif CJK JP） — [伝わるデザイン](https://tsutawarudesign.com/yomiyasuku2.html)。ただしスライドではゴシック体が既定。

#### P15 行間は文字サイズの約 70%（行送り約 1.7 倍）、字間は約 5%、1 行は短すぎず長すぎず
- **原則**: 日本語の行間（行と行のあき）は文字サイズの 0.7 文字分前後にする。字間はわずかに空ける。
- **手順・チェック項目**: 
  - 行間は「フォントサイズの 70% 前後」。ゴシック体は明朝体より広めにし、1 行の文字数が少ないときは狭める。PowerPoint では「段落 → 行間 → 倍数」で調整する — [伝わるデザイン「文字組み」](https://tsutawarudesign.com/yomiyasuku4.html)
  - 字間は文字サイズの 5% 程度（20pt なら 1pt）。PowerPoint の「広く」は広すぎることが多い。英単語は「標準」に戻す — [同上](https://tsutawarudesign.com/yomiyasuku4.html)
  - 1 行の長さ: 日本語で 1 行 10 文字以下、英語で 3 語以下になると読みにくい。ただし「明確な基準はない」と明記されている。長すぎる行も次の行を見失いやすい — [同上](https://tsutawarudesign.com/yomiyasuku4.html)
- **良い例・悪い例**: 箇条書きでも行間を十分にとったほうが読みやすい。かぎ括弧や中黒の前後に余計なアキが出る場合は、字間を詰めるか半角記号で直す — [伝わるデザイン「文字組み」](https://tsutawarudesign.com/yomiyasuku4.html)
- **出典の食い違い**: 愛知県総合教育センターの教材は、行間を文字サイズの 70% 前後としつつ、固定値では文字サイズの 1.5〜1.8 倍という目安も挙げている。文書向けで、スライド専用の基準ではない — [愛知県教育資料（docx）](https://apec.aichi-c.ed.jp/kyouka/jouho/contents/2021/jissen/16.files/moji.docx)。「行間 70%」は行送りに直すと約 1.7 倍で、1.5〜1.8 倍の範囲に収まる（推論による換算）。
- **根拠の種類**: 個人の経験則と、教育機関の規範
- **適用範囲・反対意見**: 1 行の長さについては、出典自身が「明確な基準はない」と述べている。

#### P16 揃えは左揃えを基本にし、1 枚の中で揃え方を混ぜない
- **原則**: 横書きの文章、小見出し、タイトルは左揃えにする。中央揃えは 1 文だけ、図が 1 つだけの場合などに限る。
- **手順・チェック項目**: 同じページで中央揃えと左揃えを混ぜない。「全部中央揃えにするか、全部左揃えにする」。右揃えはまれ — [伝わるデザイン「文字組み」](https://tsutawarudesign.com/yomiyasuku4.html)
- **良い例・悪い例**: 悪い例は、複数行の段落を中央揃えにしたもの。行頭の位置がばらばらになり、段落として認識しにくくなる — [同上](https://tsutawarudesign.com/yomiyasuku4.html)
- **根拠の種類**: 個人の経験則
- **適用範囲・反対意見**: 反対する出典は見つからなかった。高橋佑磨氏は、資料の見やすさに注意すべき要素として「フォント」「行間」「余白」「揃える」「文字の強弱」の五つを挙げている — [PRESIDENT（2016-03-08 掲載、2015-02-02 号、記者 鈴木工）](https://president.jp/articles/-/17536)

#### P17 文字サイズの段階は 2〜3 に絞り、見出しと本文の差（ジャンプ率）で階層を示す
- **原則**: 重要度ごとに文字サイズを細かく分けない。見出しと本文の大きさの差で階層を作る。
- **手順・チェック項目**: スライド全体で使う文字サイズは 2〜3 段階（例: 見出し、本文、注記）にする。強調は大きさか太さのどちらかで統一する。
- **出典と数値**:
  - 高橋佑磨氏の解説記事: 重要度に応じて文字サイズを際限なく増やすとコントラストが曖昧になるので、通常の資料では 2〜3 段階に絞る — [ギズモード・ジャパン「morisawa biz」（検索抜粋、本文未確認）](https://www.gizmodo.jp/2019/02/morisawa-biz.html)
  - ジャンプ率は、本文の文字サイズに対する見出しの文字サイズの比率。高いとにぎやか・躍動的・若年向け、低いと落ち着き・高級感・大人っぽい印象になる、と説明されている。数値の基準は示されていない — [Web 担当者 Forum（2018-07-19、取得は 403、検索抜粋）](https://webtan.impress.co.jp/u/2018/07/19/29972)
  - 名古屋大学の資料: 見出し 36pt 以上、本文 28pt 以上（比は約 1.3 倍） — [名古屋大学 高等教育研究センター DesignPresentation.pdf（2018-03-23 作成、日本語本文は抽出できず検索抜粋）](https://web.cshe.nagoya-u.ac.jp/asg/designpresentation/DesignPresentation.pdf)
  - アサーション・エビデンスのチェックリスト: 見出し 28pt、本文 18〜24pt（比は約 1.2〜1.6 倍、推論による換算） — [UNM（Penn State のチェックリストを転載）](https://cpl.health.unm.edu/AssetListing/Using-PowerPoint-Effectively-2506/Checklist-for-Assertion-Evidence-Slides-5559)
- **根拠の種類**: 個人の経験則と組織規範。比率の数値に実証的な根拠はない。
- **適用範囲・反対意見**: ジャンプ率は印象（トーン）の調整にも使われるので、「高いほど良い」という規則にはならない。

#### P18 色は 4 色まで（背景・文字・メイン・強調）にし、テーマ色を決めて繰り返す
- **原則**: 背景色・文字色・メイン色・強調色を合わせておよそ 4 色にとどめ、ページごとにその場で色を選ばない。
- **手順・チェック項目**: 『伝わるデザイン』の規則 — [伝わるデザイン「配色」](https://tsutawarudesign.com/miyasuku5.html)
  - 背景は基本的に白。投影専用なら黒や濃紺も可。
  - 文字色は背景と大きく違う色（黒やグレー）にする。
  - メイン色は、多用しても不快にならない落ち着いた色にする。
  - 強調色は最重要箇所だけに使い、少量でも目立つ色（赤やオレンジ）にする。
  - PowerPoint 標準の、彩度・明度が高すぎる色（黄、赤、青、明るい緑）は避ける。
  - 色相が大きく違っても、明度が近く彩度が高い組み合わせはハレーション（文字がちかちかする）を起こすので避ける。
  - 背景に色を付けたいが色数を増やしたくない場合はグレーを使う。
  - 細部の色は 4 色に数えない。背景・文字・強調の 3 色だけでもよい。
- **良い例・悪い例**: 悪い例は、ページごとに違う色を使うこと、赤地に青い文字のような高彩度で同じ明度の組み合わせ。
- **出典（別の流儀）**: 資料デザインの著書がある森重湧太氏は、PRESIDENT WOMAN のインタビューで、コーポレートカラーをメインにし、2 番目の色を補色から選ぶと述べている — [PRESIDENT WOMAN（検索抜粋）](https://president.jp/articles/woman-print/23084)、[関連記事](https://president.jp/articles/woman-print/22963)
- **根拠の種類**: 個人の経験則
- **適用範囲・反対意見**: 色覚多様性への配慮から、色数を抑えること自体が推奨されている（P21 を参照）。

#### P19 1 枚 1 メッセージにし、文字量の目安は 1 枚 100 字以内
- **原則**: 1 枚のスライドには情報を一つだけ載せ、文字量を抑える。
- **手順・チェック項目**: 本文が 100 字（日本語）を超えたら、分割するか図に置き換えることを検討する。
- **出典と数値**: 森重湧太氏は「1 スライドにつき 100 文字以内」を目指し、「1 スライドにつき 1 情報」を鉄則にすれば文字が増えすぎるのを防げると述べている — [PRESIDENT WOMAN（検索抜粋、どちらの記事かは未特定）](https://president.jp/articles/woman-print/23084)。英語の実験では、アサーション・エビデンス条件のスライドが平均 21.2 語、従来条件が 41.5 語だった — [Garner & Alley 2013](https://www.ijee.ie/articles/Vol29-6/23_ijee2791ns.pdf)
- **根拠の種類**: 個人の経験則（100 字）。英語の語数は実験条件の記述で、上限として検証されたものではない。
- **適用範囲・反対意見**: 日本語の字数と英語の語数は直接比べられない。Duarte も「各スライドを一つの正確な論点に絞れ」と述べている — [Duarte「The Glance Test」](https://www.duarte.com/resources/guides-tools/the-glance-test/)

### Inferences
- 日本語の数値規範（行間 70%、字間 5%、4 色、2〜3 段階、100 字）は、どれも個人の経験則で、実験で検証されたものではない。スキルでは「既定値」として採用し、「根拠は実務家の経験則」と明記するのが誠実。
- AI 生成スライドで日本語特有の失敗になりやすいのは、MS ゴシックなどの既定フォント、擬似ボールド、日本語の斜体、長体や平体、和欧混植の大きさの不揃い。いずれもフォント名と書式属性で機械的に検査できる。

### Gaps
- 『伝わるデザインの基本』の書籍本文、および公式サイトのプレゼン資料の作例ページ（sakurei2.html。作例は SVG 画像で、テキストを抽出できなかった）は確認できなかった。同ページは「まだ未完成」と記載されている。
- 森重湧太氏の書籍本文（フォントサイズや色の具体的な数値）は確認できなかった。
- 名古屋大学の PDF は日本語フォントの抽出ができず、36pt と 28pt は検索結果の要約に頼った。
- ジャンプ率の数値基準（例: 見出しは本文の何倍）について、根拠のある出典は見つからなかった。
- 余白の量（例: 周囲に何 % の余白を取るか）について、数値の出典は見つからなかった。

---

## 5. アクセシビリティ：コントラスト、色覚多様性、投影時の最小文字サイズと距離

### Takeaway
コントラストの規範は WCAG 2.2 の 1.4.3（通常の文字は 4.5:1、大きい文字は 3:1）と、1.4.11（図表の要素は 3:1）が根拠になる。ただし WCAG はウェブを対象としており、スライドや投影については何も述べていない。色覚については、日本人男性の約 5%（20 人に 1 人）が先天的な色覚の特性を持つとされ、赤と緑の組み合わせを避け、色以外の手がかり（形、線種、直接ラベル）を併用するのが一致した推奨。最小文字サイズは出典によって 18pt から 30pt 以上まで割れており、根拠はどれも経験則か組織規範。

### Cited Findings

#### P20 文字と背景のコントラスト比は 4.5:1 以上、グラフの要素は 3:1 以上
- **原則**: 文字と背景のコントラスト比を WCAG の閾値以上にする。グラフの線や棒など、理解に必要な図形も背景に対して十分なコントラストを持たせる。
- **手順・チェック項目**:
  - 通常の文字は 4.5:1 以上、大きい文字（18pt 以上、または太字 14pt 以上。CSS では約 24px と 18.5px）は 3:1 以上（WCAG 1.4.3、レベル AA）。
  - 閾値の比較では丸めない。4.499:1 は不合格。
  - より高いレベルの AAA（1.4.6）は 7:1 で、視力 20/80 程度に対応する。
  - グラフや図などの非テキスト情報は 1.4.11 の対象になる。
  - 出典: [W3C, Understanding SC 1.4.3 Contrast (Minimum), WCAG 2.2](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html)
- **根拠と数値**: 3:1 は、ISO・ANSI 規格が通常の視力向けに推奨する最小値。4.5:1 は、視力 20/40（およそ 80 歳の典型的な視力）に伴うコントラスト感度の低下（約 1.5 倍）を補うための値で、3 × 1.5 = 4.5 — [W3C](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html)
- **根拠の種類**: 組織規範（国際的な標準化団体）に、視覚研究と ISO・ANSI 規格の裏づけがあるもの
- **適用範囲・反対意見**: 
  - 同じページは、スライド、プレゼンテーション、投影には言及していない — [W3C](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html)
  - 『伝わるデザイン』は感覚過敏への配慮から、コントラストを強くしすぎないよう勧めている。文字は純粋な黒ではなく濃いグレー（HSV の明度を 5〜10% 上げる程度）、背景は薄いグレーやクリーム色などほぼ無彩色にする — [伝わるデザイン「配色（バリアフリー）」](https://tsutawarudesign.com/universal1.html)。これは WCAG の最小値と矛盾しない（WCAG に上限はない）が、「黒地に白」「白地に純黒」を最適とは見ない立場。
  - 細い書体や特殊な書体は指定した色より薄く表示されることがあるので、最小値を満たしていても太めの書体か高めのコントラストを勧めている（参考情報で、規定ではない） — [W3C](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html)

#### P21 色だけで情報を区別させない。赤と緑を避け、明度差と形の違いを併用する
- **原則**: 色覚の多様性を前提に、色相だけに頼らず、明度・形・線種・ラベルでも区別できるようにする。
- **手順・チェック項目**: 『伝わるデザイン』の規則 — [伝わるデザイン「配色（バリアフリー）」](https://tsutawarudesign.com/universal1.html)
  1. 赤と緑の組み合わせは避け、青やオレンジで代替する。暖色同士・寒色同士、明度が近い色同士も避ける。
  2. 暖色と寒色を組み合わせる。同系色なら明度に差を付ける。
  3. グレースケールで印刷しても区別できるか確認する。
  4. 凡例をやめ、項目名を線の近くに直接書く。
  5. マーカーの形（●○△□）、線種（点線・太線）、塗りのパターンを変える。
  6. 文字の強調には赤や緑を使わず、オレンジや水色に下線や太字を併用する。
  7. 発表中は「白抜きの丸」「右側の棒」のように、色以外の言葉でも指し示す。
- **出典と数値**: 先天的な色覚特性を持つ人は日本人男性の 20 人に 1 人（5%）、女性の 500 人に 1 人（0.2%）とされ、そのうち 2 型（D 型）が約 75%、1 型（P 型）が約 25%。元データは平成 12 年版『障害者白書』。カラーユニバーサルデザイン機構（CUDO）などが作った「カラーユニバーサルデザイン推奨配色セット」が自治体のガイドラインに収録されている（例: 赤は朱色寄りの R255 G75 B0） — [鳥取県 カラーユニバーサルデザイン（検索抜粋）](https://www.pref.tottori.lg.jp/item/1100584.htm)
- **根拠の種類**: 組織規範（自治体ガイドライン、CUDO）と個人の経験則。有病率は政府統計に基づく。
- **適用範囲・反対意見**: 有病率は 2000 年版の白書に基づく古い値。反対意見は見つからなかった。

#### P22 最小文字サイズは出典によって 18〜36pt と割れており、どの値も経験則か組織規範
- **原則**: 会場の最後列から読める大きさにする。ただし「何 pt 以上」という数値に実証的な根拠はなく、出典ごとに値が違う。
- **出典ごとの数値（すべて記録）**:
  - Guy Kawasaki（何百件もの起業家の売り込みを聞いてきた立場で書いた） — [InformationWeek](https://www.informationweek.com/it-infrastructure/powerpoint-rules-that-could-save-our-sanity): 30pt 未満のフォントを使わない。最適なフォントサイズは聴衆の最年長者の年齢を 2 で割った値、という冗談も添えている — [Entrepreneur（Kawasaki 名義の転載）](https://www.entrepreneur.com/article/192718)
  - Alley 系のアサーション・エビデンスのチェックリスト: 見出し 28pt、本文 18〜24pt、参考文献 12〜14pt（太字にしない）、Calibri などの太めのサンセリフ — [UNM 転載チェックリスト](https://cpl.health.unm.edu/AssetListing/Using-PowerPoint-Effectively-2506/Checklist-for-Assertion-Evidence-Slides-5559)、[Northeastern 大学の講義ページ](https://course.ccs.neu.edu/cs7976f19/Materials/Slide-guidelines.html)
  - 名古屋大学の資料: 見出し 36pt 以上、本文 28pt 以上 — [名古屋大学（検索抜粋）](https://web.cshe.nagoya-u.ac.jp/asg/designpresentation/DesignPresentation.pdf)
  - WCAG の「大きい文字」の閾値は 18pt（ウェブ向けで、スライドの最小サイズを定めるものではない） — [W3C](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html)
  - 『伝わるデザイン』は数値を示さず、「なるべく文字を大きくすることは、ユニバーサルデザインのために欠かすことができない」とだけ述べている — [伝わるデザイン「文字組み」](https://tsutawarudesign.com/yomiyasuku4.html)
- **距離に基づく規格**: AVIXA（旧 InfoComm）の DISCAS（ANSI/INFOCOMM V202.01）は、「最も遠い視聴者までの距離 ÷ 画像の高さ」（視聴比）に応じて、文字などの要素の高さが画像の高さの何 % 以上必要かを定めている。基本的な判断（BDM、視力係数 200）の表は、視聴比 0.80〜1.00 で 0.50%、1.00〜1.50 で 0.75%、1.50〜2.00 で 1.00% から始まる。精密な判断（ADM）の視力係数は 3438 — [AVIXA DISCAS BDM](https://www.avixa.org/standards/discas-calculators/discas/bdm)。選択ページでは版が V202.01:2026、計算ページでは 2016 と表記がずれている — [AVIXA DISCAS](https://www.avixa.org/standards/discas-calculators/discas)
- **根拠の種類**: Kawasaki と名古屋大学は個人の経験則・組織規範。AVIXA は業界規格（視力モデルに基づく）。
- **適用範囲・反対意見**: Kawasaki の規則はベンチャーキャピタルへの売り込み向けのもの — [InformationWeek](https://www.informationweek.com/it-infrastructure/powerpoint-rules-that-could-save-our-sanity)。学術発表の参考文献表記（12〜14pt）は、AE のチェックリストでは許容されている。

### Inferences
- 16:9 の PowerPoint スライドは 13.333 × 7.5 インチ（960 × 540pt）なので、各サイズはスライドの高さに対して 18pt が約 3.3%、24pt が約 4.4%、28pt が約 5.2%、30pt が約 5.6%、36pt が約 6.7% になる（自分で換算した値）。AVIXA の「要素の高さ %」と比べるには、文字サイズではなく実際の字面の高さで計算する必要がある。
- スライドの文字はほとんど 18pt 以上なので、WCAG を字義どおり当てはめれば 3:1 で足りる。しかし投影ではプロジェクターの輝度や部屋の明るさでコントラストが落ちやすいので、スキルの既定は 4.5:1 以上、できれば 7:1 にするのが安全側（推論。投影でコントラストが下がることを示す出典は今回は取得していない）。
- 色覚への配慮は、「強調は一色、残りはグレー」（P9）と組み合わせると自然に満たしやすい。赤と緑で良し悪しを示す信号機配色が、AI 生成グラフで最も起こりやすい違反になると予想される。

### Gaps
- 投影でコントラストがどれだけ下がるかを示した実測データや研究は取得していない。
- 「最後列から読める最小文字サイズ」を実験で決めた研究は見つからなかった。AVIXA の規格本文（有料）の表全体と字面の高さの定義は確認していない。
- CUDO の推奨配色セットの全色の値は確認していない。Okabe & Ito の jfly の配布資料は図が中心で、テキストを抽出できなかった。

---

## 6. 流布している数値ルール（6×6、10/20/30、3 秒のグランステスト）の起源と根拠

### Takeaway
6×6 ルールは起源が記録されておらず、それを検証した対照実験も見つからなかった。10/20/30 ルールは Guy Kawasaki が 2005 年にベンチャーキャピタルへの売り込み向けに書いたブログ記事が起源の個人的な経験則。3 秒のグランステストは Duarte 社が提唱する経験則で、公開された検証はない。どれも「根拠なし」または「個人の経験則」として扱うべき。

### Cited Findings

#### P23 6×6 ルール（1 枚に箇条書き 6 行まで、1 行 6 語まで）：根拠なし
- **原則として採るなら**: 箇条書きを使う場合でも、行数と 1 行の長さを抑える。
- **起源**: 記録がない。教育心理学やマルチメディア学習理論に由来するとする説明、Miller の法則（7±2）と結びつける説明があるが、どちらも原典を挙げておらず、「正確な起源ははっきり記録されていない」と認める解説もある — [SlideModel](https://slidemodel.com/6x6-rule-powerpoint/)、[Free PowerPoint Templates](https://free-power-point-templates.com/articles/the-6x6-rule-in-presentation-design)
- **変種**: 1-6-6（1 つの主題、6 行、6 語）、1-5-5、1-7-7 などがある — [Manner of Speaking](https://testbase.mannerofspeaking.org/?p=2518)
- **根拠の種類**: 根拠なし（業者のブログが中心）
- **反対意見**: Manner of Speaking の筆者は、文字でスライドを埋めないという目的には同意しつつ、6×6 は規則とは言えないと述べている。代わりの方式としてアサーション・エビデンスが挙げられている — [Manner of Speaking](https://testbase.mannerofspeaking.org/?p=2518)。Mayer の冗長性原則（P4）に照らすと、6 行 × 6 語でも、話す内容の転載であれば問題は残る（推論）。

#### P24 10/20/30 ルール（10 枚、20 分、30pt 以上）：個人の経験則
- **起源**: Guy Kawasaki のブログ記事「The 10/20/30 Rule of PowerPoint」（2005 年 12 月、blog.guykawasaki.com/2005/12/the_102030_rule.html）。何百件もの売り込みを聞いた経験から、ベンチャーキャピタルに売り込む起業家に向けて書いたもの — [InformationWeek](https://www.informationweek.com/it-infrastructure/powerpoint-rules-that-could-save-our-sanity)、[Entrepreneur（Kawasaki 名義の転載）](https://www.entrepreneur.com/article/192718)
- **内容**: 10 枚、20 分以内、30pt 未満のフォントを使わない。最適なフォントサイズは聴衆の最年長者の年齢 ÷ 2 という冗談付き — [Entrepreneur](https://www.entrepreneur.com/article/192718)
- **根拠の種類**: 個人の経験則
- **適用範囲**: 資金調達の売り込み向け。教育や学会発表への一般化は著者自身も意図していない（推論。原典は直接確認していない）。

#### P25 3 秒のグランステスト：個人・企業の経験則
- **内容**: 「聴衆はスライドの要点を 3 秒以内に理解できるか」 — [Duarte「The Glance Test™」](https://www.duarte.com/resources/guides-tools/the-glance-test/)。Duarte は「各スライドを一つの正確な論点に絞れ」とも述べている — [同上](https://www.duarte.com/resources/guides-tools/the-glance-test/)
- **起源**: Nancy Duarte の『slide:ology』と、2012 年の Harvard Business Review の記事で紹介された。KLA-Tencor の Glenn Hughes と一緒に、信号対雑音比でスライドを採点する方法として作ったとされる — [Small Wars Journal（2012）](https://smallwarsjournal.com/2012/10/22/do-your-slides-pass-the-glance-test/)、[huesworks ブログ（2009-10-04）](https://huesworks.blogspot.com/2009/10/glance-test.html)。採点で「5:1 以上なら合格」とする値は、一人のブロガーの経験に基づくもので、Duarte の公式資料のものではない — [huesworks（検索抜粋）](https://huesworks.blogspot.com/2009/10/glance-test.html)
- **根拠の種類**: 個人の経験則（公開された検証研究は見つからなかった）
- **関連する実証**: Ajani らの実験では、グラフを 10 秒見せた後の要点の再生を測り、強調版で主結論を捉える確率が約 2.5 倍になった — [Kellogg Insight](https://insight.kellogg.northwestern.edu/article/do-people-understand-your-data-visualizations)。3 秒そのものの検証ではないが、短時間で見せたときの理解は設計で変わることを示している。
- **反対意見**: Tufte は高密度を支持し（P13）、短時間で読めることを最優先にはしない。

### Inferences
- スキルでは、数値ルールを「根拠のある規則」として書かず、代わりに検査可能な代理指標に置き換えるのがよい。例えば 6×6 の代わりに「話す内容の全文が画面にない」「本文に図が一つ以上ある」、グランステストの代わりに「見出しの主張と強調色の対象が一致している」とする。
- 30pt 以上（Kawasaki）は、日本語の 1 枚 100 字（森重）と組み合わせると物理的にほぼ収まらないことがある（推論）。数値ルール同士の衝突は、用途（売り込みか、説明か）で使い分ける。

### Gaps
- Kawasaki の原典ブログ（blog.guykawasaki.com）は直接取得していない。
- Duarte の HBR 2012 記事と『slide:ology』の本文は確認していない。グランステストの採点方法の公式な定義も確認できなかった。
- 6×6 ルールを最初に提唱した人物や文献は特定できなかった。

---

## 7. よくある視覚的な失敗パターンと、専門家による直し方

### Takeaway
出典に繰り返し出てくる失敗は、(1) ツールの既定値に任せた結果（トピック見出しと箇条書き、文字の自動縮小、既定の高彩度色、MS ゴシック、枠線とグリッド線）と、(2) 目的のない飾り（テーマ写真、グラフの背景画像、凡例の往復、色の多用）に大きく分かれる。直し方は既定値を疑うことと、要素ごとに「主張を支えているか」を問うことに集約される。

### Cited Findings

#### P26 失敗パターンと修正の対応表（AI 生成スライドの検査項目の候補）

| 失敗パターン | なぜ問題か | 修正 | 出典 |
|---|---|---|---|
| トピック見出しと箇条書きだけのスライド | 信号化・一貫性・冗長性に反する。工学・科学の発表の 65%、心理学教科書の付属スライドの 80% がこの構造 | 主張を文で書いた見出し（2 行以内）と視覚的根拠にする | [Garner & Alley 2013](https://www.ijee.ie/articles/Vol29-6/23_ijee2791ns.pdf) |
| テキストボックスの自動縮小で文字が増え続ける | PowerPoint の既定は、文字が増えるとフォントを自動で縮める。冗長になりやすい | 文字を削る、スライドを分ける、自動調整を切る | [Garner & Alley 2013](https://www.ijee.ie/articles/Vol29-6/23_ijee2791ns.pdf) |
| 飾り目的の写真や、本文を絵にしただけの図 | 説明的な図の基準を満たすのは 10% 程度という調査がある | 説明する図だけを残す | [Garner & Alley 2013](https://www.ijee.ie/articles/Vol29-6/23_ijee2791ns.pdf)、[Farkas 2010](https://faculty.washington.edu/farkas/dfpubs/Farkas-Assessment%20Of%20Alleys%20Slide%20Design.pdf) |
| すべての主張に小さい図を付ける | 役に立たない図が増え、図が小さくなる | 図は数を減らして大きくし、図にできない内容は文字で示す | [Farkas 2010](https://faculty.washington.edu/farkas/dfpubs/Farkas-Assessment%20Of%20Alleys%20Slide%20Design.pdf) |
| 凡例が離れていて色で照合させる | 空間的近接に反する | 系列の端に直接ラベルを付ける | [伝わるデザイン](https://tsutawarudesign.com/universal1.html)、[SWD](https://www.storytellingwithdata.com/blog/2019/5/13/declutter-and-question-defaults) |
| 全系列が色付きの虹色グラフ | 前注意属性が競合し、何も目立たない | 全体をグレーにし、強調色は一つにする | [SWD](https://www.storytellingwithdata.com/blog/use-color-to-focus-or-to-compete-for-attention)、[Ajani et al. 2021](https://insight.kellogg.northwestern.edu/article/do-people-understand-your-data-visualizations) |
| 見出しの結論とグラフの強調がずれている | 聴衆の視線が見出しと違う対象に向かう | 見出しの対象を強調色にし、文字とグラフで色を揃える | [SWD Cisneros](https://www.storytellingwithdata.com/blog/use-color-to-focus-or-to-compete-for-attention)、[伝わるデザイン「配色」](https://tsutawarudesign.com/miyasuku5.html) |
| 枠線、濃いグリッド線、全点のマーカー | 専門的に見えない（理解への影響は小さい） | 余白で区切り、グリッド線を消し、必要な点だけに値を書く | [SWD 2019](https://www.storytellingwithdata.com/blog/2019/5/13/declutter-and-question-defaults)、[Ajani et al. 2021](https://insight.kellogg.northwestern.edu/article/do-people-understand-your-data-visualizations) |
| グラフの背後に写真やテクスチャを敷く | 解釈を難しくする | 背景は無地にし、装飾はデータの外に置く | [Bateman et al. 2010](https://vis.csail.mit.edu/classes/6.859/readings/pdfs/Bateman-UsefulJunk.pdf) |
| PowerPoint 標準の高彩度色、明度の近い補色の組み合わせ | ハレーションを起こし、落ち着かない | 彩度を下げた色にし、明度差を付ける | [伝わるデザイン「配色」](https://tsutawarudesign.com/miyasuku5.html) |
| 赤と緑で良し悪しを示す | 日本人男性の約 5% が区別しにくい | 青とオレンジにし、形・線種・ラベルを併用する | [伝わるデザイン「配色（バリアフリー）」](https://tsutawarudesign.com/universal1.html)、[鳥取県](https://www.pref.tottori.lg.jp/item/1100584.htm) |
| MS ゴシックや擬似ボールド、日本語の斜体 | 字形が粗く、太字が効かず、画面で輪郭がガタつく | メイリオ、游ゴシック、BIZ UD ゴシック、Noto Sans CJK JP を使う | [伝わるデザイン「フォントの選び方」](https://tsutawarudesign.com/yomiyasuku2.html) |
| 長体・平体（縦横比の変更） | 読み間違いが起きやすい | 縦横比は変えず、サイズか文言で調整する | [伝わるデザイン「文字組み」](https://tsutawarudesign.com/yomiyasuku4.html) |
| 複数行の文の中央揃え、揃え方の混在 | 行頭がそろわず段落を認識しにくい | 左揃えに統一する | [伝わるデザイン「文字組み」](https://tsutawarudesign.com/yomiyasuku4.html) |
| 行間が詰まっている、字間が広すぎる（PowerPoint の「広く」） | 読みにくい | 行間は約 70%、字間は約 5% にする | [伝わるデザイン「文字組み」](https://tsutawarudesign.com/yomiyasuku4.html) |
| 文字サイズの段階が多すぎる | 階層のコントラストが曖昧になる | 2〜3 段階に絞る | [ギズモード「morisawa biz」（検索抜粋）](https://www.gizmodo.jp/2019/02/morisawa-biz.html) |
| 要点と無関係なアニメーション | 注意を散らす | 説明の順番に合わせた段階表示だけに使う | [Atkinson（Zelazny）](https://www.robertgaskins.com/files/five-experts-dispute-edward-tufte-on-powerpoint-sociable-media-cliff-atkinson.htm) |
| 階層の深い箇条書き（コロンビア号の例: 6 段階、19 行） | 重要な情報が階層に埋もれる | 階層を浅くし、文や図で関係を示す | [Farkas（Tufte 事例の紹介）](https://faculty.washington.edu/farkas/dfpubs/Farkas-Toward%20A%20Better%20Understanding%20of%20PowerPoint.pdf)、[edwardtufte.com](https://www.edwardtufte.com/notebook/the-columbia-evidence/) |

- **根拠の種類**: 表の各行は、右の列の出典の種類に従う。実証研究に基づく行は、トピック見出しと箇条書き、凡例の往復、虹色グラフ、背景画像、デクラッター（理解への効果は否定的）。それ以外は組織規範か個人の経験則。

### Inferences
- 機械的に検査しやすい順に並べると次のとおり。AI 生成スライドの品質検査では、この順に自動化するのが現実的。
  1. フォント名と書式（擬似ボールド、斜体、縦横比）
  2. コントラスト比（4.5:1）
  3. 色数（4 色以下、強調色は 1 色）
  4. 赤と緑の組み合わせの有無
  5. 揃え方の混在
  6. 文字サイズの段階数と最小サイズ
  7. 凡例か直接ラベルか
  8. 本文に図があるか
  9. 台本と画面の文字の重複
  10. 見出しの対象と強調色の一致
- 失敗の多くは「既定値のまま」から生じるので、スキルの指示は「既定値を変える」形で書くと効果的。例えば「グラフ生成時に枠線・グリッド線・凡例をオフにし、全系列をグレーにしてから強調色を 1 系列に付ける」。

### Gaps
- 3D グラフ、二重軸、切り詰めた縦軸といったグラフ固有の誤りは、今回の出典（Few の表の抜粋など）では具体的に確認できなかった。
- 失敗パターンの頻度を AI 生成スライドで測ったデータは見つからなかった。人が作ったスライドの頻度は、Garner & Alley が引く 65〜80% のみ。
