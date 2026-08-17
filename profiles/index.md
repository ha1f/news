---
layout: page
title: "プロファイル"
---

同じ日のニュースを、職種ごとの関心に合わせて別の切り口でまとめています。

{% assign profile_pages = site.pages | where: "layout", "profile" | sort: "title" %}

<ul class="profile-nav-list">
{% for p in profile_pages %}
<li>
  <a href="{{ p.url | relative_url }}">{{ p.title | escape }}</a>
  {% if p.description %}<span class="profile-nav-desc"> — {{ p.description | escape }}</span>{% endif %}
  {%- assign latest_post = site.posts | where: "profile", p.profile | first -%}
  {%- if latest_post -%}
  <br><span class="profile-nav-desc"><a href="{{ latest_post.url | relative_url }}">{{ latest_post.date | date: "%-m月%-d日" }}のフィード →</a></span>
  {%- endif -%}
</li>
{% endfor %}
</ul>

## 自分用のフィードを作る

既存のプロファイルに合うものがない場合、2つの方法でカスタムフィードを作れます。

### リクエストする

興味のある分野を伝えるだけで、あなた専用のプロファイルを作成します。[こちらからリクエスト](https://github.com/ha1f/news/issues/new?template=profile-request.yml)してください。

### 自分で作る（GitHub ユーザー向け）

リポジトリを [Fork](https://github.com/ha1f/news/fork) し、好みの設定を編集すると、毎日自分向けにキュレーションされたニュースが届きます。詳細は [README の「Forkして使う」](https://github.com/ha1f/news#forkして使う) をご覧ください。
