<BODY>
<CENTER>
<BR>
<BR>
<h1>PHP Test Page</h1>
<BR>
<B>
This is a PHP text based counter - it should increase each time you click the "Reload" button
</B>
<BR><BR><BR>
<script language="php">
$file = fopen("count.txt","r+");
$count = fread($file, filesize("count.txt"));
fclose($file);
$count += 1;
$file = fopen("count.txt","w+");
fputs($file, $count);
fclose($file);
</script>
<table border=1 cellspacing=0 cellpadding=10>
<tr><td bordercolor="black"><font size=5><b><script language="php">include("./count.txt");</script></b></font></tr></table>
<P>
<script language="php">phpinfo();include("./count.txt");</script>
<P>
<BR>
<BR>
</BODY>

