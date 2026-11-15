import os,re,json,glob,sys,urllib.parse,html,shutil
sys.path.insert(0,os.path.dirname(__file__))
from parse import parse,unq
from markdownify import markdownify as md
ROOT='/workspace/work/lifetea'; RAW=ROOT+'/_raw'
posts={}
def score(p):
    # individual page > listing copy; then more comments; then Wayback over CC on ties; then newer capture
    # feed items (source wayback-feed) rank below any page copy: they may be excerpts
    return (1 if p['_ind'] else 0, len(p['comments'] or []), 0 if p['source']=='wayback-feed' else 1, 1 if p['source']=='wayback' else 0, p['ts'])
def add(p):
    if p['id'] is None:
        # single-post page whose title link is relative (e.g. a2927 "@美国"): take the id from the capture URL
        m=re.search(r'/article/(\d+)',p.get('src',''))
        if p.get('_ind') and m: p['id']=int(m.group(1)); p['href']=unq(p['src'].replace(':80/','/',1))
        else: return
    if p['id'] not in posts or score(p)>score(posts[p['id']]): posts[p['id']]=p
files=sorted(glob.glob(RAW+'/pages/*.html'))
for f in files:
    if not os.path.exists(f+'.src'): continue
    isind=not os.path.basename(f).startswith('o')
    for p in parse(f):
        p['_ind']=isind and p.get('comments') is not None
        if not isind: p['comments']=None
        p.setdefault('comments',None); p['source']='wayback'
        add(p)
# Common Crawl copies: 2008-2014 captures (_raw/cc_pages/README.md) and 2015-2019 captures of the still-running
# original site (_raw/cc_late/README.md); both are source "commoncrawl" with crawl id + capture in front matter
import warnings; warnings.filterwarnings('ignore')
for f in sorted(glob.glob(RAW+'/cc_pages/*.html'))+sorted(glob.glob(RAW+'/cc_late/*.html')):
    if not os.path.exists(f+'.src'): continue
    ts,u,crawl=open(f+'.src').read().split()
    try: r=parse(f)
    except Exception: continue
    for p in r:
        p['_ind']=len(r)==1 and '/article/' in u
        if not p['_ind']: p['comments']=None
        p.setdefault('comments',None); p['source']='commoncrawl'; p['crawl']=crawl; p['src']=u
        add(p)
# RSS/Atom feed captures fetched by _raw/fetch_posts.py (stage 3): last resort for posts no page copy has
from bs4 import BeautifulSoup
import datetime,email.utils
for f in sorted(glob.glob(RAW+'/feeds/*.xml')):
    if not os.path.exists(f+'.src'): continue
    ts,u=open(f+'.src').read().split(' ',1)
    s=BeautifulSoup(open(f,'rb').read(),'xml')
    for it in s.find_all(['item','entry']):
        ln=it.find('link'); href=(ln.get('href') or ln.get_text()) if ln else ''
        m=re.search(r'/article/(\d+)',href)
        if not m: continue
        body=it.find('content') or it.find('encoded') or it.find('description') or it.find('summary')
        d=''
        pd=it.find('pubDate') or it.find('published') or it.find('updated')
        if pd:
            t=pd.get_text(strip=True)
            try: d=email.utils.parsedate_to_datetime(t).date().isoformat()
            except Exception: d=t[:10] if re.match(r'\d{4}-\d\d-\d\d',t) else ''
        cat=it.find('category'); cat=(cat.get('term') or cat.get_text(strip=True)) if cat else ''
        add(dict(id=int(m.group(1)),title=it.find('title').get_text(strip=True) if it.find('title') else '',date=d,category=cat,
                 href=unq(href),body=body.get_text() if body else '',ts=ts,src=u.strip(),comments=None,_ind=False,source='wayback-feed'))
img_have=set()
for f in glob.glob(RAW+'/img/**/*',recursive=True):
    if os.path.isfile(f) and not f.endswith(('.src','.fail','.fail2','.nf')): img_have.add(os.path.relpath(f,RAW+'/img'))
missing_img={}
used_img=set()
def fix_img(m_src,pid):
    s=html.unescape(m_src)
    u=urllib.parse.urlparse(s)
    host=u.netloc.split(':')[0].lower()
    if host in ('','lifetea.org','www.lifetea.org') and u.path.startswith('/'):
        rel=unq(u.path).lstrip('/')
        if rel in img_have: used_img.add(rel); return '../../'+rel.replace(' ','%20')
        missing_img.setdefault(s,set()).add(pid)
        return 'https://web.archive.org/web/2010/http://lifetea.org/'+urllib.parse.quote(rel)
    missing_img.setdefault(s,set()).add(pid)
    return s
def esc(s): return s.replace('\\','\\\\').replace('"','\\"')

import html as _html
_MOJ=re.compile(r'[\u0080-\u00ff\u0152\u0153\u0160\u0161\u0178\u017d\u017e\u0192\u02c6\u02dc\u2013\u2014\u2018-\u201e\u2020-\u2022\u2026\u2030\u2039\u203a\u20ac\u2122]{2,}')
def _enc(ch):
    try: return ch.encode('cp1252')
    except UnicodeEncodeError:
        if ord(ch)<256: return bytes([ord(ch)])
        raise
def _unmoj(m):
    s=m.group(0)
    try: u=b''.join(_enc(c) for c in s).decode('utf-8')
    except Exception: return s
    return u if re.search(r'[\u3000-\u9fff\uff00-\uffef]',u) else s
def clean_text(t):
    t=re.sub(r'(?m)^[\ue5e5]+','',t)          # GBK 0xA3A0 indent read as private-use char
    t=t.replace('\ue5e5','\u3000')
    t=_MOJ.sub(_unmoj,t)                       # UTF-8 bytes shown as cp1252
    t=re.sub(r'&#(\d+);',lambda m:_html.unescape(m.group(0)),t)
    return t
out=ROOT+'/posts'
if os.path.exists(out): shutil.rmtree(out)
index=[]
for pid,p in sorted(posts.items()):
    p['title']=clean_text(p['title'])
    body=re.sub(r'(<img[^>]*?\bsrc=")([^"]+)(")',lambda m:m.group(1)+fix_img(m.group(2),pid)+m.group(3),p['body'])
    body=re.sub(r"(<img[^>]*?\bsrc=')([^']+)(')",lambda m:m.group(1)+fix_img(m.group(2),pid)+m.group(3),body)
    mdb=md(body,heading_style='ATX').strip()
    mdb=re.sub(r'\n{3,}','\n\n',mdb)
    y=p['date'][:4] if p['date'] else 'undated'
    fn='%s-a%d.md'%(p['date'] or 'undated',pid)
    if p['source'] in ('wayback','wayback-feed'):
        srcl='source: '+p['source']+'\nwayback_url: "https://web.archive.org/web/%s/%s"\n'%(p['ts'],p['src'])
    elif False:
        srcl='source: wayback\nwayback_url: "https://web.archive.org/web/%s/%s"\n'%(p['ts'],p['src'])
    else:
        srcl='source: commoncrawl\ncrawl: %s\ncapture: "%s %s"\n'%(p['crawl'],p['ts'],esc(p['src']))
    fm='---\ntitle: "%s"\ndate: %s\ncategory: "%s"\npost_id: %d\noriginal_url: "%s"\n%scomments: %s\n---\n\n'%(esc(p['title']),p['date'] or '""',esc(p['category']),pid,esc(p['href']),srcl,len(p.get('comments') or []) if p.get('comments') is not None else '"not captured"')
    txt=fm+'# '+p['title']+'\n\n'+mdb+'\n'
    if p['comments']:
        txt+='\n---\n\n## 评论（%d）\n\n'%len(p['comments'])
        for c in p['comments']:
            a=c['author'] if not c['url'] else '[%s](%s)'%(c['author'],c['url'])
            txt+='**%s** · %s\n\n%s\n\n'%(a,c['date'],md(c['html']).strip())
    os.makedirs(out+'/'+y,exist_ok=True)
    txt=clean_text(txt)
    open(out+'/'+y+'/'+fn,'w').write(txt)
    index.append(dict(id=pid,title=p['title'],date=p['date'],year=y,category=p['category'],path='posts/%s/%s'%(y,fn),source=p['source'],ncom=len(p['comments'] or [])))
json.dump(dict(index=index,missing_img={k:sorted(v) for k,v in missing_img.items()},used_img=sorted(used_img),img_have=len(img_have)),open(ROOT+'/_build.json','w'),ensure_ascii=False,indent=0)
print('posts',len(index),'img_have',len(img_have),'used',len(used_img),'missing refs',len(missing_img))
