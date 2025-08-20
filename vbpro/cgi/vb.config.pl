#################################################################
#  _     _ _      _                  ______              _      #
# (_)   (_|_)    (_)  _             (____  \            | | PRO #
#  _     _ _  ___ _ _| |_ ___   ____ ____)  ) ___   ___ | |  _  #
# | |   | | |/___) (_   _) _ \ / ___)  __  ( / _ \ / _ \| |_/ ) #
#  \ \ / /| |___ | | | || |_| | |   | |__)  ) |_| | |_| |  _ (  #
#   \___/ |_(___/|_|  \__)___/|_|   |______/ \___/ \___/|_| \_) #
# Configuration File                                            #
#                                                               #
# You must setup and configure all of the following items       #
# before the VBPro system will work properly. Also, be sure     #
# that all of the individual CGIs point to the configuration    #
# file.                                                         #
#################################################################

# $templatedir - This is the path of the directory where VBPro
# template files are stored. These files are used only in the
# master admin program. Nevertheless, they are crucial; at least
# one template file must be installed in this directory for the
# master admin program to work.
$templatedir = "/home/www/policyofliberty/vbpro/cgi/vbfiles/vbtemplates";

# $masterpass - This is the path of the password file for the
# master administrator. A default version of this file was
# included in the VBPro distribution. 
$masterpass = "/home/www/policyofliberty/vbpro/cgi/vbfiles/masteradmin.pass";

# $cgilib - This is the path of the CGI-LIB library. Written by
# Steve Brenner, CGI-LIB is a popular file containing many
# functions that making processing forms, among other things,
# easier for developers such as Command-O Software. This file
# is required.
$cgilib = "/library/cgi-lib.pl";

# $sharedlib - Path to the Command-O VBPro shared library. This
# file contains VBPro code that is used by most of the three
# programs. Putting it all here saves space since it doesn't need to
# be written multiple times.
$sharedlib = "/home/www/policyofliberty/vbpro/cgi/vbfiles/vb.shared.lib.pl";

# $mailprog - This is the location of your mail program on your
# server (this is usually called sendmail). If you want to
# find this and have a shell account, login and type
# "which sendmail" (no quotes).
$mailprog = "/usr/sbin/sendmail";

# $basebookdir - This is the path of the directory where books
# will be created. This may be something like
# /usr/local/etc/httpd/vbpro/books or something similar to
# that. Information about guestbooks will be stored in this
# directory. BE CAREFUL -- don't end this value with a /!
# Follow the example above.
$basebookdir = "/home/www/policyofliberty/vbpro/books";

# $picture_url - This is the URL of the directory storing
# the factory-default images used in the various admin
# programs.
$picture_url = "http://policyofliberty.net/vbpro/pics";

# $logouturl - URL of a page to show after the user or admin is
# disconnected from the admin programs. This can be anything, really.
$logouturl = "http://policyofliberty.net/vbpro/loggedout.html";

# $newbooks_path - When a new guestbook is created by the Master Admin
# module, it needs a directory on your web site to store its files.
# This variable sets the default directory to use.
#
# For example, if you created a new book named "test", another directory
# would be created in this directory, called "test". This test directory
# would store the entry file, the form, and the thanks file for the
# new guestbook.
#
# Note that once you set this, you are not really stuck with it. If
# you want to create a new guestbook elsewhere, you simply have to
# change the path from this to a new path while you're creating the book
# using the master admin program. Be sure not to end with a "/"!
$newbooks_path = "/home/www/policyofliberty/vbpro";

# $newbooks_url - URL for the folder described above. Be sure not to end
# with a "/"!
$newbooks_url = "http://policyofliberty.net/vbpro";

# $cgi_url - URL of the vbpro (form posting) CGI. This value is used
# by the Master Admin program when making new books. Particularly, it
# will automatically place this value in templates that ask for it.
# (All Command-O templates use this technique.)
$cgi_url = "http://policyofliberty.net/vbpro/cgi/vbpro.cgi";

# $inactive_time - Maximum allowable idle time between action on
# the admin programs. This value is in minutes. You should probably set
# this value anywhere from 5-15 minutes. Too small a value will frustrate
# anyone who takes a long time to modify a book or fill out a form. Too
# big a value will dimish this feature's usefullness.
$inactive_time = 15;
