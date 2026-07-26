---
layout: page
title: "アーカイブ"
---

<div class="archive-search">
  <input type="text" id="archive-filter" placeholder="キーワードで絞り込み…" autocomplete="off">
</div>

<p id="archive-no-results" class="archive-no-results" hidden>該当する記事が見つかりません</p>

{% assign posts_by_month = site.posts | group_by_exp: "post", "post.date | date: '%Y%m'" | sort: "name" | reverse %}

{% for group in posts_by_month %}
<div class="archive-month" data-month="{{ group.name }}">
<h2>{{ group.items.first.date | date: '%Y年%-m月' }}</h2>

<ul class="archive-list">
{% for post in group.items %}
  <li data-content="{{ post.content | strip_html | strip_newlines | truncatewords: 100 | escape }}">
    <a href="{{ post.url | relative_url }}">{{ post.title }}</a>
    {% if post.excerpt %}<p class="archive-excerpt">{{ post.excerpt | strip_html | truncatewords: 30 }}</p>{% endif %}
  </li>
{% endfor %}
</ul>
</div>
{% endfor %}

<script>
(function() {
  var input = document.getElementById('archive-filter');
  var noResults = document.getElementById('archive-no-results');
  var months = document.querySelectorAll('.archive-month');
  if (!input) return;

  input.addEventListener('input', function() {
    var query = this.value.toLowerCase().trim();
    var totalVisible = 0;

    for (var i = 0; i < months.length; i++) {
      var items = months[i].querySelectorAll('.archive-list li');
      var monthVisible = 0;

      for (var j = 0; j < items.length; j++) {
        var content = (items[j].getAttribute('data-content') || '').toLowerCase();
        var title = items[j].textContent.toLowerCase();
        var match = !query || content.indexOf(query) !== -1 || title.indexOf(query) !== -1;
        items[j].style.display = match ? '' : 'none';
        if (match) monthVisible++;
      }

      months[i].style.display = monthVisible > 0 ? '' : 'none';
      totalVisible += monthVisible;
    }

    noResults.hidden = totalVisible > 0 || !query;
  });

  input.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
      this.value = '';
      this.dispatchEvent(new Event('input'));
    }
  });
})();
</script>
