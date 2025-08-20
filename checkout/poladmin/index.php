<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<HTML>
<HEAD>
<TITLE> Add a product </TITLE>
</HEAD>
<BODY>
<?php
///error_reporting(15);
$cs = mysql_connect("localhost", "c_policyof", "bfE31eBD");
mysql_select_db("c_policyof");

if($_GET['action'] == "delete"){
	if(!$_GET['id']){
die("No Product ID Specified. Go Back.");
	}
///$cs2 = mysql_connect("localhost", "c_policyof", "bfE31eBD");
///mysql_select_db("c_policyof");
if($result = mysql_query("DELETE FROM products WHERE (ID = '$_GET[id]')", $cs)){
print "<center><font color=\"#0000FF\"><b><BR>Product deletion was successful!</b></font>";
@mysql_free_result($result);
}else{
print "<center><font color=\"#FF0000\"><b><BR>Product deletion was NOT successful.</b></font>";
}
///mysql_close($cs2);
} /// end if action is delete


if($_POST['action'] == "posting"){
set_time_limit(1060);
if($_POST['productID'] == ""){
switch($_FILES['file']['error']){
case 0:
/// do nothing
break;
case 1:
echo "<center><font color=\"#FF0000\"><b><BR>The uploaded Product file exceeds the upload_max_filesize directive in php.ini (2 Megs). <a href=\"javascript: self.history.back()\">Go Back.</a></b></font></center><BR>";
mysql_close($cs);
die;
break;
case 2:
echo "<center><font color=\"#FF0000\"><b><BR>The uploaded Product file exceeds the MAX_FILE_SIZE directive that was specified in the html form (5 megs). <a href=\"javascript: self.history.back()\">Go Back.</a></b></font></center><BR>";
mysql_close($cs);
die;
break;
case 3:
echo "<center><font color=\"#FF0000\"><b><BR>The uploaded file was only partially uploaded. <a href=\"javascript: self.history.back()\">Go Back.</a></b></font></center><BR>";
mysql_close($cs);
die;
break;
case 4:
echo "<center><font color=\"#FF0000\"><b><BR>No product file was uploaded. <a href=\"javascript: self.history.back()\">Go Back.</a></b></font></center><BR>";
mysql_close($cs);
die;
break;
case 5:
echo "<center><font color=\"#FF0000\"><b><BR>Uploaded Product file size 0 bytes. <a href=\"javascript: self.history.back()\">Go Back.</a></b></font></center><BR>";
mysql_close($cs);
die;
break;
} /// end switch
///die("<hr>$file_name - $file_size - $file_type - $file<hr>");
///$data = addslashes(fread(fopen($file, "r"), $file_size));
$file_name = eregi_replace("[^A-Za-z0-9_.]", " ", $file_name);
if(copy($_FILES['file']['tmp_name'],$_SERVER['DOCUMENT_ROOT']."/e-books/$file_name")){
print "<BR><BR><font color=\"#0000FF\"><b><center>File uploaded OK.</center></b></font><BR>";
}else{
mysql_close($cs);
die("<center><font color=\"#FF0000\"><b><BR>There was an error storing the file on the server. <a href=\"javascript: self.history.back()\">Go Back.</a></b></font></center><BR>");
}
///////////////////////////////////////
///////////////////////////////////////
switch($_FILES['picture']['error']){
case 0:
/// do nothing
break;
case 1:
echo "<center><font color=\"#FF0000\"><b><BR>The uploaded Picture file exceeds the upload_max_filesize directive in php.ini (2 Megs). <a href=\"javascript: self.history.back()\">Go Back.</a></b></font></center><BR>";
mysql_close($cs);
die;
break;
case 2:
echo "<center><font color=\"#FF0000\"><b><BR>The uploaded Picture file exceeds the MAX_FILE_SIZE directive that was specified in the html form (5 megs). <a href=\"javascript: self.history.back()\">Go Back.</a></b></font></center><BR>";
mysql_close($cs);
die;
break;
case 3:
echo "<center><font color=\"#FF0000\"><b><BR>The uploaded Picture file was only partially uploaded. <a href=\"javascript: self.history.back()\">Go Back.</a></b></font></center><BR>";
mysql_close($cs);
die;
break;
case 4:
echo "<center><font color=\"#FF0000\"><b><BR>No Picture file was uploaded. <i>(using default \"No Photo Available\")</i></b></font></center><BR>";
$picture = "../noPhoto.gif";
$picture_size = filesize($picture);
$_FILES['picture']['type'] = "image/gif";
break;
case 5:
echo "<center><font color=\"#FF0000\"><b><BR>Uploaded Product file size 0 bytes. <i>(using default \"No Photo Available\")</i></b></font></center><BR>";
$picture = "../noPhoto.gif";
$picture_size = filesize($picture);
$_FILES['picture']['type'] = "image/gif";
break;
} /// end switch

///if($_FILES['picture']['type'] != "image/jpeg" && $_FILES['picture']['type'] != "image/gif"){
if((!eregi("jpeg", $_FILES['picture']['type'])) && (!eregi("gif", $_FILES['picture']['type']))){
mysql_close($cs);
die("<center><font color=\"#FF0000\"><b><BR>The uploaded Picture file has to be a jpg of gif file format <i>(upload format is ".$_FILES['picture']['type'].")</i>. <a href=\"javascript: self.history.back()\">Go Back.</a></b></font></center><BR>");
}
$data2 = addslashes(fread(fopen($picture, "r"), $picture_size));
///////////////////////////////////////////////////////////////////////
///print $_FILES[file][type]."<HR>";
$query = "INSERT INTO products (ID,product_name,product_data,product_type,password,price,shipping,picture,picture_type,date,downloadable) VALUES ('', '$file_name', '$data', '".$_FILES['file']['type']."', '$_POST[password]', '$_POST[price]', '$_POST[shipping]', '$data2', '".$_FILES['picture']['type']."', now(), '$_POST[downloadable]')";
if($result = mysql_query($query, $cs)){
@mysql_free_result($result);
print "<BR><BR><font color=\"#0000FF\"><b><center>Product data successfully stored!</center></b></font><BR><BR>";
}else{
print "<BR><BR><font color=\"#FF0000\"><b><center>There was a problem storing the data. SQL Server said: <i>\"".mysql_error($cs)."\"</i><BR>Please try again or contact the programming administrator.</center></b></font><BR><BR>";
///print "<hr>$query</hr>";
}

}else{ /// else it is an update
///////////////////
//////////////////
switch($_FILES['file']['error']){
case 0:
///echo "<center><font color=\"#0000FF\"><b><BR>Product file name/data being updated for product $_POST[productID]...</b></font></center>";
$data = "OK";
$file_name = eregi_replace("[^A-Za-z0-9_.]", " ", $file_name);
if(copy($_FILES['file']['tmp_name'],$_SERVER['DOCUMENT_ROOT']."/e-books/$file_name")){
print "<BR><BR><font color=\"#0000FF\"><b><center>Product File uploaded and DB updated OK.</center></b></font><BR>";
}else{
mysql_close($cs);
die("<center><font color=\"#FF0000\"><b><BR>There was an error storing the file on the server. <a href=\"javascript: self.history.back()\">Go Back.</a></b></font></center><BR>");
}
break;
case 1:
echo "<center><font color=\"#FF0000\"><b><BR>The uploaded Product file exceeds the upload_max_filesize directive in php.ini (2 Megs). <a href=\"javascript: self.history.back()\">Go Back.</a></b></font></center><BR>";
mysql_close($cs);
die;
break;
case 2:
echo "<center><font color=\"#FF0000\"><b><BR>The uploaded Product file exceeds the MAX_FILE_SIZE directive that was specified in the html form (5 megs). <a href=\"javascript: self.history.back()\">Go Back.</a></b></font></center><BR>";
mysql_close($cs);
die;
break;
case 3:
echo "<center><font color=\"#FF0000\"><b><BR>The uploaded file was only partially uploaded. <a href=\"javascript: self.history.back()\">Go Back.</a></b></font></center><BR>";
mysql_close($cs);
die;
break;
case 4:
echo "<center><font color=\"#FF0000\"><b><BR>No product file was uploaded - Keeping current settings for product $_POST[productID].</b></font></center>";
break;
case 5:
echo "<center><font color=\"#FF0000\"><b><BR>Uploaded Product file size 0 bytes. <a href=\"javascript: self.history.back()\">Go Back.</a></b></font></center><BR>";
mysql_close($cs);
die;
break;
} /// end switch
//////////////////////////////////////////////////////////////////////////////
switch($_FILES['picture']['error']){
case 0:
echo "<center><font color=\"#0000FF\"><b><BR>Picture file name/data being updated for product $_POST[productID]...</b></font></center>";
$data2 = addslashes(fread(fopen($picture, "r"), $picture_size));
break;
case 1:
echo "<center><font color=\"#FF0000\"><b><BR>The uploaded Picture file exceeds the upload_max_filesize directive in php.ini (2 Megs). <a href=\"javascript: self.history.back()\">Go Back.</a></b></font></center><BR>";
mysql_close($cs);
die;
break;
case 2:
echo "<center><font color=\"#FF0000\"><b><BR>The uploaded Picture file exceeds the MAX_FILE_SIZE directive that was specified in the html form (5 megs). <a href=\"javascript: self.history.back()\">Go Back.</a></b></font></center><BR>";
mysql_close($cs);
die;
break;
case 3:
echo "<center><font color=\"#FF0000\"><b><BR>The uploaded Picture file was only partially uploaded. <a href=\"javascript: self.history.back()\">Go Back.</a></b></font></center><BR>";
mysql_close($cs);
die;
break;
case 4:
echo "<center><font color=\"#FF0000\"><b><BR>No Picture file was uploaded - Keeping current settings for product $_POST[productID].</b></font></center>";
break;
case 5:
echo "<center><font color=\"#FF0000\"><b><BR>Uploaded Product file size 0 bytes - Keeping current settings for product $_POST[productID].</b></font></center>";
break;
} /// end switch
if($_FILES['picture']['name']){
if((!eregi("jpeg", $_FILES['picture']['type'])) && (!eregi("gif", $_FILES['picture']['type']))){
mysql_close($cs);
die("<center><font color=\"#FF0000\"><b><BR>The uploaded Picture file has to be a jpg of gif file format <i>(upload format is ".$_FILES['picture']['type'].")</i>. <a href=\"javascript: self.history.back()\">Go Back.</a></b></font></center><BR>");
}
}


if($data){
$whereclause .= ", product_name = '$file_name', product_data = '', product_type = '".$_FILES['file']['type']."'";
}

if($_POST['price']){
$whereclause .= ", price = '$_POST[price]'";
echo "<center><font color=\"#0000FF\"><b><BR>Price is being updated for product $_POST[productID]...</b></font></center>";
}else{
echo "<center><font color=\"#FF0000\"><b><BR>No price - keeping current settings for product $_POST[productID].</b></font></center>";
}
if($_POST['password']){
$whereclause .= ", password = '$_POST[password]'";
echo "<center><font color=\"#0000FF\"><b><BR>Password is being updated for product $_POST[productID]...</b></font></center>";
}else{
echo "<center><font color=\"#FF0000\"><b><BR>No password - keeping current settings for product $_POST[productID].</b></font></center>";
}
if($_POST['shipping']){
$whereclause .= ", shipping = '$_POST[shipping]'";
echo "<center><font color=\"#0000FF\"><b><BR>Shipping is being updated for product $_POST[productID]...</b></font></center>";
}else{
echo "<center><font color=\"#FF0000\"><b><BR>No shipping - keeping current settings for product $_POST[productID].</b></font></center>";
}
if($data2){
$whereclause .= ", picture = '$data2', picture_type = '".$_FILES['picture']['type']."'";
}
if($whereclause){
$whereclause .= " WHERE (ID = '$_POST[productID]')";
}
$query = "UPDATE products SET date = now()$whereclause";
if($result = mysql_query($query, $cs)){
@mysql_free_result($result);
print "<BR><BR><font color=\"#FF0000\"><b><center>Product data successfully updated!</center></b></font><BR><BR>";
}else{
print "<BR><BR><font color=\"#FF0000\"><b><center>There was a problem updating the data. SQL Server said: <i>\"".mysql_error($cs)."\"</i><BR>Please try again or contact the programming administrator.</center></b></font><BR><BR>";
///print "<hr>$query</hr>";
}
//////////////////
//////////////////
} /// end if it is a new product or an update
///mysql_close($cs);
} /// end if there was a post
?>
  <table align="center" border="1" width="863" cellspacing="0" cellpadding="0" bordercolorlight="#000000">
    <tr>
      <td width="20" bgcolor="#C0C0C0"><font face="Verdana" size="1">ID</font></td>
      <td width="181" bgcolor="#C0C0C0"><font face="Verdana" size="1">Name</font></td>
      <td width="124" bgcolor="#C0C0C0"><font face="Verdana" size="1">Product
        Password</font></td>
      <td width="78" bgcolor="#C0C0C0"><font face="Verdana" size="1">Price</font></td>
      <td width="88" bgcolor="#C0C0C0"><font face="Verdana" size="1">Shipping</font></td>
      <td width="136" bgcolor="#C0C0C0"><font face="Verdana" size="1">Picture</font></td>
      <td width="136" bgcolor="#C0C0C0"><font face="Verdana" size="1">Entry Date</font></td>
      <td width="58" bgcolor="#C0C0C0"><font face="Verdana" size="1">Download</font></td>
    </tr>
<?php
///$cs = mysql_connect("localhost", "c_policyof", "bfE31eBD");
///mysql_select_db("c_policyof");
$query = "SELECT * FROM products ORDER BY ID";
$result = mysql_unbuffered_query($query, $cs);
while($row = mysql_fetch_array($result)){
$assembly .= "<option value=\"".$row["ID"]."\">product # ".$row["ID"]."</option>\n";
	if($row['downloadable'] != "Y"){
	$extension = ''; 
$parts = split('\.', $row['product_name']); 
if (count($parts) > 1) $extension = end($parts); 
if (!$extension && count($parts) > 2) $ext = prev($parts);
$row['product_name'] = str_replace(".$extension", "", $row['product_name']);
	}
?>

    <tr>
      <td width="20"><?php echo $row["ID"] ?><hr><font size="1" face="Verdana"><a href="<?php echo $_SERVER['PHP_SELF'] ?>?action=delete&id=<?php echo $row["ID"] ?>" onClick="if(confirm('Are you sure? This cannot be undone.')){return true}else{return false}">Delete?</a></font></td>
      <td width="181"><?php echo $row["product_name"] ?></td>
      <td width="124"><?php echo $row["password"] ?></td>
      <td width="78"><?php echo $row["price"] ?></td>
      <td width="88"><?php echo $row["shipping"] ?></td>
      <td width="136"><img src="../images.php?id=<?php echo $row["ID"] ?>" alt="" border="0" height="100" width="100"></td>
      <td width="136"><?php echo $row["date"] ?></td>
      <td width="58"><?php echo $row["downloadable"] ?></td>
    </tr>
	<?php
} /// end WHILE
mysql_free_result($result);
mysql_close($cs);
	?>
  </table>


<script>
function formcheck(){
if(document.products.file.value == "" && document.products.productID.options[document.products.productID.selectedIndex].value == ""){
alert("Please choose a product file to upload. Even if it is a text file. The name of the product is always the name of the file.")
return false
}
if(document.products.password.value == "" && document.products.downloadable.checked){
if(confirm("You indicated this is a downloadable product. A password was not chosen.\r\n\r\nPress OK to proceed anyway\r\n\r\n          or          \r\nCANCEL to stop and enter one.")){
return true
}else{
return false
}
}
if(document.products.price.value == "" && document.products.productID.options[document.products.productID.selectedIndex].value == ""){
alert("Please enter a price.")
return false
}

if(document.products.shipping.value == "" && (!document.products.downloadable.checked)){
if(confirm("You indicated this is a NOT a downloadable product. Shipping cost has no value.\r\n\r\nPress OK to proceed anyway\r\n\r\n          or          \r\nCANCEL to stop and enter a shipping value.")){
return true
}else{
return false
}
}


}
</script>
<form name="products" method="POST" enctype="multipart/form-data" action="<?php echo $_SERVER['PHP_SELF'] ?>" onSubmit="return formcheck()">
<input type="hidden" name="action" value="posting">
<input type="hidden" name="MAX_FILE_SIZE" value="50000000">
  <table align="center" border="1" width="560" cellspacing="0" cellpadding="0">
    <tr>
      <td width="560" colspan="2" bgcolor="#808080">
	  <font face="Verdana" size="2" color="#FFFFFF"><b>Please enter the product details
        below and then upload it.</b></font></td>
    </tr>
	 <tr>
      <td width="560" colspan="2">
	  <font face="Verdana" size="1" color="#000000">Updating a product? Choose it from this menu:</font>
	  <select name="productID">
<option value="">New Product</option>
<?php echo $assembly ?>
	  </select>
	  </td>
    </tr>
    <tr>
      <td width="231"><font face="Verdana" size="2">Product File</font></td>
      <td width="313"><font face="Verdana" size="2"><input type="file" name="file" size="20"><br><font face="Verdana" size="1"><i>(always required)</i></font></font></td>
    </tr>
    <tr>
      <td width="231"><font face="Verdana" size="2">Password</font></td>
      <td width="313"><font face="Verdana" size="2"><input type="text" name="password" size="20"></font></td>
    </tr>
    <tr>
      <td width="231"><font face="Verdana" size="2">Price</font></td>
      <td width="313"><font face="Verdana" size="2"><input type="text" name="price" size="20"><br></font><font face="Verdana" size="1">(No
        &quot;$&quot;. Only numbers and decimals - Decimals required)</font></td>
    </tr>
    <tr>
      <td width="231"><font face="Verdana" size="2">Shipping</font></td>
      <td width="313"><font face="Verdana" size="2"><input type="text" name="shipping" size="20"><br></font><font face="Verdana" size="1">(No
        &quot;$&quot;. Only numbers and decimals - Decimals required)</font></td>
    </tr>
    <tr>
      <td width="231"><font face="Verdana" size="2">Picture <i>(.jpg &amp; .gif
        only)</i></font></td>
      <td width="313"><font face="Verdana" size="2"><input type="file" name="picture" size="20"></font></td>
    </tr>
    <tr>
      <td width="231"><font face="Verdana" size="2">Is it a downloadable Product?</font></td>
      <td width="313"><font face="Verdana" size="2"><input type="checkbox" name="downloadable" value="Y">
        Check for &quot;Yes&quot;</font></td>
    </tr>
    <tr>
      <td width="544" colspan="2"></td>
    </tr>
    <tr>
      <td width="544" colspan="2" align="center"><font face="Verdana" size="2"><input type="Submit" name="button" value="Upload Product"></font></td>
    </tr>
  </table>
  </form>
</body>

</BODY>
</HTML>
