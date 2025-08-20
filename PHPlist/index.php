<?php
if(!$HTTP_POST_VARS){
header("Location: ../join.php");
die;
}
define ('news_ok_IN',true);
include ("globals.inc.php");
if ($_POST['action'] == "submit"){
if ($_SERVER['REQUEST_METHOD'] != "POST"){
die ("no dice");
}
function custom_filter ($value, $required, $field){
global $missing;
$filter=htmlspecialchars($value);
$filter=strip_tags($filter);
$filter=trim($filter);
if(get_magic_quotes_gpc()){
$filter=stripslashes($filter);
}
if ($required == "required"){
if (!$filter){
$missing .= "$field<br>";
}
}
return $filter;
}
$email = custom_filter($_POST['email'], "required", "Email");
$f_name = custom_filter($_POST['f_name'], "$fn_req", "first name");
$l_name = custom_filter($_POST['l_name'], "$ln_req", "last name");
$address = custom_filter($_POST['address'], "$add_req", "address");
$city = custom_filter($_POST['city'], "$city_req", "city");
$state = custom_filter($_POST['state'], "$state_req", "state");
$zip_code = custom_filter($_POST['zip_code'], "$zip_req", "zip code");
$phone= custom_filter($_POST['phone'], "$phone_req", "phone number");
$age = custom_filter($_POST['age'], "$age_req", "age group");
if ($missing){
die ("you are missing the following required values:<br><br>$missing");
}
/*include ("main.data.php")  type in include to your database info include if you have one.*/
if (!$list_conn = mysql_connect("$news_server", "$news_user", "$news_pass")){
die  ("<br><br><br><br>The database is down, try back later.");
}
mysql_select_db($news_db);
$list_query = "SELECT email FROM PHPlist WHERE (email = '$email')";
if ($list_result = mysql_query($list_query)){
$list_number=mysql_num_rows($list_result);
if (!$list_number){
$list_query = "INSERT INTO PHPlist (ID, f_name, l_name, address, city, state, zip_code, phone, email, age) VALUES ('', '$f_name', '$l_name', '$address', '$city', '$state', '$zip_code', '$phone', '$email', '$age')";
if ($list_result = mysql_query($list_query)){
print "<center>Thanks for signing up!<br><br><br><a href=\"http://www.policyofliberty.net/\">click to return to our home page.</a></center>";////remove or comment this out if you use a custom page for confirmation and thanks.
/*
use this if you want to have a custom page for confirmation and thanks.
include("thanks.php");
die;
*/
}else{
die ("Can't insert to DB.");
}
}else{
die ("<br><br><br><br>That email address is already in use.");
}
}else{
mysql_close($list_conn);
die ("<br><br><br><br>Database is not responding, try back later. Sorry!");
}
}
/*delete function for form at bottom.*/
if ($_POST['action'] == "delete"){
if ($_SERVER['REQUEST_METHOD'] != "POST"){
die ("no dice");
}
$email = strip_tags($_POST['email']);
$email = htmlspecialchars($email);
$email = trim($email);
/*include ("main.data.php")  type in include to your database info include if you have one.*/
if (!$list_conn = mysql_connect("$news_server", "$news_user", "$news_pass")){
die  ("<br><br><br><br>The database is down. Try back later.");
}
mysql_select_db($news_db);
$query = "SELECT email FROM PHPlist WHERE (email = '$email')";
$result = mysql_query ($query);
$count = mysql_num_rows ($result);
if ($count >= "1"){
$there = "yes";
}else{
$there = "no";
$deleted = "<font color='#FF0000'>The account has not been deleted so either it did not exist or the email address was not entered properly.</font><BR><BR><a href='../'>Click here for the home page.</a>";
}
if ($there == "yes"){
$list_query = "DELETE FROM PHPlist WHERE (email = '$email')";
if ($list_result = mysql_query($list_query)){
$deleted = "<b>Email has been removed successfully</b><BR><BR><a href='../'>Click here for the home page.</a>";
}else{
$deleted = "SQL query did not execute.";
}
}
mysql_close($list_conn);
}
/*end delete function.*/
if(!$_POST['action'] || $_POST['action'] == "delete"){
?>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<html><head><title><?php echo "$newsletter_title"?></title>
<link rel="stylesheet" href="<?php echo "$css_file"?>">
</head><body>
<table align="center" border="0" width="300" cellpadding="0" cellspacing="0">

<tr><td width="50%"><p align="right">Email Address:&nbsp;&nbsp;</p></td>
<form method="POST" action="<? echo $_SERVER['PHP_SELF'] ?>">
<input type="hidden" name="action" value="submit">
<td><input class="PHP_form" type="text" name="email" size="20"></td></tr>
<tr><td width="50%"><p align="right">First Name:&nbsp;&nbsp;</td><td><input class="PHP_form" type="text" name="f_name" size="20"></td></tr>
<tr><td width="50%"><p align="right">Last Name:&nbsp;&nbsp;</td><td><input class="PHP_form" type="text" name="l_name" size="20"></td></tr>
<tr><td width="50%"><p align="right">Mailing Address:&nbsp;&nbsp;</td><td><textarea class="PHP_form" rows="2" name="address" cols="20"></textarea></td></tr>
<tr><td width="50%"><p align="right">City:&nbsp;&nbsp;</td><td><input class="PHP_form" type="text" name="city" size="15"></td></tr>
<tr><td width="50%"><p align="right">State:&nbsp;&nbsp;</td>
<td><select class="PHP_form" name='state'size='1'>
<option selected value='unknown'>-State-</option>
<option value='CA'>CA</option>
<OPTION VALUE='AK'>AK</OPTION>
<OPTION VALUE='AL'>AL</OPTION>
<OPTION VALUE='AR'>AR</OPTION>
<OPTION VALUE='AS'>AS</OPTION>
<OPTION VALUE='AZ'>AZ</OPTION>
<OPTION VALUE='CO'>CO</OPTION>
<OPTION VALUE='CT'>CT</OPTION>
<OPTION VALUE='DC'>DC</OPTION>
<OPTION VALUE='DE'>DE</OPTION>
<OPTION VALUE='FL'>FL</OPTION>
<OPTION VALUE='GA'>GA</OPTION>
<OPTION VALUE='HI'>HI</OPTION>
<OPTION VALUE='IA'>IA</OPTION>
<OPTION VALUE='ID'>ID</OPTION>
<OPTION VALUE='IL'>IL</OPTION>
<OPTION VALUE='IN'>IN</OPTION>
<OPTION VALUE='KS'>KS</OPTION>
<OPTION VALUE='KY'>KY</OPTION>
<OPTION VALUE='LA'>LA</OPTION>
<OPTION VALUE='MA'>MA</OPTION>
<OPTION VALUE='MD'>MD</OPTION>
<OPTION VALUE='ME'>ME</OPTION>
<OPTION VALUE='MI'>MI</OPTION>
<OPTION VALUE='MN'>MN</OPTION>
<OPTION VALUE='MO'>MO</OPTION>
<OPTION VALUE='MS'>MS</OPTION>
<OPTION VALUE='MT'>MT</OPTION>
<OPTION VALUE='NC'>NC</OPTION>
<OPTION VALUE='ND'>ND</OPTION>
<OPTION VALUE='NE'>NE</OPTION>
<OPTION VALUE='NH'>NH</OPTION>
<OPTION VALUE='NJ'>NJ</OPTION>
<OPTION VALUE='NM'>NM</OPTION>
<OPTION VALUE='NV'>NV</OPTION>
<OPTION VALUE='NY'>NY</OPTION>
<OPTION VALUE='OH'>OH</OPTION>
<OPTION VALUE='OK'>OK</OPTION>
<OPTION VALUE='OR'>OR</OPTION>
<OPTION VALUE='PA'>PA</OPTION>
<OPTION VALUE='RI'>RI</OPTION>
<OPTION VALUE='SC'>SC</OPTION>
<OPTION VALUE='SD'>SD</OPTION>
<OPTION VALUE='TN'>TN</OPTION>
<OPTION VALUE='TX'>TX</OPTION>
<OPTION VALUE='UT'>UT</OPTION>
<OPTION VALUE='VT'>VT</OPTION>
<OPTION VALUE='VA'>VA</OPTION>
<OPTION VALUE='WA'>WA</OPTION>
<OPTION VALUE='WI'>WI</OPTION>
<OPTION VALUE='WV'>WV</OPTION>
<OPTION VALUE='WY'>WY</OPTION>
</SELECT></td></tr>
<tr><td width="50%"><p align="right">Zip Code:&nbsp; </td><td><input class="PHP_form" type="text" name="zip_code" size="12"></td></tr>
<tr><td width="50%"><p align="right">Phone Number:&nbsp; </td><td><input class="PHP_form" type="text" name="phone" size="15"></td></tr>
<tr><td width="50%" colspan="2"><p align="center"><input class="PHP_butt" type="submit" value="join" name="B1"><input class="PHP_butt" type="reset" value="clear" name="B2"></form></p></td></tr>

<tr><form method="POST" action="<? echo $_SERVER[PHP_SELF] ?>"><input type="hidden" name="action" value="delete">
<td colspan="2" align="center"><br><span><? echo "$deleted"; ?></span><br><br><span>Enter email address to be removed:</span><br>
<input class="PHP_form" type="text" value="" name="email" size="20"><br><input class="PHP_form" type="submit" value="remove" name="button"></td></form></tr></table>
</body></html>
<?php
}
?>