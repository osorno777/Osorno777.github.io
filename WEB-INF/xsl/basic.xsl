<!-- This is a very basic XSL file just reworking the <a> tag -->

<!-- Disable escaping, so < isn't printed as &lt;. -->
<xsl:output disable-output-escaping='true'/>

<!-- Copy unknown tags to the output -->

<xsl:template match='*|@*'>
  <xsl:copy>
    <xsl:apply-templates select='node()|@*'/>
  </xsl:copy>
</xsl:template>

<!-- Rewrite <a href='foo'> to enable cookies -->
<xsl:template match='a[@href]'>
<a href='<%= response.encodeURL("{@href}") %>'>
  <xsl:apply-templates select='node()|@*[name(.)!="href"]'/>
</a>
</xsl:template>
