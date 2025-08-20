<?if ( !defined('wwwf_IN') ){die ("LAMER!!!!, you have been mangled.<br>
$HTTP_USER_AGENT<br>
$REMOTE_ADDR");}
define ('wwwf_IN',true);?>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<HTML><HEAD>
<TITLE><?echo "$title"?></TITLE>
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=iso-8859-1">
<meta name="description" content="<?echo "$desc"?>">
<meta name="keywords" content="<?echo "$key"?>">
<META NAME="GOOGLEBOT" CONTENT="INDEX, FOLLOW">
<META NAME="ROBOTS" CONTENT="INDEX, FOLLOW">
<meta name="author" content="Nick Mask">
<link rel="stylesheet" type="text/css" href="externals/pstyle.css">
<noscript><IMG src="http://www.housingmedia.com/tracking/pphlogger.php?id=eric&st=img"></noscript>
<SCRIPT LANGUAGE="JavaScript">
<!--
function newImage(arg) {
	if (document.images) {
		rslt = new Image();
		rslt.src = arg;
		return rslt;
	}
}
function changeImages() {
	if (document.images && (preloadFlag == true)) {
		for (var i=0; i<changeImages.arguments.length; i+=2) {
			document[changeImages.arguments[i]].src = changeImages.arguments[i+1];
		}
	}
}
var preloadFlag = false;
function preloadImages() {
	if (document.images) {
		engnav1_over = newImage("images/engnav1.gif");
		freenav1_over = newImage("images/freenav1.gif");
		booksnav1_over = newImage("images/booksnav1.gif");
		papersnav1_over = newImage("images/papersnav1.gif");
		linksnav1_over = newImage("images/linksnav1.gif");
		quotesnav1_over = newImage("images/quotesnav1.gif");
		contactnav1_over = newImage("images/contactnav1.gif");
		joinnav1_over = newImage("images/joinnav1.gif");
		aboutnav1_over = newImage("images/aboutnav1.gif");
		preloadFlag = true;
	}
}
-->
</SCRIPT>
<!-- End Preload Script -->
</HEAD>
<BODY BGCOLOR="#ffffff" leftmargin="0" topmargin="0" marginwidth="0" marginheight="0" ONLOAD="preloadImages();">
<table width="771" height="56" bgcolor="#ffffff" cellpadding="0" cellspacing="0" border="0">
<TR><td bgcolor="#009966" width="771" background="<?echo "$titleimg"?>" align="right" valign="top"><form method="POST" action="PHPlist/index.php"><input type="hidden" name="action" value="submit">
<input class="form" type="text" value="Join our newsletter!" onFocus="this.value=''" name="email" size="17">
<input class="form" type="submit" value="Join!" name="email">&nbsp;</form></td></TR></table>
<TABLE WIDTH="771" BORDER="0" CELLPADDING="0" CELLSPACING="0"><? include ("toproll.php")?></TABLE>
<!-- start page content -->
