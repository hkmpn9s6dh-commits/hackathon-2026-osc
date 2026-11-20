#!/bin/sh
# Reproduce every number in the OSC audit. Pure Python 3.8+, no network, no deps.
set -e
cd "$(dirname "$0")/.."
py -3 scripts/build.py
py -3 verify/verify.py
