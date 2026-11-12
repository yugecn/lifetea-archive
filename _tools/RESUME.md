Fetcher: cd /workspace/work/lifetea/_raw && IV=6 nohup setsid python3 fetch2.py > fetch2.out 2>&1 < /dev/null & disown
(resumable: skips pages/*.html and img/* already fetched or .fail-marked; Wayback blocks at >~8 req/min, so keep IV>=6)
Progress: grep -c OK _raw/fetch2.log ; done when _raw/fetch2.done exists
Publish: bash _tools/push.sh  (shell credentials github)

Album (photo.lifetea.org) recovery:
- _tools/album.py builds images/album/ (+manifest.csv, inventory.csv); sync.sh runs it, so push.sh picks up new matches.
- Slow fetcher for tecinese.com (older blog domain) images: cd _raw/album && IV=180 IV2=9 nohup setsid python3 slow_fetch.py > slow_fetch.out 2>&1 < /dev/null &
  (album-matched files first at 1 req/180s; the remaining ~457 waits for _raw/fetch2.done, then IV2). Log: _raw/album/slow_fetch.log; done marker slow_fetch.done. Output: _raw/tecinese/
- Wayback CDX evidence in _raw/album/cdx_*.txt; Common Crawl/archive.today checked (no images).

Album pass 2 (2026-11-13):
- Common Crawl: index.commoncrawl.org is flaky (504/false 404) and HTTPS to it fails through the proxy; use _raw/album/cc/ccidx.py, which binary-searches each crawl's cluster.idx on data.commoncrawl.org via HTTP ranges (all 129 crawls done -> cc/idx_*.txt, merged cc/all.txt). Result: zero image records for *.lifetea.org / *.tecinese.com; 1,427 HTML records 2008–2012 fetched into cc/warc/ (ccget.py), parsed to cc/cc_items.json (item path, CC page, thumb /d/ URL + dims, resized /d/ URL + dims). album.py reads it: extends inventory and rejects filename matches whose aspect ratio differs >8% from the album thumbnail.
- Blog copies matching album names: _raw/album/blog_album_fetch.py (JOBS=blog_album_jobs.json, then JOBS=blog_album_jobs2.json; IV=12; log blog_album_fetch.log). Writes into _raw/img like fetch2.py, so fetch2 skips them later.
- Dead ends: Memento TimeTravel (proxy 403), MemGator (404), LoC (Cloudflare), Archive-It (403), arquivo.pt (no lifetea; tecinese only 2018+ spam), UKWA/NLA (not applicable); Wayback lifetea.org/gallery*, www.lifetea.org/gallery*, photo.lifetea.org/main.php non-HTML: nothing; no hotlinks found by web search.
- fetch2.py was NOT running at 2026-11-12 23:29 UTC (log ends with BLOCK 000); restart per the line above when Wayback traffic allows.
