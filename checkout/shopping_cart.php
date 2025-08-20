<?php 
session_start(); 
header("Cache-Control: no-store, no-cache, must-revalidate");  // HTTP/1.1 
///$priceEach = "5.95"; 
 foreach($HTTP_GET_VARS as $key => $value) {  
            $key = eregi_replace("[^0-9A-z_.]", "", $key); 
            $value = eregi_replace("[^0-9|.]", "", $value); 
            if($value == "0"){ 
            $value = ""; 
            } 
            ///print $key." - ".$value."<BR>"; 
            if(ereg("pol_", $key)){ /// don't set unnecessary cookies 
            setcookie("$key", "$value"); 
            } 
            if($value != "0" && $value != ""){ 
            $HTTP_COOKIE_VARS["$key"] = $value; 
            } 
    } 
    if($HTTP_GET_VARS){ 
header("Location: $_SERVER[PHP_SELF]");
die;
    }  
?>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<HTML><HEAD>
<TITLE>Policy of Liberty - Dr. John Cobin</TITLE>
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=iso-8859-1">
<meta name="description" content="Books/papers on free market economics and policy, pro-life policy, Cobin CV, links, photos, other resources, allodial title, fire safety regulation, building regulation, free market policy, drug legalization, abortion debate, etc...">
<meta name="keywords" content="allodial title, allodialism, allodial policy, free market textbook, homeschool books, economics books for homeschoolers, public policy and Christians, creation and evolution, Christian homeschool books, public policy books, pro-life books, abortion issue, Christians and government, building regulation, allodial title, tax protesting, revolution, fire safety regulation, accreditation of higher education, public choice economics, Virginia school, Austrian economics, law and economics, subjectivist economics, knowledge problem, market failure, government failure, urban regulation, fire safety regulation, romantic vision of government, public, choice, Austrian, economics, law, rent seeking, right, allodial, regulation, policy, vote, government, Bible, pro-life, Christian, building, zoning, liberty, planning, market, Chile, abortion debate, public school, Romans 13, feudal, privatization, allodial property">
<META NAME="GOOGLEBOT" CONTENT="INDEX, FOLLOW">
<META NAME="ROBOTS" CONTENT="INDEX, FOLLOW">
<meta name="author" content="Nick Mask">
<link rel="stylesheet" type="text/css" href="../externals/pstyle.css">
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
		engnav1_over = newImage("../images/engnav1.gif");
		freenav1_over = newImage("../images/freenav1.gif");
		booksnav1_over = newImage("../images/booksnav1.gif");
		papersnav1_over = newImage("../images/papersnav1.gif");
		linksnav1_over = newImage("../images/linksnav1.gif");
		quotesnav1_over = newImage("../images/quotesnav1.gif");
		contactnav1_over = newImage("../images/contactnav1.gif");
		joinnav1_over = newImage("../images/joinnav1.gif");
		aboutnav1_over = newImage("../images/aboutnav1.gif");
		preloadFlag = true;
	}
}
-->
</SCRIPT>
<!-- End Preload Script -->
</HEAD>
<BODY BGCOLOR="#ffffff" leftmargin="0" topmargin="0" marginwidth="0" marginheight="0" ONLOAD="preloadImages();">
<table width="771" height="56" bgcolor="#ffffff" cellpadding="0" cellspacing="0" border="0">
<TR><td bgcolor="#009966" width="771" background="../home.jpg" align="right" valign="top"><form method="POST" action="../PHPlist/index.php"><input type="hidden" name="action" value="submit">
<input class="form" type="text" value="Join our newsletter!" onFocus="this.value=''" name="email" size="17">
<input class="form" type="submit" value="Join!" name="email">&nbsp;</form></td></TR></table>
<TABLE WIDTH="771" BORDER="0" CELLPADDING="0" CELLSPACING="0"><tr><td><img src="../white.gif" height="2" width="48"></td>
<td><img src="../white.gif" height="2" width="144"></td>
<td><img src="../white.gif" height="2" width="136"></td>
<td><img src="../white.gif" height="2" width="120"></td>
<td><img src="../white.gif" height="2" width="44"></td>
<td><img src="../white.gif" height="2" width="58"></td>
<td><img src="../white.gif" height="2" width="62"></td>
<td><img src="../white.gif" height="2" width="41"></td>
<td><img src="../white.gif" height="2" width="73"></td>
<td><img src="../white.gif" height="2" width="45"></td></tr>
<tr><td bgcolor="ffffff"><A HREF="../index.php"><IMG alt="Policy of Liberty Home" NAME="engnav1" SRC="../images/engnav2.gif" height="21" BORDER="0"></A></TD>
<TD bgcolor="ffffff"><A HREF="../freemarket.php" ONMOUSEOVER="changeImages('freenav1', '../images/freenav2.gif'); return true;" ONMOUSEOUT="changeImages('freenav1', '../images/freenav1.gif'); return true;"><IMG alt="Free Market Textbook" NAME="freenav1" SRC="../images/freenav1.gif" height="21" BORDER="0"></A></TD>
<TD bgcolor="ffffff"><A HREF="../books.php" ONMOUSEOVER="changeImages('booksnav1', '../images/booksnav2.gif'); return true;" ONMOUSEOUT="changeImages('booksnav1', '../images/booksnav1.gif'); return true;"><IMG alt="Public Policy Books" NAME="booksnav1" SRC="../images/booksnav1.gif" height="21" BORDER="0"></A></TD>
<TD bgcolor="ffffff"><A HREF="../papers.php" ONMOUSEOVER="changeImages('papersnav1', '../images/papersnav2.gif'); return true;" ONMOUSEOUT="changeImages('papersnav1', '../images/papersnav1.gif'); return true;"><IMG alt="Articles and Papers" NAME="papersnav1" SRC="../images/papersnav1.gif" height="21" BORDER="0"></A></TD>
<TD bgcolor="ffffff"><A HREF="../links.php" ONMOUSEOVER="changeImages('linksnav1', '../images/linksnav2.gif'); return true;" ONMOUSEOUT="changeImages('linksnav1', '../images/linksnav1.gif'); return true;"><IMG alt="Links" NAME="linksnav1" SRC="../images/linksnav1.gif" height="21" BORDER="0"></A></TD>
<TD bgcolor="ffffff"><A HREF="../quotes.php" ONMOUSEOVER="changeImages('quotesnav1', '../images/quotesnav2.gif'); return true;" ONMOUSEOUT="changeImages('quotesnav1', '../images/quotesnav1.gif'); return true;"><IMG alt="Quotes" NAME="quotesnav1" SRC="../images/quotesnav1.gif" height="21" BORDER="0"></A></TD>
<TD bgcolor="ffffff"><A HREF="../contact.php" ONMOUSEOVER="changeImages('contactnav1', '../images/contactnav2.gif'); return true;" ONMOUSEOUT="changeImages('contactnav1', '../images/contactnav1.gif'); return true;"><IMG alt="Contact Policy of Liberty" NAME="contactnav1" SRC="../images/contactnav1.gif" height="21" BORDER="0"></A></TD>
<TD bgcolor="ffffff"><A HREF="../join.php" ONMOUSEOVER="changeImages('joinnav1', '../images/joinnav2.gif'); return true;" ONMOUSEOUT="changeImages('joinnav1', '../images/joinnav1.gif'); return true;"><IMG alt="Join Policy of Liberty" NAME="joinnav1" SRC="../images/joinnav1.gif" height="21" BORDER="0"></A></TD>
<TD bgcolor="ffffff"><A HREF="../about.php" ONMOUSEOVER="changeImages('aboutnav1', '../images/aboutnav2.gif'); return true;" ONMOUSEOUT="changeImages('aboutnav1', '../images/aboutnav1.gif'); return true;"><IMG alt="About Dr. John Cobin" NAME="aboutnav1" SRC="../images/aboutnav1.gif" height="21" BORDER="0"></A></TD>
<td><img src="../dkgreen.gif" height="21" width="45"></td></tr>
<tr><td colspan="10"><img src="../white.gif" height="2" width="771"></td></tr></TABLE>
<!-- start page content -->
<TABLE cellpadding="0" cellspacing="0" border="0" width="771" height="240">
<tr><td>
<!-- begin cart -->
<style type="text/css">
.recipebook1{
height: 20px;
width: 120px;
border: solid 1px;
border-color: #000000;
background: #ffffff url('../../images/inputback.gif');
font: 14px/16px "Calligraph421 BT", "Calligraph421 BT", "CAC Krazy Legs Bold", sans-serif;color: #000000;
}
.recipebook{
height: 35px;
width: 230px;
border: solid 1px;
border-color: #000000;
background: url('../../images/inputback.gif');
font-family:Verdana;
color:#000000;
}
.scart{
font-family:Verdana,Arial;
font-size:9pt;
}
</style>
<span style="font-family:Verdana,Arial;size:10pt;">
<form name="pol_cart" method="GET" action="shopping_cart.php" onSubmit="return concatit()">
  <table class="scart" align="center" border="0" width="560" cellspacing="0" cellpadding="0">
    <tr>
      <td align="center" width="74" bgcolor="#CCCCCC"><b>Remove</b></td>
      <td align="center" width="67" bgcolor="#CCCCCC"><b>Qty.</b></td>
      <td align="center" width="205" bgcolor="#CCCCCC"><b>Description</b></td>
      <td align="center" width="105" bgcolor="#CCCCCC"><b>Price ea.</b></td>
      <td align="center" width="99" bgcolor="#CCCCCC"><b>Subtotal</b></td>
    </tr>
<?php
while(list($key,$value) = each($HTTP_COOKIE_VARS)) {  
        if(ereg("pol_", $key)){ 
            $polcount++;
$keyJava = $key;
$key = str_replace("pol_", "", $key);
$key = str_replace("_", " ", $key);
///print $value."<hr>";
$array = explode("|", $value);
$value = $array[0];
$priceEach = $array[1];
$shippingEach = $array[2];
$shipping += $value*$shippingEach;
            $total += $value*$priceEach;
$items += $value;  
$javascript .= "if(document.pol_cart.$keyJava.value != \"0\"){\ndocument.pol_cart.$keyJava.value = document.pol_cart.$keyJava.value+'|$priceEach|$shippingEach'\n}\n";
?> 
    <tr>
      <td width="74" bgcolor="#FFFFCC" align="center">&nbsp;<input type="checkbox" name="remove" value="yes" onCLick="document.pol_cart.<?php echo $keyJava ?>.value='0'"></td>
      <td width="67" bgcolor="#FFFFCC" align="center"><input type="text" name="<?php echo $keyJava ?>" value="<?php echo $value ?>" size="2" maxlength="4"></td>
      <td width="205" bgcolor="#FFFFCC" align="center"><?php
if($shippingEach > "0"){
$extension = "";
$extension1 = substr($key, -4, 4);
$extension2 = substr($key, -5, 5);
///print "$extension1 & $extension2<hr>";
if($extension1 == " pdf" || $extension1 == " htm" || $extension1 == " doc" || $extension1 == " PDF" || $extension1 == " HTM" || $extension1 == " DOC"){
$key = str_replace("$extension1", "", $key);
}elseif($extension2 == " html" || $extension2 == " HTML"){
///$extension = str_replace(" ", ".", $extension);
$key = str_replace("$extension2", "", $key);
}
	}else{
$extension = "";
$extension1 = substr($key, -4, 4);
$extension2 = substr($key, -5, 5);
///print "$extension1 & $extension2<hr>";
if($extension1 == " pdf" || $extension1 == " htm" || $extension1 == " doc" || $extension1 == " PDF" || $extension1 == " HTM" || $extension1 == " DOC"){
$extension = str_replace(" ", ".", $extension1);
$key = str_replace("$extension1", "$extension", $key);
}elseif($extension2 == " html" || $extension2 == " HTML"){
$extension = str_replace(" ", ".", $extension2);
$key = str_replace("$extension2", "$extension", $key);
}
}	  
	  echo $key ?></td>
      <td width="105" bgcolor="#FFFFCC" align="center">$<?php echo $priceEach ?></td>
      <td width="99" bgcolor="#FFFFCC" align="center">$<?php echo number_format($value*$priceEach, 2) ?></td>
    </tr>
<?php
        } 
    } /// end while loop

    if($polcount <= "0"){ 
print "<center><font color=\"#FF0000\">There is nothing in your shopping cart.</font></center>"; 
    }else{ 
///print "<BR><BR>Total is ".number_format($total, 2).".<hr>"; 
    }
?>
  </table>
<script language="Javascript">
function concatit(){
<?php echo $javascript ?>
return true;
}
</script>
  <table align="center" border="0" width="560" cellspacing="0" cellpadding="0">
        <tr>
      <td width="318" align="center">&nbsp;</td>
      <td width="133" align="center">&nbsp;</td>
      <td width="99" align="center">&nbsp;</td>
    </tr>
    <tr>
      <td width="318" align="center" rowspan="2"><input class="recipebook1" type="submit" name="button" value="Update Cart"><BR><font size="2"><a href="products.php"><<< Continue Shopping</a></font></td>
      <td width="133" align="right">Shipping: </td>
      <td width="99" align="center">$<?php echo number_format($shipping, 2) ?></td>
    </tr>
    <tr>
      <td width="133" align="right">Grand Total: </td>
      <td width="99" align="center"><b>$<?php echo number_format($total+$shipping, 2) ?></b></td>
    </tr>
  </table>
  </form>
<?php
if($items > 0){
?>
  <form method="POST" action="https://www.policyofliberty.net/checkout/checkout.php">
<input type="hidden" value="<?php echo $shipping ?>" name="shipping">
<input type="hidden" value="<?php echo $total+$shipping ?>" name="total">
<input type="hidden" value="<?php echo $tax ?>" name="tax">
<input type="hidden" value="Recipe Book" name="prodDescription">
<BR><BR><center><input type="submit" class="recipebook" name="button" value="Proceed to Checkout Page >>>"></center>
  </form>
<?php
}
print urldecode("+");
?>
</span>
<!-- end cart -->
</td></tr></TABLE>
<table cellpadding="0" cellspacing="0" width="771" border="0"><tr><TD bgcolor="#ffffff" colspan="4"><IMG height="3" alt="Policy of Liberty is your source for books/papers on free market economics and pro-life policy as well as quotes and links to economic related issues" align="center" src="../white.gif" width="771" border="0"></TD></tr>
<TR><TD bgcolor="#99cc99"><IMG height="20" alt="Policy of Liberty is your source for books/papers on free market economics and pro-life policy as well as quotes and links to economic related issues" src="../end.gif" width="360" border="0" align="center"></TD><TD bgcolor="#99cc99"><IMG height="20" alt="Policy of Liberty is your source for books/papers on free market economics and pro-life policy as well as quotes and links to economic related issues" align="center" src="../backg.gif" width="27" border="0"></TD><TD bgcolor="#99cc99"><IMG height="20" alt="Policy of Liberty is your source for books/papers on free market economics and pro-life policy as well as quotes and links to economic related issues" align="center" src="../bottom.gif" width="318" border="0"></TD><td bgcolor="#99cc99"><A onmouseover="changeImages('indnav_01',	 '../images/indnav_01-over.gif'); return true;" onmouseout  ="changeImages('indnav_01', '../images/indnav_01.gif'); return true;" href="../sindex.html"><IMG height="20" alt="Policy of Liberty en Espanol" src="../images/indnav_01.gif" width="66" border="0" name="indnav_01" align="center"></A></td></TR>
<tr><TD bgcolor="#ffffff" colspan="4"><IMG height="3" alt="Policy of Liberty is your source for books/papers on free market economics and pro-life policy as well as quotes and links to economic related issues" align="center" src="../white.gif" width="771" border="0"></TD></tr>
<tr><TD bgcolor="#99cc99" colspan="4" height="15" width="771"><span class="foot">&nbsp;&nbsp;&nbsp;<a href="../index.php" class="foot" title="Policy of Liberty is you source for books/papers on free market economics and pro-life policy as well as quotes and links to economic related issues">home</a> &nbsp;|&nbsp; <a href="../freemarket.php" class="foot" title="Free Market Textbook">free market textbook</a> &nbsp;|&nbsp; <a href="../books.php" class="foot" title="Public Policy Books">public policy books</a> &nbsp;|&nbsp; <a href="../papers.php" class="foot" title="Articles and Papers">articles & papers</a> &nbsp;|&nbsp; <a href="../links.php" class="foot" title="Links">links</a> &nbsp;|&nbsp; <a href="../quotes.php" class="foot" title="Quotes">quotes</a> &nbsp;|&nbsp; <a href="../contact.php" class="foot" title="Contact Policy of Liberty">contact</a> &nbsp;|&nbsp; <a href="../join.php" class="foot" title="Join Policy of Liberty">join</a> &nbsp;|&nbsp; <a href="../about.php" class="foot" title="About Dr. John Cobin">about me</a></span></TD></tr></table><br></BODY></HTML>