---
layout: page
title: "プロファイル"
---

プロファイルフィードでは、トップページとは異なる記事を届けます。同じニュースソースの中から、各職種の関心に特化した記事をピックアップしているため、全体フィードには載らない専門的な話題も見つかります。

{% assign profile_pages = site.pages | where: "layout", "profile" | sort: "title" %}

<ul class="profile-nav-list">
{% for p in profile_pages %}
<li>
  <a href="{{ p.url | relative_url }}">{{ p.title | escape }}</a>
  {% if p.description %}<span class="profile-nav-desc"> — {{ p.description | escape }}</span>{% endif %}
  {%- if p.topics.size > 0 -%}
  <br><span class="profile-nav-topics">{%- for topic in p.topics -%}<a class="profile-nav-topic" href="{{ p.url | relative_url }}?tag={{ topic | url_encode }}">{{ topic | escape }}</a>{%- unless forloop.last -%} {%- endunless -%}{%- endfor -%}</span>
  {%- endif -%}
  {%- assign latest_post = site.posts | where: "profile", p.profile | first -%}
  {%- if latest_post -%}
  <br><span class="profile-nav-desc"><a href="{{ latest_post.url | relative_url }}">{{ latest_post.date | date: "%-m月%-d日" }}のフィード →</a></span>
  {%- endif -%}
  {%- if p.profile -%}
  <br><span class="profile-nav-desc"><a href="{{ '/profiles/' | append: p.profile | append: '-feed.xml' | relative_url }}" aria-label="{{ p.title | escape }} を RSS で購読"><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="currentColor" style="vertical-align: -1px; margin-right: 3px;"><circle cx="6.18" cy="17.82" r="2.18"/><path d="M4 4.44v2.83c7.03 0 12.73 5.7 12.73 12.73h2.83c0-8.59-6.97-15.56-15.56-15.56zm0 5.66v2.83c3.9 0 7.07 3.17 7.07 7.07h2.83c0-5.47-4.43-9.9-9.9-9.9z"/></svg>RSS で購読</a></span>
  {%- endif -%}
  {%- if latest_post -%}
  {%- if latest_post.content contains '<li>' -%}
  {%- assign article_items = latest_post.content | split: '<li>' -%}
  {%- assign article_count = 0 -%}
  <ul class="archive-article-titles">
    {%- for item in article_items offset: 1 -%}
      {%- if item contains '</a>' -%}
        {%- assign before_close_a = item | split: '</a>' | first -%}
        {%- assign link_text = before_close_a | strip_html -%}
        {%- if link_text.size > 1 -%}
          {%- assign article_count = article_count | plus: 1 -%}
          {%- if article_count <= 3 -%}
          <li><a href="{{ latest_post.url | relative_url }}#article-{{ forloop.index }}">{{ link_text }}</a></li>
          {%- endif -%}
        {%- endif -%}
      {%- endif -%}
    {%- endfor -%}
    {%- assign remaining = article_count | minus: 3 -%}
    {%- if remaining > 0 -%}
    <li class="archive-article-more"><a href="{{ latest_post.url | relative_url }}">他{{ remaining }}件</a></li>
    {%- endif -%}
  </ul>
  {%- endif -%}
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
