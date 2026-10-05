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

{%- comment -%}絞り込み前に受け取る HTML が記事の蓄積に比例して増え続けないよう、
ページに直接描くのは直近 initial_months か月分だけにする (#354)。それより前の月は
archive-older.html に描き、「過去の記事を表示」か絞り込みを始めた時点で取得して差し込む。
JS が動かない読者にはそのままリンクとして働く。月数は archive-older.html と共有するため _config.yml に置く{%- endcomment -%}
{%- assign initial_months = site.archive_initial_months | default: 3 -%}
<div id="archive-months">
{% include archive-months.html groups=posts_by_month offset=0 limit=initial_months %}
</div>
{%- assign older_months = posts_by_month.size | minus: initial_months -%}
{%- if older_months > 0 %}
<div class="archive-older"><a id="archive-show-older" class="archive-show-more" href="{{ '/archive-older.html' | relative_url }}">過去の記事を表示（他{{ older_months }}ヶ月分）</a></div>
{%- endif %}

<script>
(function() {
  var INITIAL_MONTHS = {{ initial_months }};
  var input = document.getElementById('archive-filter');
  var noResults = document.getElementById('archive-no-results');
  var monthsEl = document.getElementById('archive-months');
  var months = monthsEl.querySelectorAll('.archive-month');
  var tagButtons = document.querySelectorAll('.archive-tag');
  var activeTag = null;
  var tagFeedEl = document.getElementById('archive-tag-feed');
  var tagFeedLink = document.getElementById('archive-tag-feed-link');
  var tagFeedName = document.getElementById('archive-tag-feed-name');
  var tagsBaseUrl = '{{ "/tags/" | relative_url }}';
  var moreBtn = document.getElementById('archive-show-older');
  var showAll = !moreBtn;

  // 直近 INITIAL_MONTHS か月より前は archive-older.html にあり、ページには入っていない
  // (#354)。「過去の記事を表示」を押すか絞り込みを始めた時点で取得して差し込む。
  // 取得に失敗したら moreBtn をリンクのまま残し、読者が自分で開けるようにする
  var olderLoaded = !moreBtn;
  var olderInFlight = false;
  // 失敗したら、読者が次に操作するまで取り直さない。取得後の applyFilters が
  // 絞り込み中に再び取得を始めるので、抑止が無いと失敗→再取得が止まらなくなる
  var olderFailed = false;
  var focusFirstOlder = false;

  function loadOlderMonths() {
    if (olderLoaded || olderInFlight || olderFailed) return;
    if (typeof fetch !== 'function' || typeof DOMParser !== 'function') return;
    olderInFlight = true;
    fetch(moreBtn.href)
      .then(function(res) { return res.ok ? res.text() : Promise.reject(res.status); })
      .then(function(html) {
        var doc = new DOMParser().parseFromString(html, 'text/html');
        var older = doc.querySelectorAll('#archive-months .archive-month');
        // 200 でも中身が想定外 (ログイン画面・プロキシのエラーページ) なら失敗として扱う。
        // 0 件を「読み込み済み」にすると、リンクが消えたまま古い月に二度と届かない
        if (older.length === 0) return Promise.reject('empty');
        for (var i = 0; i < older.length; i++) {
          monthsEl.appendChild(document.importNode(older[i], true));
        }
        months = monthsEl.querySelectorAll('.archive-month');
        olderLoaded = true;
      })
      .catch(function() { olderFailed = true; })
      .then(function() {
        olderInFlight = false;
        applyFilters();
        // 表示されてからでないとフォーカスできないので applyFilters の後
        var first = olderLoaded && focusFirstOlder && months[INITIAL_MONTHS];
        var heading = first && first.style.display !== 'none' && first.querySelector('h2');
        if (heading) {
          heading.setAttribute('tabindex', '-1');
          heading.focus();
        }
        focusFirstOlder = false;
      });
  }

  // 本文テキストは絞り込みを始めるまで取得しない (#354)。到着するまでは
  // タイトルと日付だけで当て、到着したら applyFilters をもう一度回して
  // 本文一致を足す。取得に失敗しても絞り込み自体は止めず、当たり幅が
  // タイトル・日付どまりになるだけにする
  var contentIndex = null;
  var indexInFlight = false;
  var indexTriedQuery = null;
  var contentIndexUrl = '{{ "/archive-index.json" | relative_url }}';

  // 同じクエリでは取得を繰り返さないが、失敗したあと次の入力が来れば取り直す。
  // 一度の失敗 (電波の瞬断、一瞬の 5xx) がその訪問のあいだ本文一致を殺したまま
  // になると、読者には手がかりが何も出ない
  function loadContentIndex(query) {
    if (contentIndex || indexInFlight || indexTriedQuery === query) return;
    if (typeof fetch !== 'function') return;
    indexTriedQuery = query;
    indexInFlight = true;
    fetch(contentIndexUrl)
      .then(function(res) { return res.ok ? res.json() : Promise.reject(res.status); })
      .then(function(data) { contentIndex = data; })
      .catch(function() {})
      .then(function() {
        indexInFlight = false;
        // この applyFilters は取得中にクエリが変わっていると新しい取得を始める
        // (indexInFlight が立ち直す) ので、その場合は目印を消さない。消すと次の失敗で
        // また取得が走り、読者が何も触らなくても再取得が止まらなくなる。
        // 取得が走らなかったときだけ抑止を解き、次に読者が動いたとき取り直せるようにする
        applyFilters();
        if (!contentIndex && !indexInFlight) indexTriedQuery = null;
      });
  }

  if (moreBtn) {
    moreBtn.addEventListener('click', function(e) {
      // 取得できない環境と、新しいタブで開く操作 (修飾キー) はリンクのまま通す
      if (typeof fetch !== 'function' || typeof DOMParser !== 'function') return;
      if (e.button !== 0 || e.ctrlKey || e.metaKey || e.shiftKey || e.altKey) return;
      e.preventDefault();
      showAll = true;
      olderFailed = false;
      // 押したリンク自身が消えるので、取得後にフォーカスを先頭の古い月の見出しへ移す
      // (キーボード・読み上げの利用者が位置を見失わないように)
      focusFirstOlder = true;
      loadOlderMonths();
      applyFilters();
    });
  }

  function articleTitles(item) {
    return item.querySelectorAll('.archive-article-titles > li:not(.archive-article-more)');
  }

  function hasArticleTag(li, tag) {
    return (li.getAttribute('data-tags') || '').split(',').indexOf(tag) !== -1;
  }

  // 記事単位のトピックを持つ日で、そのトピックの記事
  function titlesWithTag(item, tag) {
    var result = [];
    if (!tag || !item.hasAttribute('data-article-tags')) return result;
    var titles = articleTitles(item);
    for (var i = 0; i < titles.length; i++) {
      if (hasArticleTag(titles[i], tag)) result.push(titles[i]);
    }
    return result;
  }

  // 既定は先頭3件だけを見せる。キーワードで絞ったときは一致した見出し「だけ」を
  // 残して、何が一致したのかを結果から読み取れるようにする。見出しが1件も一致
  // しない日（概況文や本文で一致した日）は既定の3件に戻す。
  // トピックで絞ったときは、記事単位のトピックを持つ日ならそのトピックの記事「だけ」を
  // 残す (#354)。キーワードとの併用では、そのうち見出しが一致したものに絞る
  function revealMatchingTitles(item, query, tag) {
    var titles = articleTitles(item);
    var more = item.querySelector('.archive-article-more');
    var matched = [];
    var tagged = titlesWithTag(item, tag);
    var pool = tagged.length > 0 ? tagged : titles;

    if (query) {
      for (var i = 0; i < pool.length; i++) {
        if (pool[i].textContent.toLowerCase().indexOf(query) !== -1) matched.push(pool[i]);
      }
    }
    if (matched.length === 0 && tagged.length > 0) matched = tagged;

    var hiddenCount = 0;
    for (var j = 0; j < titles.length; j++) {
      var show = matched.length > 0
        ? matched.indexOf(titles[j]) !== -1
        : !titles[j].classList.contains('archive-article-extra');
      titles[j].hidden = !show;
      if (!show) hiddenCount++;
    }

    if (more) {
      more.hidden = hiddenCount === 0;
      var link = more.querySelector('a');
      // トピックで絞った日の残りは「同じトピックの続き」ではなく別トピックの記事
      if (link && hiddenCount > 0) link.textContent = (tagged.length > 0 ? '別トピック' : '他') + hiddenCount + '件';
    }
  }

  function applyFilters() {
    var query = (input ? input.value : '').toLowerCase().trim();
    var isFiltering = !!(query || activeTag);
    if (query) loadContentIndex(query);
    if (isFiltering) loadOlderMonths();
    var totalVisible = 0;

    for (var i = 0; i < months.length; i++) {
      if (!showAll && !isFiltering && i >= INITIAL_MONTHS) {
        months[i].style.display = 'none';
        continue;
      }

      var items = months[i].querySelectorAll('.archive-list > li');
      var monthVisible = 0;

      for (var j = 0; j < items.length; j++) {
        var matchTag = true;
        var matchQuery = true;

        if (activeTag) {
          // 記事単位のトピックを持つ日は、そのトピックの記事が1本でもあるかで当てる
          matchTag = items[j].hasAttribute('data-article-tags')
            ? titlesWithTag(items[j], activeTag).length > 0
            : hasArticleTag(items[j], activeTag);
        }

        if (query) {
          var url = items[j].getAttribute('data-url');
          var indexed = (contentIndex && url && contentIndex[url]) || '';
          var content = indexed.toLowerCase();
          var titleEl = items[j].querySelector('a');
          var title = (titleEl ? titleEl.textContent : '').toLowerCase();
          // 日付バッジも絞り込みの対象にする。新形式の title には日付が入らないので、
          // これが無いと「9月20日」のような日付での絞り込みが効かなくなる (#341)
          var dateEl = items[j].querySelector('.archive-item-date');
          var dateText = (dateEl ? dateEl.textContent : '').toLowerCase();
          matchQuery = content.indexOf(query) !== -1 || title.indexOf(query) !== -1
            || dateText.indexOf(query) !== -1;
        }

        var visible = matchTag && matchQuery;
        items[j].style.display = visible ? '' : 'none';
        if (visible) {
          monthVisible++;
          revealMatchingTitles(items[j], query, activeTag);
        }
      }

      months[i].style.display = monthVisible > 0 ? '' : 'none';
      totalVisible += monthVisible;
    }

    // 古い月を取得できなかったとき (取得中を除く) は、絞り込み中でもリンクを残す。
    // 結果が直近の月だけに偏っていることを読者が知る手がかりはこれしかない
    if (moreBtn) moreBtn.hidden = olderLoaded ? (showAll || isFiltering) : olderInFlight;
    // 本文インデックスの取得中は「見つかりません」を出さない。本文でしか
    // 当たらない語は到着するまで 0 件に見えるので、断定して出すと読者には
    // 「無かった」と読める (実測: 50KB/s の回線で最大約3秒この状態だった)
    // 古い月を取得できていない間 (取得中・失敗) も同じ理由で出さない。直近の月に無くても
    // 古い月で当たりうる。失敗時は残したリンクが「まだ先がある」ことを示す
    noResults.hidden = totalVisible > 0 || (!query && !activeTag) || (indexInFlight && !!query)
      || (!olderLoaded && isFiltering);
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
      olderFailed = false;
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
    input.addEventListener('input', function() {
      olderFailed = false;
      applyFilters();
    });
    // 本文インデックスは検索窓に触れた時点で取りにいく。1文字目を待つと、
    // 到着までのあいだタイトル・日付だけで当たった少ない結果が完成品の顔で出る。
    // 窓に触れない読者 (タグ・「過去の記事も見る」だけ) は取得しない
    input.addEventListener('focus', function() { loadContentIndex(''); });
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
