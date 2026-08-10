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
</li>
{% endfor %}
</ul>

## 自分用のフィードを作る

既存のプロファイルに合うものがなくても、自分の関心に合わせたカスタムフィードを作れます。GitHub でリポジトリを [Fork](https://github.com/ha1f/news/fork) し、好みの設定を編集するだけで、毎日自分向けにキュレーションされたニュースが届くようになります。

始め方の詳細は [README の「Forkして使う」](https://github.com/ha1f/news#forkして使う) をご覧ください。
