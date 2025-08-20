<?php
function display_ahp_photo(){
$fp = fopen("noPhoto.gif", "r");
$content = fread($fp, filesize("noPhoto.gif"));
fclose($fp);
Header("Content-type: image/gif");
echo $content;
die;
}

if(!$_GET['id']){
display_ahp_photo();
}else{

$cs = mysql_connect("localhost", "c_policyof", "bfE31eBD");
mysql_select_db("c_policyof");
$query = "SELECT picture, picture_type FROM products WHERE(ID = '$_GET[id]')";
$result = mysql_query($query, $cs);
while ($row = mysql_fetch_array($result)) { 
$data = $row["picture"];
$type = $row["picture_type"];
}
if(!$data){
display_ahp_photo();
}
mysql_close($cs);
Header("Content-type: image/$type");
die("$data");
}
?>