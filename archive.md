---
layout: page
title: "アーカイブ"
---

{%- assign profile_pages = site.pages | where: "layout", "profile" | sort: "title" -%}
{%- if profile_pages.size > 0 -%}
<p class="archive-profile-nav">プロファイル別:
{%- for p in profile_pages -%}
  <a href="{{ p.url | relative_url }}">{{ p.title | escape }}</a>
  {%- unless forloop.last %} / {% endunless -%}
{%- endfor -%}
</p>
{%- endif -%}

{% assign default_posts = site.posts | where_exp: "post", "post.profile == nil" %}

{%- assign all_tags = "" -%}
{%- for post in default_posts -%}
  {%- for tag in post.tags -%}
    {%- assign all_tags = all_tags | append: tag | append: "," -%}
  {%- endfor -%}
{%- endfor -%}
{%- assign tag_array = all_tags | split: "," | uniq | sort -%}
{%- if tag_array.size > 0 -%}
<div class="archive-tags" role="group" aria-label="トピックフィルタ">
  <span class="archive-tags-label">トピック:</span>
  {%- for tag in tag_array -%}
    {%- if tag != "" -%}
    <button class="archive-tag" data-tag="{{ tag | escape }}">{{ tag | escape }}</button>
    {%- endif -%}
  {%- endfor -%}
</div>
{%- endif -%}

<p id="archive-tag-feed" class="profile-feed-link" hidden>
  <a id="archive-tag-feed-link" href="#">
    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="currentColor" style="vertical-align: -2px; margin-right: 4px;"><circle cx="6.18" cy="17.82" r="2.18"/><path d="M4 4.44v2.83c7.03 0 12.73 5.7 12.73 12.73h2.83c0-8.59-6.97-15.56-15.56-15.56zm0 5.66v2.83c3.9 0 7.07 3.17 7.07 7.07h2.83c0-5.47-4.43-9.9-9.9-9.9z"/></svg>
    「<span id="archive-tag-feed-name"></span>」を RSS で購読
  </a>
</p>

<div class="archive-search">
  <input type="text" id="archive-filter" placeholder="キーワードで絞り込み…" autocomplete="off">
</div>

<p id="archive-no-results" class="archive-no-results" hidden>該当する記事が見つかりません</p>

{% assign posts_by_month = default_posts | group_by_exp: "post", "post.date | date: '%Y%m'" | sort: "name" | reverse %}

{% for group in posts_by_month %}
<div class="archive-month" data-month="{{ group.name }}">
<h2>{{ group.items.first.date | date: '%Y年%-m月' }}</h2>

<ul class="archive-list">
{% for post in group.items %}
  <li data-content="{{ post.content | strip_html | strip_newlines | truncatewords: 100 | escape }}" data-tags="{{ post.tags | join: ',' | escape }}">
    <a href="{{ post.url | relative_url }}">{{ post.title }}</a>
    {% if post.tags.size > 0 %}<span class="archive-item-tags">{{ post.tags | join: " / " }}</span>{% endif %}
    {% if post.excerpt %}<p class="archive-excerpt">{{ post.excerpt | strip_html | truncatewords: 30 }}</p>{% endif %}
  </li>
{% endfor %}
</ul>
</div>
{% endfor %}

<script>
(function() {
  var INITIAL_MONTHS = 3;
  var input = document.getElementById('archive-filter');
  var noResults = document.getElementById('archive-no-results');
  var months = document.querySelectorAll('.archive-month');
  var tagButtons = document.querySelectorAll('.archive-tag');
  var activeTag = null;
  var tagFeedEl = document.getElementById('archive-tag-feed');
  var tagFeedLink = document.getElementById('archive-tag-feed-link');
  var tagFeedName = document.getElementById('archive-tag-feed-name');
  var tagsBaseUrl = '{{ "/tags/" | relative_url }}';
  var showAll = months.length <= INITIAL_MONTHS;
  var moreBtn = null;

  if (!showAll) {
    moreBtn = document.createElement('button');
    moreBtn.className = 'archive-show-more';
    var hiddenCount = months.length - INITIAL_MONTHS;
    moreBtn.textContent = '過去の記事を表示（他' + hiddenCount + 'ヶ月分）';
    months[months.length - 1].parentNode.appendChild(moreBtn);
    moreBtn.addEventListener('click', function() {
      showAll = true;
      applyFilters();
    });
  }

  function applyFilters() {
    var query = (input ? input.value : '').toLowerCase().trim();
    var isFiltering = !!(query || activeTag);
    var totalVisible = 0;

    for (var i = 0; i < months.length; i++) {
      if (!showAll && !isFiltering && i >= INITIAL_MONTHS) {
        months[i].style.display = 'none';
        continue;
      }

      var items = months[i].querySelectorAll('.archive-list li');
      var monthVisible = 0;

      for (var j = 0; j < items.length; j++) {
        var matchTag = true;
        var matchQuery = true;

        if (activeTag) {
          var tags = (items[j].getAttribute('data-tags') || '').split(',');
          matchTag = tags.indexOf(activeTag) !== -1;
        }

        if (query) {
          var content = (items[j].getAttribute('data-content') || '').toLowerCase();
          var titleEl = items[j].querySelector('a');
          var title = (titleEl ? titleEl.textContent : '').toLowerCase();
          matchQuery = content.indexOf(query) !== -1 || title.indexOf(query) !== -1;
        }

        var visible = matchTag && matchQuery;
        items[j].style.display = visible ? '' : 'none';
        if (visible) monthVisible++;
      }

      months[i].style.display = monthVisible > 0 ? '' : 'none';
      totalVisible += monthVisible;
    }

    if (moreBtn) moreBtn.hidden = showAll || isFiltering;
    noResults.hidden = totalVisible > 0 || (!query && !activeTag);
    if (tagFeedEl) {
      if (activeTag) {
        tagFeedLink.href = tagsBaseUrl + encodeURIComponent(activeTag) + '/feed.xml';
        tagFeedName.textContent = activeTag;
        tagFeedEl.hidden = false;
      } else {
        tagFeedEl.hidden = true;
      }
    }
  }

  applyFilters();

  for (var k = 0; k < tagButtons.length; k++) {
    tagButtons[k].addEventListener('click', function() {
      var tag = this.getAttribute('data-tag');
      if (activeTag === tag) {
        activeTag = null;
        this.classList.remove('active');
      } else {
        for (var b = 0; b < tagButtons.length; b++) {
          tagButtons[b].classList.remove('active');
        }
        activeTag = tag;
        this.classList.add('active');
      }
      applyFilters();
    });
  }

  if (input) {
    input.addEventListener('input', applyFilters);
    input.addEventListener('keydown', function(e) {
      if (e.key === 'Escape') {
        this.value = '';
        applyFilters();
      }
    });
  }

  var params = new URLSearchParams(location.search);
  var urlTag = params.get('tag');
  if (urlTag) {
    for (var t = 0; t < tagButtons.length; t++) {
      if (tagButtons[t].getAttribute('data-tag') === urlTag) {
        activeTag = urlTag;
        tagButtons[t].classList.add('active');
        applyFilters();
        break;
      }
    }
  }
})();
</script>
