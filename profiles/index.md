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
