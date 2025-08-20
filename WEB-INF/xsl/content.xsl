<xsl:output disable-output-escaping='true'/>

<xsl:template match='table-of-contents'>
  <center>
  <table width="90%" class=toc border=3>
  <tr><td>
  <#
     HttpServletRequest req;
     req = (HttpServletRequest) out.getPage().getRequest();
     NavItem item = nav.findURL(req.getRequestURI());

     for (; item.getPrevious() != null; item = item.getPrevious()) {
     }

     for (; item != null; item = item.getNext()) {
       out.print("<" + "a href=\"" + item.getLink() + "\">");
       out.print(item.getTitle());
       out.print("<" + "/a><br>");
     }
  #>
  </td></tr></table>
  </center>
</xsl:template>

<xsl:template match='var'>
  <span class=meta><xsl:apply-templates/></span>
</xsl:template>
