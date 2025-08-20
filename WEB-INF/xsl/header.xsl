<xsl:stylesheet>
<xsl:output method='html' disable-output-escaping=yes/>

<xtp:directive.page import='javax.servlet.*'/>
<xtp:directive.page import='javax.servlet.http.*'/>
<xtp:directive.page import='javax.servlet.jsp.*'/>
<xtp:directive.page import='org.xml.sax.*'/>
<xtp:directive.page import='com.caucho.web.*'/>
<xtp:directive.page import='com.caucho.vfs.*'/>

<#!
  String top = "/";
  Navigation nav = null;

  void initNavigation(XslWriter out)
    throws IOException, SAXException
  {
    PageContext page = (PageContext) out.getProperty("caucho.page.context");
    ServletContext app = page.getServletContext();
    HttpServletRequest req = (HttpServletRequest) page.getRequest();

    String url = req.getContextPath() + req.getServletPath();
    int p = url.lastIndexOf('/');
    String base = url.substring(0, p);
    Path pwd = (Path) out.getProperty("caucho.pwd");

    ServletContext topApp = app.getContext("/");

    ArrayList paths = new ArrayList();
    while (p >= 0) {
      String realPath = topApp.getRealPath(url.substring(0, p + 1));
      Path path = pwd.lookupNative(realPath);

      paths.add(path);
      if (path.lookup("toc.xml").exists())
        out.addCacheDepend(path.lookup("toc.xml"));

      p = url.lastIndexOf('/', p - 1);
    }

    nav = Navigation.createNested(paths, base);

    if (nav == null)
      nav = new Navigation();

    top = nav.getAttribute("top");
    if (top == null || top == "")
      top = "/";
  }

  void writeFamilyNavigation(XslWriter out)
    throws IOException, SAXException
  {
    PageContext page = (PageContext) out.getProperty("caucho.page.context");
    HttpServletRequest req = (HttpServletRequest) page.getRequest();

    String url = req.getContextPath() + req.getServletPath();
    NavItem item = nav.findURL(url);

    ArrayList list = null;
    if (item != null)
      list = item.familyNavigation();

    if (list == null || list.size() == 0)
      return;

    for (int i = 0; i < list.size(); i++) {
      NavItem child = (NavItem) list.get(i);
      if (child == null) {
        out.pushElement("hr");
        out.popElement();
      }
      else {
        String link = child.getLink();
        if (link.startsWith("/"));
          link = link.substring(1);

        out.pushElement("a");
        out.setAttribute("href", top + link);
        out.println(child.getTitle());

        out.popElement();
        out.pushElement("br");
        out.popElement();
      }
    }
  }
#>

<xsl:template match="html">
  <# initNavigation(out); #>
  <html>
  <head>
    <title><{title}></title>
    <link rel="STYLESHEET" type="text/css">
      <xsl:attribute name='href'>/css/default.css</xsl:attribute>
    </link>
  </head>

  <xsl:apply-templates select='body'/>
  </html>
</xsl:template>

<xsl:template match="body">
  <body bgcolor=white>
  <xsl:attribute name='background'><#= top #>images/background.gif</xsl:attribute>
  <!-- Column Formatting -->
  <table cellpadding=0 cellspacing=0 border=0 width="100%" summary="">
  <tr valign=top>

  <!-- Left Column: logo and navigation -->
  <td width=120>
  <img src="<#= top #>images/caucho.gif" width=120 height=40 alt=caucho>
    <xsl:attribute name='src'><#= top #>images/caucho.gif</xsl:attribute>
  </img>
  <br/>
 
  <# writeFamilyNavigation(out); #>
  </td>
  
  <!-- Spacing Column -->
  <td width=30>
  <img alt="" width=30 height=1>
    <xsl:attribute name='src'><#= top #>images/caucho.gif</xsl:attribute>
  </img>
  </td>

  <!-- Center Column: title and content -->
  <td width='70%'>

  <!-- top title -->
  <table width="100%" cellspacing=0 cellpadding=0 border=0 summary="">
  <tr class=toptitle>
  <td>
  <xsl:attribute name='background'><#= top #>images/hbleed.gif</xsl:attribute>
      <font class=toptitle size="+3">&nbsp;<{../head/title}></font>
  </td></tr>
  <tr><td><br/>

  <xsl:apply-templates/>

  <!-- Footer -->
  </td></tr></table>

  <hr/>
  <table width="100%" cellspacing=0 cellpadding=0 border=0>
  <tr>
  <#
     HttpServletRequest req;
     req = (HttpServletRequest) out.getPage().getRequest();
     NavItem item = nav.findURL(req.getRequestURI());

     NavItem prev = item.getPreviousPreorder();
     if (prev != null) {
       out.print("<td><a href=\"" + prev.getLink() + "\">");
       out.print(prev.getTitle() + "</a></td>");
     }
     else
       out.print("<td>&nbsp;</td>");

     out.print("<td width=\"100%\">&nbsp;</td>");

     NavItem next = item.getNextPreorder();
     if (next != null) {
       out.print("<td><a href=\"" + next.getLink() + "\">");
       out.print(next.getTitle() + "</a></td>");
     }
     else
       out.print("<td>&nbsp;</td>");
  #>
  </tr></table>
  </td><td width="20%">&nbsp;</td></tr></table>
  </body>
</xsl:template>

</xsl:stylesheet>
