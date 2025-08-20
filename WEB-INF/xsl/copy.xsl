<!-- The default XSL file just brings in the header -->
<xsl:output disable-output-escaping='true'/>

<xsl:template match='*|@*'>
  <xsl:copy>
    <xsl:apply-templates select='node()|@*'/>
  </xsl:copy>
</xsl:template>