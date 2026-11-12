Fetcher: cd /workspace/work/lifetea/_raw && IV=6 nohup setsid python3 fetch2.py > fetch2.out 2>&1 < /dev/null & disown
(resumable: skips pages/*.html and img/* already fetched or .fail-marked; Wayback blocks at >~8 req/min, so keep IV>=6)
Progress: grep -c OK _raw/fetch2.log ; done when _raw/fetch2.done exists
Publish: bash _tools/push.sh  (shell credentials github)
