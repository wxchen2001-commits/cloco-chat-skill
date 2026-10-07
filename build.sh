#!/usr/bin/env bash
# Rebuild cloco/ and dist/cloco.zip from the latest upstream jfimbett/cloco.
# Requires: git, python3 with PyYAML, zip.
set -euo pipefail
cd "$(dirname "$0")"
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
git clone -q --depth=1 https://github.com/jfimbett/cloco.git "$tmp/cloco-src"
python3 tools/build.py "$tmp/cloco-src" "$tmp/out"
rm -rf cloco && mv "$tmp/out/cloco" cloco
mkdir -p dist && rm -f dist/cloco.zip
zip -qrX dist/cloco.zip cloco -x '*/__pycache__/*'
echo "wrote dist/cloco.zip — upload it at claude.ai/customize/skills"
