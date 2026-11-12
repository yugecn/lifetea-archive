# 相册 photo.lifetea.org 抢救说明

原相册是 Gallery2（2005–2011，约 117 个子相册、1544 张已知照片）。Wayback Machine 存了约 1,970 个相册**网页**，但几乎没有存图片文件本身：
对 `photo.lifetea.org/d/` 和 `main.php?g2_view=core.DownloadItem` 的全部抓取记录（所有年份、所有状态码）中，只有 9 个真正的图片文件（6 张相册封面缩略图、2 张缩略图、1 张 464×600 展示图）；2022 年的 47 条 /d/ 记录都是域名过期后的 301 跳转。

- `manifest.csv`：每个已恢复文件的来源（存档网址、大小、像素、匹配方式）。
- `inventory.csv`：所有已知相册照片（来自存档的照片页地址）及其状态（recovered / missing）。
- “filename match”= 同名照片在博客文章（lifetea.org/images/ 或更早的 tecinese.com）里用过的版本，通常是博客尺寸，不是原图；按文件名匹配，极少数可能不是同一张。

此目录由 `_tools/album.py` 自动生成，后台抓取完成后重新运行 `_tools/push.sh` 会补上更多照片。
