#!/usr/bin/env bash
# PR の CI（jekyll-build-check.yml の「Screenshot pages」）で撮るページと幅の正本。
# workflow は保護パス（人間のマージが要る）なので、撮る対象のように変わりやすい中身はここに置く。
#
# 使い方: ci_screenshots.sh <配信中サイトの base URL>（例 http://localhost:4000/news）
#   repo ルートで、_site をビルドしてサイトを配信した後に実行する。画像は screenshots/ に出る
#   PLAYWRIGHT_VERSION は workflow の env（Renovate が更新する）から受け取る
set -e
base="${1:?配信中サイトの base URL を渡す}"
: "${PLAYWRIGHT_VERSION:?workflow の env で PLAYWRIGHT_VERSION を渡す}"

mkdir -p screenshots
shot() {
  npx --yes "playwright@$PLAYWRIGHT_VERSION" screenshot --browser chromium --full-page \
    --viewport-size "$1" --color-scheme "$2" "$3" "screenshots/$4"
}
shot 1280,900 light "$base/" home-light.png
shot 1280,900 dark  "$base/" home-dark.png
shot 375,812  light "$base/" home-mobile-light.png
shot 375,812  dark  "$base/" home-mobile-dark.png
latest=$(find _site -regex '.*/20[0-9][0-9]/.*\.html' | sort | tail -1)
if [ -n "$latest" ]; then
  path="${latest#_site/}"
  shot 1280,900 light "$base/$path" article-light.png
  shot 1280,900 dark  "$base/$path" article-dark.png
fi
if [ -f _site/archive.html ]; then
  shot 1280,900 light "$base/archive.html" archive-light.png
  shot 1280,900 dark  "$base/archive.html" archive-dark.png
fi
if [ -f _site/profiles/index.html ]; then
  shot 1280,900 light "$base/profiles/" profiles-light.png
  shot 1280,900 dark  "$base/profiles/" profiles-dark.png
fi
profile=$(find _site/profiles -name '*.html' ! -name 'index.html' | sort | head -1)
if [ -n "$profile" ]; then
  path="${profile#_site/}"
  shot 1280,900 light "$base/$path" profile-light.png
  shot 1280,900 dark  "$base/$path" profile-dark.png
fi
