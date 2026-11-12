#!/usr/bin/env python3
"""Assemble recovered photo.lifetea.org (Gallery2) album photos into images/album/.
Sources (best available per photo, largest file wins):
  1. Wayback captures of photo.lifetea.org/d/<id>-<serial>/<file> (_raw/album/wb_d)
  2. Blog copies of the same file on lifetea.org/images/ (_raw/img/images, from fetch2.py)  [matched by filename]
  3. Copies on tecinese.com, the earlier blog domain (_raw/tecinese, from slow_fetch.py)    [matched by filename]
Writes images/album/<album path>/<file>, images/album/manifest.csv, images/album/inventory.csv."""
import os,re,glob,csv,shutil,urllib.parse
from PIL import Image
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW=ROOT+'/_raw'; OUT=ROOT+'/images/album'
def norm_path(u):
    p=u.split('/v/',1)[1].split('?')[0]
    return urllib.parse.unquote(p).replace('+',' ')
items={}   # lower path -> (path, first_ts, page_url)
albums=set()
for fn in [RAW+'/cdx_domain.txt',RAW+'/album/cdx_photo_non200.txt']:
    if not os.path.exists(fn): continue
    for l in open(fn):
        f=l.split()
        if len(f)<3 or 'photo.lifetea.org' not in f[1] or '/v/' not in f[1]: continue
        p=norm_path(f[1])
        if p.lower().endswith('.html'):
            p=p[:-5]
            k=p.lower()
            if k not in items or f[0]<items[k][1]: items[k]=(p,f[0],f[1])
        elif p.endswith('/'): albums.add(p.rstrip('/'))
# file sources
def scan(d):
    r={}
    for f in glob.glob(d+'/**/*',recursive=True):
        if os.path.isfile(f) and not f.endswith(('.src','.fail')):
            r.setdefault(os.path.basename(f).lower(),[]).append(f)
    return r
blog=scan(RAW+'/img'); tec=scan(RAW+'/tecinese')
def src_of(f):
    s=f+'.src'
    if os.path.exists(s):
        ts,u=open(s).read().split(' ',1); return 'https://web.archive.org/web/%sid_/%s'%(ts,u.strip())
    return ''
def dims(f):
    try: return '%dx%d'%Image.open(f).size
    except Exception: return ''
rows=[]; inv=[]
os.makedirs(OUT,exist_ok=True)
# 1. Wayback /d/ captures
cover_alb={'NIUNIU2004':'pets/NIUNIU2004','0501':'live/0501','2niu+niu':'pets/2niu niu','060708':'live/060708','070115PS':'live/070115PS','060801':'live/060801'}
direct={}
for f in sorted(glob.glob(RAW+'/album/wb_d/*')):
    if f.endswith('.src'): continue
    name=os.path.basename(f); iid,fn=name.split('__',1)
    stem=fn.rsplit('.',1)[0]
    if stem in cover_alb:
        dest='%s/_album-cover.jpg'%cover_alb[stem]; kind='album cover thumbnail'; title=cover_alb[stem]
    else:
        k=[k for k in items if k.endswith('/'+fn.lower())]
        p=items[k[0]][0] if k else 'unsorted/'+fn
        dest=p; kind='full-size (resized 464x600 display copy)' if iid.endswith('-1') else 'thumbnail'; title=p
        direct[p.lower()]=(f,kind)
    os.makedirs(os.path.dirname(OUT+'/'+dest),exist_ok=True); shutil.copy2(f,OUT+'/'+dest)
    rows.append([dest,title,kind,'Wayback Machine','http://photo.lifetea.org/d/%s/%s'%(iid,fn),os.path.getsize(f),dims(f),'exact (Gallery2 item %s)'%iid])
# 2/3. filename matches
for k,(p,ts,page) in sorted(items.items()):
    fn=os.path.basename(p).lower()
    cands=[(os.path.getsize(f),f,'lifetea.org blog copy (Wayback)') for f in blog.get(fn,[])]+[(os.path.getsize(f),f,'tecinese.com copy (Wayback)') for f in tec.get(fn,[])]
    best=None
    if k in direct: best=(os.path.getsize(direct[k][0]),direct[k][0],'Wayback /d/')
    for c in cands:
        if best is None or c[0]>best[0]: best=c
    status='missing'
    if best:
        status='recovered: '+best[2]
        if best[1] not in [d[0] for d in direct.values()]:
            os.makedirs(os.path.dirname(OUT+'/'+p),exist_ok=True); shutil.copy2(best[1],OUT+'/'+p)
            rows=[r for r in rows if r[0]!=p]
            rows.append([p,p,'blog-size copy (matched by filename)',best[2],src_of(best[1]),best[0],dims(best[1]),'filename match'])
    inv.append([p,'https://web.archive.org/web/%s/%s'%(ts,page),status])
with open(OUT+'/manifest.csv','w',newline='') as fh:
    w=csv.writer(fh); w.writerow(['file','album/title','kind','archive','source_url','bytes','pixels','match']); w.writerows(sorted(rows))
with open(OUT+'/inventory.csv','w',newline='') as fh:
    w=csv.writer(fh); w.writerow(['album_photo','archived_item_page','status']); w.writerows(inv)
rec=sum(1 for r in inv if r[2]!='missing')
print('album items known',len(inv),'albums',len(albums),'recovered',rec,'files in manifest',len(rows))
