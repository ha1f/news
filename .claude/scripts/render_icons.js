// assets/favicon.svg から PNG アイコンを再生成する。
// 変換ツール（convert / rsvg-convert 等）がこの環境に無いため、Playwright の
// Chromium に SVG を描かせてスクリーンショットを撮る。アクセント色を変えたら
// favicon.svg だけを直し、このスクリプトで PNG を作り直す。
//
//   node .claude/scripts/render_icons.js
//
// 出力: assets/favicon-32x32.png (32x32) / assets/apple-touch-icon.png (180x180)
const path = require('path');
const fs = require('fs');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || '/opt/node22/lib/node_modules/playwright');

const ROOT = path.resolve(__dirname, '..', '..');
const SRC = path.join(ROOT, 'assets', 'favicon.svg');
const TARGETS = [
  { size: 32, out: path.join(ROOT, 'assets', 'favicon-32x32.png') },
  { size: 180, out: path.join(ROOT, 'assets', 'apple-touch-icon.png') },
];

(async () => {
  const svg = fs.readFileSync(SRC, 'utf8');
  const browser = await chromium.launch();
  try {
    for (const { size, out } of TARGETS) {
      const ctx = await browser.newContext({
        viewport: { width: size, height: size },
        deviceScaleFactor: 1,
      });
      const page = await ctx.newPage();
      await page.setContent(
        `<!doctype html><meta charset="utf-8">` +
        `<style>html,body{margin:0;padding:0;background:transparent}` +
        `svg{display:block;width:${size}px;height:${size}px}</style>` +
        svg
      );
      await page.screenshot({ path: out, omitBackground: true });
      await ctx.close();
      console.log(`${path.relative(ROOT, out)} (${size}x${size})`);
    }
  } finally {
    await browser.close();
  }
})();
