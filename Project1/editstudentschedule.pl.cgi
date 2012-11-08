#!/usr/bin/perl

#This script runs the student profile capabilities, which include viewing
#the instructors' available lesson slots, and adding a lesson.

use strict;

use HTML::CalendarMonthSimple;
use CGI::Cookie;

my $calendar_1;
my $calendar_2;
my $insCal_1;
my $insCal_2;
my $studFile;
my $chosenInsFile;
my $inListFile = "BIGInstructorList.txt";

print "Content-type: text/html\n\n";
	print <<EndOfPrinting;
<html><head>
		<title>InstraSchedule</title>
		<link rel="stylesheet" type="text/css" href="css/main.css" media="screen" />
		<link rel="stylesheet" type="text/css" href="css/print.css" media="print" />
		<!--[if lte IE 6]>
		<link rel="stylesheet" type="text/css" href="css/ie6_or_less.css" />
		<![endif]-->
		<script type="text/javascript" src="js/common.js"></script>
<title>
InstraSchedule Sign Up</title></head>
<body id = "type-a">
	<div id="wrap">

			<div id="header">
				<div id="site-name"> InstraSchedule </div>
				<ul id="nav">
					<li><a href="./viewstudentschedule.pl.cgi"> View My Calendar </a></li>
					<li><a href="./logout.pl.cgi"> Logout </a></li>
				</ul>
			</div>
	<div id="content-wrap">
	<div id = "content">
EndOfPrinting

my %cookies = CGI::Cookie->fetch;
for (keys %cookies)
{
       my $current = $cookies{$_};
       if($current->name =~ m/InstraSchedulestudentloginfo/)
       {BuildCalName($current->name);}
}
sub BuildCalName()
{
       my $userID = $_;
       $userID =~ s/InstraSchedulestudentloginfo=//;
       $userID =~ s/@//;
	   my $filename = "STUDENTCAL" . $userID . ".txt";
       $studFile = $filename;
}

my $l = $ENV{CONTENT_LENGTH};

if($l==0)
{
	selectInstructor($inListFile);
}

else
{
	read(STDIN, my $form, $ENV{'CONTENT_LENGTH'});
	my @pairs = split(/&/, $form);
	my %F;
	my $pair;
	my $name;
	my $value;
	foreach $pair (@pairs) 
	{
		($name, $value) = split(/=/, $pair);
		$value =~ tr/+/ /;
		$value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
		$F{$name} = $value;
	}
	
	if($F{'selectInstructor'})
	{
		my $instructor = $F{'instructormenu'};
		#print "<html><p>input: $instructor</p></html>";
		my $printName = $instructor;
		$instructor =~ s/@//;
		$chosenInsFile = "INSTRUCTORCAL" . $instructor .".txt";
		#print "<html><p>input: $chosenInsFile</p></html>";
		selectedInstructorSched($chosenInsFile);
		print "<html><h1>$printName\'s Calendar</h1></html>";
		printInstructorCals();
		my ($isP, $li) = containsVideo($chosenInsFile);
		if($isP)
		{
			printVideo($li);
		}			
		addLessonMenu($chosenInsFile, $studFile);		
	}
	elsif($F{'addLesson'})
	{
		my $lesson = $F{'saddmenu'};
		$chosenInsFile = $F{'ins'};
		#print "<html><h1>$chosenInsFile</h1></html>";
		genCalendars($studFile);
		my $v = addStudentLesson($lesson, $studFile, $chosenInsFile);
		if($v)
		{
			print "<html><h1>Lesson Added</h1></html>";
			returnHome();
		}
		else
		{
			returnHome();
		}
	}
	elsif($F{'returnHome'})
	{
		selectInstructor($inListFile);
	}
}

###############################################################################
#Methods used above

###############################################################################

#This prints the student's upcoming lessons

sub printSchedule
{
	print $calendar_1->as_HTML;
	print "<br><br>";
	print $calendar_2->as_HTML;
}

###############################################################################

#This generates the student's schedule from the student's sheet. 

sub genCalendars
{
	my $lessonsFile = $_[0];
   
	my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) =
		localtime(time);
    $year += 1900; #Gets correct year
    $mon++; #Adjusts month index
    #Makes 1st calendar (empty)
	$calendar_1 = new HTML::CalendarMonthSimple('year'=>$year,'month'=>$mon);
	$calendar_1->bgcolor('FFFF99');
	$calendar_1->border(10);
	#Makes 2nd calendar (empty)
	if($mon == 12) #if December
	{
		$year++;
	}
	$mon++;
	my $nextMonth = $mon % 12;
	
	$calendar_2 = new HTML::CalendarMonthSimple('year'=>$year,'month'=>$nextMonth);
	$calendar_2->border(10);
	$calendar_2->bgcolor('FFFF99');

	#Rename variables for clarity below
	
	my $month_1 = --$mon;
	my $month_2 = $nextMonth;

	#Build the calendar from the lesson sheet
	#The lesson sheet stores info as:
	#"$m $day $slotholder $startTime $endTime\n";

   my $line;

   open(FH, "$lessonsFile");

   while(<FH>)
   {
		$line = $_;
		chomp($line);
		if($line =~ m/(\d+)(\s)(\d+)(\s)([a-zA-Z0-9_\-\.]+)(\s)(\d+)(\.)(\d+)(\s)(\d+)(\.)(\d+)/)
		{
			my($month, $day, $student, $start, $end) = split(" ", $line);

			if($month != undef) #checks for blank line
			{
				#adjust start and end formatting
				my ($s_hour, $s_mins, $e_hour, $e_mins);

				if($start =~ m/(\d+)(\.)(\d+)/)
				{
					$s_hour = $1;
					$s_mins = $3;
					$s_mins = $s_mins * .6; #multiply by 60, divide by 100
					if($s_mins == 0)
					{
						$s_mins = "00";
					}
					if($s_mins == 3)
					{
						$s_mins = "30";
					}
					$start = $s_hour . ":" . $s_mins;
				}

				if($end =~ m/(\d+)(\.)(\d+)/)
				{
					$e_hour = $1;
					$e_mins = $3;
					$e_mins = $e_mins * .6;
					if($e_mins == 0)
					{
						$e_mins = "00";
					}
					if($e_mins == 3)
					{
						$e_mins = "30";
					}
					$end = $e_hour . ":" . $e_mins;
				}

				my $lesson_string = "$student $start-$end<br><br>";		
		
				if($month == $month_1) #First calendar
				{
					$calendar_1->addcontent($day, $lesson_string);
				}
				elsif($month == $month_2) #Second calendar
				{
					$calendar_2->addcontent($day, $lesson_string);
				}
			}#End of if
		}
	}#End of file reading
	close(FH);
}

###############################################################################

#This refreshes the student's schedule and student sheet when the months switch
#over

sub refCalendars
{
	my $docName = $_[0]; #The associated lesson sheet
	my $month2 = $calendar_2->month();
	my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) =
		localtime(time);
    $year += 1900; #Gets correct year
    $mon++; #Gets correct month
	if($mon == $month2)#If the current month corresponds to the 2nd cal
					   #then we need to shift the calendars
	{	
		my $line;
		my @lessons;
		open(FH, $docName)||die "Error opening $docName";
		#create an array of only lessons from the current month, which was
		#month 2
		while(<FH>)
		{
			$line = $_;
			chomp($line);
			if($line =~ m/($month2)(\s)(\d+)(\s)([a-zA-Z0-9_\-\.]+)(\s)(\d+)(\.)(\d+)(\s)(\d+)(\.)(\d+)/)
			{
				push(@lessons, $line);
			}
		}
		#Print the updated lesson sheet
		open(FH2, ">$docName") || die "Error opening $docName";
		for my $l(@lessons)
		{
			print FH2 $l . "\n";
		}
	}
}

###############################################################################

#This prints a select menu to view an instructor's available lessons

sub selectInstructor
{

	my $instructors = $_[0]; #The instructors list file
	my @i_list;
	my $line;
	open(FH, $instructors) || die "Couldn't open $instructors.";
	while(<FH>)
	{
		$line = $_;
		chomp($line);
		push(@i_list, $line);
	}

	my $message;
	my $empty = 0;
	if(scalar @i_list == 0) #Nothing valid to remove
	{
	 	$message = "No available instructors";
	 	push(@i_list, $message);
		$empty = 1;
	}
unless($empty)
{
print <<END_OF_PRINTING;
<html>
<body>
<h1>Select an Instructor</h1>
<form action="editstudentschedule.pl.cgi" method=POST>
<select name = "instructormenu">
END_OF_PRINTING
for my $l(@i_list)
{
	print"<option value = \"$l\">$l</option>";
}
print<<END_OF_PRINTING;
</select>
<input type="submit" name = "selectInstructor" value="Submit">
</body>
<html>
END_OF_PRINTING
}
else
{
	print "<html><p>$message</p></html>";
}

}

###############################################################################

#This generates the calendars of the selected instructor

sub selectedInstructorSched
{
	my $instructorFile = $_[0];
	my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) =
		localtime(time);
    $year += 1900; #Gets correct year
    $mon++; #Adjusts month index
    #Makes 1st calendar (empty)
	$insCal_1 = new HTML::CalendarMonthSimple('year'=>$year,'month'=>$mon);
	$insCal_1->bgcolor('#3BB9FF');
	$insCal_1->border(10);
	#Makes 2nd calendar (empty)
	if($mon == 12) #if December
	{
		$year++;
	}
	$mon++;
	my $nextMonth = $mon % 12;
	
	$insCal_2 = new HTML::CalendarMonthSimple('year'=>$year,'month'=>$nextMonth);
	$insCal_2->border(10);
	$insCal_2->bgcolor('#3BB9FF');

	#Rename variables for clarity below
	
	my $month_1 = --$mon;
	my $month_2 = $nextMonth;

	#Build the calendar from the lesson sheet
	#The lesson sheet stores info as:
	#"$m $day $slotholder $startTime $endTime\n";

	#This only prints slots that are available for
	#user privacy

   my $line;

    open(FH, "$instructorFile");
	#my $test;
	#while(<FH>)
	#{
		#$test = $_;
		#chomp($test);
		#if($test =~ m/(\d+)(\s)(\d+)(\s)(AVAILABLE\*SLOT)(\s)(\d+)(\.)(\d+)(\s)(\d+)(\.)(\d+)/)
		#{
			#print "<html><p>Hello $test</p></html>";
		#}
	#}


   while(<FH>)
   {
		$line = $_;
		chomp($line);
		if($line =~ m/(\d+)(\s)(\d+)(\s)(AVAILABLE\*SLOT)(\s)(\d+)(\.)(\d+)(\s)(\d+)(\.)(\d+)/)
		{
			#print "<html><p>Lesson Found</p></html>";
			my($month, $day, $openSlot, $start, $end) = split(" ", $line);

			if($month != undef) #checks for blank line
			{
				#adjust start and end formatting
				my ($s_hour, $s_mins, $e_hour, $e_mins);

				if($start =~ m/(\d+)(\.)(\d+)/)
				{
					$s_hour = $1;
					$s_mins = $3;
					$s_mins = $s_mins * .6; #multiply by 60, divide by 100
					if($s_mins == 0)
					{
						$s_mins = "00";
					}
					if($s_mins == 3)
					{
						$s_mins = "30";
					}
					$start = $s_hour . ":" . $s_mins;
				}

				if($end =~ m/(\d+)(\.)(\d+)/)
				{
					$e_hour = $1;
					$e_mins = $3;
					$e_mins = $e_mins * .6;
					if($e_mins == 0)
					{
						$e_mins = "00";
					}
					if($e_mins == 3)
					{
						$e_mins = "30";
					}
					$end = $e_hour . ":" . $e_mins;
				}

				my $lesson_string = "$openSlot $start-$end<br><br>";		
		
				if($month == $month_1) #First calendar
				{
					$insCal_1->addcontent($day, $lesson_string);
				}
				elsif($month == $month_2) #Second calendar
				{
					$insCal_2->addcontent($day, $lesson_string);
				}
			}#End of if
		}
	}#End of file reading
	close(FH);
}

###############################################################################

#This prints the selected instructor's calendars

sub printInstructorCals
{
	print $insCal_1->as_HTML;
	print "<br><br>";
	print $insCal_2->as_HTML;
}

###############################################################################

#This makes a return home button

sub returnHome
{
	print "<html><form action=\"editstudentschedule.pl.cgi\" method=POST></html>";
	print "<html><br><input type=\"submit\" name =\"returnHome\"value=\"Return Home\">";
}

###############################################################################

#This prints a drop down of available lessons, from which the student can pick
#and schedule a lesson

sub addLessonMenu
{
	my $lessons = $_[0]; #Gets selected instructors lesson sheet
	#print "<html><p>File: $lessons</p></html>";
	my $user = $_[1];
	$user =~ s/STUDENTCAL//;
	$user =~ s/.txt//;

	my $line;
	my @months = ("0", "Jan", "Feb","Mar","Apr","May","Jun",
	"Jul","Aug","Sep","Oct","Nov","Dec");

	my $mon;
	my $year;
	my $check_day;

	#The following is done to get the current day.
	#Lessons can only be removed if they are after
	#the current day. That is, if it is April 10,
	#The lessons from April 1 through April 10, inclusive
	#will not be printed as options for cancellation.

	my ($sec,$min,$hour,$mday, $m) =
			localtime(time);

$m++; #shifts index
my $current_month = $m;
my $next_month = $m +1;

my @list; #Will hold lessons
open(FH, "$lessons");
while(<FH>)
{
	$line = $_;
		
	my $lesson_option;
	chomp($line);
	#				  1:$m 			  3:$day     5:$slotholder         7-9:$startTime    11-13:$endTime
	if($line =~ m/(\d+)(\s)(\d+)(\s)(AVAILABLE\*SLOT)(\s)(\d+)(\.)(\d+)(\s)(\d+)(\.)(\d+)/)
	{
		#print "<html><p>Lesson Found</p></html>";
		$check_day = $3;
		my $valid_this;
		my $valid_next;
		if(($1 == $current_month && $check_day > $mday) || ($1 == $next_month)) #print as option to delete only if lesson comes after today
		{		
			#modify start and end time for printing
			my $s_mins = $9 * .6; #multiply by 60, divide by 100
			if($s_mins == 0)
			{
				$s_mins = "00";
			}
			if($s_mins == 3)
			{
				$s_mins = "30";
			}
			my $e_mins = $13 * .6;
			if($e_mins == 0)
			{
				$e_mins = "00";
			}
			if($e_mins == 3)
			{
				$e_mins = "30";
			}
			$lesson_option = $months[$1] . " " . $3 . " " . $5 . " " . $7 . ":" . $s_mins ."-" . $11 .":" .$e_mins;
			push(@list, $lesson_option);
		}
	}
}
my $message;
my $empty = 0;
if(scalar @list == 0) #Nothing valid to remove
{
	 $message = "No available lessons";
	 push(@list, $message);
	$empty = 1;
}

unless($empty)
{
print <<END_OF_PRINTING;
<html>
<body>
<h1>Pick a Lesson Time</h1>
<form action="editstudentschedule.pl.cgi" method=POST>
<select name = "saddmenu">
END_OF_PRINTING
for my $l(@list)
{
	print"<option value = \"$l\">$l</option>";
}
print<<END_OF_PRINTING;
</select>
<input type="submit" name = "addLesson" value="Add">
<input type = "text" name = "ins" id="hiddenfield" value = $lessons>
</body>
<html>
END_OF_PRINTING

	my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
	my $stat = "LESSONADD;" . $user . "(" . $min . ":" . $hour . ":" . $mday . ":" . (++$mon) . ":" . ($year+1900) . ")\n";
	open (FH, ">>BIGStudentStats.txt") || die "Died opening BIGStudentStats.txt";
	print FH $stat;
	close FH;

}
else
{
	print"<html><p>$message</p></html>";
}

}

###############################################################################

#Gets appropriate calendar

sub getCal
{
	my $m = $_[0];
	my ($sec,$min,$hour,$mday,$mon) =
		localtime(time);
    $mon++; #Adjusts month index
	if($m ==$mon)
	{
		return $calendar_1;
	}
	else
	{
		return $calendar_2;
	}
}	

###############################################################################

#This adds the lesson to the lesson sheet, modifying the instructor's lesson
#sheet and the student's lesson sheet

sub addStudentLesson
{
	#get inputs from post - the selected lesson string
	my $lessonString = $_[0];
	my $student_sheet = $_[1];
	my $instructor_sheet = $_[2];

	my ($m, $day, $slot, $t) =  split(" ", $lessonString);
	my($s_time, $e_time) = split("\-", $t);
	my ($s_hour, $s_mins) = split(":", $s_time);
	my ($e_hour, $e_mins) = split(":", $e_time);
	my $startTime;
	my $endTime;

	my %monthHash;
	$monthHash{'Jan'} = 1;
	$monthHash{'Feb'} = 2;
	$monthHash{'Mar'} = 3;
	$monthHash{'Apr'} = 4;
	$monthHash{'May'} = 5;
	$monthHash{'Jun'} = 6;
	$monthHash{'Jul'} = 7;
	$monthHash{'Aug'} = 8;
	$monthHash{'Sep'} = 9;
	$monthHash{'Oct'} = 10;
	$monthHash{'Nov'} = 11;
	$monthHash{'Dec'} = 12;

	$m = $monthHash{$m};

	#Adjust to decimal

	if($s_mins == "00"){$s_mins = .0;}
	elsif($s_mins == "15"){$s_mins = .25;}
	elsif($s_mins == "30"){$s_mins = .50;}
	elsif($s_mins == "45"){$s_mins = .75;}
	
	if($e_mins == "00"){$e_mins = .0;}
	elsif($e_mins == "15"){$e_mins = .25;}
	elsif($e_mins == "30"){$e_mins = .50;}
	elsif($e_mins == "45"){$e_mins = .75;}


	#Get number from string for hour

	if($s_hour =~ m/(\d+)/)
	{
		$s_hour = $1;
	}

	if($e_hour =~ m/(\d+)/)
	{
		$e_hour = $1;
	}

	$startTime = $s_hour + $s_mins;
	$endTime = $e_hour + $e_mins;
	
	my $studCal = getCal($m);

	#Check to see if the slot chosen overlaps with another lesson
	#already schedule

	my $length = 64; #the last slot is 23:45-24:00; corresponds to 63
	my @slots_list;
	my $index;
	for($index = 0; $index <= 63; $index++)
	{
		$slots_list[$index] = 0; #initializes each slot to empty;
		#print "<html><br>$index : $slots_list[$index]</html>";
	}

	#Get info from the calendar
	my $lessons = $calendar_1->getcontent($day);
	my @lessons_list = split("<br><br>", $lessons); #Gets day's lessons, stored
											 #in 24-hour time

	my ($start, $end,$start_hour, $start_mins, $end_hour,$end_mins);
	#Gets lessons time information and flags slots in the array
	#This information is taken directly from the specified calendar day

	for my $l(@lessons_list)
	{	#corresponds to (1)login name, and (3)time slot
		if($l =~ m/([a-zA-Z0-9_\-\.]+)(\s)(\d+:\d+\-\d+:\d+)/)
		{
			my $time = $3;
			($start, $end) = split("\-", $time);
			if($start =~ m/(\d+)(:)(\d+)/)
			{
				$start_hour = $1;
				$start_mins = $3;
				if($start_mins == 15)
				{
					$start_mins = .25;
				}
				elsif($start_mins == 30)
				{
					$start_mins = .5;
				}
				elsif($start_mins == 45)
				{
					$start_mins = .75;
				}
				elsif($start_mins == 00)
				{
					$start_mins = .0;
				}
			}#End for start time
			if($end =~ m/(\d+)(:)(\d+)/)
			{
				$end_hour = $1;
				$end_mins = $3;
				if($end_mins == 15)
				{
					$end_mins = .25;
				}
				elsif($end_mins == 30)
				{
					$end_mins = .5;
				}
				elsif($end_mins == 45)
				{
					$end_mins = .75;
				}
				elsif($end_mins == 00)
				{
					$end_mins = .0;
				}
			}#End for end time
		}#End of reg-ex check
		
		#flagging the array
		
		#first shift the hours index, such that 8 corresponds
		#to 0, then multiply by 4 to account for minutes slots
		$start_hour = $start_hour - 8;
		$start_hour = $start_hour * 4;
		$end_hour = $end_hour - 8;
		$end_hour = $end_hour * 4;

		#now get the offset for the minutes, i.e. multiply by 4
		$start_mins = $start_mins * 4;
		$end_mins = $end_mins * 4;
		#now add to get the start position and end position in the
		#array for the lesson;
		my $start_index = $start_hour + $start_mins;
		my $end_index = $end_hour + $end_mins;
		
		#Adjust end index for fencepost, i.e. subtract 1
		$end_index--; 
		#print"<html><br>lesson: $l start index: $start_index</html>";
		#print"<html><br>lesson: $l end index: $end_index</html>";
		#flag each position that fits the slot in the array

		my $i;
		for($i = $start_index; $i<=$end_index; $i++)
		{
			$slots_list[$i] = 1;
		}

	}#End of for loop

	#Now check against the input lesson
		
	#Adjust $startTime and $endTime
	my $s_index = ($startTime - 8) * 4;
	my $e_index = (($endTime - 8) * 4);
	#Adjust end time for fence post, i.e. -1
	$e_index--;
	
	my $j;
	my $error_message = "<p>Your input overlaps with another lesson.<br>
		Please enter a valid lesson slot.</p><br>";
	my $valid = 1; #initialized to true
	for($j = $s_index; $j<=$e_index; $j++)
	{
		if($slots_list[$j] == 1)#if there is an overlap
		{
			print "<html><h1>$error_message</h1></html>";
			$valid = 0;
			$j = $e_index + 1; #breaks for loop
		}
	}

	#Add the lesson to the student sheet. Modify instructor sheet.
	#Adds as: (example, April 10 from 1 pm to 2:15 pm)
	#4 10 student 13 14.25

	if($valid)
	{
		my $user;
		if($student_sheet =~ m/(STUDENTCAL)([a-zA-Z0-9_\-\.]+)(\.txt)/)
		{
			$user = $2;
		}
		open(FH, ">>$student_sheet") || die "Error opening $student_sheet";
		#print"<html><br>file name: $lesson_sheet</html>";
		my $mo = $studCal->month();
		#Checks to make sure prints with proper formatting

		unless($endTime =~ m/(\d+)(.)(\d+)/)
		{
			$endTime = $endTime .".0";
		}
		unless($startTime =~ m/(\d+)(.)(\d+)/)
		{
			$startTime = $startTime .".0";
		}
		print FH "$mo $day $user $startTime $endTime\n";
		#print"<html><br>$m $day $open $startTime $endTime</html>";
		close(FH);

		#Modify instructor sheet
		my @less_list;
		my $li;
		open(FH2, "$instructor_sheet") || die "Error opening $instructor_sheet";
		while(<FH2>)
		{
			$li = $_;
			chomp($li);
			unless($li =~ m/($mo)(\s)($day)(\s)(AVAILABLE\*SLOT)(\s)($startTime)(\s)($endTime)/)
			{
				push(@less_list,$li);
			}
		}
		close(FH2);
		
		open(FH3, ">$instructor_sheet") || die "Error opening $instructor_sheet";
		for my$less(@less_list)
		{
			print FH3 $less . "\n";
		}
		print FH3 "$mo $day $user $startTime $endTime\n"; #modified lesson
		close(FH3);		
	}
	if($valid)
	{
		return 1;
	}
	else
	{
		return 0;
	}				
}

###############################################################################

#Prints instructor's demo video

sub printVideo
{
my $l = $_[0];
print<<END_OF_PRINTING;
<html>
<body>
<br><br>
Instructor's Demo Video:
<br>
<iframe width="420" height="345"
src="$l">
</iframe>
</body>
</html>


END_OF_PRINTING
}

###############################################################################

#This method checks to see if a lesson sheet contains

sub containsVideo
{
	my $sheet = $_[0]; #Instructor sheet
	open(FH, $sheet);
	my $line;
	my $URL;
	my @returns;
	while(<FH>)
	{
		$line = $_;
		chomp($line);
		if($line =~ m/(http:\/\/)(www\.)(youtube)(\.com)/)
		{
			$URL = $line;
			push(@returns, 1);
			push(@returns, $URL);
			return @returns;
		}
	}
	close FH;
	push(@returns, 0); #No URL found
	return @returns;			
}
