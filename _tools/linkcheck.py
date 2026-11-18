#!/usr/bin/env python3
"""Check every local href/src in the generated html (and css url()) resolves to a file."""
import os,re,glob,collections,urllib.parse
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
files=['index.html']+[os.path.relpath(f,ROOT) for d in ('p','page','archive','category') for f in glob.glob(ROOT+'/'+d+'/*.html')]
bad=collections.Counter(); kinds=collections.Counter(); ext=collections.Counter(); n=0
for f in files:
    h=open(os.path.join(ROOT,f),encoding='utf-8').read()
    for attr,u in re.findall(r'\b(href|src)="([^"]*)"',h):
        if u.startswith(('http://','https://','mailto:','javascript:','mms:','//','data:')):
            ext['wayback' if 'web.archive.org' in u else 'external']+=1; continue
        u=urllib.parse.unquote(u.split('#')[0].split('?')[0])
        if not u: continue
        n+=1
        t=os.path.normpath(os.path.join(ROOT,os.path.dirname(f),u))
        k='image' if '/images/' in t else os.path.splitext(t)[1]
        kinds[k]+=1
        if not t.startswith(ROOT) or not os.path.isfile(t): bad[(k,os.path.relpath(t,ROOT))]+=1
css=open(ROOT+'/assets/css/default.css').read()
for u in re.findall(r"url\('([^']+)'\)",css):
    n+=1
    if not os.path.isfile(os.path.normpath(os.path.join(ROOT,'assets/css',u))): bad[('css',u)]+=1
print('pages',len(files),'local links',n,dict(kinds),'external',dict(ext))
print('broken unique',len(bad),'broken total',sum(bad.values()))
for (k,t),c in bad.most_common(40): print(c,k,t)
