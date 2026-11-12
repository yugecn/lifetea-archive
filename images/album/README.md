# 相册 photo.lifetea.org 抢救说明

原相册是 Gallery2（2005–2011，约 117 个子相册；已知照片清单由 Wayback 的 1544 张 + Common Crawl 2008–2010 抓取的相册网页补充的约 560 张组成）。Wayback Machine 存了约 1,970 个相册**网页**，但几乎没有存图片文件本身：
对 `photo.lifetea.org/d/` 和 `main.php?g2_view=core.DownloadItem` 的全部抓取记录（所有年份、所有状态码）中，只有 9 个真正的图片文件（6 张相册封面缩略图、2 张缩略图、1 张 464×600 展示图）；2022 年的 47 条 /d/ 记录都是域名过期后的 301 跳转。

- `manifest.csv`：每个已恢复文件的来源（存档网址、大小、像素、匹配方式）。
- `inventory.csv`：所有已知相册照片（来自存档的照片页地址）及其状态（recovered / missing）。
- `version` 列：thumb（≤200 像素的缩略图）/ resized（展示图或博客尺寸副本）/ original（原图，目前没有任何一张存世）。
- Common Crawl（全部 129 个索引，2008–2026）只存了相册和博客的网页，没有任何图片文件；它补充的照片名单用于下面的文件名匹配，并给出每张照片缩略图的长宽比。
- “filename match”= 同名照片在博客文章（lifetea.org/images/ 或更早的 tecinese.com）里用过的版本，通常是博客尺寸，不是原图；按文件名匹配；凡是 Common Crawl 里有该照片缩略图尺寸的，都核对了长宽比（误差 <8%），不符的（例如不同相机的同名 DSC 文件）已排除。“no album thumbnail to cross-check” 的几张只靠文件名，极少数可能不是同一张。

此目录由 `_tools/album.py` 自动生成，后台抓取完成后重新运行 `_tools/push.sh` 会补上更多照片。
