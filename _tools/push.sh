#!/bin/bash
# Rebuild from _raw and push progress. Run with GitHub credentials.
cd /workspace/work/lifetea && ./_tools/sync.sh && git add -A && git -c user.name=yugecn -c user.email=9625098+yugecn@users.noreply.github.com commit -qm "Archive update $(date -u +%F\ %H:%M)" ; git -c http.sslCAInfo="$SSL_CERT_FILE" push -q origin main
