<?define ('wwwf_IN',true);
$title = "Contact Policy of Liberty";
$desc = "Books/papers on free market economics and policy, pro-life policy, Cobin CV, links, photos, other resources, allodial title, fire safety regulation, building regulation, free market policy, drug legalization, abortion debate";
$key = "allodial title, allodialism, allodial policy, free market textbook, homeschool books, economics books for homeschoolers, public policy and Christians, creation and evolution, Christian homeschool books, public policy books, pro-life books, abortion issue, Christians and government, building regulation, allodial title, tax protesting, revolution, fire safety regulation, accreditation of higher education, public choice economics, Virginia school, Austrian economics, law and economics, subjectivist economics, knowledge problem, market failure, government failure, urban regulation, fire safety regulation, romantic vision of government, public, choice, Austrian, economics, law, rent seeking, right, allodial, regulation, policy, vote, government, Bible, pro-life, Christian, building, zoning, liberty, planning, market, Chile, abortion debate, public school, Romans 13, feudal, privatization, allodial property";
$alt = "Policy of Liberty is your source for books/papers on free market economics and pro-life policy as well as quotes and links to economic related issues";
$titleimg = "contact.jpg";include ("top.php")?>
<TABLE cellpadding="0" cellspacing="0" border="0" width="771" height="240">
<tr><td rowspan="2"><IMG height="240" alt="Contact Policy of Liberty" src="images/contact.jpg" width="359" border="0"></td>
<td valign="top"><p class="pl">Policy of liberty is dedicated to the advancement of liberty and responsibility in society. Its philosophy is nearly libertarian (rather than neo-conservative) on economic issues, adhering to biblical norms for social issues but rarely looking to the state for solutions to social problems. POL provides resources, links, books and articles, an email list, photos and links to famous economists, great quotations for liberty.</p></td></tr>
<tr><td width="409" bgcolor="#CCCCCC" height="90" border="2" align="right"></td></tr></TABLE>
<table cellpadding="0" cellspacing="0" width="771" border="0" bgcolor="#999999">
<tr><td><img src="white.gif" height="3" width="771" alt="<? echo "$alt" ?>"></td></tr>
<tr><td><p class="white"><b>Please contact us by completing the following form:</b></p></td></TD></tr></table>
<table cellpadding="0" cellspacing="1" WIDTH="771" border="0" class="news"><form method="post" action="<? echo $_SERVER['PHP_SELF']?>" name="cont">
<tr><td width="771"><img src="white.gif" width="771" height="1" alt="<? echo "$alt" ?>"></td></tr>
<tr><td align="center" class="pl">
<?if (!$_POST['action']){?>
<br><span class="pl"><b>Please use this form to contact us:</b></span><br><br>
<form method="post" action="<? echo $_SERVER['PHP_SELF']?>" name="cont">
<input type="hidden" name="action" value="submit">
<span class="pl">Your name:</span><br>
&nbsp;&nbsp;<input class="form" type="text" onFocus="this.value=''" name="name" value="&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*required" size="40" maxlength="50"><br><br>
<span class="pl">Your email address:</span><br>
&nbsp;&nbsp;<input class="form" type="text" onFocus="this.value=''" name="email" value="&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*required" size="40" maxlength="40"><br><br>
<span class="pl">Your message:</span><br>
&nbsp;&nbsp;<textarea class="form" name="comments" cols="45" rows="8"></textarea><br><br>
&nbsp;&nbsp;<input class="form" type="submit" name="Submit" value="Send"><input class="form" type="reset" name="Reset" value="Clear">
<?
}
if($_POST['action'] == "submit"){
$email = htmlspecialchars($email);
$comments = htmlspecialchars($comments);
$name = htmlspecialchars($name);
$date = date("F j, Y, g:i a");
$to = "jcobin@PolicyOfLiberty.net";
$subject = "Comments from the on-line contact form";
$from_header = "From:$email";
if($comments != "" and $email != "")
{mail("$to", "$subject", "
$name completed the contact form on $date
Their message:
$comments", "$from_header");?>
<p class="pl">Thank you <? echo "$name" ?>, for getting in touch.<BR>The email address that you sent was:<BR><B><? echo "$email" ?></B><BR>Here is what you sent:<BR><B><? echo "$comments" ?></B><br>If you asked a question or requested info, we will be in touch soon.<br><br>Thanks,<br>Dr. John M. Cobin</p>
<?}else{
print("<span class=\"pl\"><B>Unable to send.</B><BR>No comments were submitted or your email address is missing.<BR>Please go back and be sure to fill in all fields.</span>");
}
}?>
<br><br></td></tr></form></table>
<table cellpadding="0" cellspacing="0" width="771" border="0"><? include ("base.php")?>
