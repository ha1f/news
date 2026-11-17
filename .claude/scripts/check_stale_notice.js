#!/usr/bin/env node
// 配信停止の表示 (#652, _includes/stale-notice.html) を、ブラウザの時計をずらして確かめる。
//
//   node .claude/scripts/check_stale_notice.js <base URL> [スクリーンショットの出力先 dir]
//   例: node .claude/scripts/check_stale_notice.js http://localhost:4000/news/ /tmp/shots
//
// base URL は `_site` を `<dir>/news/` に置いて配信したもの (baseurl: /news)。
// トップと全プロファイルについて、各ページの一覧の先頭の日付を「最新」として
//   (a) 最新の当日 (JST) → 表示なし
//   (b) 翌日 → 「今日（M月D日）の分は…」
//   (c) 2日後 → 「M月D日〜今日（M月D日）の分は…」
// を検査する。失敗を集計してから最後に結果を出し、1件でも失敗すれば exit 1。
const path = require('path');
let playwright;
try {
  playwright = require('playwright');
} catch (e) {
  playwright = require('/opt/node22/lib/node_modules/playwright');
}

const base = process.argv[2];
const shotDir = process.argv[3];
if (!base) {
  console.error('usage: check_stale_notice.js <base URL> [screenshot dir]');
  process.exit(2);
}

// 期待値はテスト側で直書きの規則から作る (表示側のコードを流用しない)
function label(y, m, d) {
  const t = new Date(Date.UTC(y, m - 1, d));
  return `${t.getUTCMonth() + 1}月${t.getUTCDate()}日`;
}

(async () => {
  const browser = await playwright.chromium.launch();
  const failures = [];
  const pages = [''];
  {
    const page = await browser.newPage();
    await page.goto(new URL('profiles/', base).href);
    const hrefs = await page.$$eval('a[href*="/profiles/"]', as =>
      as.map(a => a.getAttribute('href')).filter(h => /\/profiles\/[a-z-]+\.html$/.test(h)));
    for (const h of [...new Set(hrefs)]) pages.push(new URL(h, base).pathname.replace(new URL(base).pathname, ''));
    await page.close();
  }
  if (pages.length < 2) failures.push('プロファイルのページが見つからない');

  let checked = 0;
  for (const p of pages) {
    const url = new URL(p, base).href;
    // 最新の日付は時計をずらさずに読む
    const probe = await browser.newPage();
    await probe.goto(url);
    const listSel = p === '' ? '.post-list' : '#archive-months';
    const dates = await probe.$$eval(`${listSel} li[data-date]`, lis => lis.map(li => li.getAttribute('data-date')));
    const latest = dates[0] || null;
    // 表示側は「先頭が最新」を前提にしている。並び順が変わったら前提ごと崩れるので確かめる
    if (latest && dates.some(x => x > latest)) failures.push(`${p || 'top'}: 一覧の先頭 ${latest} が最新でない`);
    await probe.close();
    if (!latest) { failures.push(`${p || 'top'}: 一覧の data-date が無い`); continue; }
    const [y, m, d] = latest.split('-').map(Number);
    const cases = [
      { name: 'same-day', offset: 0, expect: null },
      { name: 'next-day', offset: 1, expect: `今日（${label(y, m, d + 1)}）の分はまだ配信されていません。最新は${label(y, m, d)}の分です。` },
      { name: 'two-days', offset: 2, expect: `${label(y, m, d + 1)}〜今日（${label(y, m, d + 2)}）の分はまだ配信されていません。最新は${label(y, m, d)}の分です。` },
    ];
    for (const c of cases) {
      // 端末は JST 以外 (ロサンゼルス) に置き、JST の日付の境目のすぐ内側の 00:30 と 23:30 で見る。
      // JST 00:30 は UTC でも LA でも前日なので、JST 以外の日付で数える誤りを落とせる
      for (const [scheme, jstHour] of [['light', 0], ['dark', 23]]) {
        const context = await browser.newContext({ colorScheme: scheme, viewport: { width: 375, height: 812 }, timezoneId: 'America/Los_Angeles' });
        const page = await context.newPage();
        await page.clock.setFixedTime(new Date(Date.UTC(y, m - 1, d + c.offset, jstHour - 9, 30, 0)));
        await page.goto(url);
        const notice = page.locator('.stale-notice');
        const visible = await notice.isVisible();
        const text = visible ? (await notice.textContent()).trim() : null;
        const where = `${p || 'top'} ${c.name} ${scheme} JST${jstHour}:30`;
        if (c.expect === null && visible) failures.push(`${where}: 表示されるべきでないのに出た: ${text}`);
        if (c.expect !== null && text !== c.expect) failures.push(`${where}: 期待「${c.expect}」 実際「${text}」`);
        if (shotDir && (scheme === 'light' || p === '')) {
          const name = `${(p || 'top').replace(/[\/.]/g, '_')}-${c.name}-${scheme}.png`;
          await page.screenshot({ path: path.join(shotDir, name), clip: { x: 0, y: 0, width: 375, height: 812 } });
        }
        checked++;
        await context.close();
      }
    }
  }
  await browser.close();
  if (failures.length) {
    console.log(`NG ${failures.length} 件 / 検査 ${checked} 件`);
    for (const f of failures) console.log('  ' + f);
    process.exit(1);
  }
  console.log(`OK 検査 ${checked} 件 (${pages.length} ページ × 3 日付 × light・JST 00:30 / dark・JST 23:30、端末は LA)`);
})();
