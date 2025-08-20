<!-- The default XSL file just brings in the header -->
<xsl:output method='html' disable-output-encoding='true'/>

<xsl:import href='copy.xsl'/>

<xsl:template match='body'>
<body bgcolor='white'>
  <h1><xsl:apply-templates select='/html/head/title/node()'/></h1>

  <xsl:apply-templates/>
</body>
</xsl:template>

<xsl:template match='table-of-contents'/>

<xsl:template match='var'>
  <em><xsl:apply-templates/></em>
</xsl:template>
