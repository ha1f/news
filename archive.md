---
layout: page
title: "アーカイブ"
---

{% assign posts_by_month = site.posts | group_by_exp: "post", "post.date | date: '%Y%m'" | sort: "name" | reverse %}

{% for group in posts_by_month %}
## {{ group.items.first.date | date: '%Y年%-m月' }}

<ul class="archive-list">
{% for post in group.items %}
  <li>
    <a href="{{ post.url | relative_url }}">{{ post.title }}</a>
    {% if post.excerpt %}<p class="archive-excerpt">{{ post.excerpt | strip_html | truncatewords: 30 }}</p>{% endif %}
  </li>
{% endfor %}
</ul>
{% endfor %}
