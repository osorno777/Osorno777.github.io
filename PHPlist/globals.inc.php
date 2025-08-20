<?
if ( !defined('news_ok_IN') ){die ("Oops!");}
/* is is assumed that you use yourdomain.com/PHPlist/ as your root for this script, if you don't change the paths below.
provide your website, email, contact name, title for newsletter and the close for your emails.*/
$PHPlist_web_site = "http://www.policyofliberty.net";
$PHPlist_from_address = "jcobin@policyofliberty.net";
$PHPlist_from_name = "John Cobin";
$newsletter_title = "Policy of Liberty E-newsletter";
$css_file = "PHPlist.css";
$news_close = "Thanks for subscribing to the \"$newsletter_title\",\n$PHPlist_from_name\n$PHPlist_web_site";

/* define the database vars here.  ex. localhost, mySQL username, pass, the database name. */
$news_server = "localhost";
$news_user = "c_policyof";
$news_pass = "bfE31eBD";
$news_db = "c_policyof";

/* decide what will be required from the form submit.
off makes the variable not required, on makes it required!*/
$fn_req = "off";
$ln_req = "off";
$add_req = "off";
$city_req = "off";
$state_req = "off";
$zip_req = "off";
$phone_req = "off";
$age_req = "off";

/*  DO NOT CHANGE BELOW HERE!
will do list:
- make gui install with all options gui
- view all records in sortable table
- bulk email address add feature
- HTML email capability

$DB_create= "
#
# Table structure for table `PHPlist`
#

CREATE TABLE PHPlist (
  ID int(11) NOT NULL auto_increment,
  f_name varchar(250) default NULL,
  l_name varchar(250) default NULL,
  address varchar(250) default NULL,
  city varchar(250) default NULL,
  state varchar(100) default NULL,
  zip_code varchar(50) default NULL,
  phone varchar(50) default NULL,
  email varchar(200) default NULL,
  age varchar(50) default NULL,
  PRIMARY KEY  (ID)
) TYPE=MyISAM COMMENT='PHPlist is THE newsletter software of choice';";
*/
?>