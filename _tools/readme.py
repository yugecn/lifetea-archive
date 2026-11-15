import json,os,collections,html,glob,datetime
ROOT='/workspace/work/lifetea'; RAW=ROOT+'/_raw'
b=json.load(open(ROOT+'/_build.json'))
idx=b['index']
plan=json.load(open(RAW+'/plan.json'))
all_ids=sorted(int(k) for k in plan['ids'])
got={p['id'] for p in idx}
fails=sorted(i for i in (int(os.path.basename(f)[:-10]) for f in glob.glob(RAW+'/pages/[0-9]*.html.fail')) if i not in got)
NOTPOST={548,573}  # WordPress-era ?p= ids (pre-Textpattern), not posts
pending=[i for i in all_ids if i not in got and i not in fails and i not in NOTPOST]
imgs_cdx=[l for l in open(RAW+'/main.txt') if len(l.split())>2 and l.split()[2].startswith('image') and l.split()[0]<'20140101']
img_fail=glob.glob(RAW+'/img/**/*.fail',recursive=True)
by=collections.defaultdict(list)
for p in idx: by[p['year']].append(p)
years=sorted(by)
dated=[p['date'] for p in idx if p['date']]
size=0
for d in ('posts','images'):
    for r,_,fs in os.walk(ROOT+'/'+d):
        for f in fs: size+=os.path.getsize(os.path.join(r,f))
L=[]
L.append('# Chinese Tea · lifetea.org 存档\n')
L.append('christina@Nanjing 的博客 **lifetea.org**（“Chinese Tea”，Textpattern 系统）的私人抢救存档。域名过期后被他人用于垃圾页面，本存档从 Internet Archive Wayback Machine 和 Common Crawl（2008–2019 年的抓取；原博客一直在线到约 2019 年）中恢复属于原博客的内容，之后的垃圾页面已全部排除。每篇文章的 front matter 用 `source` 注明来源（`wayback` 或 `commoncrawl` + `crawl` 抓取批次）。\n')
L.append('## 统计\n')
L.append('| 项目 | 数量 |\n|---|---|')
L.append('| 已恢复文章 | %d |'%len(idx))
L.append('| 时间跨度 | %s – %s |'%(min(dated) if dated else '-',max(dated) if dated else '-'))
L.append('| 其中来自 Common Crawl | %d |'%sum(1 for p in idx if p.get('source')=='commoncrawl'))
L.append('| 评论（随文章一并保存） | %d |'%sum(p['ncom'] for p in idx))
AI=json.load(open(RAW+'/cc_pages/archive_index.json')) if os.path.exists(RAW+'/cc_pages/archive_index.json') else {}
if AI: L.append('| 博客归档页（Pigeonhole，2012 年 Common Crawl 快照）列出的文章 | %d（其中已恢复 %d） |'%(len(AI),sum(1 for k in AI if int(k) in got)))
L.append('| Wayback 中存有快照的文章 ID | %d（原文章 ID 最大为 %d，未被存档的 ID 无法恢复） |'%(len(all_ids),max(all_ids)))
L.append('| 已下载图片 | %d / %d（Wayback 中有快照的图片） |'%(b['img_have'],len(imgs_cdx)))
L.append('| 文章引用但未能取得的图片 | %d |'%len(b['missing_img']))
L.append('| 存档体积（posts + images） | %.1f MB |'%(size/1e6))
if pending: L.append('| 尚未抓取（待续） | %d 篇 |'%len(pending))
L.append('\n更新于 %s。\n'%datetime.date.today().isoformat())
L.append('## 目录结构\n\n- `posts/YYYY/YYYY-MM-DD-a<文章ID>.md`：每篇文章一份 Markdown，带 front matter（标题、日期、分类、原始链接、来源：Wayback 链接或 Common Crawl 抓取批次），正文后附评论（只从列表页取得的文章标为 "not captured"）。\n- `images/`：原博客 `/images/` 下的图片原文件。文章里的图片已改为相对路径；未能恢复的图片保留指向 Wayback 的链接。\n- `MISSING.md`：缺失的文章与图片清单。\n- `index.html`：可直接在浏览器打开的简单目录页。\n')
L.append('## 文章索引\n')
for y in years:
    L.append('### %s（%d 篇）\n'%(y,len(by[y])))
    for p in sorted(by[y],key=lambda x:(x['date'],x['id'])):
        t=p['title'].replace('[','［').replace(']','］') or '（无题）'
        L.append('- %s [%s](%s)%s%s'%(p['date'][5:] if p['date'] else '',t,p['path'].replace(' ','%20'),' · '+p['category'] if p['category'] else '',' · %d 条评论'%p['ncom'] if p['ncom'] else ''))
    L.append('')
L.append('## 未收录的相关内容\n\n- **相册 photo.lifetea.org**（Gallery2）：Wayback 存有约 1,970 个相册页面，但只存了 9 张图片本身，照片基本无法恢复，未纳入本存档。\n- **angie.lifetea.org**：同域名下的另一位作者（Angie）的博客，非本人内容，未纳入。\n- 详细缺失清单见 [MISSING.md](MISSING.md)。\n')
open(ROOT+'/README.md','w').write('\n'.join(L))
M=['# 缺失清单\n']
M.append('## 抓取失败的文章 ID（Wayback 有记录但取不到正文）\n')
M.append(', '.join(map(str,fails)) or '无')
if pending: M.append('\n## 尚未抓取的文章 ID（抓取仍在进行）\n\n'+', '.join(map(str,pending)))
if AI:
    nowhere=sorted(int(k) for k in AI if int(k) not in got and int(k) not in plan['ids'] and str(k) not in plan['ids'])
    nowhere=[i for i in nowhere if str(i) not in plan['ids']]
    if nowhere:
        M.append('\n## 归档页列出、但没有任何存档副本的文章（%d 篇）\n'%len(nowhere))
        for i in nowhere: M.append('- a%d %s（%s）'%(i,AI[str(i)]['title'],AI[str(i)]['month']))
M.append('\n## 文章中引用但未能取得的图片\n')
for k,v in sorted(b['missing_img'].items()): M.append('- `%s` — 文章 %s'%(k,', '.join('a%d'%i for i in v)))
open(ROOT+'/MISSING.md','w').write('\n'.join(M)+'\n')
H=['<!doctype html><meta charset="utf-8"><title>Chinese Tea · lifetea.org 存档</title><style>body{font:16px/1.7 -apple-system,"PingFang SC",sans-serif;max-width:760px;margin:40px auto;padding:0 16px;color:#333}h2{border-bottom:1px solid #ddd}li{list-style:none}span{color:#999;margin-right:.6em}</style><h1>Chinese Tea · lifetea.org</h1><p>christina@Nanjing · %d 篇文章</p>'%len(idx)]
for y in years:
    H.append('<h2>%s</h2><ul>'%y)
    for p in sorted(by[y],key=lambda x:(x['date'],x['id'])):
        H.append('<li><span>%s</span><a href="%s">%s</a></li>'%(p['date'][5:],html.escape(p['path']),html.escape(p['title'] or '（无题）')))
    H.append('</ul>')
open(ROOT+'/index.html','w').write('\n'.join(H))
print('readme ok', len(idx), len(pending))
