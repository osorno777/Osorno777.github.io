#!/usr/bin/perl
#    Last change:  B    12 Mar 1999    9:15 am
$emailprogram = '/var/qmail/bin/qmail-inject' ;
$mailon = 0 ;                   # Mailprogram directory path and switch.
$emailfile = "email.txt" ;      # Set mailon = 0 to stop email confirmation

###############################################################################
#
# Advanced Free-For-All
#
# Version 2.00
#
# Source:       http://www.trellian.com/affa
#
# Last updated:	11 Mar 1999
#
# Copyright (c) 1999, Trellian Pty Ltd / Pixeltech Design Pty Ltd
#
# This program may be distributed and/or modified provided the original
# headers, copyright notices and links remain intact.
#
###############################################################################

require 5.001;

$configFile = "affa.cfg";

# Config defaults
#
%defaults = (
    Delimiter	=> '\s*,\s*',
    TargetFile  => "links.html",
    HeaderFile  => "header.htm",
    FooterFile  => "footer.htm",
    DatabaseFile => "db.txt",
    LinkTemplate => '<A HREF="$url">$title</A> - $description',
    TextReject	=> "",
    CaseTransform => "No",
    CaseReject	=> 3,
    DuplicateURLReject => "Yes",
    MaximumCount => 100,
    MaximumSize	=> 2,
    DomainReject => "",
    Lifespan	=> 0,
    TestURL	=> "No",
    TestURLTimeout => 20,
    Administrator => "webmaster",
    LogFile	=> "",
    SortOrder	=> "Post",
    SubstituteList => "",
    Categories  => "Computer, Business, Education, Entertainment, Government, Miscellaneous, Personal",
    MaxTitleLen => 40,
    MaxDescriptionLen => 80,
    MaxURLLen	=> 0,
    RejectIfTooLong => "No",
    AcceptMessage => "Thank you, your link has been added.",
    URLPrefixAccept => "http://",
    AllowDescription => "No",
);

($dataBaseError, $testURLError, $substError, $createHTMLError, $logFileError,
    $readConfigError, $configFileError) = (1..10);

$DBdelim = ",";				# Delimiter used in database
$daySeconds = 60 * 60 * 24;		# The number of seconds in a day
$kb = 1024;				# The number of bytes in a Kb
$HTTPport = 80;				# Default HTTP port
$| = 1;					# Do not buffer output
$ok = "OK";				# OK sentinel
$acceptTitle = "Submission Accepted";	# Do not change
$rejectTitle = "Submission Rejected";	# Do not change
$sysError = "System Error";		# What to call internal errors
$progURL = "http://www.pixeltech.com.au/download";
$categoryParam = "category";		# Paramater for category
$titleParam = "title";			# Paramater for title
$urlParam = "url";			# Paramater for URL
$descriptionParam = "description";	# Paramater for description
$emailParam = "email";                  # Parameter for email

if ($ENV{SCRIPT_NAME})
{
    print "Content-type:	text/html\n\n";

    %config = &readConfig($configFile);

    %in = &readParse;

    # Accept FFA params for compatibility
    $in{$categoryParam} = $in{section} unless $in{$categoryParam};

    if ("$in{$urlParam}$in{$titleParam}" ||
    	"$in{$descriptionParam}$in{$categoryParam}")
    {
	open(DB, "+<$config{DatabaseFile}") || &error($dataBaseError);
	&post();
    }
    else
    {
	open(DB, "<$config{DatabaseFile}") || &error($dataBaseError);
	&showHTML(*STDOUT);
    }
}
else
{
    %config = &readConfig($configFile);

    open(DB, "+<$config{DatabaseFile}");
    &maintenance();
}

    close(DB);

# Input from form
# Uses: RejectMessage, AllowDescription
sub post
{
    my($url, $title, $description, $category, $email, $check);

    $in{url} =~ s#/*$##;   # Remove trailing `/' (which can confuse comparator)

    $url = $in{$urlParam};
    $title = $in{$titleParam};
    $description = $in{$descriptionParam} if $config{AllowDescription};
    $category = $in{$categoryParam};
    $email = $in{$emailParam};

    ($url, $title, $description, $category, $email) =
	&substitute($url, $title, $description, $category, $email);

    $check = &checkPost($url, $title, $description, $category, $email);
    $entry = &encodeEntry($url, $title, $description, $category, $email);

    if ($check eq $ok)
    {
	&addLink($entry);
	&purge(0);
	&createHTML;
	&logPost("Accept: $entry");
	&printMessage($acceptTitle, $config{AcceptMessage});

        my($email);
        $email = $in{$emailParam};

        if ( $mailon )
          {

            open (SEND, $emailfile) ;
            @emailmessage = <SEND> ;
            close (SEND) ;

            open (MESSAGE,"|$emailprogram -t") ;

            $toline = "To: $email\n" ;
            $fromline = "From: $config{Administrator}\n" ;
            $subjectline = "Subject: Your Link Submission\n\n" ;

            $confirm1 = "Thank-you for posting your link.  This is a once off confirmation email.\n\n" ;
            $confirm2 = "$title\n" ;
            $confirm3 = "$url\n" ;
            $confirm4 = "$section\n" ;
            $confirm5 = "\n" ;

            $remove1 = " This is a once off email, your address has not been added to any lists.\n" ;
            $remove2 = " There is no need to request a remove.\n" ;
            $remove3 = " \n" ;

            print MESSAGE $toline ;
            print MESSAGE $fromline ;
            print MESSAGE $subjectline ;

            print MESSAGE $confirm1 ;
            print MESSAGE $confirm2 ;
            print MESSAGE $confirm3 ;
            print MESSAGE $confirm4 ;
            print MESSAGE $confirm5 ;

            print MESSAGE $remove1 ;
            print MESSAGE $remove2 ;
            print MESSAGE $remove3 ;

            foreach ( @emailmessage )
             {
                print MESSAGE "$_" ;
             }


            close (MESSAGE) ;

          }
    }
    else
    {
	&logPost("Reject [$check]: $entry");
	&printMessage($rejectTitle, $check);
    }
}

# Read in and parse form input. Pinched from Steven E. Brenner's cgi-lib.pl
# code, which requires the following credit and copyright:
#
#	Copyright 1994 Steven E. Brenner
#
# This is effectively a rewrite. Just the important subroutine was included so
# that it wouldn't be necessary to distribute multiple files.
#
sub readParse
{
    my($i, $key, $val, %in, @in, $in);

    # Read in text
    if ($ENV{'REQUEST_METHOD'} eq "GET")
    {
	$in = $ENV{'QUERY_STRING'};
    }
    elsif ($ENV{'REQUEST_METHOD'} eq "POST")
    {
	read(STDIN, $in, $ENV{'CONTENT_LENGTH'});
    }

    @in = split(/&/, $in);

    foreach $i (0 .. $#in)
    {
	# Convert plus's to spaces
	$in[$i] =~ s/\+/ /g;

	# Split into key and value.
	($key, $val) = split(/=/,$in[$i],2); # splits on the first =.

	# Convert %XX from hex numbers to alphanumeric
	$key =~ s/%(..)/pack("c",hex($1))/ge;
	$val =~ s/%(..)/pack("c",hex($1))/ge;

	# Associate key and value
	$in{$key} .= "\0" if (defined($in{$key})); # \0 is the multiple sep
	$in{$key} .= $val;
    }

    %in;				# Return paramater list hash
}

# Checks to see if posting passes all rules according to the config file
# Uses: TextReject, CaseReject, DuplicateURLReject, DomainReject, TestURL,
# Categories, MaxTitleLen, MaxDescriptionLen, MaxURLLen, RejectIfTooLong,
# URLPrefixAccept, TestURLMessage, TextRejectMessage, CaseRejectMessage,
# DuplicateURLRejectMessage, DomainRejectMessage, CategoryRejectMessage,
# RejectIfTooLongMessage, MinTitleLen, MinDescriptionLen, MinURLLen,
# RejectIfTooShortMessage, MustContain, MustContainRejectMessage
sub checkPost
{
    my($url, $title, $description, $category) = @_;
    my($testString, $compressString);
    my($protocol, $domain, $path, $HTMLFile);

    $testString = "$title $description";
    $compressString = $testString;
    $compressString =~ s/[^A-Za-z]+//;
    ($protocol, $domain, $path) = ($url =~ m#(\w+)://([^/]+)(.*)#);
    ($HTMLFile) = ($path =~ m#([^/]+\.[^/]+)$#) || "";
    $path = substr($path, 0, length($path) - length($HTMLFile) + 1);

    return $config{TestURLMessage} if !$domain;	# Invalid URL supplied

    # Check TextReject
    foreach (split(/$config{Delimiter}/, $config{TextReject}))
    {
	return $config{TextRejectMessage} if $testString =~ /$_/i;
	return $config{TextRejectMessage} if $compressString =~ /$_/i;
    }

    # Check CaseReject
    return $config{CaseRejectMessage} if $config{CaseReject} &&
	(($testString =~ /\b([A-Z]+)\b/g)[$config{CaseReject} - 1]);

    # Check DuplicateURLReject
    return $config{DuplicateURLRejectMessage}
	if &isTrue($config{DuplicateURLReject}) &&
	grep(m#$protocol://$domain$path$DBdelim#oi, <DB>);
    seek(DB, 0, 0);			# Rewind DB file for later

    # Check DomainReject
    foreach (split(/$config{Delimiter}/, $config{DomainReject}))
    {
	return $config{DomainRejectMessage} if $domain =~ /$_$/;
    }

    # Check TestURL
    return $config{TestURLMessage}
	if &isTrue($config{TestURL}) && !&testURL($url);

    # Check Categories
    return $config{CategoryRejectMessage} if !grep(/$category/o,
	split(/$config{Delimiter}/, $config{Categories}));

    # Check RejectIfTooLong
    if (&isTrue($config{RejectIfTooLong}))
    {
	# Check MaxTitleLen
	return $config{RejectIfTooLongMessage} if $config{MaxTitleLen} &&
	    length($title) > $config{MaxTitleLen};
	# Check MaxDescriptionLen
	return $config{RejectIfTooLongMessage} if $config{MaxDescriptionLen} &&
	    !isTrue($config{AllowDescription}) && length($description) >
	    $config{MaxDescriptionLen};
    }

    # Check MaxURLLen
    return $config{RejectIfTooLongMessage} if $config{MaxURLLen} &&
	length($url) > $config{MaxURLLen};

    # Check MinTitleLen
    return $config{RejectIfTooShortMessage}
	if length($title) < $config{MinTitleLen};
    # Check MinDescriptionLen
    return $config{RejectIfTooShortMessage}
	if !isTrue($config{AllowDescription}) && length($description) <
	$config{MinDescriptionLen};
    # Check MinURLLen
    return $config{RejectIfTooShortMessage}
	if length($url) < $config{MinURLLen};

    # Check URLPrefixAccept
    return $config{TestURLMessage} if !grep(/$protocol/,
	split(/$config{Delimiter}/, $config{URLPrefixAccept}));

    # Check MustContain
    $testString = join('|', split(/$config{Delimiter}/, $config{MustContain}));
    return $config{MustContainRejectMessage} if
	$config{MustContain} && $title !~ /$testString/i;

    $ok;					# Accept!
}

# Connects to URL and reads just the header to test for valid URL
# Uses: TestURLTimeout
sub testURL
{
    eval { use Socket; };

    $INC{"Socket.pm"} || &error($testURLError);

    my($url) = @_;
    my($proto, $port, $sin);
    my($protocol, $domain, $path);
    my($version, $code, $message);

    ($protocol, $domain, $port, $path) =
	($url =~ m#(\w+)://([^/:]+)(:\d+)?(.*)(:\d+)?#);

    $path = "/" unless $path;

    $proto = getprotobyname('tcp');

    socket(HTTP, PF_INET, SOCK_STREAM, $proto) || return 0;
    $port = substr($port, 1) if $port;
    $port = $HTTPport unless $port;

    if (fork())
    {
	# Parent here
	return (wait() == -1) || $?;		# Wait for child to terminate
    }
    else
    {
	# Child does the checking and returns the right status
	$SIG{ALRM} = sub { exit(0); };
	alarm($config{TestURLTimeout});

	$sin = sockaddr_in($port, inet_aton($domain)) || exit(0);
	connect(HTTP, $sin) || exit(0);

	select(HTTP);
	$| = 1;
	select(STDOUT);

	print HTTP "HEAD $path HTTP\nHOST: $domain\n\n";

	($version, $code, $message) = split(/\s+/, <HTTP>, 3);
	chomp($message);

	close(HTTP);

	exit($code == 404 ? 0 : 1);
    }
}

# Purge old entries if limits are exceeded
# Uses: MaximumCount, MaximumSize, Lifespan
sub purge
{
    my($confirm) = @_;
    my(@db, $expiryTime, $i, $fileSize, $smallest, $smallestVal);

    $expiryTime = $^T - $daySeconds * $config{Lifespan};
    $fileSize = -s DB;

    eval { flock(DB, 2); };	# Lock DB file (eval to trap if unimplemented)
    @db = <DB>;			# Read in entire database

    # Process Lifespan
    if ($config{Lifespan})
    {
	for ($i = 0; $i <= $#db; $i++)
	{
	    if ((split(/$DBdelim/, $db[$i]))[4] < $expiryTime)
	    {
		$fileSize -= length($db[$i]);
		splice(@db, $i, 1);
		$i--;
	    }
	}
    }

    # Process MaximumCount and MaximumSize
    while (($config{MaximumCount} && ($#db + 1) > $config{MaximumCount}) ||
	($config{MaximumSize} && $fileSize > $config{MaximumSize} * $kb))
    {
	$smallest = 0;
	$smallestVal = (split(/$DBdelim/, $db[0]))[4];

	for ($i = 1; $i <= $#db; $i++)
	{
	    if ((split(/$DBdelim/, $db[$i]))[4] < $smallestVal)
	    {
		$smallest = $i;
		$smallestVal = (split(/$DBdelim/, $db[$i]))[4];
	    }
	}

	$fileSize -= length($db[$smallest]);
	splice(@db, $smallest, 1);
    }

    seek(DB, 0, 0);		# Seek to BOF
    print DB @db;		# Regurgitate DB file
    truncate(DB, tell(DB));	# Truncate at current location

    eval { flock(DB, 8); };	# Unlock DB file
    seek(DB, 0, 0);		# Seek to BOF
}

# Create a database entry based on URL, title, description and category
sub encodeEntry
{
    my($url, $title, $description, $category) = @_;

    join($DBdelim, $url, $title, $description, $category, $^T);
}

# Apply any modification directives in the config file
# Uses: CaseTransform, SubstituteList, MaxTitleLen, MaxDescriptionLen,
sub substitute
{
    my($url, $title, $description, $category) = @_;
    my($escDelim);

    # Process CaseTransform
    if (&isTrue($config{CaseTransform}))
    {
	# Force mixed-case
	$title =~ s/([A-Z])(\w+)/"$1\L$2"/ge;
	$description =~ s/([A-Z])(\w+)/"$1\L$2"/ge if $description;
    }

    # Process SubstituteList
    foreach (split(/$config{Delimiter}/, $config{SubstituteList}))
    {
	eval("\$title =~ s$_; 1;") || &error($substError);
	eval("\$description =~ s$_; 1;") || &error($substError);
    }

    # Process MaxTitleLen
    $title = substr($title, 0, $config{MaxTitleLen});

    # Process MaxDescriptionLen
    $description = substr($description, 0, $config{MaxDescriptionLen});

    $escDelim = ord($DBdelim);
    $url =~ s/$DBdelim/&#$escDelim;/go;
    $title =~ s/$DBdelim/&#$escDelim;/go;
    $description =~ s/$DBdelim/&#$escDelim;/go;
    $category =~ s/$DBdelim/&#$escDelim;/go;

    ($url, $title, $description, $category);
}

# Add a new link to database
sub addLink
{
    my($entry) = @_;

    eval { flock(DB, 2); };	# Lock DB file (eval to trap if unimplemented)
    seek(DB, 0, 2);		# Seek to EOF
    print DB "$entry\n";	# Append entry
    eval { flock(DB, 8); };	# Unlock DB file
    seek(DB, 0, 0);		# Seek to BOF
}

# Generates resulting HTML page
# Uses: HeaderFile, FooterFile, SortOrder, Categories, TargetFile
sub createHTML
{
    if ($config{TargetFile})
    {
	open(HTML, ">$config{TargetFile}") || &error($createHTMLError);
    }
    else
    {
	return;
    }

    print HTML "<!-- DO NOT EDIT THIS FILE - IT IS CREATED AUTOMATICALLY BY ",
	"XXX\n     ($progURL) -->\n";
    print HTML "<!-- Last updated: ", scalar(localtime), " -->\n";
    print HTML "<!-- Number of links: ", ($#items + 1), " -->\n\n";

    &showHTML(*HTML);

    close(HTML);
}

sub showHTML
{
    local(*HTML) = @_;
    my(@items, $category, $printCategory);
    my($sortOrder) = "$config{SortOrder}Sort";

    @items = sort $sortOrder <DB>;	# Read in entire database and sort
    seek(DB, 0, 0);			# Rewind to BOF

    # Print header
    if ($config{HeaderFile} && open(FILE, "<$config{HeaderFile}"))
    {
	print HTML <FILE>;
	close(FILE);
    }

    # Process Categories
    foreach $category (split(/$config{Delimiter}/, $config{Categories}))
    {
	$printCategory = $config{CategoryTemplate};
	$printCategory =~ s/\$category/$category/g;

	# Process SortOrder
	foreach (grep(/$DBdelim$category$DBdelim/, @items))
	{
	    print HTML "$printCategory\n" if $printCategory;
	    $printCategory = "";

	    print HTML &makePretty($_);
	}
    }

    # Print footer
    if ($config{FooterFile} && open(FILE, "<$config{FooterFile}"))
    {
	print HTML <FILE>;
	close(FILE);
    }
}

# Sort in posting order
sub postSort
{
    (split(/$DBdelim/, $a))[4] <=> (split(/$DBdelim/, $b))[4];
}

# Sort in reverse-posting order
sub reverseSort
{
    (split(/$DBdelim/, $b))[4] <=> (split(/$DBdelim/, $a))[4];
}

# Sort in alphabetical order on title
sub alphaSort
{
    lc((split(/$DBdelim/, $a))[1]) cmp lc((split(/$DBdelim/, $b))[1]);
}

# Turn a database string into a pretty display
sub makePretty
{
    my($url, $title, $description, $category, $time) =
	split(/$DBdelim/, $_[0]);

    $_ = $config{LinkTemplate};
    s/\$url/$url/g;
    s/\$title/$title/g;
    s/\$description/$description/g;
    s/\$date/gmtime($time)/eg;

    "$_\n";
}

# Print out message
sub printMessage
{
    my($title, @message) = @_;

    print "<HEAD><TITLE>$title</TITLE></HEAD>\n", @message, "\n";
}

# Print out error message, log and exit
sub error
{
    my($errorNum) = @_;
    my($administrator);

    &logPost("$sysError $errorNum") if $errorNum != $logFileError;

    $administrator = "Please notify <A HREF=\"mailto:$config{Administrator}" .
	"?Subject=XXX $sysError $errorNum\">$config{Administrator}</A>" if
	$config{Administrator};

    &printMessage($rejectTitle, "$sysError $errorNum", "<P>$administrator");

    exit 1;
}

# Log posting
# Uses: LogFile
sub logPost
{
    return if !$config{LogFile};

    open(LOGFILE, ">>$config{LogFile}") || &error($logFileError);

    print LOGFILE scalar(localtime), ": ", @_, "\n";

    close(LOGFILE);
}

# Print out usage information
sub usage
{
    print <<EOUSAGE;

Usage:

	-i	Install - Do everything required to set this up
	-t	Test all URLs and remove each broken link, after confirmation
	-c	Create - Re-creates the target HTML file, after purging all
		expired links based on Lifespan, MaximumCount and MaximumSize
		(with confirmation) and re-sorts file if necessary (i.e. after
		changing `SortOrder' in the config file) 
	-r LINK	Remove `LINK' from listing. `LINK' is given as a keyword in the
		title or the URL. The user will be asked for confirmation
	-f	Force - Do not ask for confirmations
	-e	Export - Export the database.
	-h	Help - Display this help

EOUSAGE
}

# Maintenance mode
sub maintenance
{
    eval { use Getopt::Std; };

    getopts('itcr:fe');			# Read in options

    $opt_i && &install;
    $opt_t && &testAll(!$opt_f);
    $opt_c && do
	{
	    &purge(!$opt_f);
	    &createHTML;
	};
    $opt_r && &removeLink($opt_r, !$opt_f);
    $opt_e && do
	{
	    print <DB>;
	    seek(DB, 0, 0);
	};

    &usage if !"$opt_i$opt_t$opt_c$opt_r$opt_e";
}

# Installation
sub install
{
    my($mode, @script, $perl, $perlGuess);

    $mode = (stat($0))[2];

    # Check for script executability
    print "Checking for executability...\n";
    chmod($mode | 0111, $0) if ($mode & 0111) != 0111 &&
	&isTrue(&confirm("Y", "Shall I make myself publically executable ",
	"[Y/n]? "));

    # Check for perl location and update script if necessary
    print "Checking for PERL location...\n";
    if (open(SCRIPT, "<$0"))
    {
	chomp($perl = <SCRIPT>);		# Read in first line
	$perl = substr($perl, 2);		# Strip off !#
	$perl =~ s/\s.*//;			# Strip off parameters
	chomp($perlGuess = `which perl5`);	# Definitely version 5
	chomp($perlGuess = `which perl`) if $perlGuess !~ m#^/#;

	if (!-x $perl && ($perl = &confirm($perlGuess, "Where is the PERL ",
	    "program [$perlGuess]? ")))
	{
	    print "Updating script\n";
	    @script = <SCRIPT>;			# Read in entire script
	    open(SCRIPT, ">$0");		# Re-open in write-mode
	    print SCRIPT "#!$perl\n", @script;	# Dump script
	}

	close(SCRIPT);
    }

    # Check for target HTML file and optionally create if it does not exist
    print "Checking for target HTML file...\n";
    if ($config{TargetFile} && !-e $config{TargetFile} &&
    	&isTrue(&confirm("Y", "\nThe target HTML file does not exist. The ",
	"Web server may not be able to create\nthis unless it has write ",
	"permission to the directory, and so you may have\nproblems. Should ",
	"I create an empty HTML file for you [Y/n]? ")))
    {
	print "Creating target HTML file...\n";
	&createHTML;
    }

    # Set the ACTION attribute in the header
    # XXX


    # Check target HTML file permissions and optionally chmod if not
    # world-writeable
    print "Checking target HTML file permission...\n";
    $mode = (stat($config{TargetFile}))[2];

    if ($mode ne "" && ($mode & 0222) != 0222 && &isTrue(&confirm("Y",
	"\nUnless the server is running as the superuser or as your user, it ",
	"will not\nbe able to update the HTML file (you will get ",
	"`$sysError $createHTMLError').\nShould I make the HTML file ",
	"writeable\nby all [Y/n]? ")))
    {
	print "Changing permission on HTML file...\n";
	chmod(0666, $config{TargetFile});
    }

    # Check for database file and optionally create if it does not exist
    print "Checking database file...\n";
    if (!-e $config{DatabaseFile} && &isTrue(&confirm("Y", "\nThe database ",
	"file does not exist. The Web server may not be able to create\nthis ",
	"unless it has write permission to the directory, and so you may ",
	"have\nproblems. Should I create an empty database file for you ",
	"[Y/n]? ")))
    {
	print "Creating database file...\n";
	open(DBFILE, ">$config{DatabaseFile}") ||
	    die("I was unable to create the database file.\n");
	close(DBFILE);
    }

    # Check database file permissions and optionally chmod if not
    # world-writeable
    print "Checking database file permission...\n";
    $mode = (stat($config{DatabaseFile}))[2];

    if ($mode ne "" && ($mode & 0222) != 0222 && &isTrue(&confirm("Y",
	"\nUnless the server is running as the superuser or as your user, it ",
	"will not\nbe able to update the database file (you will get ",
	"`$sysError $dataBaseError').\nShould I make the database file ",
	"writeable\nby all [Y/n]? ")))
    {
	print "Changing permission on HTML file...\n";
	chmod(0666, $config{DatabaseFile});
    }

    print "Installation complete.\n";
}

# Test all URLs in the database sequentially for valid links. Record all broken
# links and remove.
sub testAll
{
    my($confirm) = @_;
    my($conf, %delete, $line);

    TEST: while (<DB>)
    {
	chomp;
	s/$DBdelim.*//;
	print "Testing: $_... ";
	if (&testURL($_))
	{
	    print "OK.\n";
	}
	else
	{
	    print "\n\tCould not open";
	    $conf = ($confirm && &confirm("N",
		" - [Retry/Delete/Ignore] ? ")) || ((print "\n"), "d");
	    redo TEST if $conf =~ /^r/i;
	    $delete{$_}++ if $conf =~ /^d/i;
	}
    }
    seek(DB, 0, 0);			# Rewind for later

    &removeLinks(%delete);
}

# Prompt for a confirmation to remove links that match
sub removeLink
{
    my($text, $confirm) = @_;
    my(%delete, $url);

    while (<DB>)
    {
	$url = $_;
	chomp($url);
	$url =~ s/$DBdelim.*//;
	$delete{$url}++ if /$text/ && (!$confirm ||
	    &isTrue(&confirm("N", "Remove $url [y/N] ? ")));
    }
    seek(DB, 0, 0);			# Rewind for later

    &removeLinks(%delete);
}

# Remove URLs from database and update
sub removeLinks
{
    my(%delete) = @_;
    my(@db, $i);

    eval { flock(DB, 2); };	# Lock DB file (eval to trap if unimplemented)
    @db = <DB>;			# Read in entire database

    # Process Lifespan
    for ($i = 0; $i <= $#db; $i++)
    {
	chomp($_ = $db[$i]);
	s/$DBdelim.*//;

	if ($delete{$_})
	{
	    print "Deleting $_\n";
	    splice(@db, $i, 1);
	    $i--;
	}
    }

    seek(DB, 0, 0);		# Seek to BOF
    print DB @db;		# Regurgitate DB file
    truncate(DB, tell(DB));	# Truncate at current location

    eval { flock(DB, 8); };	# Unlock DB file
    seek(DB, 0, 0);		# Seek to BOF

    &createHTML;		# Let's update the HTML file
}

# Print out some text and wait for user input. The first paramater is the
# default which is returned if the user presses enter without typing anything.
sub confirm
{
    my($input);

    print @_[1 .. $#_];

    chomp($input = <STDIN>);
    $input || $_[0];
}

# Suck in the config file and return the options
sub readConfig
{
    my(%config) = %defaults;		# Read in defaults first
    my($line) = 0;

    open(CONFIG, "<$configFile") || &error($readConfigError);

    while (<CONFIG>)
    {
	$line++;
	s/\s+$//;			# Chop off any whitespace at end
	next if /^#/ || /^$/;		# Ignore comments and blank lines

	(($option, $value) = /\s*(\w+)\s*=\s*(.*)/) ||
	    &error("$configFileError - $line");

	$config{$option} = $value;
    }

    close(CONFIG);

    %config;				# Return config hash
}

# Returns true if config parameter is true. Accepts case-insensitive `Yes',
# `Y', `True', `1' as true.
sub isTrue
{
    my($param) = @_;

    scalar($param =~ /^((y(es)?)|(true)|1)$/i);
}



