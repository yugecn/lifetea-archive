import re,json,os,sys,glob,urllib.parse,datetime
from bs4 import BeautifulSoup
RAW='/workspace/work/lifetea/_raw/pages'
def unq(s):
    for _ in range(3):
        n=urllib.parse.unquote(s)
        if n==s: break
        s=n
    return s
def parse(path):
    b=open(path,'rb').read().decode('utf-8','replace')
    ts,src=open(path+'.src').read().split(' ',1)
    s=BeautifulSoup(b,'lxml')
    out=[]
    for e in s.select('#content div.entry'):
        t=e.select_one('.entrytitle a')
        if not t: continue
        href=t.get('href','')
        m=re.search(r'/article/(\d+)',href) or re.search(r'/archive/(\d+)',href)
        tm=e.select_one('.entrytime'); ds=tm.get_text(strip=True).lstrip('@ ').strip() if tm else ''
        try: d=datetime.datetime.strptime(ds,'%b %d, %Y').date().isoformat()
        except Exception:
            m2=re.match(r'(\d{1,2})月\s*(\d{1,2}),\s*(\d{4})',ds)   # zh-cn locale of the 2017-2019 site: "3月 05, 2011"
            d='%s-%02d-%02d'%(m2.group(3),int(m2.group(1)),int(m2.group(2))) if m2 else ''
        body=e.select_one('.entrybody')
        cat=''
        ca=e.select_one('.entrymeta a')
        if ca:
            cat=ca.get_text(strip=True)
            if not cat:
                q=urllib.parse.urlparse(ca.get('href','')).query
                cat=unq(urllib.parse.parse_qs(q).get('c',[''])[0]) if 'c=' in q else ''
        out.append(dict(id=int(m.group(1)) if m else None,title=t.get_text(strip=True),date=d,category=cat,
             href=unq(href),body=body.decode_contents() if body else '',ts=ts,src=src.strip()))
    comments=[]
    for li in s.select('ol.comments > li'):
        c=li.find('cite'); md=li.select_one('.commentmetadata')
        a=c.find('a') if c else None
        txt=li.find('div') or li
        h=txt.decode_contents()
        h=re.sub(r'(?s)^.*?</small>','',h).strip()
        comments.append(dict(author=c.get_text(strip=True) if c else '',url=a.get('href') if a else '',
            date=md.get_text(strip=True) if md else '',html=h))
    if len(out)==1: out[0]['comments']=comments
    return out
if __name__=='__main__':
    print(json.dumps(parse(sys.argv[1]),ensure_ascii=False,indent=1)[:3000])
