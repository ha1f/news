# ソース利用条件の棚卸し

monetization 監査の成果物。全22ソースのフィード/API 利用条件を一次情報（各ソースの規約・robots.txt）で確認し、現行運用（非営利・見出しの日本語リライト＋原文直リンク＋事実ベースの短い要点・本文/画像転載なし）と収益化（課金・広告）の両方に対する適合を整理する。

- **確認日**: 2026-08-28（対象 commit: `3db0218`）。規約は変わるため、再監査時はこの日付からの差分を見る
- **2026-08-29 更新**: オーナー方針（#241）により AI 利用を明示的に制限する4ソース（Ars Technica・Wired・The Verge・Lobsters）を除外。各ソースの利用条件は references/sources/*.md の「利用条件」セクションに転記した（一次利用はそちら。本表は監査時点の詳細根拠・横断整理）
- **注意**: 本整理は弁護士等の専門家による法的助言ではない。「要判断」は解釈が分かれうる論点であり、規約違反の認定ではない。最終判断（リスク受容・許諾照会・除外）はオーナーが行う
- 詳細な引用・確認過程は監査 run の記録（[audits/monetization.md](../monetization.md) の監査履歴）を参照

## 総括

- **収益化（課金・広告のいずれも）を現行ソース構成のまま始める根拠は無い。** 22ソース中、商用利用を明示許可するものは無く、明示禁止（書面許可制）または実質要許諾が過半: Condé Nast 系（Ars Technica・Wired）、PMC（The Verge）、MIT Tech Review、Nature、Science、日経、ITmedia、はてな、Reddit、dev.to、Product Hunt。Qiita は「データを元にしたサービスへの広告設置収益化は規約違反」と公式ヘルプが明言
- **相対的に好条件**: InfoQ（「要約＋InfoQ へのリンクバック」を規約が明示許可）。Hacker News（API 自体に条件規定なし・robots.txt が JSON を明示 Allow）
- **現行の非営利運用にも論点がある**（下記「現行運用に関わる発見」）。特に Condé Nast の生成 AI/RAG 条項、Lobsters の `ai-input=no`、ITmedia の改変禁止、日経フィードの非公式性
- **帰属＋原文直リンクの現行運用は、明文義務のあるソース（TechCrunch・The Verge・ITmedia 等）と整合**している

## ソース別一覧

| ソース | 規約（確認先） | 商用利用 | 主な条件・制限 | 要判断・備考 |
|---|---|---|---|---|
| Ars Technica | [Condé Nast User Agreement](https://www.condenast.com/user-agreement/)（2024-10-10版） | 明示禁止（書面許可制） | 非商用限定を RSS にも適用と明記。再公開・集約・キャッシュを包括禁止（検索エンジンのみ例外） | 生成 AI/RAG での利用を「非商用」からも明示除外。robots.txt は Claude 系 UA を全面拒否 |
| dev.to | [Terms](https://dev.to/terms) | 明示禁止（personal, non-commercial viewing 限定） | copy / public display / mirror 禁止 | 規約はボイラープレートで公開 RSS/API 提供の実態と乖離。収益化時は要判断 |
| GitHub Trending | 経由: [GitHubTrendingRSS](https://github.com/mshibanami/GitHubTrendingRSS)（MIT）/ 本体: [GitHub AUP §7](https://docs.github.com/en/site-policy/acceptable-use-policies/github-acceptable-use-policies) | 要判断（AUP の利用目的列挙は研究・アーカイブのみ） | MIT はコードのみでデータに及ばない。repo 説明文は各オーナーの著作物 | 経由フィードはスクレイピング生成・個人運営（持続性リスク中）。フォーク自前ホストや GitHub API への切替が緩和策 |
| Hacker News | [公式 API](https://github.com/HackerNews/API) / [YC Legal](https://www.ycombinator.com/legal/) | API 自体は規定なし | 認証不要・レート制限なし。firebaseio の robots.txt は `*.json` を明示 Allow | YC サイト規約の商用禁止が API データに及ぶかは要判断。22ソース中最も条件が軽い |
| InfoQ | [Terms](https://www.infoq.com/terms-and-conditions/) | 規定なし（非商用限定の文言なし） | 全文転載禁止。**「要約＋InfoQ へのリンクバック」を明示許可** | 現行運用は許可文言の範囲内と読める。商用の明示許可ではない点のみ留意（照会先 feedback@infoq.com） |
| Lobsters | [About](https://lobste.rs/about)（規約ページ無し） | 規定なし | フィードは「public」と明言 | robots.txt が一般 UA を全面 Disallow ＋ `Content-Signal: ai-input=no, ai-train=no`。AI 処理する現行形態と緊張関係（要判断・小規模運営で問い合わせ容易） |
| MIT Tech Review | [ToS](https://www.technologyreview.com/terms-of-service/) / [Republishing](https://www.technologyreview.com/republishing/) | 明示禁止（再利用は有償ライセンスとして販売） | ToS が RSS に適用と冒頭で明記。書面許可なき複製・再配信禁止 | ライセンス窓口 licensing@technologyreview.com |
| Product Hunt | [ToS](https://www.producthunt.com/legal?section=terms-of-service) / [API docs](https://api.producthunt.com/v2/docs) | 非商用限定（API は「商用は要連絡」と明記） | API は帰属＋リンクバックを要請。ToS はクロール禁止（/feed の位置付け不明確） | 収益化時は hello@producthunt.com へ連絡が実質必要 |
| Reddit | [User Agreement](https://redditinc.com/policies/user-agreement)（2026-07-01版） / [Data API Terms](https://www.redditinc.com/policies/data-api-terms) | 書面合意なき商用利用を禁止 | robots.txt が全面 Disallow（自動取得の許諾根拠が曖昧）。UGC の改変禁止（表示整形を除く） | RSS 固有規定なし。商用は別途契約なしでは不可と読むのが安全。**22ソース中最高リスク級** |
| TechCrunch | [RSS Terms of Use](https://techcrunch.com/rss-terms-of-use/) / [ToS](https://techcrunch.com/terms-of-service/)（2025-05-01版） | RSS 規約に規定なし・一般 ToS は非商用限定（要判断） | **帰属＋原文直リンクが明文義務**。フィード内容の改変禁止。フィードへの広告組込み禁止 | 見出しの日本語リライトが「改変」に当たるかは要判断 |
| The Verge | [PMC Terms of Use](https://www.pmc.com/terms-of-use/)（2026-08-21版） | 明示禁止（"whether or not for profit" の事業利用も禁止） | Content Feeds 条項: テキスト・リンクの改変禁止、帰属義務、原文直リンク必須、中間ページ禁止。AI ツールでの取得を明示禁止 | 2026年6月に PMC が Vox Media を買収し規約が変わった。旧 Vox の「見出し＋リンク共有は許諾不要」FAQ の効力は要判断 |
| Wired | [Condé Nast User Agreement](https://www.condenast.com/user-agreement/) | 明示禁止（Ars と同一） | 同上 | RSS 案内ページに "add it to your site" の文言あり（条件規定なし・要判断） |
| 日経新聞 | [リンクポリシー](https://www.nikkei.com/info/link.html) / [著作権](https://www.nikkei.com/info/copyright.html) / [配信元 RSS愛好会](https://rss.wor.jp/about) | 実質禁止（営利目的の記事リンク利用・事業者クリッピングを明示禁止） | 出典が日経である旨の明記必須。無許諾の複製・翻案・ボット収集禁止 | **フィード自体が日経非公式の第三者（有志）配信**で予告なく停止されうる。法的リスクと供給安定性の両面で他ソースと質が異なる |
| Nature | [Terms](https://www.nature.com/info/terms-and-conditions)（2025-12-15版） | 明示許可制 | **"feeds" を名指しで** syndicate/make available 禁止、DB 化・publication 化禁止。帰属義務あり | 非商用の現状でも「publication を populate する」該当性は要判断。許諾窓口 permissions@nature.com |
| Science | [AAAS Terms](https://www.aaas.org/terms-of-use)（science.org 側は bot 遮断で直接取得不可・要再確認） | 不可（personal, non-commercial 限定） | 体系的取得・DB 化・再配布は express consent 必要。帰属維持義務 | robots.txt はフィードパスを明示 Allow（クロール自体は許可） |
| Dribbble | [ToS](https://dribbble.com/terms)（2025-03-17版） | 規定なし（明示許可なし＋広範な複製・scraping 禁止） | Dribbble Content の copy / publicly display 等を禁止。ライセンスは freely revocable | 公式に stories.rss を公開している事実と規約文言が矛盾。要判断 |
| GIGAZINE | 規約ページ不存在（[About](https://gigazine.net/news/about/) 等を確認） | 規定なし | robots.txt に `Crawl-delay: 100`（フィードパスは許可） | 規定なし＝許諾ありではない。収益化時は要問い合わせ |
| ITmedia | [RSS 利用条件](https://corp.itmedia.co.jp/media/rss_condition/)（2020-04-01改定） / [コンテンツ利用](https://corp.itmedia.co.jp/media/image/) | 条件付き（私的利用のみ無償。商用は要許諾・基本有償） | **発信元表示必須**。改変・一部削除・抜粋転載・翻案の禁止（相談可） | 「見出しリライト＋要点のみ」が改変禁止に触れるおそれ（要判断）。22ソース中最も規定が明確 |
| Publickey | 規約不存在（[About](https://www.publickey1.jp/about-us.html) 等を確認） | 規定なし | robots.txt 制限なし | 個人運営で問い合わせ先公開あり。収益化時は直接確認が現実的 |
| Qiita | [利用規約](https://qiita.com/terms) / [公式ヘルプ](https://help.qiita.com/ja/articles/points-when-creating-application-using-qiita-data) | **広告収益化は規約違反と公式ヘルプが明言**。課金も「転用・再販」該当のおそれ | 著作権は投稿者に留保。スクレイピング不許可（フィード/API は提供） | 非営利の現状に明示禁止規定は見当たらず。承諾を得れば可の建付け |
| はてなブックマーク | [Developer Center 規約](https://developer.hatena.ne.jp/license) / [アクセス頻度の注意](https://b.hatena.ne.jp/help/entry/notice_access) | 実質要許諾（商用は「特別に許諾を行った場合を除」き禁止） | 取得情報の第三者提供・再配布許諾の禁止。**RSS 取得は30分毎程度まで**（現行の日次取得は適合） | フィード中身は第三者記事の見出しで権利は各発行元に帰属する二重構造 |
| Zenn | [利用規約](https://zenn.dev/terms) | 規定なし（フィード固有条件なし） | UGC の無断転載・二次配布禁止（著作権は投稿者に留保） | フィードは[公式案内](https://zenn.dev/zenn/articles/zenn-feed-rss)あり。リンク＋事実要点は転載非該当の読みが自然だが要判断 |

## 現行運用（非営利）に関わる発見

収益化前でも認識しておくべき点。リスク受容・対応の判断はオーナー（hold issue で依頼）:

1. **生成 AI での処理に対する意思表示**: Condé Nast（Ars・Wired）は生成 AI/RAG での利用を「非商用」からも明示除外。PMC（The Verge）は AI ツールでの取得を明示禁止。Lobsters は `Content-Signal: ai-input=no` を宣言。また大半の米系ソースが robots.txt で Anthropic 系クローラ UA を名指し拒否（フィード取得はクローラ UA でないため直接には該当しないが、意思表示として留意）
2. **フィード内容の改変禁止条項と見出しリライト**: TechCrunch・PMC・ITmedia は改変禁止を明文化。原題を保持し要点を別立てにする表示への変更で緩和しうるが、解釈は分かれる
3. **日経の非公式フィード**: 配信元（RSS愛好会）は日経の許諾に基づかず、日経は事業者のクリッピング的利用を禁止。継続利用の可否と、公式 RSS のあるグループ媒体（日経ビジネス電子版等）への差し替えが選択肢
4. **Nature の feeds 名指し禁止条項**: 非商用でもフィードの再配信・DB 化を禁止する文言があり、キュレーションへの該当性は要判断
5. **運用面の適合確認済み**: 取得は日次1回で、はてなの頻度要請（30分毎まで）に適合。記事ごとのソース表示名＋原文直リンクは帰属義務のあるソースと整合

## 収益化の形態別チェックリスト（法令）

法令要件の一次情報確認結果（e-Gov・消費者庁・総務省、2026-08-28 確認）。詳細な条文・運用資料の引用は監査 run の記録を参照。

### 課金開始前

- [ ] 「特定商取引法に基づく表記」ページ作成（対価・支払時期方法・提供時期・解約条件・動作環境・継続契約の旨と期間。特商法11条＋施行規則23/24条）
- [ ] 氏名・住所・電話番号の方針決定: 全部表示（個人は戸籍上の氏名）or「請求により遅滞なく開示」の省略運用＋開示フロー整備（消費者庁 通信販売広告Q&A Q15〜Q17）
- [ ] 最終確認画面（Stripe Checkout 等を含む）で表示: 期間・自動更新の旨／各回代金と総額（無料期間→有償移行の時期と金額）／支払時期方法／提供時期／解約条件と方法（特商法12条の6＋申込段階表示ガイドライン）
- [ ] 解約導線の実装（オンライン完結推奨。手段を限定するなら最終確認画面に明記）
- [ ] 利用規約・返金/途中解約条項の消費者契約法チェック（弁護士確認）
- [ ] ポイント・前払い商品を発行しない前提の維持（資金決済法の登録不要の整理を崩さない。決済プロバイダ経由の対価受領のみなら為替取引に該当しない整理）
- [ ] **商用不可ソースの扱い決定**（上記一覧の「収益化ブロッカー」への対応: 除外・許諾照会・代替）

### 広告開始前

- [ ] 広告・アフィリエイト・タイアップ枠に「広告」「PR」等の明瞭表示（景表法ステマ告示〔令和5年内閣府告示19号、2023-10-01施行〕＋運用基準）
- [ ] 編集記事と広告のレイアウト区別ルールの文書化（広告主が内容に関与した記事は広告表記必須）
- [ ] 広告と記事選定の独立性の方針決定（GUARDRAILS が人間に留保）
- [ ] Qiita 等「広告収益化を規約違反と明言」しているソースの扱い決定
- [ ] 広告収入の発生は電気通信事業を「営む」該当となり得るため、解析導入前チェックリストも同時実施

### 解析・広告タグ導入前

- [ ] 導入タグの棚卸し（送信される情報・送信先事業者名・利用目的の一覧化）
- [ ] 「外部送信ポリシー」ページを日本語・平易に作成しフッター等から全ページ到達可能に（電気通信事業法27条の12＋施行規則22条の2の28/29。ニュース配信サイトは対象役務類型に該当、利用者数の多寡は無関係〔総務省FAQ〕。無料・広告なしの間は「営む」非該当の可能性があるが、収益発生後は該当し得る）
- [ ] プライバシーポリシーの整合更新（legal 監査と併走）

## 次回監査への引き継ぎ

- Science（science.org）の ToS はボット遮断で直接確認できず AAAS 規約＋検索スニペットで補完した。再監査時に原文の直接確認を試みる
- 特商法12条の6（2022-06-01）・外部送信規律（2023-06-16）の施行日は二次情報ベース。正式文書に載せる場合は官報・e-Gov 沿革で確認する
- The Verge は PMC 買収（2026年6月）直後で規約が動いている。次回は PMC 規約の版日付の変化を確認する
