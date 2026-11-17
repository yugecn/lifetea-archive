#!/bin/bash
set -e
cd /workspace/work/lifetea
mkdir -p images; rm -rf images/20[0-9][0-9] images/misc
[ -d _raw/img/images ] && (cd _raw/img/images && find . -type f ! -name '*.src' ! -name '*.fail' ! -name '*.fail2' ! -name '*.nf' -exec cp -p --parents {} ../../../images/ \;) || true  # rsync not installed
python3 _tools/album.py || true
python3 _tools/build.py
python3 _tools/reorg.py
python3 _tools/readme.py
