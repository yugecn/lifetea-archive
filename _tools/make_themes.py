import os, json, shutil, glob
RAW='/workspace/work/lifetea/_raw/theme'
OUT='/workspace/work/lifetea/themes'
def w(p,s):
    os.makedirs(os.path.dirname(p),exist_ok=True); open(p,'w').write(s.strip('\n')+'\n')

# ---------- shared forms (classic Textpattern 4.0 era markup, from archived pages) ----------
ARTICLE_DEFAULT='''<div class="entry">
<div class="entrytitle">
<txp:permlink><txp:title /></txp:permlink> <span class="entrytime"> @ <txp:posted format="%b %d, %Y" /></span>
</div>
<div class="entrybody">
<txp:body />
</div>
<div class="entrymeta">
Posted in <txp:category1 link="1" title="1" /><txp:if_individual_article><txp:else /> | <txp:comments_invite wraptag="" /></txp:if_individual_article>
</div>
</div>
<txp:if_individual_article>
<div class="commentsblock">
<txp:if_comments>
<h3 id="comment"><txp:comments_count /> Responses to "<txp:title />"</h3>
<txp:comments break="li" wraptag="ol" class="comments" />
</txp:if_comments>
<txp:if_comments_allowed>
<txp:comments_form />
</txp:if_comments_allowed>
</div>
</txp:if_individual_article>'''
LISTING='''<li><txp:permlink><txp:title /></txp:permlink> <span class="entrytime"><txp:posted format="%Y-%m-%d" /></span></li>'''
SEARCH='''<div class="entry">
<div class="entrytitle"><txp:permlink><txp:title /></txp:permlink> <span class="entrytime"> @ <txp:posted format="%b %d, %Y" /></span></div>
<div class="entrybody"><txp:search_result_excerpt /></div>
</div>'''
COMMENTS='''<div class="<txp:if_author>authorcomment</txp:if_author>">
<cite><txp:comment_name /></cite> Says:<br />
<small class="commentmetadata"><txp:comment_permlink> <txp:comment_time format="%Y-%m-%d" /></txp:comment_permlink></small>
<txp:comment_message />
</div>'''
COMMENT_FORM='''<h3 id="respond">Leave A Reply</h3>
<txp:comments_error wraptag="ul" break="li" />
<p><txp:comment_name_input /> <label for="name">Name (required)</label></p>
<p><txp:comment_email_input /> <label for="email">Email (will not be published) (required)</label></p>
<p><txp:comment_web_input /> <label for="web">Website</label></p>
<p id="remember"><txp:comment_remember /></p>
<p><txp:comments_help /></p>
<p><txp:comment_message_input /></p>
<p><txp:comment_preview /> <txp:comment_submit /></p>'''
PLAINLINKS='''<txp:linkdesctitle /><br />'''

def common_forms(base):
    w(f'{base}/forms/article/default.txp',ARTICLE_DEFAULT)
    w(f'{base}/forms/article/article_listing.txp',LISTING)
    w(f'{base}/forms/article/search_results.txp',SEARCH)
    w(f'{base}/forms/comment/comments.txp',COMMENTS)
    w(f'{base}/forms/comment/comments_display.txp','<txp:comments break="li" wraptag="ol" class="comments" />\n<txp:if_comments_allowed><txp:comments_form /></txp:if_comments_allowed>')
    w(f'{base}/forms/comment/comment_form.txp',COMMENT_FORM)
    w(f'{base}/forms/link/plainlinks.txp',PLAINLINKS)
    w(f'{base}/forms/file/files.txp','<txp:file_download_link><txp:file_download_name /></txp:file_download_link>')
    for d in ['category','section']:
        os.makedirs(f'{base}/forms/{d}',exist_ok=True); open(f'{base}/forms/{d}/.gitkeep','w').close()

# ---------- classic sidebar (2006-2010) ----------
SIDEBAR_CLASSIC='''<div id="sidebar-1">
<ul id="menu">
	<li>Home
		<ol><a href="<txp:site_url />">Home</a></ol></li>
	<li>About
		<ol>christina@Nanjing,China <br /> {email}</ol>
	</li>
	<li>My Album
		<ol><a href="http://photo.lifetea.org/">My Album</a></ol></li>
	<li>Archives
		<ol><a href="<txp:site_url />archive/">Archives</a></ol></li>
	<li>Recent Entries
	近期文章<br /><txp:recent_articles section="article" limit="15" wraptag="ol" break="li" class="recent_articles" />
	</li>
	<li>Recent Comments
	<txp:recent_comments limit="15" wraptag="ol" break="li" class="recent_comments" />
	</li>
	<li>Categories
	<txp:category_list wraptag="ol" break="li" class="category_list" />
	</li>
	<li>Favorite Sites
	<txp:linklist category="favorite" form="plainlinks" wraptag="ol" break="li" class="linklist" />
	</li>
	<li>Blog Life
	<txp:linklist category="bloglife" form="plainlinks" wraptag="ol" break="li" class="linklist" />
	</li>
	<li>Photo Life
	<txp:linklist category="photolife" form="plainlinks" wraptag="ol" break="li" class="linklist" />
	</li>
	<li>Feeds
	<ol>
	<li><txp:feed_link flavor="rss" label="RSS" title="RSS Feed" /></li>
	<li><txp:feed_link flavor="atom" label="Atom" title="Atom Feed" /></li>
	</ol></li>
</ul>
</div>'''
MENUJS_NOTE='<!-- squidfingers.com collapsible menu (Travis Beckham, 2003), kept as in the original -->\n<script type="text/javascript" src="<txp:site_url />js/menu.js"></script>'

def classic_page(headid, css_tag, body_tpl):
    return f'''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en">
<head>
	<meta http-equiv="content-type" content="text/html; charset=utf-8" />
	<meta http-equiv="imagetoolbar" content="no" />
	<title><txp:page_title /></title>
	{css_tag}
	{MENUJS_NOTE}
</head>
<body>
<div id="container">
<div id="{headid}">
&nbsp;
</div>
<div id="wrapper">
<txp:output_form form="sidebar" />

<div id="content">
{body_tpl}
</div>
</div>
<div id="foot">
Design by <a href="http://www.ryanarrowsmith.com/">Ryan Arrowsmith</a> but feel free to share / Proudly powered by <a href="http://www.textpattern.com/">Textpattern</a>.
</div>
</div>
</body>
</html>'''

BODY_DEFAULT='''<txp:if_individual_article>
<txp:article />
<p>
<txp:link_to_prev><txp:prev_title /></txp:link_to_prev>
<txp:link_to_next><txp:next_title /></txp:link_to_next>
</p>
<txp:else />
<txp:if_search>
<h3>Search results</h3>
<txp:article form="search_results" limit="20" />
<txp:else />
<txp:article limit="10" />
<p>
<txp:older>Previous</txp:older>
<txp:newer>Next</txp:newer>
</p>
</txp:if_search>
</txp:if_individual_article>'''
BODY_ARCHIVE='''<div class="entry">
<div class="entrytitle">Archives</div>
<div class="entrybody">
<txp:article_custom section="article" limit="9999" form="article_listing" wraptag="ol" class="archive_list" />
</div>
</div>'''
BODY_ERROR='''<div class="entry">
<div class="entrytitle"><txp:error_status /></div>
<div class="entrybody"><p><txp:error_message /></p>
<p><a href="<txp:site_url />">Back to Chinese Tea</a></p></div>
</div>'''

def manifest(title,ver,desc):
    return json.dumps({"title":title,"version":ver,"description":desc,"author":"christina@Nanjing (design based on Ryan Arrowsmith)","author_uri":"http://lifetea.org/","txp-type":"textpattern-theme"},ensure_ascii=False,indent=2)

def extract_menu_js():
    s=open(f'{RAW}/home-2007.html',errors='ignore').read()
    a=s.find('<script type="text/javascript">')+len('<script type="text/javascript">'); b=s.find('</script>',a)
    return s[a:b].strip()

def put_imgs(base, names):
    for n in names:
        src=f'{RAW}/img-{n}'
        if os.path.exists(src) and os.path.getsize(src)>0:
            os.makedirs(f'{base}/images',exist_ok=True); shutil.copy(src,f'{base}/images/{n}')

def classic(name,title,ver,desc,headid,email,styles,default_style,imgs):
    base=f'{OUT}/{name}'
    shutil.rmtree(base,ignore_errors=True)
    w(f'{base}/manifest.json',manifest(title,ver,desc))
    common_forms(base)
    w(f'{base}/forms/misc/sidebar.txp',SIDEBAR_CLASSIC.replace('{email}',email))
    css='<txp:css format="link" media="screen" />'
    w(f'{base}/pages/default.txp',classic_page(headid,css,BODY_DEFAULT))
    w(f'{base}/pages/archive.txp',classic_page(headid,css,BODY_ARCHIVE))
    w(f'{base}/pages/error_default.txp',classic_page(headid,css,BODY_ERROR))
    for label,f in styles:
        shutil.copy(f'{RAW}/{f}',f'{base}/styles/{label}.css') if os.path.isdir(f'{base}/styles') else (os.makedirs(f'{base}/styles'),shutil.copy(f'{RAW}/{f}',f'{base}/styles/{label}.css'))
    shutil.copy(f'{RAW}/{default_style}',f'{base}/styles/default.css')
    w(f'{base}/js/menu.js',extract_menu_js())
    put_imgs(base,imgs)

classic('ctea-lifetea-2007','Chinese Tea 2007','2007.07','lifetea.org 2006–2009 版式：左侧折叠菜单，顶部大图。还原自 Wayback 2007-01 与 2007-07 的样式表。',
        'head','hqoo@hotmail.com',[('default-2007-01','css-2007-01.css'),('default-2007-07','css-2007-07.css')],'css-2007-07.css',['467.jpg','905.jpg','fish-bottom.jpg'])
classic('ctea-lifetea-2010','Chinese Tea 2010','2010.11','lifetea.org 2010 版式：同一侧栏结构，换了顶部大图与配色细节。还原自 Wayback 2010-06 与 2010-11 的样式表。',
        'header','tecinese@gmail.com',[('default-2010-06','css-2010-06.css'),('default-2010-11','css-2010-11.css')],'css-2010-11.css',['1323.jpg','4896.jpg','fish-bottom.jpg'])

# ---------- 2011-2013 accordion theme ----------
def acc(name):
    base=f'{OUT}/{name}'; shutil.rmtree(base,ignore_errors=True)
    w(f'{base}/manifest.json',manifest('Chinese Tea 2011','2012.06','lifetea.org 2011–2013 版式：顶部大图 + jQuery 折叠菜单（ddaccordion），HTML5。还原自 Wayback 2011-02 至 2012-06 的样式表。'))
    common_forms(base)
    w(f'{base}/forms/misc/sidebar.txp','''<div id="menu">
<a href="<txp:site_url />"><h3 class="menuheader">Homepage</h3></a>
<h3 class="menuheader expandable">About</h3>
<div class="categoryitems">christina@Nanjing,China <br />tecinese@gmail.com</div>
<a href="http://photo.lifetea.org/"><h3 class="menuheader">Album</h3></a>
<a href="<txp:site_url />archive/"><h3 class="menuheader">Archives</h3></a>
<h3 class="menuheader expandable">Article</h3>
<div class="categoryitems"><txp:recent_articles section="article" limit="15" wraptag="ol" break="li" class="recent_articles" /></div>
<h3 class="menuheader expandable">Comments</h3>
<div class="categoryitems"><txp:recent_comments limit="15" wraptag="ol" break="li" class="recent_comments" /></div>
<h3 class="menuheader expandable">Category</h3>
<div class="categoryitems"><txp:category_list wraptag="ol" break="li" class="category_list" /></div>
<h3 class="menuheader expandable">Collection</h3>
<div class="categoryitems"><txp:linklist category="collection" form="plainlinks" wraptag="ol" break="li" class="linklist" /></div>
<h3 class="menuheader expandable">Blogger</h3>
<div class="categoryitems"><txp:linklist category="blogger" form="plainlinks" wraptag="ol" break="li" class="linklist" /></div>
<h3 class="menuheader expandable">Photograph</h3>
<div class="categoryitems"><txp:linklist category="photograph" form="plainlinks" wraptag="ol" break="li" class="linklist" /></div>
<h3 class="menuheader expandable">Aggregation</h3>
<ol class="categoryitems">
<li><txp:feed_link flavor="rss" label="RSS" title="RSS Feed" /></li>
<li><txp:feed_link flavor="atom" label="Atom" title="Atom Feed" /></li>
</ol>
</div>''')
    def page(body):
        return f'''<!doctype html>
<html class="no-js">
<head>
<meta http-equiv="content-type" content="text/html; charset=utf-8" />
<title><txp:page_title /></title>
<txp:css format="link" />
<script type="text/javascript" src="<txp:site_url />js/modernizr.js"></script>
<script type="text/javascript" src="<txp:site_url />js/jquery.js"></script>
<script type="text/javascript" src="<txp:site_url />js/jquery-ui.js"></script>
<script type="text/javascript" src="<txp:site_url />js/ddaccordion.js"></script>
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
<txp:output_form form="sidebar" />
<div id="content">
{body}
</div>
</div>
</div>
<footer>Best not view with IE 9-. Apple Safari, Google Chrome &amp; Mozilla Firefox recommended.</footer>
</body>
</html>'''
    w(f'{base}/pages/default.txp',page(BODY_DEFAULT))
    w(f'{base}/pages/archive.txp',page(BODY_ARCHIVE))
    w(f'{base}/pages/error_default.txp',page(BODY_ERROR))
    os.makedirs(f'{base}/styles',exist_ok=True)
    for lab in ['2011-02','2011-02b','2011-08','2012-06']:
        shutil.copy(f'{RAW}/css-{lab}.css',f'{base}/styles/default-{lab}.css')
    shutil.copy(f'{RAW}/css-2012-06.css',f'{base}/styles/default.css')
    os.makedirs(f'{base}/js',exist_ok=True)
    for j in ['modernizr.js','jquery.js','jquery-ui.js','ddaccordion.js']:
        if os.path.exists(f'{RAW}/{j}'): shutil.copy(f'{RAW}/{j}',f'{base}/js/{j}')
    put_imgs(base,['5115.jpg','1907.jpg','5380.jpg','5515.jpg','titlebar.png','titlebar-active.png'])
acc('ctea-lifetea-2011')
print('ok')
