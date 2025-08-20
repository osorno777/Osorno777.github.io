<?
define ('news_ok_IN',true);
include("../globals.inc.php");
if (!$list_conn = mysql_connect("$news_server", "$news_user", "$news_pass")){
die  ("<br><br><br><br>The database is down. Try back later.");
}
mysql_select_db($news_db);
if($_POST['action'] == "send"){
set_time_limit(1500);
$list_query = "SELECT f_name, l_name, email FROM PHPlist";
if ($list_result = mysql_query($list_query)){
if (!get_magic_quotes_gpc()){
$news_body = stripslashes ($_POST['news_body']);
$news_subject = stripslashes ($_POST['news_subject']);
}
$news_body = htmlspecialchars($news_body);
$news_body = strip_tags($news_body);
$news_body = trim($news_body);
$news_subject = htmlspecialchars($news_subject);
$news_subject = strip_tags($news_subject);
$news_subject = trim($news_subject);
while ($row = mysql_fetch_object($list_result)){
$count++;
$f_name = trim($row->f_name);
$l_name = trim($row->l_name);
if ($f_name == ""){
$greeting = "Hello,";
}
else
{
$greeting = "Hello $f_name,";
}
$email = trim($row->email);
print "$email<BR>";
mail("$email","$_POST[news_subject]","$greeting
$news_body

$news_close
","From:Policy of Liberty<$PHPlist_from_address>");
}
}
else{
die ("I was unable to get names and email addresses!");
}
}////end of the send function
if ($_POST['action'] == "edit"){
$list_query = "SELECT email FROM PHPlist WHERE (email = '$email')";
if ($list_result = mysql_query($list_query)){
$list_number=mysql_num_rows($list_result);
if ($_POST['edit'] == "add"){
if (!$list_number){
$list_query = "INSERT INTO PHPlist (email) VALUES ('$email')";
if ($list_result = mysql_query($list_query)){
print "successful!";
}else{
die ("I can't insert to the DB.<br><br>$list_query");
}
}else{
die ("<br><br><br><br>That email address is in use.");
}
}else{
$list_query = "DELETE FROM PHPlist WHERE (email = '$email')";
if ($list_result = mysql_query($list_query)){
print "<p align=\"center\">successfully deleted</span>";
}else{
print "The query failed to remove email addresses programatically";
}
}
}else{
mysql_close($list_conn);
die ("<br><br><br><br>The database is down, try back in a few minutes.");
}
}////closing the edit function
$list_query = "SELECT ID FROM PHPlist";
if ($list_result = mysql_query($list_query)){
$sub_num=mysql_num_rows($list_result);
if ($sub_num == ""){
$sub_num = "no";
}
}else{
mysql_close($list_conn);
die ("<br><br><br><br>The database is down, try back in a few.");
}
?>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<html><head><title><?php echo "$newsletter_title"?> Administration Page</title>
<link rel="stylesheet" href="<?php echo "../$css_file"?>"></head>
<body>
<?
if($_POST['action'] != "send"){
?>
<table align="center" border="1" cellpadding="0" cellspacing="0" width="550">
<tr><form method="POST" action="<? echo $_SERVER['PHP_SELF'] ?>"><input type="hidden" value="send" name="action">
<td align="center"><span align="center">You currently have <?php echo "$sub_num" ?> subscribers to your newsletter.</span><br><br></td></tr>
<tr><td align="center"><span align="center">Type the Title of the newsletter here:</span><br>
<span align="center"><input class="PHP_form" type="text" name="news_subject" size="30"></span></td></tr>
<tr><td align="center"><span align="center">Type your newsletter here:<br>(This can be HTML or plain text.)</span><br>
<span><textarea class="PHP_form" rows="17" name="news_body" cols="66"></textarea></span></td></tr>
<tr><td align="center"><input class="PHP_butt" type="submit" value="Send Newsletter" name="B1"><input class="PHP_butt" type="reset" value="Clear" name="B2"></td></form></tr></table>
<?}else{?>
<table align="center" border="1" cellpadding="0" cellspacing="0" width="550">
<tr><td><span align="center">Here is what you just sent your <? echo "$count" ?> members:</span><br><p align="left"><? echo nl2br($news_body) ?></p></td></tr></table>
<?}?>
<br><br>
<?
///if($_POST['action'] != "edit"){
?>
<table align="center" border="1" cellpadding="0" cellspacing="0" width="550">
<tr><form method="POST" action="<? echo $_SERVER['PHP_SELF'] ?>"><input type="hidden" value="edit" name="action">
<td align="center"><span align="center">You have removed this address: </span><span align="center"><input class="PHP_form" value="<?php echo $_POST['email'] ?>" type="text" name="subject" size="30"></span></td></tr>
<tr><td align="center"><span align="center">To manually add or remove an account, enter their email address here:</span><br>
<span align="center"><input class="PHP_form" type="text" name="email" size="30"></span></td></tr>
<tr><td align="center"><span align="center"><input type="radio" name="edit" value="add">add&nbsp;&nbsp;&nbsp;&nbsp;<input type="radio" name="edit" value="delete">remove</span></td></tr>
<tr><td align="center"><input class="PHP_butt" type="submit" value="Add/Remove Email from PHPlist" name="B1"></td></form></tr></table>
</body></html>