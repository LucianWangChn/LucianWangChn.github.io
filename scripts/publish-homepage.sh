#!/usr/bin/env bash
# Run on the existing Linux web server with permission to write the website.
# Usage: bash publish-homepage.sh /absolute/path/homepage-interactive.tar.gz
set -euo pipefail

target=/var/www/lucianwang.com
archive=$(realpath -- "${1:?Pass the update archive path}")
expected_index=942a536862d4880fd391d75aec1b6b18a538b18adf58f871b79253b1c947c2d0

test "$(realpath -- "$target")" = "$target" || { echo 'Unexpected website path'; exit 1; }
test -f "$target/index.html"
test -w "$target"
actual_index=$(sha256sum "$target/index.html" | cut -d ' ' -f 1)
test "$actual_index" = "$expected_index" || { echo 'Live homepage changed since review; compare it before deploying.'; exit 1; }
members=$(tar -tzf "$archive" | LC_ALL=C sort)
expected_members=$(printf '%s\n' assets/motion.css assets/motion.js index.html | LC_ALL=C sort)
test "$members" = "$expected_members" || { echo 'Unexpected archive members'; exit 1; }

stamp=$(date -u +%Y%m%dT%H%M%SZ)
backup="/var/backups/lucianwang-homepage/$stamp"
mkdir -p -- "$backup/staged"
cp -p -- "$target/index.html" "$backup/index.html"
tar -xzf "$archive" -C "$backup/staged" --no-same-owner --no-same-permissions

# Install assets before atomically replacing the entry page.
install -m 644 "$backup/staged/assets/motion.css" "$target/assets/.motion.css.next"
mv -- "$target/assets/.motion.css.next" "$target/assets/motion.css"
install -m 644 "$backup/staged/assets/motion.js" "$target/assets/.motion.js.next"
mv -- "$target/assets/.motion.js.next" "$target/assets/motion.js"
install -m 644 "$backup/staged/index.html" "$target/.index.html.next"
mv -- "$target/.index.html.next" "$target/index.html"
printf 'Updated homepage. Baseline backup: %s/index.html\n' "$backup"
printf 'Rollback: cp -p -- %q %q\n' "$backup/index.html" "$target/index.html"
