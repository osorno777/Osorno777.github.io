<?php
error_reporting(0);
Header("Cache-Control: must-revalidate");  /// don't cache this page anytime

if($SERVER_PORT != "443"){
die("<b>Wrong Port.</b>"); /// Or some other smart remaRK.
}

$buttonName = "Process My Order";
////if(!$amount){$amount = "1.00";} /// debug disregard
if($_POST['action'] == "go"){
if($_SERVER['REQUEST_METHOD'] != "POST" || (!$HTTP_POST_VARS)){
die("<b>Illegal access attempt.</b>");
}


//////// begin filtering ///////
function attic($v1, $v2){
$filtered = trim($v1);
$filtered = strip_tags($filtered);
if($v2 == "email"){
$filtered = eregi_replace("[^0-9a-z.@_-]", "", $filtered);
}elseif($v2 == "textarea"){
$filtered = eregi_replace("[^0-9a-z.-@_' !?\"\$]", "", $filtered);
}elseif($v2 == "num"){
$filtered = eregi_replace("[^0-9]", "", $filtered);
}elseif($v2 == "amount"){
$filtered = eregi_replace("[^0-9.]", "", $filtered);
}else{
$filtered = eregi_replace("[^0-9a-z., #()-]", "", $filtered);
}

$filtered = htmlspecialchars("$filtered", ENT_QUOTES);
if(get_magic_quotes_gpc()){
$filtered = stripslashes($filtered);
}

return $filtered;
} /// end custom filter

$bfname = attic($bfname, "alpha");
$blname = attic($blname, "alpha");
$bsaddress = attic($bsaddress, "alpha");
$bcity = attic($bcity, "alpha");
$bstate = attic($bstate, "alpha");
$bzip = attic($bzip, "alpha");
$bcountry = attic($bcountry, "alpha");
$sfname = attic($sfname, "alpha");
$slname = attic($slname, "alpha");
$saddress = attic($saddress, "alpha");
$scity = attic($scity, "alpha");
$sstate = attic($sstate, "alpha");
$szip = attic($szip, "alpha");
$scountry = attic($scountry, "alpha");
$phone = attic($phone, "alpha");
$email = attic($email, "email");
$card_num = attic($card_num, "num");
$month = attic($month, "num");
$year = attic($year, "num");
$comments = attic($comments, "textarea");
$amount = attic($amount, "amount");
$cvv2 = attic($cvv2, "num");

///// end filtering  ////////
$today = date("F j, Y, g:i a");
$e = "$month/$year";
////// set AuthorizeNet post variables for DC method ///// 
$ordernumber = time();      /// an easy incremental way to assign an order number (seconds since the epoch)  
$version = "3.1"; 
$xlogin = "25686policy";  /// safely hidden from the public! Yeah!
$xpass = ""; /// keep it tight
$delimiter = "TRUE";     /// tell it to delimit the data 
$adcurl = "FALSE";       /// necessary for direct connect to be FALSE 
$xmethod = "CC";         /// Credit Card or Echeck 
$card = "$card_num";           /// ex. 422222222222222 
$expdate = "$e";           /// ex. 10/02 
$xamount = "$amount";     /// ex. 2.00 or 2 
$character = "|";         //// The pipe is the safest delimiter character 
$xtype = "AUTH_CAPTURE";  //// DEFAULT, use the VT for all other types 
$tr = "FALSE";             /// is it a test request? either TRUE or FALSE
if($cvv2){
$cv2 = "&x_Card_Code=$cvv2";           /// fraud control 3 digit number
}else{
$cv2 = "&x_Card_Code=$cvv2";
} 
///// end setting POST variables ///  
/////  url encode for the post //// 
//// although not necessary, these variables will be there for when you tighten up or loosen up requirements re: AVS 
$bfname = urlencode($bfname); 
$blname = urlencode($blname); 
$bsaddress = urlencode($bsaddress); 
$bcity = urlencode($bcity); 
$bzip = urlencode($bzip); 
$bphone = urlencode($bphone); 
//// end url encoding for the post ///  
///////// debug area to test filtering // ///////////////////
	////////////////////// /* uncomment below to debug */
/*
while(list($key, $val) = each($HTTP_POST_VARS)) {
$key = stripslashes($key);
$val = stripslashes($val);
$key = urlencode($key);
$val = urlencode($val);
$postString = "$key=$val<br>";
echo $postString;
  }
*/ ///die("19 Firstname: $bfname<BR>Last name: $blname<BR>Address: $bsaddress<BR>City: $bcity<BR>State: $bstate<BR>Zip: $bzip<BR>Country: $bcountry<BR>Ship Name: $sfname<BR>Ship Address: $saddress<BR>Ship City: $scity<BR>Ship State: $sstate<BR>Ship Zip: $szip<BR>Ship Country: $scountry<BR>Email: $email<BR>Phone: $phone<BR>Credit Card: $card_num<BR>Exp Month: $month<BR>Exp Year: $year<BR>Combined: $e<BR>Amount: $amount<BR>Comments: $comments<BR><BR>------------------------------------<BR><BR>"); 
///////////////////////////////////////// 
///////// end debug area  //////////////   
//////////////// Begin cURL engine //////////////////////////// 
/////////////////////////////////////////////////////////////// 
////////// The Heart of TRUE PHP E-Commerce! ////////////////// 
/////////////////////////////////////////////////////////////// 
$ch = curl_init();                                                                    /// initialize a cURL session 
curl_setopt ($ch, CURLOPT_URL,"https://secure.authorize.net/gateway/transact.dll");   /// set the cURL post URL 
curl_setopt ($ch, CURLOPT_HEADER, 0);                                                 /// Don't return the header in the response 
curl_setopt($ch, CURLOPT_POST, 1);                                                    /// Make it a POST, not a GET 
curl_setopt($ch, CURLOPT_POSTFIELDS, "x_Invoice_Num=$ordernumber&x_Test_Request=$tr&x_First_Name=$bfname&x_Last_Name=$blname&x_Address=$bsaddress&x_City=$bcity&x_Zip=$bzip&x_Phone=$phone&x_Version=$version&x_Login=$xlogin&x_Password=$xpass&x_ADC_Delim_Data=$delimiter&x_ADC_URL=$adcurl&x_method=$xmethod&x_type=$xtype&x_Card_Num=$card&x_Exp_Date=$expdate&x_Amount=$xamount&x_ADC_Delim_Character=$character$cv2");  /// Here is the POST string 
curl_setopt ($ch, CURLOPT_RETURNTRANSFER, 1);                                         /// Set the response into a variable 
$x = curl_exec ($ch);                                                                 /// Execute this session & set the variable from the response 
curl_close ($ch);                                                                     /// Close the cURL session 
///////////////////////////////////////////////////////////////// 
//////////////////////////////////////////////////////////////// 
////////////// End cURL engine /////////////////////////////////  
///////////// BEGIN url decode any data to be displayed /////// 
$bfname = urldecode($bfname); 
$blname = urldecode($blname); 
$bsaddress = urldecode($bsaddress); 
$bcity = urldecode($bcity); 
$bzip = urldecode($bzip); 
$phone = urldecode($phone); 
///////////  END url decode any data to be displayed  //////


} /// end if the form is submitted
?>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<HTML><HEAD>
<TITLE>Policy of Liberty - Dr. John Cobin</TITLE>
<link rel="stylesheet" type="text/css" href="../externals/pstyle.css">
<SCRIPT LANGUAGE="JavaScript">

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

function corpcard(){
document.ghost.blname.value = "   "
alert("If you are using a corporate card, just hit the space bar a couple of times in the \"Last Name\" field\n\nafter you have entered the name on your corporate card into the \"First Name\" field.");
}
function same(){
document.ghost.sfname.value = document.ghost.bfname.value
document.ghost.slname.value = document.ghost.blname.value
document.ghost.saddress.value = document.ghost.bsaddress.value
document.ghost.scity.value = document.ghost.bcity.value
document.ghost.sstate.value = document.ghost.bstate.value
document.ghost.szip.value = document.ghost.bzip.value
document.ghost.scountry.value = document.ghost.bcountry.value
}

function cvvs(){
window.open("cvv2.php", "CVV2", "scrollbars=yes,width=500,height=600,resizable=yes")
}

var ns6=document.getElementById&&!document.all?1:0
 
var head="display:''"
var folder=''

function expandit(curobj){
folder=ns6?curobj.nextSibling.nextSibling.style:document.all[curobj.sourceIndex+1].style
if (folder.display=="none"){
folder.display=""
}else{
folder.display="none"
}

}

function checkemail(){


			invalidChars = " /:,;\"<>~#$^&*()=+'"
	
			///if (document.ghost.email.value != "") {

			for (i=0; i<invalidChars.length; i++) {
				badChar = invalidChars.charAt(i)
				if (document.ghost.email.value.indexOf(badChar,0) > -1) {
					alert("An invalid character was detected in your E-Mail address")
					document.ghost.email.focus()
			       document.ghost.email.select()
					return false
				}
			}
			atPos = document.ghost.email.value.indexOf("@",1)
			if (atPos == -1) {
			   alert("A problem may have been found in your E-mail address (the '@' symbol), please double check it.")
				document.ghost.email.focus()
			   document.ghost.email.select()
				return false
			}
			if (document.ghost.email.value.indexOf("@",atPos+1) != -1) {
			   alert("Too many '@' symbols in the E-mail address!")
			   document.ghost.email.focus()
			   document.ghost.email.select()

				return false
			}
			periodPos = document.ghost.email.value.indexOf(".",atPos)
			if (periodPos == -1) {
				alert("There is a missing period after the '@' symbol, please re-check the address!")	
				document.ghost.email.focus()
			   document.ghost.email.select()
				return false
			}
			if (periodPos+3 > document.ghost.email.value.length)	{
			   alert("There is some information missing after the period of your E-mail address e.g. \".net\" or \".com\" or \".edu\" etc...")
			   document.ghost.email.focus()
			   document.ghost.email.select()

				return false
			}

     ///}
}

function checkform(){
proceed = "yes"
checkemail()

fix = "Some required missing information is missing...\n\n";
message = "";

if(document.ghost.bfname.value == ""){
message += "-- Billing First Name\n";
proceed = "no";
}
if(document.ghost.blname.value == ""){
message += "-- Billing Last Name\n";
proceed = "no";
}
if(document.ghost.bsaddress.value == ""){
message += "-- Billing Address\n";
proceed = "no";
}
if(document.ghost.bcity.value == ""){
message += "-- Billing City Info\n";
proceed = "no";
}
if(document.ghost.bstate.value == ""){
message += "-- Billing State Info\n";
proceed = "no";
}
if(document.ghost.bzip.value == ""){
message += "-- Billing Zip Code\n";
proceed = "no";
}
if(document.ghost.phone.value == ""){
message += "-- Phone Number\n";
proceed = "no";
}
if(document.ghost.card_num.value == ""){
message += "-- Credit Card Number\n";
proceed = "no";
}
if(document.ghost.month.value == "" || document.ghost.month.value == "99"){
message += "-- Card Expiration Month\n";
proceed = "no";
}
if(document.ghost.year.value == "" || document.ghost.year.value == "99"){
message += "-- Card Expiration Year\n";
proceed = "no";
}


if(proceed == "no"){
alert(fix+message);
return false;
}


b1.style.cursor='wait'
document.ghost.submit_button.disabled=true
}

//-->
</script>
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
<!-- begin main content area -->

<?php
if($_POST['action'] != "go"){

?>
<form name="ghost" method="post" action="checkout.php" onSubmit="return checkform()">

  <table border="0" width="566" cellspacing="0" cellpadding="0" align="center">
    <tr>
      <td width="284"><font face="Verdana" size="2"><b>Billing Information</b></font></td>
      <td width="282"><font face="Verdana" size="1" color="#FF0000">** </font><font face="Verdana" size="1"><i>Required
        fields</i></font></td>
    </tr>
    <tr>
      <td width="564" colspan="2">
      <table border="1" cellpadding="0" cellspacing="0" class="bordercolor" width="539"><tr><td width="535">
  <table border="0" width="535" bgcolor="#CCCC99" cellspacing="0" cellpadding="0">
    <tr>
      <td width="124"><font face="Verdana" size="1" color="#FF0000">**</font><font size="2" face="Verdana">First Name <b>or</b><BR><font size="1">(<a href="javascript: corpcard()"><font color="#0000FF">Corp. Card Name</font></a>)</font></font></td>
      <td width="240"><input class="<?php echo $checkout ?>" type="text" name="bfname" size="20" maxlength="50"><font face="Verdana" size="1">cardholder's</font></td>
      <td width="199" rowspan="6" align="center"><font face="Arial"> <a href="javascript: void(thewindow = window.open('https://www.thawte.com/cgi/server/certdetails.exe?code=USPOLI22', 'validate', config='height=400,width=450,toolbar=no,menubar=no,scrollbars=yes,resizable=no,location=no,directories=no,status=yes'))"><img alt="Click to verify Policy Of Liberty" src="stampcrp.gif" border="0" width="134" height="85"></a></font></td><input type="hidden" name="action" value="go"><input type="hidden" name="amount" value="<?php echo $_POST['total'] ?>"><input type="hidden" name="shipping" value="<?php echo $_POST['shipping'] ?>">
    </tr>
    <tr>
      <td width="124"><font face="Verdana" size="1" color="#FF0000">**</font><font size="2" face="Verdana">Last Name:</font></td>
      <td width="240"><input class="<?php echo $checkout ?>" type="text" name="blname" size="20" maxlength="50"><font face="Verdana" size="1">cardholder's</font></td>
    </tr>
    <tr>
      <td width="124"><font face="Verdana" size="1" color="#FF0000">**</font><font size="2" face="Verdana">Billing Address:</font></td>
      <td width="240"><input class="<?php echo $checkout ?>" type="text" name="bsaddress" size="20" maxlength="60"></td>
    </tr>
    <tr>
      <td width="124"><font face="Verdana" size="1" color="#FF0000">**</font><font size="2" face="Verdana">City:</font></td>
      <td width="240"><input class="<?php echo $checkout ?>" type="text" name="bcity" size="20" maxlength="40"></td>
    </tr>
    <tr>
      <td width="124"><font face="Verdana" size="1" color="#FF0000">**</font><font size="2" face="Verdana">State:</font></td>
      <td width="240"><select class="<?php echo $checkout ?>" size="1" name="bstate">
          <option value="99" selected>Choose...</option>
          <option value="AK">AK</option>
          <option value="AL">AL</option>
          <option value="AR">AR</option>
          <option value="AS">AS</option>
          <option value="AZ">AZ</option>
          <option value="CA">CA</option>
          <option value="CO">CO</option>
          <option value="CT">CT</option>
          <option value="DC">DC</option>
          <option value="DE">DE</option>
          <option value="FL">FL</option>
          <option value="GA">GA</option>
          <option value="HI">HI</option>
          <option value="IA">IA</option>
          <option value="ID">ID</option>
          <option value="IL">IL</option>
          <option value="IN">IN</option>
          <option value="KS">KS</option>
          <option value="KY">KY</option>
          <option value="LA">LA</option>
          <option value="MA">MA</option>
          <option value="MD">MD</option>
          <option value="ME">ME</option>
          <option value="MI">MI</option>
          <option value="MN">MN</option>
          <option value="MO">MO</option>
          <option value="MS">MS</option>
          <option value="MT">MT</option>
          <option value="NC">NC</option>
          <option value="ND">ND</option>
          <option value="NE">NE</option>
          <option value="NH">NH</option>
          <option value="NJ">NJ</option>
          <option value="NM">NM</option>
          <option value="NV">NV</option>
          <option value="NY">NY</option>
          <option value="OH">OH</option>
          <option value="OK">OK</option>
          <option value="OR">OR</option>
          <option value="PA">PA</option>
          <option value="RI">RI</option>
          <option value="SC">SC</option>
          <option value="SD">SD</option>
          <option value="TN">TN</option>
          <option value="TX">TX</option>
          <option value="UT">UT</option>
          <option value="VT">VT</option>
          <option value="VA">VA</option>
          <option value="WA">WA</option>
          <option value="WI">WI</option>
          <option value="WV">WV</option>
          <option value="WY">WY</option>
        </select></td>
    </tr>
    <tr>
      <td width="124"><font face="Verdana" size="1" color="#FF0000">**</font><font size="2" face="Verdana">Zip:</font></td>
      <td width="240"><input class="<?php echo $checkout ?>" type="text" name="bzip" size="10" maxlength="12"></td>
    </tr>
    <tr>
      <td width="124"><font size="2" face="Verdana">Country:</font></td>
      <td width="440" colspan="2"><select class="<?php echo $checkout ?>" name="bcountry">
          <option value="AR">ARGENTINA*</option>
          <option value="AU">AUSTRALIA*</option>
          <option value="AT">AUSTRIA*</option>
          <option value="BS">BAHAMAS</option>
          <option value="BE">BELGIUM*</option>
          <option value="BR">BRAZIL*</option>
          <option value="CA">CANADA*</option>
          <option value="CL">CHILE</option>
          <option value="CR">COSTA RICA</option>
          <option value="DK">DENMARK*</option>
          <option value="DO">DOMINICAN REPUBLIC</option>
          <option value="FI">FINLAND*</option>
          <option value="FR">FRANCE*</option>
          <option value="DE">GERMANY*</option>
          <option value="GB">GREAT BRITAIN*</option>
          <option value="GR">GREECE*</option>
          <option value="GT">GUATEMALA</option>
          <option value="HK">HONG KONG</option>
          <option value="IL">ISRAEL*</option>
          <option value="IT">ITALY*</option>
          <option value="IE">REPUBLIC OF IRELAND</option>
          <option value="MY">MALAYSIA*</option>
          <option value="MX">MEXICO*</option>
          <option value="NL">NETHERLANDS*</option>
          <option value="NZ">NEW ZEALAND*</option>
          <option value="NO">NORWAY*</option>
          <option value="PA">PANAMA</option>
          <option value="PT">PORTUGAL*</option>
          <option value="PR">PUERTO RICO*</option>
          <option value="SG">SINGAPORE*</option>
          <option value="ES">SPAIN*</option>
          <option value="SE">SWEDEN*</option>
          <option value="CH">SWITZERLAND*</option>
          <option value="TW">TAIWAN*</option>
          <option value="TH">THAILAND*</option>
          <option value="US" selected>UNITED STATES*</option>
        </select></td>
    </tr>
  </table>
</td></tr></table>

      </td>
    </tr>
    <tr>
      <td width="282" align="right"><font face="Verdana" size="2"><b> <input type="checkbox" name="sameship" value="yes" onClick="same()"></b></font><font face="Verdana" size="2"><b>&nbsp;</b></font></td>
      <td width="280"><font face="Verdana" size="2"><b>Shipping Address the same?</b></font></td>
    </tr>
    <tr>
      <td width="564" colspan="2"><font face="Verdana" size="2"><b>Shipping Address</b> <i>(if applicable)</i></font></td>
    </tr>
    <tr>
      <td width="564" colspan="2">
      <table border="1" cellpadding="0" cellspacing="0" class="bordercolor" width="541"><tr><td width="537">
  <table border="0" width="537" bgcolor="#CCCC99" cellspacing="0" cellpadding="0">
    <tr>
      <td width="129"><font size="2" face="Verdana">First Name:</font></td>
      <td width="188">&nbsp;<input class="<?php echo $checkout ?>" type="text" name="sfname" size="20" maxlength="50"></td>
      <td width="248" rowspan="2" valign="bottom"><font face="Verdana" size="1" color="#FF0000">**</font><font face="Verdana" size="2">Phone:</font></td>
    </tr>
    <tr>
      <td width="129"><font size="2" face="Verdana">Last Name:</font></td>
      <td width="188">&nbsp;<input class="<?php echo $checkout ?>" type="text" name="slname" size="20" maxlength="50"></td>
    </tr>
    <tr>
      <td width="129"><font size="2" face="Verdana">Billing Address:</font></td>
      <td width="188">&nbsp;<input class="<?php echo $checkout ?>" type="text" name="saddress" size="20" maxlength="60"></td>
      <td width="248"><input class="<?php echo $checkout ?>" type="text" name="phone" size="20" maxlength="20"></td>
    </tr>
    <tr>
      <td width="129"><font size="2" face="Verdana">City:</font></td>
      <td width="188">&nbsp;<input class="<?php echo $checkout ?>" type="text" name="scity" size="20" maxlength="40"></td>
      <td width="248" valign="bottom"><font face="Verdana" size="1" color="#FF0000">**</font><font face="Verdana" size="2">Email:</font></td>
    </tr>
    <tr>
      <td width="129"><font size="2" face="Verdana">State:</font></td>
      <td width="188">&nbsp;<select class="<?php echo $checkout ?>" size="1" name="sstate">
          <option value="99" selected>Choose...</option>
          <option value="AK">AK</option>
          <option value="AL">AL</option>
          <option value="AR">AR</option>
          <option value="AS">AS</option>
          <option value="AZ">AZ</option>
          <option value="CA">CA</option>
          <option value="CO">CO</option>
          <option value="CT">CT</option>
          <option value="DC">DC</option>
          <option value="DE">DE</option>
          <option value="FL">FL</option>
          <option value="GA">GA</option>
          <option value="HI">HI</option>
          <option value="IA">IA</option>
          <option value="ID">ID</option>
          <option value="IL">IL</option>
          <option value="IN">IN</option>
          <option value="KS">KS</option>
          <option value="KY">KY</option>
          <option value="LA">LA</option>
          <option value="MA">MA</option>
          <option value="MD">MD</option>
          <option value="ME">ME</option>
          <option value="MI">MI</option>
          <option value="MN">MN</option>
          <option value="MO">MO</option>
          <option value="MS">MS</option>
          <option value="MT">MT</option>
          <option value="NC">NC</option>
          <option value="ND">ND</option>
          <option value="NE">NE</option>
          <option value="NH">NH</option>
          <option value="NJ">NJ</option>
          <option value="NM">NM</option>
          <option value="NV">NV</option>
          <option value="NY">NY</option>
          <option value="OH">OH</option>
          <option value="OK">OK</option>
          <option value="OR">OR</option>
          <option value="PA">PA</option>
          <option value="RI">RI</option>
          <option value="SC">SC</option>
          <option value="SD">SD</option>
          <option value="TN">TN</option>
          <option value="TX">TX</option>
          <option value="UT">UT</option>
          <option value="VT">VT</option>
          <option value="VA">VA</option>
          <option value="WA">WA</option>
          <option value="WI">WI</option>
          <option value="WV">WV</option>
          <option value="WY">WY</option>
        </select></td>
      <td width="248"><input class="<?php echo $checkout ?>" type="text" name="email" size="20" maxlength="70"></td>
    </tr>
    <tr>
      <td width="129"><font size="2" face="Verdana">Zip:</font></td>
      <td width="188">&nbsp;<input class="<?php echo $checkout ?>" type="text" name="szip" size="10" maxlength="12"></td>
      <td width="248" align="center">&nbsp;</td>
    </tr>
    <tr>
      <td width="129"><font size="2" face="Verdana">Country:</font></td>
      <td width="437" colspan="2">&nbsp;<select class="<?php echo $checkout ?>" name="scountry">
          <option value="AR">ARGENTINA*</option>
          <option value="AU">AUSTRALIA*</option>
          <option value="AT">AUSTRIA*</option>
          <option value="BS">BAHAMAS</option>
          <option value="BE">BELGIUM*</option>
          <option value="BR">BRAZIL*</option>
          <option value="CA">CANADA*</option>
          <option value="CL">CHILE</option>
          <option value="CR">COSTA RICA</option>
          <option value="DK">DENMARK*</option>
          <option value="DO">DOMINICAN REPUBLIC</option>
          <option value="FI">FINLAND*</option>
          <option value="FR">FRANCE*</option>
          <option value="DE">GERMANY*</option>
          <option value="GB">GREAT BRITAIN*</option>
          <option value="GR">GREECE*</option>
          <option value="GT">GUATEMALA</option>
          <option value="HK">HONG KONG</option>
          <option value="IL">ISRAEL*</option>
          <option value="IT">ITALY*</option>
          <option value="IE">REPUBLIC OF IRELAND</option>
          <option value="MY">MALAYSIA*</option>
          <option value="MX">MEXICO*</option>
          <option value="NL">NETHERLANDS*</option>
          <option value="NZ">NEW ZEALAND*</option>
          <option value="NO">NORWAY*</option>
          <option value="PA">PANAMA</option>
          <option value="PT">PORTUGAL*</option>
          <option value="PR">PUERTO RICO*</option>
          <option value="SG">SINGAPORE*</option>
          <option value="ES">SPAIN*</option>
          <option value="SE">SWEDEN*</option>
          <option value="CH">SWITZERLAND*</option>
          <option value="TW">TAIWAN*</option>
          <option value="TH">THAILAND*</option>
          <option value="US" selected>UNITED STATES*</option>
        </select></td>
    </tr>
  </table>
</td></tr>
</table>

      </td>
    </tr>
    <tr>
      <td nowrap width="282" valign="bottom"><font face="Verdana" size="2"><b>Credit Card Information</b></font></td>
      <td width="280"><img src="creditcards.gif" border="0" alt="We accept Visa, Mastercard, & Discover."></td>
    </tr>
    <tr>
      <td width="564" colspan="2">
      <table border="1" cellpadding="0" cellspacing="0"><tr><td>
  <table border="0" width="560" bgcolor="#CCCC99" height="151" cellspacing="0" cellpadding="0">
    <tr>
      <td width="115" align="left" height="24"><font face="Verdana" size="1" color="#FF0000">**</font><font size="2" face="Verdana">Card Number:</font></td>
      <td width="159" align="left" height="24"><font size="2"><input class="<?php echo $checkout ?>" type="text" name="card_num" size="20" maxlength="20" value=""></font></td>
      <td width="261" align="left" height="24"><font size="2" face="Verdana">Comments:</font></td>
    </tr>
    <tr>
      <td width="112" height="29"><font face="Verdana" size="1" color="#FF0000">**</font><font size="2" face="Verdana">Expire Month:</font></td>
      <td width="159" height="29"><font size="2">&nbsp;<select class="<?php echo $checkout ?>" size="1" name="month">
          <option selected value="99" selected>Choose...</option>
          <option value="01">(1)January</option>
          <option value="02">(2)February</option>
          <option value="03">(3)March</option>
          <option value="04">(4)April</option>
          <option value="05">(5)May</option>
          <option value="06">(6)June</option>
          <option value="07">(7)July</option>
          <option value="08">(8)August</option>
          <option value="09">(9)September</option>
          <option value="10">(10)October</option>
          <option value="11">(11)November</option>
          <option value="12">(12)December</option>
        </select></font></td>
      <td width="261" rowspan="4" height="119"><textarea class="<?php echo $checkout ?>" rows="7" name="comments" cols="30" maxlength="400"></textarea></td>
    </tr>
    <tr>
      <td width="112" height="29"><font face="Verdana" size="1" color="#FF0000">**</font><font size="2" face="Verdana">Expire Year:</font></td>
      <td width="159" height="29"><font size="2">&nbsp;<select class="<?php echo $checkout ?>" size="1" name="year">
          <option selected value="99" selected>Choose...</option>
          <option value="02">2002</option>
          <option value="03">2003</option>
          <option value="04">2004</option>
          <option value="05">2005</option>
          <option value="06">2006</option>
          <option value="07">2007</option>
          <option value="08">2008</option>
          <option value="09">2009</option>
          <option value="10">2010</option>
          <option value="11">2011</option>
          <option value="12">2012</option>
        </select></font></td>
    </tr>
    <tr>
      <td width="112" height="29"><font face="Verdana" size="1" color="#FF0000">**</font><font size="2" face="Verdana">3 Digit CVV2<br><b>or</b> 4 Digit CID</font></td>
      <td width="159" height="29"><font size="2"><input class="cvv" type="text" name="cvv2" size="3" maxlength="4"> 
        </font> 
        <a href="javascript: cvvs()"><font face="Verdana" size="1" color="#0000FF">Where
        is my CVV2?</font></a></td>
    </tr>
    <tr>
      <td width="112" height="20"><font face="Verdana" size="2">Total Charge:</font></td>
      <td width="159" height="20">
	  <b><font face="Verdana" size="2">&nbsp;<font color="#008000">$<?php echo $_POST['total'] ?></font></font></b></td>
    </tr>
  </table>
</td></tr></table>

      </td>
    </tr>
    <tr>
      <td colspan="2" align="right" width="564"><font face="Verdana" size="1"><i>
&nbsp;Orders will appear as Policy Of Liberty.</i></font></td>
    </tr>
    <tr>
      <td colspan="2" align="center" width="564"><input class="ordersubmit" type="submit" value="<?php echo $buttonName ?>" name="submit_button" onClick="expandit(this)"></td>
    </tr>
    <tr>
      <td colspan="2" align="center" width="564">&nbsp;
<span style="display:none" style=&{head};>
<BR><font color='#FF0000' size="1"><B><i>Please stand by...</i></b></font>
</span>
</td>
    </tr>
  </table>
  </form>
  <?php
}

if($action == "go"){
///	echo $x; 
	$adminemail = "jcobin@policyofliberty.net,rlawson@americashomeplace.com"; /// alertness@policyofliberty.net
	$result = explode("|", $x); /// seperate the result string from authorizeNet into an array 
	$date = (date ("m/d/Y")); 
	$time = (date ("h:i:s A")); 
	$reasoncode = $result[2];   /// code for the response 
	$reasontext = $result[3];  /// description of response 
	$approvalcode = $result[4];  /// six digit approval code 
	$avs = $result[5];           /// avs code
$cvv2result = $result[38]; /// CVV2 data

$cvv2result = trim($cvv2result);
if($cvv2result == "M"){
$cvv2result = "CVV2 Matched";
}elseif($cvv2result == "N"){
$cvv2result = "No CVV2 Match";
}elseif($cvv2result == "P"){
$cvv2result = "CVV2 Not Processed";
}elseif($cvv2result == "S"){
$cvv2result = "CVV2 Should Have Been Present";
}elseif($cvv2result == "U"){
$cvv2result = "Issuer unable to process CVV2 request";
}else{
$cvv2result = "No CVV2 response";
} 
////////// begin intrepting AVS 
if($avs == "A"){ 
$avs = "Address (Street) matches, ZIP does not"; 
}elseif($avs == "B"){ 
$avs = "Address information not provided for AVS check"; 
}elseif($avs == "E"){ 
$avs = "AVS error"; 
}elseif($avs == "G"){ 
$avs = "Non U.S. Card Issuing Bank"; 
}elseif($avs == "N"){ 
$avs = "No Match on Address (Street) or Zip"; 
}elseif($avs == "P"){ 
$avs = "AVS not applicable for this transaction"; 
}elseif($avs == "R"){ 
$avs = "Retry-System unavailable or timed out"; 
}elseif($avs == "S"){ 
$avs = "Service not supported by user"; 
}elseif($avs == "U"){ 
$avs = "Address information is unavailable"; 
}elseif($avs == "W"){ 
$avs = "9 Digit ZIP matches, Address (Street) does not"; 
}elseif($avs == "X"){ 
$avs = "Address (Street) and 9 Digit ZIP match"; 
}elseif($avs == "Y"){ 
$avs = "Address (Street) and 5 Digit ZIP match"; 
}elseif($avs == "Z"){ 
$avs = "5 Digit ZIP matches, Address (Street) does not"; 
}else{ $avs = "No response"; 
} 
////////// end interpreting AVS 
$transid = $result[6]; //// transaction id  
//////////////////////// begin if card was approved  /////////// 
if($result[0] == "1"){ 
?> 
<!-- begin approval html format -->  
<center><img src="approved.gif" border="0" alt="This transaction was approved."></center>
<br> <br><h4> Thank you <?php echo "$bfname $blname" ?>!<BR><br> 
Please print out a copy of this page for your records.<br>
<?php
if($email){
	print "An email has been sent to <a href=\"mailto:$email\"><font color='#0000ff'>$email</font></a>.<BR><BR>";
	}else{
		print "No email address was provided.<BR><BR>";}
?> Amount: <B>$<?php echo $amount ?></b><BR> Transaction ID: <b><?php echo $transid ?></b><BR> Order Number: <b><?php echo $ordernumber ?></b><br> Date/Time: <b><?php echo "$date $time" ?></b><br><BR><BR> <center>We appreciate you!</center> <!-- end approval html format --> 
<?php 
//////////// mail out a confirmation to the customer /////

/////// assemble the products  /////////

$product_assembly = strip_tags(htmlspecialchars($model1));

////// end product assembly  ////////////  
//// Some people customize their user agent with quotes and other data, so make it safe!  ////// 
if(!get_magic_quotes_gpc()){  
$os = addslashes($HTTP_USER_AGENT); 
}else{ 
$os = $HTTP_USER_AGENT; } 
///////////// end making user agent safe  //////////

////////// encrypt the card number or expire date /////////////

$key = "12";

function keyED($txt,$encrypt_key)
{
$encrypt_key = md5($encrypt_key);
$ctr=0;
$tmp = "";
for ($i=0;$i<strlen($txt);$i++)
{
if ($ctr==strlen($encrypt_key)) $ctr=0;
$tmp.= substr($txt,$i,1) ^ substr($encrypt_key,$ctr,1);
$ctr++;
}
return $tmp;
}
function encrypt($txt,$key)
{
srand((double)microtime()*1000000);
$encrypt_key = md5(rand(0,32000));
$ctr=0;
$tmp = "";
for ($i=0;$i<strlen($txt);$i++)
{
if ($ctr==strlen($encrypt_key)) $ctr=0;
$tmp.= substr($encrypt_key,$ctr,1) .
(substr($txt,$i,1) ^ substr($encrypt_key,$ctr,1));
$ctr++;
}
return keyED($tmp,$key);
}
function decrypt($txt,$key)
{
$txt = keyED($txt,$key);
$tmp = "";
for ($i=0;$i<strlen($txt);$i++)
{
$md5 = substr($txt,$i,1);
$i++;
$tmp.= (substr($txt,$i,1) ^ $md5);
}
return $tmp;
}
$key1 = "key1";
$key2 = "key2";
$key3 = "key3";
$encryptedcard = base64_encode(keyED(encrypt(keyED($card,$key1),$key2),$key3));
$encryptede = base64_encode(keyED(encrypt(keyED($e,$key1),$key2),$key3));

/////////// end card encryption /////////////
$parsedurl = parse_url($HTTP_SESSION_VARS["referurl"]); 
$rh = gethostbyaddr($REMOTE_ADDR);

////////// CART Assembly
$cs = mysql_connect("localhost", "c_policyof", "bfE31eBD");
mysql_select_db("c_policyof");
while(list($key,$value) = each($HTTP_COOKIE_VARS)) {  
        if(ereg("pol_", $key)){ 
$key = str_replace("pol_", "", $key);
$key = str_replace("_", " ", $key);

$array = explode("|", $value);
$value = $array[0];
$priceEach = $array[1];
$shippingEach = $array[2];



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



$keyDBName = $key;
$total += $value*$priceEach;
$items += $value; 
$product_assembly .= "($value) $key - $$priceEach ea.\n";

$query = "INSERT INTO orders (ID,fullName,Email,orderNumber,Products,Date) VALUES ('', '$bfname $blname', '$email', '$ordernumber', '$keyDBName', '".time()."')";

if($result = mysql_query($query, $cs)){
/// nothing
}else{
$error .= mysql_error($cs)."\n";
$queryE .= addslashes($query)."\n";
$errorOccured = "yes";
}


 }
}
mysql_close($cs);

if($errorOccured == "yes"){
print "<BR><center><b>There was an error storing your shopping cart contents into the database. John Cobin has been notified and he will send you a download link via email if you supplied an email address. If not, please contact him at <a href=\"mailto:jcobin@policyofliberty.net\">jcobin@policyofliberty.net</a>. Please excuse this inconvenience. Thanks!</b></center>";
mail("$adminemail", "Cart Contents DB Storage Error", "
John,
	The following problems were reported while trying to store the contents of the shopping cart.

----	Errors -----
$error
----------------
---- SQL Query -----
$queryE
-------------------
 Name: $bfname $blname
 Address: $bsaddress
 City: $bcity
 State: $bstate
 Zip: $bzip
 Country: $bcountry
  Phone: $phone
 E-Mail: $email
----------------
       Charge Amount: $$amount
            Shipping: $_POST[shipping]
	Order Number: $ordernumber 
      Transaction ID: $transid
           Date/Time: $date $time
", "From:Policy of Liberty System<noreply@policyofliberty.net>");
}
$cs = mysql_connect("localhost", "c_policyof", "bfE31eBD");
mysql_select_db("c_policyof");
print "<script>
function downloadit(x){
	///alert(x);
	if(x){
window.open('download.php?action=&command='+x+'&on=".$ordernumber."', 'downloads', 'width=300,height=100,resizable=yes');
}else{
alert('Choose a product to download first.');
}
}
</script>
<select name=\"product_download\" size=\"1\" onChange=\"downloadit(this.value)\">\n<option value=\"\">Select a product to download...</option>\n";
$query = "SELECT o.ID, o.Products, p.password FROM orders o, products p WHERE(o.orderNumber = '$ordernumber' AND o.Products = p.product_name AND p.downloadable = 'Y')";
$result = mysql_query($query, $cs);
while($row = mysql_fetch_array($result)){
print "<option value=\"$row[ID]\">$row[Products] - password= $row[password]</option>\n";
$password_assembly .= "$row[Products] - password= '$row[password]'\n";
}
mysql_close($cs);
print "</select>";
///////// END Cart Assembly

 if($email){
mail("$email", "Order confirmation #$ordernumber", "Hello $bfname $blname, 	
Thank you for your order. If you need to make changes to your
order, please send an email to customerservice@policyofliberty.net.

       Charge Amount: $$amount
            Shipping: $_POST[shipping]
	Order Number: $ordernumber 
      Transaction ID: $transid
           Date/Time: $date $time
To re-download your products within the next 3 days,
visit this url and enter your oder number:
http://www.policyofliberty.net/checkout/download.php
-------- Order Contents -------
$product_assembly ------------------------------- 
$password_assembly
----------------------------------------
IP Address: $REMOTE_ADDR 
Operating System: $os
ISP Gateway: $rh  
", "From:Policy Of Liberty<customerservice@policyofliberty.net>");
}  
/////////// end a mailout to customer and begin mailout to the admin //// 
mail("$adminemail", "Order #$ordernumber", "Hello,
 	Order details below...
              Amount: $amount
           Shipping: $_POST[shipping]
Authorization Code: $approvalcode
       Order Number: $ordernumber
     Transaction ID: $transid
          Date/Time: $date $time
                AVS: $avs
              CVV2: $cvv2result

 -------Billing Data ---------
 Name: $bfname $blname
 Address: $bsaddress
 City: $bcity
 State: $bstate
 Zip: $bzip
 Country: $bcountry
  Phone: $phone
 E-Mail: $email
 --------------- 
------ Order Contents -----
$product_assembly ---------------------------

 ------ Shipping Data ------
 Ship Name: $sfname $slname
 Address: $saddress
 City: $scity
 State: $sstate
 Zip: $szip
 Country: $scountry
 ----------------
  Comments: $comments
  IP Address: $REMOTE_ADDR
 Operating System: $os
ISP Gateway: $rh  ", "From:Policy Of Liberty<customerservice@policyofliberty.net>");
 //////////// end sending emails  ///////    
}
 /// end if the response was approved ///////////////////
/////////////////////  end if card was approved /////////
///////////////////////// begin if card was declined  ///////// 
if($result[0] == "2"){ 
$reasoncode = trim($reasoncode); 
if($reasoncode == "2"|| $reasoncode == "3"){ 
$note = " - This was a general card decline";
}

if(!get_magic_quotes_gpc()){  
$os = addslashes($HTTP_USER_AGENT); 
}else{ 
$os = $HTTP_USER_AGENT;
} 
$rh = gethostbyaddr($REMOTE_ADDR);
 ////////////  Begin email handling of more severe responses  /////// 
switch($reasoncode){ 
case 4: 
$notice = "NOTE: This card may have been reported lost or stolen."; 
mail("$adminemail", "Possible stolen card", " 
A card was used, and AuthorizeNet returned a '4' reason code suggesting to pick up the card if possible.  
Customer name was $bfname $blname 
Phone number: $phone 
E-Mail: $email

CardNUm: $card - $month/$year
CVV2: $cvv2result
AVS: $avs

IP: $REMOTE_ADDR
OS: $os
ISP Gateway: $rh  ", "From:Policy Of Liberty Fraud Detection<customerservice@policyofliberty.net>"); 
BREAK; 
case 41: 
$notice = "NOTE: Fraud score limit exceeded as configured by Policy Of Liberty"; 
mail("$adminemail", "High Fraud Score", " 
A reason code of $reasoncode was returned. 
This means that the fraud score returned was higher than what Policy Of Liberty has set in the control panel.  
Customer name was $bfname $blname 
Phone number: $phone 
E-Mail: $email
CVV2: $cvv2result
AVS: $avs
Amount: $amount
IP: $REMOTE_ADDR
OS: $os
ISP Gateway: $rh  ", "From:Policy Of Liberty Fraud Score<customerservice@policyofliberty.net>"); 
BREAK;
default: 
mail("$adminemail", "General Card Decline", " 
This card was declined.  
Customer name was $bfname $blname 
Phone number: $phone 
E-Mail: $email
CVV2: $cvv2result
AVS: $avs
Amount: $amount

IP: $REMOTE_ADDR
OS: $os
ISP Gateway: $rh  ", "From:Policy Of Liberty Checkout Monitor<customerservice@policyofliberty.net>"); 
BREAK;
}
 /// end switch statement ///////
//////  end email handling of more sever responses  //////// 
?> <center><h3>Declined</h3></center><BR><BR> I'm sorry, but your card was declined. 
<br> The below data may help you determine why the card was 
declined, and correct it: <br>
<BR> Reason: <b><?php echo "$reasontext $note" ?></b><br>
 Address verification: <b><?php echo $avs ?></b><br>
CVV2 Response: <b><?php echo $cvv2result ?></b><BR><BR>
You entered:<br> Cardholder's First Name: <B><?php echo $bfname ?></b><BR>
 Cardholder's Last Name: <B><?php echo $blname ?></b><BR>
 Cardholder's Billing Address: <B><?php echo $bsaddress ?></b><BR> 
Cardholder's City: <B><?php echo $bcity ?></b><BR> 
Cardholder's State: <B><?php echo $bstate ?></b><BR> 
Cardholder's Zip: <B><?php echo $bzip ?></b><BR>  
Expires: <b><?php echo "$month/$year" ?></b><BR> <br> 
<font color="#FF0000"><?php echo $notice ?></font> <BR>
<BR> You may hit your back button and retry the same card, or try a different card.  
<?php
	 }
		  /// end if the card was declined ////////////////
			///////////////////  end if card was declined  //////////     
			////////////////////// begin if there was an error from AuthorizeNet /////// 
if($result[0] == "3"){

if(!get_magic_quotes_gpc()){  
$os = addslashes($HTTP_USER_AGENT); 
}else{ 
$os = $HTTP_USER_AGENT;
} 
$rh = gethostbyaddr($REMOTE_ADDR);
	 $reasoncode = trim($reasoncode); 
	switch($reasoncode){ 
	case 11: 
	$notice = "NOTE: Duplicate transaction detected, please try again in 2 minutes."; 
	BREAK; 
	case 14: 
	$notice = "NOTE: Invalid Referer URL - Policy Of Liberty has been notified"; 
	mail("$adminemail", "Invalid referring URL", " 
	A list of valid referring urls has been configured and 
	a transaction was placed, and the referrer did not match any.  
	An error code of 3 was reurned from Authorize.Net.  
	This is an automated email notifying you. 
	This is a general processing error and the card was neither approved or denied.  
	Customer name was $bfname $blname 
	Phone number: $phone 
	E-Mail: $email 
	CVV2: $cvv2result
AVS: $avs

IP: $REMOTE_ADDR
OS: $os
ISP Gateway: $rh
 Please contact this customer to see if they were able to complete the transaction.  ", "From:Policy Of Liberty<customerservice@policyofliberty.net>"); 
BREAK; 
case 19: 
case 20: 
case 21: 
case 22: 
case 23: 
case 25: 
case 35: 
$notice = "NOTE: This error occured from our credit card gateway provider. We apologize for the inconvenience. Policy Of Liberty has been notified. Please try again in 5 minutes."; 
mail("$adminemail", "AuthorizeNet Processing error", " 
A reason code of $reasoncode was reurned. This is a general
processing error of an attempted transaction from AuthorizeNet.  
An error code of 3 was reurned from Authorize.Net.  
This is an automated email notifying you. This is a 
general processing error and the card was neither approved or denied.  

Customer name was $bfname $blname 
Phone number: $phone 
E-Mail: $email 
CVV2: $cvv2result
AVS: $avs

IP: $REMOTE_ADDR
OS: $os
ISP Gateway: $rh
 Please contact this customer to see if they were able to complete the transaction.   ",
	"From:Policy Of Liberty<customerservice@policyofliberty.net>"); 
BREAK; 
case 26: 
$notice = "NOTE: This error occured from our credit card gateway provider. We apologize for the inconvenience. Policy Of Liberty has been notified. Please try again in 5 minutes."; 
mail("$adminemail", "AuthorizeNet Processing error Category 2", " 
A reason code of $reasoncode was reurned. This is a general processing error 
of an attempted transaction from AuthorizeNet. This one suggests that 
the processing company be contacted.  An error code of 3 was reurned from Authorize.Net.  
This is an automated email notifying you. This is a general processing 
error and the card was neither approved or denied.  

Customer name was $bfname $blname 
Phone number: $phone 
E-Mail: $email 
	
CVV2: $cvv2result
AVS: $avs

IP: $REMOTE_ADDR
OS: $os
ISP Gateway: $rh
 Please contact this customer to see if they were able to complete the transaction.   ", "From:Policy Of Liberty<customerservice@policyofliberty.net>"); 
BREAK; 
case 33: 
$notice = "NOTE: This field can not be left blank."; BREAK;
default: 
mail("$adminemail", "General Card Decline", " 
This card was declined.  
Customer name was $bfname $blname 
Phone number: $phone 
E-Mail: $email
CVV2: $cvv2result
AVS: $avs
Amount: $amount

IP: $REMOTE_ADDR
OS: $os
ISP Gateway: $rh  ", "From:Policy Of Liberty Checkout Monitor<customerservice@policyofliberty.net>"); 
BREAK;
} 
///end switch  
?> 
<center><h3>Declined - Possible missing or incorrect data</h3></center>
<BR><BR> I'm sorry, but your card was declined. <br> 
The below data may help you determine why the card was declined, and correct it: <br>
<BR> Reason: <b><?php echo "$reasontext $note" ?></b><br> 
Address verification: <b><?php echo $avs ?></b><br>
CVV2 Response: <b><?php echo $cvv2result ?></b><BR><BR>
You entered:<BR> Cardholder's First Name: <B><?php echo $bfname ?></b><BR>
 Cardholder's Last Name: <B><?php echo $blname ?></b><BR> 
Cardholder's Address: <B><?php echo $bsaddress ?></b><BR> 
Cardholder's City: <B><?php echo $bcity ?></b><BR> 
Cardholder's State: <B><?php echo $bstate ?></b><BR> 
Cardholder's Zip: <B><?php echo $bzip ?></b><BR>  
Expires: <b><?php echo "$month/$year" ?></b><BR> <br> 
<font color="#FF0000"><?php echo $notice ?></font> <BR>
<BR> You may hit your back button and retry the same card, or try a different card. 
<?php 
} 
/// end if there was an error ////////////////
	////////////  end if there was an error from AuthorizeNet  //////        
}
		  /// end string interpretation /////////////////////////
			///////////// End transaction response interpretation  ////
?>

<!-- end main content area -->
</td></tr></TABLE>
<table cellpadding="0" cellspacing="0" width="771" border="0"><tr><TD bgcolor="#ffffff" colspan="4"><IMG height="3" alt="Policy of Liberty is your source for books/papers on free market economics and pro-life policy as well as quotes and links to economic related issues" align="center" src="../white.gif" width="771" border="0"></TD></tr>
<TR><TD bgcolor="#99cc99"><IMG height="20" alt="Policy of Liberty is your source for books/papers on free market economics and pro-life policy as well as quotes and links to economic related issues" src="../end.gif" width="360" border="0" align="center"></TD><TD bgcolor="#99cc99"><IMG height="20" alt="Policy of Liberty is your source for books/papers on free market economics and pro-life policy as well as quotes and links to economic related issues" align="center" src="../backg.gif" width="27" border="0"></TD><TD bgcolor="#99cc99"><IMG height="20" alt="Policy of Liberty is your source for books/papers on free market economics and pro-life policy as well as quotes and links to economic related issues" align="center" src="../bottom.gif" width="318" border="0"></TD><td bgcolor="#99cc99"><A onmouseover="changeImages('indnav_01',	 '../images/indnav_01-over.gif'); return true;" onmouseout  ="changeImages('indnav_01', '../images/indnav_01.gif'); return true;" href="../sindex.html"><IMG height="20" alt="Policy of Liberty en Espanol" src="../images/indnav_01.gif" width="66" border="0" name="indnav_01" align="center"></A></td></TR>
<tr><TD bgcolor="#ffffff" colspan="4"><IMG height="3" alt="Policy of Liberty is your source for books/papers on free market economics and pro-life policy as well as quotes and links to economic related issues" align="center" src="../white.gif" width="771" border="0"></TD></tr>
<tr><TD bgcolor="#99cc99" colspan="4" height="15" width="771"><span class="foot">&nbsp;&nbsp;&nbsp;<a href="../index.php" class="foot" title="Policy of Liberty is you source for books/papers on free market economics and pro-life policy as well as quotes and links to economic related issues">home</a> &nbsp;|&nbsp; <a href="../freemarket.php" class="foot" title="Free Market Textbook">free market textbook</a> &nbsp;|&nbsp; <a href="../books.php" class="foot" title="Public Policy Books">public policy books</a> &nbsp;|&nbsp; <a href="../papers.php" class="foot" title="Articles and Papers">articles & papers</a> &nbsp;|&nbsp; <a href="../links.php" class="foot" title="Links">links</a> &nbsp;|&nbsp; <a href="../quotes.php" class="foot" title="Quotes">quotes</a> &nbsp;|&nbsp; <a href="../contact.php" class="foot" title="Contact Policy of Liberty">contact</a> &nbsp;|&nbsp; <a href="../join.php" class="foot" title="Join Policy of Liberty">join</a> &nbsp;|&nbsp; <a href="../about.php" class="foot" title="About Dr. John Cobin">about me</a></span></TD></tr></table><br></BODY></HTML>