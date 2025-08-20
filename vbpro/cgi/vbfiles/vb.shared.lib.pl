#################################################################
#  _     _ _      _                  ______              _      #
# (_)   (_|_)    (_)  _             (____  \            | | PRO #
#  _     _ _  ___ _ _| |_ ___   ____ ____)  ) ___   ___ | |  _  #
# | |   | | |/___) (_   _) _ \ / ___)  __  ( / _ \ / _ \| |_/ ) #
#  \ \ / /| |___ | | | || |_| | |   | |__)  ) |_| | |_| |  _ (  #
#   \___/ |_(___/|_|  \__)___/|_|   |______/ \___/ \___/|_| \_) #
# Shared Library, ©1997-1999                                    #
#                                                               #
# WARNING: VisitorBook Pro is Commercial Software protected     #
# under US and International copyright law. No unauthorized     #
# copying or duplication of this software will be permitted     #
#                                                               #
# You must setup and configure all of the following items       #
# before the VBPro system will work properly. Also, be sure     #
# that all of the individual CGIs point to the configuration    #
# file.                                                         #
#################################################################

#################################################################
# VistorBook Pro Info                                           #
#################################################################
  $VBProVersion = "1.0.3";
  $VBProPlatform = "UNIX/Linux/BSD";
  $VBProDate = "6/25/99"; 

#################################################################
# Subroutines                                                   #
#################################################################

sub MakeAccess  {
    $session_file = $_[0];
    $LoginTime = time();  # subtract 

    &lock("$session_file"); 
    open(SESS, ">$session_file") || die &Error("Your login session could not be created. Are you sure you are logging in properly?");
    print SESS "$LoginTime|$ENV{'REMOTE_ADDR'}";
    close(SESS);
    &unlock("$session_file");   
}

#################################################################

sub TakeAccess  {
    $session_file = $_[0];
    unlink("$session_file");
    &unlock("$session_file");   
}

#################################################################

sub CheckAccess {
    $session_file = $_[0];
    
    # Make sure the user is logged in properly, then
    # check access & make sure not idle.
    
    &lock("$session_file"); 
    open(SESS, "$session_file") || die &Error("Sorry, but you are not currently logged in. Please log in again.");
    $line = <SESS>;
    ($logintime, $logip) = split(/\|/, $line);
    close(SESS);
    
    $elapsed = time - $logintime;
    if ($elapsed > (60 * $inactive_time)) { # inactivity timer.
        # Remove the session file to be politically correct
        unlink("$session_file");
        die &Error("Sorry, you have been logged out due to the use of your account on multiple systems.");
    }
    if ($ENV{'REMOTE_ADDR'} ne "$logip")    {
        # Remove the session file because other sessions might
        # be active. Just a small security issue.
        &TakeAccess;
        die &Error("Sorry, you have been logged out due to the use of your account on multiple systems.");
    }
    $LoginTime = time;
    open(SESS, ">$session_file") || die &Error("The system cannot open your session file.");
    print SESS "$LoginTime|$ENV{'REMOTE_ADDR'}";
    close(SESS);
    &unlock("$session_file");   
}
sub RefreshForm {
    print "Content-type: text/html\n\n";
    
    print "<HTML>\n";
    print "<HEAD>\n";
    print "<TITLE>Error!</TITLE>\n";
    print "</HEAD>\n";
    print "<BODY BGCOLOR=\"#FFFFFF\">\n";
    
    print "<BLOCKQUOTE>\n";

    print "<FONT FACE=\"Verdana, Arial, Helvetica\"><H1>VBPro Admin: Error</H1></FONT>\n";
    print "<FONT FACE=\"Verdana, Arial, Helvetica\" SIZE=\"2\">\nSorry, but you are not currently logged in. Perhaps you have been idle for too long. Please enter your password below, or else any changes you just made will not be saved.<BR><BR>\n</FONT>\n
";

    print "<FORM ACTION=\"$ENV{'SCRIPT_NAME'}\" METHOD=POST>\n";
    print "<INPUT TYPE=\"hidden\" NAME=\"refresh_login\" VALUE=\"refresh_login\">\n";
    print "<INPUT TYPE=\"password\" NAME=\"pass\" SIZE=\"35\">";
    print "<INPUT TYPE=\"submit\" NAME=\"Refresh Session\" VALUE=\"Refresh Session\">\n";
    
    foreach $key (sort (keys %in))  {
        unless ($key eq "pass") {
            print "<INPUT TYPE=\"hidden\" NAME=\"$key\" VALUE=\"$in{$key}\">\n";
        }
        undef($key);
    }
    
    print "</FORM>\n";
    print "</BLOCKQUOTE>\n";

    print "</BODY>\n";
    print "</HTML>\n";
    
    exit;
}

sub GetTime {
    ($sec,$min,$hour,$mday,$mon,$year,$wday,$ydat,$isdst) = localtime(time());
    $mon++;
    $year=($year + 1900);    
    if ($min < 10) {
        $min = "0$min";
    }
    
    if ($sec < 10) {
        $sec = "0$sec";
    }
    
    $time_mode = "AM" if (!$use_24);
    
    if ($hour == 12)    {
        $time_mode = "PM";
    }
    elsif ($hour > 12 && !$use_24) {
        $hour = $hour - 12;
        $time_mode = "PM";
    }
    elsif ($hour eq "0" && !$use_24)   {
        $hour++;
    }
    $date = "$mon/$mday/$year";
    $time = "$hour:$min $time_mode";
}

#################################################################
# GetBookInfo()                                                 #
#                                                               #
# Purpose: This subroutine loads the variables, such as posting #
# information and book options, in to memory.                   #
#################################################################
sub GetBookInfo {
    &lock("$basebookdir/$book/$book.config");
    open(BOOKF, "$basebookdir/$book/$book.config") || die &Error("$!: $basebookdir/$book/$book.config (error 101)");
    $bookline = <BOOKF>;
    close(BOOKF);
    &unlock("$basebookdir/$book/$book.config");
    
    chop $bookline if($bookline =~/\n$|\r$/g);
    ($nick{$book}, $title{$book}, $sortfrom{$book}, $sortparam{$book}, $bookhtml_file{$book}, $bookhtml_url{$book}, $thankyou{$book}, $approval{$book}, $maxposts{$book}, $adminaddr{$book}, $badoption{$book}, $mailadmin{$book}, $mailuser{$book}, $blockhtml
{$book}, $postinglog{$book}, $useradmin{$book}, $future{$book}) = split(/\|/, $bookline);
    
}

#################################################################
# GetDatabaseInfo()                                             #
#                                                               #
# Purpose: This subroutine loads database information for the   #
# current guestbook in to memory. This creates an array of the  #
# fields that can be used with this guestbook.                  #
#################################################################
sub GetDatabaseInfo {
    $dbinfo = "$basebookdir/$book/book.fieldinfo.db";
    &lock("$dbinfo");
    open (DBINFO, "$dbinfo") || die &Error("$!: $dbinfo ");
    $dainfo = <DBINFO>;
    $bignames = <DBINFO>;
    $reqf = <DBINFO>;
    close (DBINFO);
    &unlock("$dbinfo");
    
    chop ($dainfo) if ($dainfo =~/\n$|\r$/);
    chop ($bignames) if ($bignames =~/\n$|\r$/);
    chop ($reqf) if ($reqf =~/\n$|\r$/);
    
    (@fnames) = split(/\|/, $dainfo);
    (@bnames) = split(/\|/, $bignames);
    (@reqfields) = split(/\|/, $reqf);
    
    $jk = 0;
    foreach $fn (@fnames)   {
        chop ($fn) if ($fn =~/\n$|\r$/);
        $fnum{$fn} = $jk;
        $fname{$jk} = $fn;
        $big_name{$fn} = $bnames[$jk];
        $jk++;
    }
    foreach $req (@reqfields)   {
        $reqdf{$req} = $req;
    }
}
# ------------------------------------------------------------- #

#################################################################
# UpdateBook()                                                  #
#                                                               #
# Purpose: Processes output of EditBookScreen().                #
#################################################################

sub UpdateBook  {
    $new_pass = $adminpw{$book};
    if ($in{'adminpw'} ne "-- edit to change --")   {
        $salt = substr($adminpw{$book}, 0, 2);
        $new_pass = crypt("$in{'adminpw'}", "$salt");
        
        &lock("$basebookdir/$book/passwd.txt");
        open(PASS, ">$basebookdir/$book/passwd.txt") || die &Error("$!: $basebookdir/$book/passwd.txt ");
        print PASS "$adminuid{$book}:$new_pass\n";
        close(PASS);
        &unlock("$basebookdir/$book/passwd.txt");
    }
    
    $cryptd = $new_pass; #log user in w/ new pass
    $in{'mailuser'} = "0" if (!$in{'mailuser'});
    $bookfile = "$basebookdir/$book/$book.config";
    &lock("$bookfile");
    open(BOOKS, ">$bookfile") || die &Error("Can't open book file", "$bookfile");
    print BOOKS "$book|$in{'title'}|$in{'sortfrom'}|$in{'sortparam'}|$bookhtml_file{$book}|$bookhtml_url{$book}|$in{'thankyou'}|$in{'approval'}|$in{'maxposts'}|$in{'adminaddr'}|$in{'badoption'}|$in{'mailadmin'}|$in{'mailuser'}|$in{'blockhtml'}|$in{'postin
glog'}|$useradmin{$book}|\n";
    close(BOOKS);
    &unlock("$bookfile");
    
    $in{'html.temp'} =~s/\r\n|\n\r|\r|\n/\n/g;
    $in{'entry.temp'} =~s/\r\n|\n\r|\r|\n/\n/g;
    $in{'email.temp'} =~s/\r\n|\n\r|\r|\n/\n/g;
    $in{'badwords'} =~s/\r\n|\n\r|\r|\n/\n/g;
    $in{'banned'} =~s/\r\n|\n\r|\r|\n/\n/g;
    
    &lock("$basebookdir/$book/book.template.txt");
    open(HTMLTMP, ">$basebookdir/$book/book.template.txt");
    print HTMLTMP $in{'html.temp'};
    close(HTMLTMP);
    &unlock("$basebookdir/$book/book.template.txt");

    &lock("$basebookdir/$book/entry.template.txt");
    open(ENTRYTMP, ">$basebookdir/$book/entry.template.txt");
    print ENTRYTMP $in{'entry.temp'};
    close(ENTRYTMP);
    &unlock("$basebookdir/$book/entry.template.txt");
    
    &lock("$basebookdir/$book/useremail.template.txt");
    open(EMAILTMP, ">$basebookdir/$book/useremail.template.txt");
    print EMAILTMP $in{'email.temp'};
    close(EMAILTMP);
    &unlock("$basebookdir/$book/useremail.template.txt");
    
    &lock("$basebookdir/$book/book.badfile.txt");
    open(BADFILE, ">$basebookdir/$book/book.badfile.txt");
    print BADFILE $in{'badwords'};
    close(BADFILE);
    &unlock("$basebookdir/$book/book.badfile.txt");
    
    &lock("$basebookdir/$book/book.banned.txt");
    open(BANNED, ">$basebookdir/$book/book.banned.txt");
    print BANNED $in{'banned'};
    close(BANNED);
    &unlock("$basebookdir/$book/book.banned.txt");
    
    $dbinfo = "$basebookdir/$book/book.fieldinfo.db";
    
    foreach $key (keys %in) {
        if ($key =~/^\d\|fname/)    {
            push (@field_names, $key);  
        }
        elsif ($key =~/^\d\|bname/) {
            push (@full_names, $key);
        }
    }
    
    $i = 0;
    foreach $field (sort @field_names)  {
        $field_line .= "$in{$field}";
        $i++;
        if ($field_names[$i])   {
            $field_line .= "|";
        }
        else    {
            $field_line .= "\n"
        }
    }
    $i = 0;
    foreach $full (sort @full_names)    {
        $full_line .= "$in{$full}";
        $i++;
        if ($full_names[$i])    {
            $full_line .= "|";
        }
        else    {
            $full_line .= "\n";
        }
    }
    
    # Since required fields don't need to be in any particular order,
    # we can just lump them all together without sorting.
    (@reqd) = split(/\0/, $in{'reqd'});
    $k = 0;
    foreach $rf (@reqd) {
        $rline .= "$rf";
        $k++;
        if ($reqd[$k])  {
            $rline .= "|"
        }
        else    {
            $rline .= "\n"
        }
    }

    $dbinfo = "$basebookdir/$book/book.fieldinfo.db";
    &lock("$dbinfo");
    open (DBINFO, ">$dbinfo") || die &Error("$!: $dbinfo ");
    print DBINFO "$field_line";
    print DBINFO "$full_line";
    print DBINFO "$rline";
    close (DBINFO);
    &unlock("$dbinfo"); 
}


#################################################################
# Error()                                                       #
#                                                               #
# Purpose: Generic error handling routine. Self-exiting.        #
#################################################################

sub Error   {
    local ($reason);
    $reason = @_[0];
    
    print &PrintHeader;
    
    print "<HTML>\n";
    print "<HEAD>\n";
    print "<TITLE>Error!</TITLE>\n";
    print "</HEAD>\n";
    print "<BODY BGCOLOR=\"#FFFFFF\">\n";
    
    print "<BLOCKQUOTE>\n";

    print "<FONT FACE=\"Verdana, Arial, Helvetica\"><H1>VBPro Admin: Error</H1></FONT>\n";
    print "<FONT FACE=\"Verdana, Arial, Helvetica\" SIZE=\"2\">\n@_\n</FONT>\n";

    print "</BLOCKQUOTE>\n";
    
    print "<HR NOSHADE SIZE=\"1\">\n";
    print "<FONT FACE=\"Verdana, Arial, Helvetica\" SIZE=\"1\">\n";
    print "<CENTER>VisitorBookPro $VBProVersion, updated $VBProDate.</CENTER>\n";
    print "</FONT>\n";
    
    print "</BODY>\n";
    print "</HTML>\n";
    
    exit;
}

# LOCK
sub lock    {
    $lck_file = $_[0];
    $lck_file .= ".lock";
    $checkt = (time() + 5);
    while(-e "$lck_file") {
        if($checkt < time()) {
            unlink("$lck_file");
        }
        else {
            select(undef, undef, undef, 0.25);
        }
    }

    open(LOCK,">$lck_file") || die &Error("Could not create lock file $lck_file");
    close(LOCK);
    chmod(0777, "$lck_file");

    die &Error("Can't create $lck_file") if (!-e $lck_file);
}

# UNLOCK
sub unlock {
    $lck_file = $_[0];
    $lck_file .= ".lock";
#   if (!-e "$lck_file")    {
#       die &Error("Can't open $lck_file");
#   }
    unlink("$lck_file");
}
