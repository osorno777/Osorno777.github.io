#!/usr/bin/perl
####################################################################
# Script:       | Poll It                                          #
# Version:      | 2.05                                             #
# By:           | Jason Berry (i2 Services, Inc. / CGI World)      #
# Contact:      | jason@cgi-world.com                              #
# WWWeb:        | http://www.cgi-world.com                         #
# Copyright:    | Jason Berry (CGI World of i2 Services, Inc.)     #
# Released      | August 09, 1998                                  #
####################################################################
# By using this software, you have agreed to the license           #
# agreement packaged with this program.                            #
#                                                                  #
####################################################################
# Variables: 
 #
   #

   $image_url = "/pollit/image.gif";
   # URL to the 'image.gif' that was packaged with this script. Upload
   # that GIF Image to your website & enter the URL to it above.


   $vote_text = "Vote!";
   # Text that is shown on the submit button when casting your vote.

   
   # Note:
   ##################################################################
          # If you're looking to use an image in one of the variables
          # below, input the IMAGE tag inside of the quotes as:
          # <IMG SRC=\"image_url.gif\"> <-- Placing backslashes (\) 
          # before the extra quotes inside a quote.
          ###########################################################


   $last_poll_text = "<LI>our Previous Polls Results";
   # Text that is linked to view the previous results of your 
   # previous poll.


   $results_not_available = "<BR>The results will be posted soon...";
   # Message shown when the number of votes is not greater then
   # the ammount you opted for when setting up a poll.

   
   $poll_not_available = "<BR>Currently there is no opinion poll available...<P>Check back soon for another poll...";
   # Message listed when a poll is not available. 
   #


   $non_SSI_CGI_FileName = "poll.cgi";
   # The name of the file that was originaly named  "Poll_It_v2.0.cgi" when
   # you received this zipped up package. If you renamed that file to poll.cgi
   # then enter "poll.cgi" above.

      


#
 #
  # (We do not support this script if you edit below this line )
   ################################################################
  #
#


%in = &ReadForm;

if ($0=~m#^(.*)(\\|/)#)	{ $cgidir = $1; }
else { $cgidir = `pwd`; chomp $cgidir; }

$script_url  = $ENV{'SCRIPT_NAME'};
$data_dir = "$cgidir/pollit_files";
$poll_options = "$data_dir/poll_options.txt";
$poll_info = "$data_dir/poll_info.txt";
$ips_file = "$data_dir/ips.txt";
$last_file = "$data_dir/last_poll.txt";
$lockdir = "$data_dir/filelock";

open(IPS,"<$ips_file");
@ips = <IPS>;
close(IPS);

$all_ips = join('|',@ips);

$addr = "$ENV{'REMOTE_ADDR'}\n";

if(@ips && $addr =~ /$all_ips/) {
   $voted = 1;
}


if($option_selected && !$voted) {


   &FileLock("$lockdir");
   open(MIPS,">>$ips_file"); 
   print MIPS "$ENV{'REMOTE_ADDR'}\n";
   close(MIPS);
   &FileUnlock("$lockdir");


   open(POPTIONS,"<$poll_options");
   while(<POPTIONS>) {
      ($option_id,$poll_option,$votes_received) = split(/=/,$_);

      if($option_id eq "total") {
         $new_total = $poll_option + 1;
         $push = "total=$new_total\n";
         push(@reprint,$push);
      }      

      else {
     
         if($option_id eq "$option_selected") {
            $new_ototal = $votes_received + 1;
            $push = "$option_id\=$poll_option\=$new_ototal\n";
            push(@reprint,$push);
         }

         else {
            push(@reprint,$_);
         }
      }

   }
   close(POPTIONS);


   &FileLock("$lockdir");
   open(REPRINT,">$poll_options");
   print REPRINT @reprint;
   close(REPRINT);
   &FileUnlock("$lockdir");

   $voted = 1;

   print "Location: $ENV{'HTTP_REFERER'}\n\n";

}



# Print Out SSI Poll Box:
###############################################################

&Template("$data_dir/_ssi_poll.html");

open(POLLINFO,"<$poll_info");
while(<POLLINFO>) {
   chop($_);
   ($pinfo,$pvalue) = split(/=/,$_);
   $$pinfo = "$pvalue";
}
close(POLLINFO);

open(POLLOPTIONS,"<$poll_options");
@unsorted_poll_options = <POLLOPTIONS>;
close(POLLOPTIONS);

foreach$unsorted(@unsorted_poll_options) {
   ($option_id,$poll_option,$votes_received) = split(/=/,$unsorted);
   chop($votes_recieved);

   if($option_id eq "total") {
      $total = $poll_option;
      $show_total = "Total Votes: $total";

   }

   

   $push = "$votes_received\=$option_id\=$poll_option";
   push(@poll_options,$push);
}


# Show Voting Results:
#####################################

if($voted) {

   foreach$p_option(sort { $b <=> $a } @poll_options) {
      ($votes_received,$option_id,$poll_option) = split(/=/,$p_option);


      if($option_id ne "total" && $total > "0") {


         $percent = (int(($votes_received / $total) * 1000)) / 10;
         $percent = substr($percent,0,4);
  
         $sign = "%";

         if($votes_received < 1) {
            $percent = "0";
         }

         $width = int($percent * 1);

         if($votes_received < 1) {
            $width = 2;
         }


         $percent = "$percent$sign";
         $image_percent = "<IMG SRC=\"$image_url\" Height=\"10\" Width=\"$width\">";
         $show_results .= &Cell('poll_results');

      }
   }


   $show_results .= &Cell('total_votes');

   if($show_results_after > $total) {
      undef($show_results);
      $show_results = "$results_not_available";
   }

}



# Show Voting Options:
#####################################

if(!$voted) {

   foreach$p_option(@poll_options) {
      ($votes_received,$option_id,$poll_option) = split(/=/,$p_option);

      if($option_id ne "total") {
         $display_options .= &Cell("show_options");
      }
   }

   if(!$display_options) { $display_options = "$poll_not_available" };

}

if($display_options) { $submit = " <BR> <INPUT Type=SUBMIT Value=\"$vote_text\">" };


open(LASTPOLL,"<$last_file");
@last_poll = <LASTPOLL>;
close(LASTPOLL);

if(@last_poll) {
   $last_poll = "<A HREF=\"$non_SSI_CGI_FileName?load=lastpoll\">$last_poll_text</A><BR>";
}


print &Template("$data_dir/_ssi_poll.html",'html');


# Load Template:                                              #
###############################################################

sub Template {  

  local(*FILE);

  if    ($_[1] eq 'html') { print "Content-type: text/html\n\n"  unless ($ContentType++ > 0); }
  elsif ($_[1] eq 'text') { print "Content-type: text/plain\n\n" unless ($ContentType++ > 0); }

  if    (!$_[0])	{ return "<br>\nTemplate : No file was specified<br>\n"; }
  elsif (!-e "$_[0]")	{ return "<br>\nTemplate : File '$_[0]' does not exist<br>\n"; }
  else {
    open(FILE, "<$_[0]") || return "<br>\nTemplate : Could open $_[0]<br>\n";
    while (<FILE>) { $FILE .= $_; }
    close(FILE);
    for ($FILE) {
      s/<!-- insert : (.*?) -->/\1/gi;				# show hidden inserts
      s/<!-- def : (\w+) -->(?:\r\n|\n)?(.*?)<!-- \/def : \1 -->/
	$CELL{$1}=$2;''/ges;					# read/remove template cells
      s/\$(\w+)\$/${$1}/g;					# translate $scalars$
      }
    }
  return $FILE;
}


# Translate Cell:                                             #
###############################################################

sub Cell {  

  my($CELL);
  for (0..$#_) { if ($_[$_]) { $CELL .= $CELL{$_[$_]}; }}

  if    (!$_[0]) { return "<br>\nCell : No cell was specified<br>\n"; }
  elsif (!$CELL) { return "<br>\nCell : Cell '$_[0]' is not defined<br>\n"; }
  else		 { $CELL =~ s/\$(\w+)\$/${$1}/g; }		# translate $scalars$
  
  return $CELL;

}


# Parse Form:                                                 #
###############################################################
# Usage    : %in = &ReadForm;                                 #
#                                                             #
###############################################################

sub ReadForm {

  my($max) = $_[1];					# Max Input Size
  my($name,$value,$pair,@pairs,$buffer,%hash);		# localize variables

  # Check input size if max input size is defined
  if ($max && ($ENV{'CONTENT_LENGTH'}||length $ENV{'QUERY_STRING'}) > $max) {
    die("ReadForm : Input exceeds max input limit of $max bytes\n");
    }

  # Read GET or POST form into $buffer
  if    ($ENV{'REQUEST_METHOD'} eq 'POST') { read(STDIN, $buffer, $ENV{'CONTENT_LENGTH'}); }
  if    ($ENV{'QUERY_STRING'}) { $buffer .= $ENV{'QUERY_STRING'}; }

  @pairs = split(/&/, $buffer);				# Split into name/value pairs
  foreach $pair (@pairs) {		

    ($name, $value) = split(/=/, $pair);		# split into $name and $value
    $value =~ tr/+/ /;					# replace "+" with " "
    $value =~ s/%([A-F0-9]{2})/pack("C", hex($1))/egi;	# replace %hex with char


    $$name = $value;
    }

  return %hash;
  }


# File Locking:                                               #
###############################################################
# Usage    : &FileLock("$lockdir");                           #
#	   : &FileUnlock("$lockdir");                         #
#                                                             #
###############################################################

sub FileLock   {
  my($i);					# sleep counter
  while (!mkdir($_[0],0777)) {			# if there already is a lock
    sleep 1;					# sleep for 1 sec and try again
    if (++$i>60) { die("File_Lock : Can't create filelock : $!\n"); }		
    }
  }

sub FileUnlock {
  rmdir($_[0]);					# remove file lock dir
  }


####################################################################

