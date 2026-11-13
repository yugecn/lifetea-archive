lifetea.org（Chinese Tea）历代主题 · 按 Textpattern 主题包格式整理
来源：Wayback Machine 存档的样式表、脚本与首页 HTML（2007-01 至 2013-12 快照）

三套主题
1. ctea-lifetea-2007  2006–2009 版：左侧折叠菜单（squidfingers 脚本），顶部大图，Ryan Arrowsmith 设计
   样式：default-2007-01.css / default-2007-07.css（default.css = 07 版）
   缺：头图 467.jpg、905.jpg 未被存档，截图里用灰底占位
2. ctea-lifetea-2010  2010 版：同一侧栏结构，换头图（1323.jpg、4896.jpg）
   样式：default-2010-06.css / default-2010-11.css（default.css = 11 月版）
3. ctea-lifetea-2011  2011–2013 版：HTML5，jQuery + ddaccordion 折叠菜单，更大头图
   样式：2011-02、2011-02b、2011-08、2012-06 四版（default.css = 2012-06，头图 5515.jpg）
   缺：titlebar.png、titlebar-active.png、/font/ 下的 Georgia 与 Lucida 网页字体未存档

每个主题目录
  manifest.json      Textpattern 主题元数据（txp-type: textpattern-theme）
  pages/             default.txp、archive.txp、error_default.txp
  forms/             article、comment、link、file、misc（sidebar）
  styles/            原版 CSS（逐字保留）
  js/                原版脚本
  images/            能找回的头图与背景
  screenshot.png     效果截图

说明
- CSS、JS、图片为原文件；pages 与 forms 无原件可下载（Textpattern 后台模板不对外公开），
  是根据存档页面的实际 HTML 结构反推重写的 txp 标签模板，输出结构与原站一致。
- 截图是用存档首页 + 原 CSS 在本地重新渲染的；正文配图大多未存档，以“原图未存档”占位。
- 导入：把某个主题目录（或其 zip）放进 Textpattern 的 themes/ 目录，在 Presentation → Themes 里导入。
- 样式里图片路径仍是 /images/xxx.jpg，导入后把 images/ 里的图上传到站点同名路径即可。
