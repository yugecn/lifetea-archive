import os,re,json,glob,sys,urllib.parse,html,shutil
sys.path.insert(0,os.path.dirname(__file__))
from parse import parse,unq
from markdownify import markdownify as md
ROOT='/workspace/work/lifetea'; RAW=ROOT+'/_raw'
posts={}
files=sorted(glob.glob(RAW+'/pages/*.html'))
for f in files:
    if not os.path.exists(f+'.src'): continue
    isind=not os.path.basename(f).startswith('o')
    for p in parse(f):
        if p['id'] is None: continue
        if p['id'] in posts and (posts[p['id']].get('_ind') and not isind): continue
        if p['id'] in posts and not isind: continue
        p['_ind']=isind
        if not isind: p['comments']=None
        p.setdefault('comments',None)
        posts[p['id']]=p
img_have=set()
for f in glob.glob(RAW+'/img/**/*',recursive=True):
    if os.path.isfile(f) and not f.endswith(('.src','.fail')): img_have.add(os.path.relpath(f,RAW+'/img'))
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
out=ROOT+'/posts'
if os.path.exists(out): shutil.rmtree(out)
index=[]
for pid,p in sorted(posts.items()):
    body=re.sub(r'(<img[^>]*?\bsrc=")([^"]+)(")',lambda m:m.group(1)+fix_img(m.group(2),pid)+m.group(3),p['body'])
    body=re.sub(r"(<img[^>]*?\bsrc=')([^']+)(')",lambda m:m.group(1)+fix_img(m.group(2),pid)+m.group(3),body)
    mdb=md(body,heading_style='ATX').strip()
    mdb=re.sub(r'\n{3,}','\n\n',mdb)
    y=p['date'][:4] if p['date'] else 'undated'
    fn='%s-a%d.md'%(p['date'] or 'undated',pid)
    wb='https://web.archive.org/web/%s/%s'%(p['ts'],p['src'])
    fm='---\ntitle: "%s"\ndate: %s\ncategory: "%s"\npost_id: %d\noriginal_url: "%s"\nwayback_url: "%s"\ncomments: %s\n---\n\n'%(esc(p['title']),p['date'] or '""',esc(p['category']),pid,esc(p['href']),wb,len(p.get('comments') or []) if p.get('comments') is not None else '"not captured"')
    txt=fm+'# '+p['title']+'\n\n'+mdb+'\n'
    if p['comments']:
        txt+='\n---\n\n## 评论（%d）\n\n'%len(p['comments'])
        for c in p['comments']:
            a=c['author'] if not c['url'] else '[%s](%s)'%(c['author'],c['url'])
            txt+='**%s** · %s\n\n%s\n\n'%(a,c['date'],md(c['html']).strip())
    os.makedirs(out+'/'+y,exist_ok=True)
    open(out+'/'+y+'/'+fn,'w').write(txt)
    index.append(dict(id=pid,title=p['title'],date=p['date'],year=y,category=p['category'],path='posts/%s/%s'%(y,fn),ncom=len(p['comments'] or [])))
json.dump(dict(index=index,missing_img={k:sorted(v) for k,v in missing_img.items()},used_img=sorted(used_img),img_have=len(img_have)),open(ROOT+'/_build.json','w'),ensure_ascii=False,indent=0)
print('posts',len(index),'img_have',len(img_have),'used',len(used_img),'missing refs',len(missing_img))
