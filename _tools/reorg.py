import os,re,glob,shutil,urllib.parse
R='/workspace/work/lifetea'; os.chdir(R)
pat=re.compile(r'\.\./\.\./images/([^)\s"\']+)')
first={}
for f in sorted(glob.glob('posts/*/*.md')):
    y=f.split('/')[1]; d=os.path.basename(f)[:10]
    for m in pat.finditer(open(f).read()):
        rel=urllib.parse.unquote(m.group(1))
        if rel.startswith('album/'): continue
        if rel not in first or (d,y)<first[rel]: first[rel]=(d,y)
from collections import Counter
cnt=Counter(v[1] for v in first.values())
def folder(rel):
    if rel not in first: return 'misc'
    d,y=first[rel]
    return y+'/'+d[5:7] if cnt[y]>900 and re.match(r'\d{4}-\d\d',d) else y
moved=0
for dp,dn,fn in os.walk('images'):
    parts=dp.split('/')
    if len(parts)>1 and (parts[1]=='album' or re.fullmatch(r'\d{4}|misc',parts[1]) and False): continue
    for n in fn:
        p=os.path.join(dp,n); rel=os.path.relpath(p,'images')
        if rel.startswith('album/'): continue
        t=os.path.join('images',folder(rel),rel); os.makedirs(os.path.dirname(t),exist_ok=True)
        shutil.move(p,t); moved+=1
for dp,dn,fn in os.walk('images',topdown=False):
    if dp!='images' and not os.listdir(dp): os.rmdir(dp)
def rw(m):
    rel=urllib.parse.unquote(m.group(1))
    if rel not in first: return m.group(0)
    return '../../images/'+urllib.parse.quote(folder(rel)+'/'+rel,safe='/')
n=0
for f in glob.glob('posts/*/*.md'):
    s=open(f).read(); s2=pat.sub(rw,s)
    if s2!=s: open(f,'w').write(s2); n+=1
print('moved',moved,'posts rewritten',n)
