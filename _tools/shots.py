import re,os,shutil,base64
RAW='/workspace/work/lifetea/_raw/theme'; OUT='/workspace/work/lifetea/themes'; IMG='/workspace/work/lifetea/images'
from playwright.sync_api import sync_playwright
cfg=[('ctea-lifetea-2007','home-2007.html'),('ctea-lifetea-2010','home-2010.html'),('ctea-lifetea-2011','home-2012.html')]
def fix(html,theme):
    d=f'{OUT}/{theme}'
    css=open(f'{d}/styles/default.css').read()
    def cssimg(m):
        n=m.group(1); p=f'{d}/images/{n}'
        return f"url('file://{p}')" if os.path.exists(p) else "url('')"
    css=re.sub(r"url\('?/images/([^')]+)'?\)",cssimg,css)
    css=re.sub(r"url\((titlebar[^)]*)\)",lambda m:f"url('file://{d}/images/{m.group(1)}')",css)
    if theme.endswith('2007'):
        html=html.replace('<div id="head">\n&nbsp;','<div id="head" style="display:flex;align-items:center;justify-content:center;background:#e9e2e7;color:#9c5e8b;font:16px sans-serif">2007 版原头图（images/905.jpg）未被 Wayback 存档',1)
    html=re.sub(r'<link[^>]+css\.php[^>]*>',lambda m: '<style>'+css+'</style>',html)
    if theme.endswith('2011'):
        html=re.sub(r"src='js/(\w[\w-]*)\.js[^']*'",lambda m:f"src='file://{d}/js/{m.group(1)}.js'",html)
        html=re.sub(r'<script type="text/javascript">var pkBase.*?</noscript>','',html,flags=re.S)
    else:
        html=re.sub(r'<script[^>]+src=[^>]*></script>','',html)
    html=re.sub(r'<embed[^>]*>','',html,flags=re.S)
    def img(m):
        n=re.search(r'(\d+)\.(jpg|gif|png)',m.group(1))
        if n:
            for e in ['jpg','gif','png']:
                p=f'{IMG}/{n.group(1)}.{e}'
                if os.path.exists(p): return f'src="file://{p}"'
        return 'src="data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22500%22 height=%22300%22%3E%3Crect width=%22100%25%22 height=%22100%25%22 fill=%22%23eeeeee%22/%3E%3Ctext x=%2250%25%22 y=%2250%25%22 font-size=%2218%22 fill=%22%23999999%22 text-anchor=%22middle%22 font-family=%22sans-serif%22%3E%E5%8E%9F%E5%9B%BE%E6%9C%AA%E5%AD%98%E6%A1%A3%3C/text%3E%3C/svg%3E" style="object-fit:cover"'
    html=re.sub(r'src="?([^"\s>]*images/[^"\s>]*)"?',img,html)
    return html
os.makedirs(f'{OUT}/_preview',exist_ok=True)
with sync_playwright() as p:
    b=p.chromium.launch()
    for theme,home in cfg:
        h=fix(open(f'{RAW}/{home}',errors='ignore').read(),theme)
        f=f'{OUT}/_preview/{theme}.html'; open(f,'w').write(h)
        pg=b.new_page(viewport={'width':1100,'height':1400})
        pg.goto('file://'+f); pg.wait_for_timeout(800)
        pg.screenshot(path=f'{OUT}/{theme}/screenshot.png',clip={'x':0,'y':0,'width':1100,'height':1300})
        shutil.copy(f'{OUT}/{theme}/screenshot.png',f'{OUT}/_preview/{theme}.png')
    b.close()
print('done')
