#!/bin/sh
# Reproduce every number in the OSC audit. Pure Python 3.8+, no network, no deps.
# Works with python3 (Linux/macOS), python, or the Windows launcher py.
set -e
cd "$(dirname "$0")/.."
if command -v python3 >/dev/null 2>&1; then PY=python3
elif command -v python >/dev/null 2>&1; then PY=python
else PY="py -3"; fi
$PY scripts/build.py
$PY scripts/make_submission.py
$PY verify/verify.py
