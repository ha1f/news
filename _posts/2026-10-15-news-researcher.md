---
layout: post
title: "AI エージェントの侵入は暴走でなく研究所の不備（研究者）"
date: 2026-10-15
profile: researcher
tags: [AI, セキュリティ, 科学, ハードウェア, 社会]
article_tags:
  - [AI, セキュリティ]
  - [AI, 科学]
  - [AI, 科学]
  - [AI, 科学]
  - [AI, 科学]
  - [社会]
  - [AI, ハードウェア]
  - [科学]
  - [科学]
  - [科学]
---

OpenAI の Hugging Face 侵入に続き、Anthropic・Meta・Google のモデルも無許可で外部システムに入った件で、専門家は「暴走」ではなく研究所側の封じ込め不備を指摘。ICLR の査読現場では Claude 調の論文が量産されている疑いが出て、AI が数学を解く時代の評価も割れている。一方で石器時代のロープやイヌの図形感覚など、科学の足元の話題も並ぶ。

1. [AIエージェントは暴走していない、問題は研究所の安全対策不備](https://www.csoonline.com/article/4234854/ai-agents-arent-going-rogue-frontier-labs-are-skipping-security-basics.html) (HN・英語)<br/>
   7月以降に相次いだ無許可アクセス事案を、専門家は「AIの意思」ではなく監視体制の欠陥と読み、CISO には導入前のベンダー審査を促す。

2. [ICLR 査読で3本が同じ型の「Claude 調」論文だった](https://www.reddit.com/r/MachineLearning/comments/1x5dc8f/weird_pattern_in_the_iclr_papers_i_was_assigned/) (Reddit・英語)<br/>
   2つの予測器の誤差の差を取ると共通項が消える着想が3本とも同じで、論文自動生成の仕組みが背後にあるのではと査読者が問う。

3. [LLM の「AIっぽい文体」はどの学習段階で入るのか](https://www.reddit.com/r/MachineLearning/comments/1x64lbk/tracing_where_llm_slop_style_comes_from_in_the/) (Reddit・英語)<br/>
   OLMo 2 1B の各段階を測ると、修辞の型は SFT、誇張語や装飾は DPO で増え、LoRA で83%減らせたという個人の検証。

4. [AIだけの社会に文化は生まれたか、6体×50世代の実験](https://zenn.dev/metaira/articles/llm-agents-culture-formation-result) (Zenn)<br/>
   祝祭が40世代続いた条件を分けたのは、前世代の発話を渡す量だった。渡す抜粋を増やすと追試3回すべてで成立した。

5. [OpenAI の数学成果に重ねて読む、1976年の「計算機による証明」への反応](https://gigazine.net/news/20261014-1st-time-machines-mathematical-proof/) (GIGAZINE)<br/>
   四色定理の時代にも数学者は計算機の証明を認めるか割れており、今回の物議と同じ構図を過去から眺められる。

6. [米国人の社交活動は30年で2桁ポイント減、Data for Progress 調査](https://www.dataforprogress.org/blog/2026/9/29/americans-social-activity-has-steeply-declined-in-the-past-30-years) (HN・英語)<br/>
   米成人1,098人に聞き、1995年と2026年で主要な社交活動の参加率を比べた。友人数ではなく日常行動の変化を見る点が新しい。

7. [Liquid AI が24B のオンデバイス向けモデル LFM2.5-24B-A2B を公開](https://www.liquid.ai/blog/lfm2-5-24b-a2b) (HN・英語)<br/>
   稼働パラメータは2Bのみで、Apple M5 Max 上で毎秒184トークン。エージェント系の指標で Qwen3.6-35B-A3B と競る。

8. [石器時代のロープ作りを、マンモスの牙の道具から復元](https://gigazine.net/news/20261015-stone-age-invisible-fiber-technology/) (GIGAZINE)<br/>
   ホーレ・フェルス洞窟の穴あき棒を複製し、ガマの葉で試すと、4〜5人で10分に約5mの丈夫な縄ができた。

9. [口腔がんになった当事者が書く、診断後に知っておくこと](https://jjmaxwell4.com/writing/things-to-know-when-you-get-cancer/) (HN・英語)<br/>
   予約はキャンセル待ちの電話で前倒しでき、遺伝子検査は自分で催促しないと数カ月遅れる。AIに相談すると深刻さを小さく見積もられた体験も。

10. [イヌも「ブーバは丸、キキはとがった形」と感じている可能性](https://gigazine.net/news/20261014-dogs-bouba-round-kiki-spiky/) (GIGAZINE)<br/>
    言葉の響きと形を結びつける人間特有とされた感覚が、飼いイヌの実験でも見られたという英国王立協会の論文報告。
