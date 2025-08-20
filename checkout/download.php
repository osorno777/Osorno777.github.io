<?php
/*
if (strstr($_SERVER["HTTP_USER_AGENT"], "MSIE"))
header("Content-Disposition: filename=testcover.pdf" . "%20"); // For IE
else
 header("Content-Disposition: attachment; filename=testcover.pdf"); // For Other browsers
 */
 /*
 $filename = "testcover.pdf";
header("Cache-control: private"); // fix for IE
header("Content-Type: application/pdf"); 
header("Content-Length: ".filesize($filename));
header("Content-Disposition: filename=acrobat.pdf");
$fp = fopen($filename, 'r');
fpassthru($fp); // ** CORRECT **
///fclose($fp);
*/

if((!$_GET['on']) || (!$_GET['command'])){
if(!$_GET['num']){
?>
<form method="GET" action="download.php">
Enter your order number: <input type="text" name="num" value=""><BR>
<input type="Submit" name="button" value="Go">
</form>
<?php
}else{
$cs = mysql_connect("localhost", "c_policyof", "bfE31eBD");
mysql_select_db("c_policyof");
print "<script>
function downloadit(x){
	///alert(x);
	if(x){
window.open('download.php?action=&command='+x+'&on=".$_GET['num']."', 'downloads', 'width=300,height=100,resizable=yes');
}else{
alert('Choose a product to download first.');
}
}
</script>
<select name=\"product_download\" size=\"1\" onChange=\"downloadit(this.value)\">\n<option value=\"\">Select a product to download...</option>\n";
$query = "SELECT o.ID, o.Products, p.password FROM orders o, products p WHERE(o.orderNumber = '$_GET[num]' AND o.Products = p.product_name AND p.downloadable = 'Y')";
$result = mysql_query($query, $cs);
while($row = mysql_fetch_array($result)){
	$countit++;
print "<option value=\"$row[ID]\">$row[Products] - $row[password]</option>\n";
}
mysql_close($cs);
print "</select>";
if($countit < 1){
die("<BR><BR>No downloads found with order number $_GET[num]. Go back.");
}
}
die;
}else{
$cs = mysql_connect("localhost", "c_policyof", "bfE31eBD");
mysql_select_db("c_policyof");
$query = "SELECT Products,Date,fullName FROM orders WHERE(ID = '$_GET[command]' AND orderNumber = '$_GET[on]')";
$result = mysql_query($query, $cs);
while($row = mysql_fetch_array($result)){
$file = $row["Products"];
$file2 = $row["Products"];
$time = $row["Date"];
$name = $row["fullName"];
} /// end while

if((time()-($time+259200)) > '259200'){
die("I'm sorry $name, but your download for (<b>$file</b>) has expired. Expiration date: ".date("F j, Y, g:i a"));
}else{
mysql_query("UPDATE orders SET download_times = download_times+1 WHERE(ID = '$_GET[command]')", $cs);
} /// end 2nd else
} /// end else
mysql_close($cs);
$file = "../e-books/$file"; ///testcover.pdf
///header ("Content-type: application/octet-stream");
///header("Content-Type: application/pdf");
if(!file_exists($file)){
die("File Not found.");
}
error_reporting(15);
///header("Content-Type: application/x-zip-compressed");
///header ("Content-disposition: attachment; filename=".$file2.";");
///header("Content-Length: ".filesize("$file"));
///readfile("$file");
///exit;
print "Right click on the link below and choose \"Save Target As...\" to save the file:<BR><a href='$file'>\"$file2\".</a>";
?>