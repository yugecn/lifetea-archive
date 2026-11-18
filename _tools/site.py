#!/usr/bin/env python3
"""Static site generator for the lifetea archive.

Renders posts/*.md into a browsable static site using the last original theme
(themes/ctea-lifetea-2011, default.css = 2012-06, header 5515.jpg).
Output (repo root, all links relative so it works under a sub-path):
  index.html, page/N.html          home, 10 posts per page, newest first
  p/<post_id>.html                 one page per post (body + comments + prev/next)
  archive/index.html               full listing by year
  archive/YYYY.html, YYYY-MM.html  year / month listings
  category/<n>.html                category listings
  assets/                          theme css/js/fonts/header image
  .nojekyll
Images are referenced from the existing images/ folder (not copied).
Usage: python3 _tools/site.py
"""
import os, re, glob, html, shutil, json, collections
import markdown

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THEME = os.path.join(ROOT, 'themes', 'ctea-lifetea-2011')
PER_PAGE = 10
SITE_TITLE = 'Chinese Tea'
E = html.escape

# ---------------------------------------------------------------- parse posts
COM_RE = re.compile(r'^\*\*(.*?)\*\* · (\d{4}-\d{2}-\d{2})\s*$')

def fm_val(v):
    v = v.strip()
    if v.startswith('"') and v.endswith('"'):
        try: return json.loads(v)
        except Exception: return v[1:-1]
    return v

def load(path):
    txt = open(path, encoding='utf-8').read()
    m = re.match(r'---\n(.*?)\n---\n', txt, re.S)
    meta = {}
    for line in m.group(1).split('\n'):
        if ':' in line:
            k, v = line.split(':', 1); meta[k.strip()] = fm_val(v)
    rest = txt[m.end():]
    body, comments_md = rest, ''
    cm = re.search(r'\n---\n+## 评论（\d+）\n', rest)
    if cm:
        body, comments_md = rest[:cm.start()], rest[cm.end():]
    body = re.sub(r'^\s*# .*\n', '', body, count=1)  # drop the H1 title (shown in entrytitle)
    comments = []
    cur = None
    for line in comments_md.split('\n'):
        mm = COM_RE.match(line)
        if mm:
            cur = {'name': mm.group(1), 'date': mm.group(2), 'lines': []}; comments.append(cur)
        elif cur is not None:
            cur['lines'].append(line)
    for c in comments:
        c['text'] = '\n'.join(c.pop('lines')).strip()
    meta['post_id'] = int(meta['post_id'])
    meta['body_md'] = body.strip()
    meta['comments_list'] = comments
    meta['category'] = meta.get('category') or ''
    return meta

posts = [load(f) for f in sorted(glob.glob(os.path.join(ROOT, 'posts', '*', '*.md')))]
posts.sort(key=lambda p: (p['date'], p['post_id']))  # oldest first
ids = {p['post_id'] for p in posts}

MD = markdown.Markdown(extensions=['sane_lists'], output_format='html')

def md(s):
    MD.reset(); return MD.convert(s)

def md_inline(s):
    h = md(s)
    return re.sub(r'^<p>(.*)</p>$', r'\1', h, flags=re.S)

def fix_links(h):
    # images: posts/YYYY/x.md used ../../images/ ; generated pages sit one level deep
    h = h.replace('"../../images/', '"{{PRE}}images/')
    h = h.replace('href="www.', 'href="http://www.')  # scheme-less links in a few old posts
    # links to other posts on the old site -> local page if we have it
    def repl(m):
        pid = int(m.group(2))
        return m.group(1) + ('{{PRE}}p/%d.html' % pid if pid in ids else m.group(0)[len(m.group(1)):])
    h = re.sub(r'(href=")https?://(?:www\.)?lifetea\.org(?::80)?/article/(\d+)[^"]*', repl, h)
    return h

for p in posts:
    p['body_html'] = fix_links(md(p['body_md']))

# ---------------------------------------------------------------- indexes
cats = collections.Counter(p['category'] or '未分类' for p in posts)
cat_names = [c for c, _ in cats.most_common()]
cat_file = {c: 'category/%d.html' % (i + 1) for i, c in enumerate(cat_names)}
years = sorted({p['date'][:4] for p in posts})
months = sorted({p['date'][:7] for p in posts})
newest = list(reversed(posts))
recent_comments = []
for p in newest:
    for c in reversed(p['comments_list']):
        recent_comments.append((c, p))
recent_comments.sort(key=lambda cp: cp[0]['date'], reverse=True)
recent_comments = recent_comments[:15]

# ---------------------------------------------------------------- templates
def rel(pre, target):
    return pre + target

def sidebar(pre):
    o = ['<div id="menu">',
         '<a href="%sindex.html"><h3 class="menuheader">Homepage</h3></a>' % pre,
         '<h3 class="menuheader expandable">About</h3>',
         '<div class="categoryitems">christina@Nanjing,China <br />lifetea.org 存档（2002–2013）</div>',
         '<a href="%sarchive/index.html"><h3 class="menuheader">Archives</h3></a>' % pre,
         '<h3 class="menuheader expandable">Article</h3>',
         '<div class="categoryitems"><ol class="recent_articles">']
    for p in newest[:15]:
        o.append('<li><a href="%sp/%d.html">%s</a></li>' % (pre, p['post_id'], E(p['title'])))
    o += ['</ol></div>', '<h3 class="menuheader expandable">Comments</h3>',
          '<div class="categoryitems"><ol class="recent_comments">']
    for c, p in recent_comments:
        name = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', c['name'])
        o.append('<li><a href="%sp/%d.html#comment">%s (%s)</a></li>' % (pre, p['post_id'], E(p['title']), E(name)))
    o += ['</ol></div>', '<h3 class="menuheader expandable">Category</h3>',
          '<div class="categoryitems"><ol class="category_list">']
    for c in cat_names:
        o.append('<li><a href="%s%s">%s (%d)</a></li>' % (pre, cat_file[c], E(c), cats[c]))
    o += ['</ol></div>', '<h3 class="menuheader expandable">Archive</h3>',
          '<div class="categoryitems"><ol class="archive_years">']
    for y in reversed(years):
        n = sum(1 for p in posts if p['date'][:4] == y)
        o.append('<li><a href="%sarchive/%s.html">%s (%d)</a></li>' % (pre, y, y, n))
    o += ['</ol></div>', '</div>']
    return '\n'.join(o)

def page(pre, title, content, footer_extra=''):
    a = pre + 'assets/'
    return f'''<!doctype html>
<html class="no-js">
<head>
<meta http-equiv="content-type" content="text/html; charset=utf-8" />
<meta name="viewport" content="width=760" />
<title>{E(title)}</title>
<link rel="stylesheet" type="text/css" media="screen" href="{a}css/default.css" />
<script type="text/javascript" src="{a}js/modernizr.js"></script>
<script type="text/javascript" src="{a}js/jquery.js"></script>
<script type="text/javascript" src="{a}js/jquery-ui.js"></script>
<script type="text/javascript" src="{a}js/ddaccordion.js"></script>
<script type="text/javascript">
ddaccordion.init({{
    headerclass: "expandable", contentclass: "categoryitems", revealtype: "click",
    mouseoverdelay: 200, collapseprev: true, defaultexpanded: [0], onemustopen: false,
    animatedefault: false, persiststate: true, toggleclass: ["", "openheader"],
    togglehtml: ["prefix", "", ""], animatespeed: "fast",
    oninit: function(headers, expandedindices){{ }},
    onopenclose: function(header, index, state, isuseractivated){{ }}
}})
</script>
</head>
<body>
<div id="container">
<div id="header">&nbsp;</div>
<div id="wrapper">
{sidebar(pre)}
<div id="content">
{content}
</div>
</div>
</div>
<footer>本站为 lifetea.org（Chinese Tea, christina@Nanjing）的静态存档，原站已关闭，评论区只读。{footer_extra}<br />
Best not view with IE 9-. Apple Safari, Google Chrome &amp; Mozilla Firefox recommended.</footer>
</body>
</html>
'''

def fmt_date(d):
    import datetime
    return datetime.date.fromisoformat(d).strftime('%b %d, %Y')

def cat_link(pre, p):
    c = p['category'] or '未分类'
    return '<a href="%s%s" title="%s">%s</a>' % (pre, cat_file[c], E(c), E(c))

def entry(pre, p, individual):
    pid = p['post_id']
    o = ['<div class="entry">',
         '<div class="entrytitle">',
         '<a href="%sp/%d.html" rel="bookmark">%s</a> <span class="entrytime"> @ %s</span>' % (pre, pid, E(p['title']), fmt_date(p['date'])),
         '</div>',
         '<div class="entrybody">', p['body_html'].replace('{{PRE}}', pre), '</div>',
         '<div class="entrymeta">', 'Posted in ' + cat_link(pre, p)]
    if not individual:
        n = len(p['comments_list'])
        o.append(' | <a href="%sp/%d.html#comment" class="comments_invite">Comments [%d]</a>' % (pre, pid, n))
    o += ['</div>', '</div>']
    if individual:
        o.append('<div class="commentsblock">')
        cl = p['comments_list']
        if cl:
            o.append('<h3 id="comment">%d Responses to &#8220;%s&#8221;</h3>' % (len(cl), E(p['title'])))
            o.append('<ol class="comments">')
            for i, c in enumerate(cl, 1):
                author = 'Christina' in c['name']
                o.append('<li id="c%d"><div class="%s">' % (i, 'authorcomment' if author else ''))
                o.append('<cite>%s</cite> Says:<br />' % (md_inline(c['name']) if c['name'] else '(匿名)'))
                o.append('<small class="commentmetadata"><a href="#c%d"> %s</a></small>' % (i, c['date']))
                o.append(fix_links(md(c['text'])).replace('{{PRE}}', pre) if c['text'] else '')
                o.append('</div></li>')
            o.append('</ol>')
        else:
            o.append('<h3 id="comment">No Responses to &#8220;%s&#8221;</h3>' % E(p['title']))
        o.append('''<h3 id="respond">Leave A Reply</h3>
<p><em>存档只读，评论已关闭。</em></p>
<form action="#" onsubmit="return false;">
<p><input type="text" id="name" size="25" disabled="disabled" /> <label for="name">Name (required)</label></p>
<p><input type="text" id="email" size="25" disabled="disabled" /> <label for="email">Email (will not be published) (required)</label></p>
<p><input type="text" id="web" size="25" disabled="disabled" /> <label for="web">Website</label></p>
<p><textarea id="message" cols="25" rows="5" disabled="disabled"></textarea></p>
<p><input type="submit" value="Submit" disabled="disabled" /></p>
</form>''')
        o.append('</div>')
    return '\n'.join(o)

def listing(pre, plist):
    o = ['<ol class="archive_list">']
    for p in plist:
        o.append('<li><a href="%sp/%d.html">%s</a> <span class="entrytime">%s</span></li>' % (pre, p['post_id'], E(p['title']), p['date']))
    o.append('</ol>')
    return '\n'.join(o)

def listing_page(pre, heading, inner):
    return '<div class="entry">\n<div class="entrytitle">%s</div>\n<div class="entrybody">\n%s\n</div>\n</div>' % (heading, inner)

# ---------------------------------------------------------------- write
written = []
def write(relpath, text):
    full = os.path.join(ROOT, relpath)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w', encoding='utf-8') as f: f.write(text)
    written.append(relpath)

# clean previous output
for d in ('p', 'page', 'archive', 'category', 'assets'):
    shutil.rmtree(os.path.join(ROOT, d), ignore_errors=True)

# assets: theme css (urls made relative, missing files dropped), js, fonts, header image
os.makedirs(os.path.join(ROOT, 'assets', 'css'))
shutil.copytree(os.path.join(THEME, 'js'), os.path.join(ROOT, 'assets', 'js'))
shutil.copytree(os.path.join(THEME, 'font'), os.path.join(ROOT, 'assets', 'font'))
os.makedirs(os.path.join(ROOT, 'assets', 'images'))
shutil.copy(os.path.join(THEME, 'images', '5515.jpg'), os.path.join(ROOT, 'assets', 'images', '5515.jpg'))
css = open(os.path.join(THEME, 'styles', 'default.css'), encoding='utf-8').read()
css = css.replace("url('/images/5515.jpg')", "url('../images/5515.jpg')")
css = css.replace(" url('/images/.jpg') repeat", "")          # empty image name in the original
css = css.replace(" url(titlebar.png) repeat-x center left", "")  # 404 on the original site too
css = css.replace("background-image: url(titlebar-active.png);", "")
def fontsrc(m):
    fam_block = m.group(0)
    keep = []
    for u, fmt in re.findall(r"url\('/font/([^')]+)'\)\s*format\('([^']+)'\)", fam_block):
        fn = u.split('?')[0].split('#')[0]
        if os.path.exists(os.path.join(THEME, 'font', fn)):
            keep.append("url('../font/%s') format('%s')" % (fn, fmt))
    return 'src: ' + ',\n         '.join(keep) + ';'
css = re.sub(r"src:\s*url\('/font/.*?;", fontsrc, css, flags=re.S)
css += '''
/* archive additions: keep wide images inside the column */
.entrybody img { max-width: 100%; height: auto; }
footer { text-align: center; color: #fff; padding: 10px 0 20px; }
footer a { color: #fff; }
.archive_list li { margin: 2px 0; }
'''
open(os.path.join(ROOT, 'assets', 'css', 'default.css'), 'w', encoding='utf-8').write(css)

# posts
for i, p in enumerate(posts):
    pre = '../'
    nav = []
    if i > 0:
        q = posts[i - 1]; nav.append('&laquo; <a href="%d.html" rel="prev">%s</a>' % (q['post_id'], E(q['title'])))
    if i < len(posts) - 1:
        q = posts[i + 1]; nav.append('<a href="%d.html" rel="next">%s</a> &raquo;' % (q['post_id'], E(q['title'])))
    content = entry(pre, p, True) + '\n<p class="prevnext">' + ' &nbsp;|&nbsp; '.join(nav) + '</p>'
    extra = ''
    if p.get('original_url'):
        extra = ' 原文：<a href="%s">%s</a>' % (E(p['original_url']), E(p['original_url']))
    write('p/%d.html' % p['post_id'], page(pre, '%s : %s' % (SITE_TITLE, p['title']), content, extra))

# home pages
npages = (len(newest) + PER_PAGE - 1) // PER_PAGE
for n in range(1, npages + 1):
    pre = '' if n == 1 else '../'
    chunk = newest[(n - 1) * PER_PAGE: n * PER_PAGE]
    body = '\n'.join(entry(pre, p, False) for p in chunk)
    def href(k):
        if k == 1: return pre + 'index.html'
        return pre + 'page/%d.html' % k
    nav = []
    if n < npages: nav.append('<a href="%s">Previous</a>' % href(n + 1))
    nav.append('<span class="pageno">%d / %d</span>' % (n, npages))
    if n > 1: nav.append('<a href="%s">Next</a>' % href(n - 1))
    body += '\n<p class="prevnext">' + ' &nbsp; '.join(nav) + '</p>'
    write('index.html' if n == 1 else 'page/%d.html' % n,
          page(pre, SITE_TITLE if n == 1 else '%s : Page %d' % (SITE_TITLE, n), body))

# archives
pre = '../'
inner = ['<p>共 %d 篇，%s–%s。按年：%s</p>' % (len(posts), years[0], years[-1],
         ' '.join('<a href="%s.html">%s</a>' % (y, y) for y in years))]
for y in reversed(years):
    yp = [p for p in newest if p['date'][:4] == y]
    ms = sorted({p['date'][:7] for p in yp}, reverse=True)
    inner.append('<h3><a href="%s.html">%s</a> (%d)</h3>' % (y, y, len(yp)))
    inner.append('<p>' + ' '.join('<a href="%s.html">%s 月</a>' % (m, int(m[5:])) for m in ms) + '</p>')
    inner.append(listing(pre, yp))
write('archive/index.html', page(pre, SITE_TITLE + ' : Archives', listing_page(pre, 'Archives', '\n'.join(inner))))
for y in years:
    yp = [p for p in newest if p['date'][:4] == y]
    ms = sorted({p['date'][:7] for p in yp}, reverse=True)
    inner = ['<p><a href="index.html">&laquo; 全部归档</a> · 月份：' +
             ' '.join('<a href="%s.html">%s 月</a>' % (m, int(m[5:])) for m in ms) + '</p>']
    for m in ms:
        mp = [p for p in yp if p['date'][:7] == m]
        inner.append('<h3><a href="%s.html">%s</a> (%d)</h3>' % (m, m, len(mp)))
        inner.append(listing(pre, mp))
    write('archive/%s.html' % y, page(pre, '%s : %s' % (SITE_TITLE, y), listing_page(pre, 'Archives : %s' % y, '\n'.join(inner))))
for i, m in enumerate(months):
    mp = [p for p in newest if p['date'][:7] == m]
    nav = ['<a href="index.html">全部归档</a>', '<a href="%s.html">%s 年</a>' % (m[:4], m[:4])]
    if i > 0: nav.insert(0, '<a href="%s.html">&laquo; %s</a>' % (months[i - 1], months[i - 1]))
    if i < len(months) - 1: nav.append('<a href="%s.html">%s &raquo;</a>' % (months[i + 1], months[i + 1]))
    body = listing_page(pre, 'Archives : %s' % m, '<p>' + ' · '.join(nav) + '</p>') + '\n' + \
        '\n'.join(entry(pre, p, False) for p in mp)
    write('archive/%s.html' % m, page(pre, '%s : %s' % (SITE_TITLE, m), body))

# categories
for c in cat_names:
    cp = [p for p in newest if (p['category'] or '未分类') == c]
    write(cat_file[c], page(pre, '%s : %s' % (SITE_TITLE, c),
          listing_page(pre, 'Category : %s (%d)' % (E(c), len(cp)), listing(pre, cp))))

open(os.path.join(ROOT, '.nojekyll'), 'w').close()
print('posts', len(posts), 'home pages', npages, 'archive pages', 1 + len(years) + len(months),
      'categories', len(cat_names), 'total html', len(written))
