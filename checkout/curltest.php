<?php
error_reporting(15);
$ch = curl_init();                                                                    /// initialize a cURL session 
curl_setopt ($ch, CURLOPT_URL,"https://www.americashomeplace.com/");				          /// set the cURL URL 
curl_setopt ($ch, CURLOPT_HEADER, 0);                                                 /// Don't return the header in the response 
curl_setopt ($ch, CURLOPT_RETURNTRANSFER, 1);                                         /// Set the response into a variable 
$x = curl_exec ($ch);                                                                 /// Execute this session & set the variable from the response 
curl_close ($ch);
print $x."<HR>";
show_source("curltest.php");
?>