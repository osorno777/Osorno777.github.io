<!-- The counter brings in the header -->

<xsl:output disable-output-escaping='true'/>
<xsl:import href='copy.xsl'/>
<xsl:import href='header.xsl'/>

<!-- 
   - This counter executes when the XTP is processed by
   - the XSL stylesheet.
  -->

<xsl:template match='counter'>
  <jsp:scriptlet>
    Integer counter;
    counter = (Integer) application.getAttribute("examples.xsl.counter");
    if (counter == null)
      counter = new Integer(1);
    else
      counter = new Integer(counter.intValue() + 1);
    application.setAttribute("examples.xsl.counter", counter);

    out.println(counter);
  </jsp:scriptlet>
</xsl:template>
