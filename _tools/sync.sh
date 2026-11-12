#!/bin/bash
set -e
cd /workspace/work/lifetea
mkdir -p images
[ -d _raw/img/images ] && rsync -a --exclude '*.src' --exclude '*.fail' _raw/img/images/ images/ || true
python3 _tools/album.py || true
python3 _tools/build.py
python3 _tools/readme.py
