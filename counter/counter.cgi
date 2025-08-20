#!/usr/bin/perl

# This is a graphical counter that is called from the <img> tag.
# Syantax is:
# <img src="pathToScript/img_counter.pl?CounterDataFile">
# So, for example, if your CounterDataFile was count.txt in the /file dir :
# <img src="cgi-bin/img_counter.pl?file/count.txt
#
# The script should be chmod 755, and your data file chmod 666 or 777


   $minLen = 6;           # minimum number of digits in bigmap
   $isHigh = 1;           # if 1, digits are 16 pixels high, to
                          # allow room for border
   $isInverse = 0;        # 1 = digits are white on black
                          # 0 = black on white
   $lockWait = 5;         # number of seconds to wait for lock
   $counterFile = $ENV{QUERY_STRING};   # where the logging file is.
                                        # This allows many counters
                                        # to run off of this script.

   &initialize;

   &incrementCount;

   &generateBitmap;
   &writeBitmap;

   exit(0);


sub writeBitmap {
   print ("Content-type: image/x-xbitmap\n\n");
   if ($isHigh) {
      printf ("#define count_width %d\n#define count_height 16\n", 
              $len*8);
   }
   else {
      printf ("#define count_width %d\n#define count_height 10\n", 
              $len*8);
   }
   printf STDOUT "static char count_bits[] = {\n";
   for($i = 0; $i < ($#bytes + 1); $i++) {
      print("0x$bytes[$i]");
      if ($i != $#bytes) {
         print(",");
         if (($i+1) % 7 == 0) {
            print("\n");
         }
      }
   }
   print("};\n");
}

# generateBitmap() - $count contains number to display
#                    $minLen contains minimum number of digits to display
#                    $isHigh is one for 16 bit high numbers (else 10)
#                    $isInverse is one for reverse (white on black);
sub generateBitmap {
   $count = $totalReads;
   @bytes = ();
   $len = length($count) > $minLen ? length($count) : $minLen;
   $formattedCount = sprintf("%0${len}d",$count);
   if ($isHigh) {
      for ($i = 0; $i < $len*3; $i++ ) {
         if ($isInverse) {
            push(@bytes,"ff");       # add three blank rows to each digit
         }
         else {
            push(@bytes,"00");
         }
      }
   }
   for ($y=0; $y < 10; $y++) {
       for ($x=0; $x < $len; $x++) {
           $digit = substr($formattedCount,$x,1);
           if ($isInverse) {             # $inv = 1 for inverted text
               $byte = substr(@invdigits[$digit],$y*3,2);
           } 
           else {
               $byte = substr(@digits[$digit],$y*3,2);
           }
           push(@bytes,$byte);
       }
   }
   if ($isHigh) {
      for ($i = 0; $i < $len*3; $i++ ) {
         if ($isInverse) {
            push(@bytes,"ff");       # add three blank rows to each digit
         }
         else {
            push(@bytes,"00");
         }
      }
   }
}

sub initialize {
  # $hostname = $ENV{REMOTE_HOST};
  # $host     = $ENV{REMOTE_ADDR};
  # $port     = $ENV{SERVER_PORT};
   # bitmap for each digit
   #  Each digit is 8 pixels wide, 10 high
   #  @invdigits are white on black, @digits black on white
   @invdigits = ("c3 99 99 99 99 99 99 99 99 c3",  # 0
                 "cf c7 cf cf cf cf cf cf cf c7",  # 1
                 "c3 99 9f 9f cf e7 f3 f9 f9 81",  # 2
                 "c3 99 9f 9f c7 9f 9f 9f 99 c3",  # 3
                 "cf cf c7 c7 cb cb cd 81 cf 87",  # 4
                 "81 f9 f9 f9 c1 9f 9f 9f 99 c3",  # 5
                 "c7 f3 f9 f9 c1 99 99 99 99 c3",  # 6
                 "81 99 9f 9f cf cf e7 e7 f3 f3",  # 7
                 "c3 99 99 99 c3 99 99 99 99 c3",  # 8
                 "c3 99 99 99 99 83 9f 9f cf e3"); # 9
   
      @digits = ("3c 66 66 66 66 66 66 66 66 3c",  # 0
                 "30 38 30 30 30 30 30 30 30 30",  # 1
                 "3c 66 60 60 30 18 0c 06 06 7e",  # 2
                 "3c 66 60 60 38 60 60 60 66 3c",  # 3
                 "30 30 38 38 34 34 32 7e 30 78",  # 4
                 "7e 06 06 06 3e 60 60 60 66 3c",  # 5
                 "38 0c 06 06 3e 66 66 66 66 3c",  # 6
                 "7e 66 60 60 30 30 18 18 0c 0c",  # 7
                 "3c 66 66 66 3c 66 66 66 66 3c",  # 8
                 "3c 66 66 66 66 7c 60 60 30 1c"); # 9
}
sub incrementCount {
   &incrementTotalReads;
}


sub incrementTotalReads {
   if (-e $counterFile) {
     open(COUNT,"$counterFile") || die("Can't open $counterFile: $!\n");
   }
   $totalReads = <COUNT>;
   #chop $totalReads;
   close(COUNT);

     $totalReads++;
     open(COUNT,">$counterFile") || die "$0: can\'t open $counterFile: $!\n";
     print (COUNT "$totalReads\n");
     close(COUNT);


}
