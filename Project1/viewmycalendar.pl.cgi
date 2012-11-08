#!/usr/bin/perl

#This script runs the instructor profile capabilities, which include adding
#slots, removing lesson slots, adding a demo video, removing a demo video,
#and viewing the upcoming lesson schedule. 

use strict;

use HTML::CalendarMonthSimple;
use CGI::Cookie;
use PDF::Create;
use LWP::Simple;

#Main method

my $calendar_1;
my $calendar_2;
my $calFile;

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
					<li><a href="./viewmycalendar.pl.cgi"> View My Calendar </a></li>
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
       if($current->name =~ m/InstraScheduleinstructorloginfo/)
       {BuildCalName($current->name);}
}
sub BuildCalName()
{
       my $userID = $_;
       $userID =~ s/InstraScheduleinstructorloginfo=//;
       $userID =~ s/@//;
	   my $filename = "INSTRUCTORCAL" . $userID . ".txt";
       $calFile = $filename;
}

my $l = $ENV{CONTENT_LENGTH};

#Page shown upon log-in

if($l==0)
{
	generateCalendars($calFile);
	refreshLessonSheet($calFile);
	generateCalendars($calFile);
	print"<html><h1>Upcoming Lessons</h1></html>";
	printBothCalendars();
	monthButton();
	my ($isP, $li) = containsVideo($calFile);
	unless($isP)
	{
		videoField();
	}
	else
	{
		removeVideoField();
		printVideo($li);
	}
	print "<html><FORM METHOD=\"POST\" ACTION=\"viewmycalendar.pl.cgi\">\n";
	print "<INPUT TYPE=\"submit\" name = \"printpdf\" VALUE=\"View PDF of Tomorrow's Lessons\">\n";
	print "</FORM></html>\n";
}

else
{
	my $current_cal;
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
	
	if($F{'monthSubmit'})
	{
		generateCalendars($calFile);
		refreshLessonSheet($calFile);
		generateCalendars($calFile);
		my $month_input = $F{'month'};
		$current_cal = calToEdit($month_input);
		printCurrentCalendar($current_cal);
		lessonButtons($month_input);
		removeMenu($calFile, $month_input);
	}

	elsif($F{'addLesson'})
	{
		generateCalendars($calFile);
		refreshLessonSheet($calFile);
		generateCalendars($calFile);
		my $d = $F{'day'};
		my $sTime = $F{'starttime'};
		my $dur = $F{'duration'};
		my $mont = $F{'mon'};
		addLesson($d, $sTime, $dur, $mont, $calFile);
		print"<html><h1>Upcoming Lessons</h1></html>";
		generateCalendars($calFile);
		printBothCalendars();
		monthButton();
		my ($isPr, $lin) = containsVideo($calFile);
		unless($isPr)
		{
			videoField();
		}
		else
		{
			removeVideoField();
			printVideo($lin);
		}
	}
	elsif ($F{'removeLesson'})
	{
		generateCalendars($calFile);
		refreshLessonSheet($calFile);
		generateCalendars($calFile);
		my $l_s = $F{'removemenu'};
		my $mot = $F{'mot'};
		removeLesson($l_s, $mot, $calFile);
		generateCalendars($calFile);
		print"<html><h1>Lesson Removed</h1></html>";
		returnHome();
	}
	elsif($F{'returnHome'})
	{
		print"<html><h1>Upcoming Lessons</h1></html>";
		generateCalendars($calFile);
		refreshLessonSheet($calFile);
		generateCalendars($calFile);
		printBothCalendars();
		monthButton();
		my ($isPr, $lin) = containsVideo($calFile);
		unless($isPr)
		{
			videoField();
		}
		else
		{
			removeVideoField();
			printVideo($lin);
		}
		print "<html><FORM METHOD=\"POST\" ACTION=\"viewmycalendar.pl.cgi\">\n";
		print "<INPUT TYPE=\"submit\" name = \"printpdf\" VALUE=\"View PDF of Tomorrow's Lessons\">\n";
		print "</FORM></html>\n";
	}
	elsif($F{'addLink'})
	{
		my $link = $F{'vidlink'};
		#print"<html><p>Link: $link</p></html>";
		my ($isPresent, $l) = containsVideo($calFile);
		#print"<html><p>isPresent: $isPresent</p></html>";
		#print"<html><p>URL: $l</p></html>";
		unless($isPresent)
		{
			addVideo($calFile, $link);
		}
		print"<html><h1>Video Added</h1></html>";
		returnHome();
	}
	elsif($F{'removeLink'})
	{
		removeVideo($calFile);
		print"<html><h1>Video Removed</h1></html>";	
		returnHome();
	}

	elsif($F{'printpdf'})
	{
		generateCalendars($calFile);
		my $pdfFile = makePDF($calFile);

		print "<html><a href=\"./$pdfFile\"> Open PDF </a></html>";
		returnHome();
	}	
}


###############################################################################
#Methods used above

###############################################################################

#This method returns to the home screen of the two calendars

sub returnHome
{
	print "<html><form action=\"viewmycalendar.pl.cgi\" method=POST></html>";
	print "<html><br><input type=\"submit\" name =\"returnHome\"value=\"Return Home\">";
}

###############################################################################

#This sub creates a drop down menu that lists the two current calendar months -
#this month and next - giving the instructor the option of picking a month
#to edit.

sub monthButton
{
	my $month1 = $calendar_1->month();
	my $month2 = $calendar_2->month();
	my @months = ("0", "Jan", "Feb","Mar","Apr","May","Jun",
	"Jul","Aug","Sep","Oct","Nov","Dec");
	my $month1_name = $months[$month1];
	my $month2_name = $months[$month2];

print <<END_OF_PRINTING;
<html>
<body>
<h1>Pick a Month to Edit:</h1>
<p>Month: </p>
<form action="viewmycalendar.pl.cgi" method=POST>
<select name = "month">
<option value = "$month1">$month1_name</option>
<option value = "$month2">$month2_name</option>
</select>
<input type="submit" name ="monthSubmit"value="Submit">
</body>
<html>
END_OF_PRINTING
}

###############################################################################

#This method uses the input from the month button to determine which calendar 
#to use for editing. It returns that calendar.

sub calToEdit
{
	my $month = $_[0]; #from the month submit button
	my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) =
		localtime(time);
	$mon++; #adjusts index
	if($month == $mon)
	{
		return $calendar_1;
	}
	else
	{
		return $calendar_2;
	}	
}

###############################################################################

#This method takes the selected month and creates drop down menus for 
#scheduling lessons. There is a drop down for the day, which is what uses the
#information of the selected month (i.e. February will only print 28 days),
#a drop down for the start time, and a drop down for the duration of the lesson.
#All of these inputs are attached to one submit button.

sub lessonButtons
{
	my $selected_month = $_[0];
	my @days_per_month = (0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31);
	my $days_num = $days_per_month[$selected_month];
	my ($sec,$min,$hour,$mday,$mon,$year) =
		localtime(time);
	$mon++; #shifts index of month to correspond to calendar
    $year += 1900; #Gets correct year
	if($year % 4 == 0 && $selected_month == 2) #A leap year
	{
		$days_num++;
	}

my $j;

if($selected_month == $mon)
{
	$j = $mday+1;
}
else
{
	$j = 1;
}

print <<END_OF_PRINTING;
<html>
<h1>Add a Lesson Slot</h1>
<p>Day:   Start Time:   Duration:</p>

<form action="viewmycalendar.pl.cgi" method=POST>
<select name = "day">
END_OF_PRINTING
my $i = $j;
for($i = $j; $i <= $days_num; $i++)
{
	print "<option value = \"$i\">$i</option>";
}
print<<END_OF_PRINTING;
</select>

<select name = "starttime">
<option value = "8.0">8:00 am</option>
<option value = "8.25">8:15 am</option>
<option value = "8.5">8:30 am</option>
<option value = "8.75">8:45 am</option>

<option value = "9.0">9:00 am</option>
<option value = "9.25">9:15 am</option>
<option value = "9.5">9:30 am</option>
<option value = "9.75">9:45 am</option>

<option value = "10.0">10:00 am</option>
<option value = "10.25">10:15 am</option>
<option value = "10.5">10:30 am</option>
<option value = "10.75">10:45 am</option>

<option value = "11.0">11:00 am</option>
<option value = "11.25">11:15 am</option>
<option value = "11.5">11:30 am</option>
<option value = "11.75">11:45 am</option>

<option value = "12.0">12:00 pm</option>
<option value = "12.25">12:15 pm</option>
<option value = "12.5">12:30 pm</option>
<option value = "12.75">12:45 pm</option>

<option value = "13.0">1:00 pm</option>
<option value = "13.25">1:15 pm</option>
<option value = "13.5">1:30 pm</option>
<option value = "13.75">1:45 pm</option>

<option value = "14.0">2:00 pm</option>
<option value = "14.25">2:15 pm</option>
<option value = "14.5">2:30 pm</option>
<option value = "14.75">2:45 pm</option>

<option value = "15.0">3:00 pm</option>
<option value = "15.25">3:15 pm</option>
<option value = "15.5">3:30 pm</option>
<option value = "15.75">3:45 pm</option>

<option value = "16.0">4:00 pm</option>
<option value = "16.25">4:15 pm</option>
<option value = "16.5">4:30 pm</option>
<option value = "16.75">4:45 pm</option>

<option value = "17.0">5:00 pm</option>
<option value = "17.25">5:15 pm</option>
<option value = "17.5">5:30 pm</option>
<option value = "17.75">5:45 pm</option>

<option value = "18.0">6:00 pm</option>
<option value = "18.25">6:15 pm</option>
<option value = "18.5">6:30 pm</option>
<option value = "18.75">6:45 pm</option>

<option value = "19.0">7:00 pm</option>
<option value = "19.25">7:15 pm</option>
<option value = "19.5">7:30 pm</option>
<option value = "19.75">7:45 pm</option>

<option value = "20.0">8:00 pm</option>
<option value = "20.25">8:15 pm</option>
<option value = "20.5">8:30 pm</option>
<option value = "20.75">8:45 pm</option>

<option value = "21.0">9:00 pm</option>
<option value = "21.25">9:15 pm</option>
<option value = "21.5">9:30 pm</option>
<option value = "21.75">9:45 pm</option>

<option value = "22.0">10:00 pm</option>
</select>

<select name = "duration">
<option value = ".5">30 minutes</option>
<option value = ".75">45 minutes</option>
<option value = "1">1 hour</option>
<option value = "1.25">1 hour 15 minutes</option>
<option value = "1.5">1 hour 30 minutes</option>
<option value = "1.75">1 hour 45 minutes</option>
<option value = "2">2 hours</option>
</select>
<input type = "text" name = "mon" id="hiddenfield" value = $selected_month>
<input type="submit" name = "addLesson" value="Add">
<br>
</form>

</body>
</html>
END_OF_PRINTING
}

###############################################################################

#This method adds a lesson to the lesson sheet, and thus the calendar. It does
#this by taking the information submitted to the lesson buttons and checking that there
#is no overlap for that month

#The way it works is to get the lessons for the specified day on the
#calendar, flag a corresponding 15-minute slot to true, and
#then check for overlaps with the lesson scheduling is attempted.

#For example, if there is a lesson from 8:30 am to 10:45 am,
#then the check array marks slots 2 (8:30-8:45), 3 (8:45-9:00),
#4, 5, 6, 7, 8, 9, and 10.

sub addLesson
{
	#get inputs from post - the start time and the day
	my $day = $_[0];
	my $startTime = $_[1];
	my $duration = $_[2];
	my $cale = $_[3]; #gets appropriate calendar month
	my $lesson_sheet = $_[4];
	my $cal = calToEdit($cale);

	my $length = 64; #the last slot is 23:45-24:00; corresponds to 63
	my @slots_list;
	my $index;
	for($index = 0; $index <= 63; $index++)
	{
		$slots_list[$index] = 0; #initializes each slot to empty;
		#print "<html><br>$index : $slots_list[$index]</html>";
	}

	#Get info from the calendar
	my $lessons = $cal->getcontent($day);
	my @lessons_list = split("<br><br>", $lessons); #Gets day's lessons, stored
											 #in 24-hour time

	my ($start, $end,$start_hour, $start_mins, $end_hour,$end_mins);
	#Gets lessons time information and flags slots in the array
	#This information is taken directly from the specified calendar day

	for my $l(@lessons_list)
	{	#corresponds to (1)login name, and (3)time slot
		if($l =~ m/([a-zA-Z0-9_\-\.\*]+)(\s)(\d+:\d+\-\d+:\d+)/)
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

	my $endTime = $startTime + $duration;
;
		
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
			print "<html>$error_message</html>";
			$valid = 0;
			$j = $e_index + 1; #breaks for loop
		}
	}

	#Add the lesson to the lesson sheet
	#Adds as: (example, April 10 from 1 pm to 2:15 pm)
	#4 10 AVAILABLE*SLOT 13 14.25

	if($valid)
	{
		open(FH, ">>$lesson_sheet") || die "Error opening $lesson_sheet";
		#print"<html><br>file name: $lesson_sheet</html>";
		my $m = $cal->month();
		my $open = "AVAILABLE*SLOT";
		#Checks to make sure prints with proper formatting

		unless($endTime =~ m/(\d+)(.)(\d+)/)
		{
			$endTime = $endTime .".0";
		}
		unless($startTime =~ m/(\d+)(.)(\d+)/)
		{
			$startTime = $startTime .".0";
		}
		print FH "$m $day $open $startTime $endTime\n";
		#print"<html><br>$m $day $open $startTime $endTime</html>";
		close(FH);
	}				
}

###############################################################################

#This sub generates two empty calendars, one for the current month
#and one for the next month. It then reads through the lesson sheet,
#adding the lessons to the appropriate days. If the instructor is new and has
#no lessons scheduled, then two empty calendars are generated.

sub generateCalendars
{
   my $lessonsFile = $_[0];
   

	my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) =
		localtime(time);
    $year += 1900; #Gets correct year
    $mon++; #Adjusts month index
    #Makes 1st calendar (empty)
	$calendar_1 = new HTML::CalendarMonthSimple('year'=>$year,'month'=>$mon);
	$calendar_1->bgcolor('#3BB9FF');
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
	$calendar_2->bgcolor('#3BB9FF');

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
		if($line =~ m/(\d+)(\s)(\d+)(\s)([a-zA-Z0-9_\-\.\*]+)(\s)(\d+)(\.)(\d+)(\s)(\d+)(\.)(\d+)/)
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

#This method prints both calendars

sub printBothCalendars
{
	print $calendar_1->as_HTML;
	print "<br><br>";
	print $calendar_2->as_HTML;
}

###############################################################################

#This method prints the calendar currently being edited

sub printCurrentCalendar
{
	my $current = $_[0];
	my $this_month = $current->monthname();
	print"<h1>Editing calendar for $this_month</h1><br>";
	print $current->as_HTML;
	print "<br>";
}

###############################################################################

#This sub reads through the lesson sheet to generate a drop down menu for
#removing lessons. A lesson slot can only be selected for removal if it is after
#the current day. That is, if today is April 10, then the lessons from April 1
#through April 10, inclusive, will not be printed as options for cancellation.

sub removeMenu
{
my $lessons = $_[0]; #Gets lessons sheet
my $cale = $_[1];

my $current_cal = calToEdit($cale);

my $current_month = $current_cal->month();
my $current_m_name = $current_cal->monthname();
my $line;

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
my $next_month = $m +1;

my @list; #Will hold lessons
open(FH, "$lessons");
while(<FH>)
{
	$line = $_;
	my $lesson_option;
	chomp($line);
	#				  1:$m 			  3:$day     5:$slotholder         7-9:$startTime    11-13:$endTime
	if($line =~ m/($current_month)(\s)(\d+)(\s)([a-zA-Z0-9_\-\.\*]+)(\s)(\d+)(\.)(\d+)(\s)(\d+)(\.)(\d+)/)
	{
		$check_day = $3;
		my $valid_this;
		my $valid_next;
		if(($m == $current_month && $check_day > $mday) || ($current_month == $next_month)) #print as option to delete only if lesson comes after today
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
			$lesson_option = $current_m_name . " " . $3 . " " . $5 . " " . $7 . ":" . $s_mins ."-" . $11 .":" .$e_mins;
			push(@list, $lesson_option);
		}
	}
}
my $message;
my $empty = 0;
if(scalar @list == 0) #Nothing valid to remove
{
	 $message = "Cannot remove a lesson";
	 push(@list, $message);
	$empty = 1;
}
unless($empty)
{
print <<END_OF_PRINTING;
<html>
<h1>Remove a Lesson from $current_m_name</h1>
<form action="viewmycalendar.pl.cgi" method=POST>
<select name = "removemenu">
END_OF_PRINTING
for my $l(@list)
{
	print"<option value = \"$l\">$l</option>";
}
print<<END_OF_PRINTING;
</select>
<input type = "text" name = "mot" id="hiddenfield" value = $current_month>
<input type="submit" name = "removeLesson" value="Remove">
</html>
END_OF_PRINTING
}

else
{
	print"<html><p>$message</p></html>";
}

}#End of method

###############################################################################

#This sub takes the input received from the Remove Menu option selection, and
#removes that lesson from the lesson sheet, and thus the calendar.
   
sub removeLesson
{
	my $lesson_string = $_[0];
	my $cale = $_[1];
	my $sheet = $_[2];
	my ($month, $day, $slotholder, $time) = split(" ", $lesson_string);
	my $current_cal = calToEdit($cale);
	#Modify time to match how it's written in the lesson sheet

	my($start, $end) = split("\-",$time);
	my $start_hour;
	my $start_mins;
	my $end_hour;
	my $end_mins;
	if($start =~ m/(\d+)(:)(\d+)/)
	{
		$start_hour = $1;
		$start_mins = $3;
		if($start_mins == 15)
		{
			$start_mins = ".25";
		}
		elsif($start_mins == 30)
		{
			$start_mins = ".5";
		}
		elsif($start_mins == 45)
		{
			$start_mins = ".75";
		}
		elsif($start_mins == 00)
		{
			$start_mins = ".0";
		}
		$start = $start_hour . $start_mins;
	}
    if($end =~ m/(\d+)(:)(\d+)/)
	{
		$end_hour = $1;
		$end_mins = $3;
		if($end_mins == 15)
		{
			$end_mins = ".25";
		}
		elsif($end_mins == 30)
		{
			$end_mins = ".5";
		}
		elsif($end_mins == 45)
		{
			$end_mins = ".75";
		}
		elsif($end_mins == 00)
		{
			$end_mins = ".0";
		}
		$end = $end_hour . $end_mins;
	}
	my $month_number = $current_cal->month();
	my $sheet_string = $month_number . " " . $day . " " . $slotholder . " " . $start . " " . $end;

	#Read the file and store it in an array

	my @lessons;
	my $line;

	open(FH, $sheet)||die "Error opening $sheet";
	while(<FH>)
	{
		$line = $_;
		chomp($line);
		push(@lessons, $line);
	}
	close(FH);
	
	#Overwrite the file, not including the removed lesson

	open(FH2, ">$sheet")||die "Error opening $sheet";
	for my $l(@lessons)
	{
		unless($l eq $sheet_string)
		{
			print FH2 $l ."\n";
		}
	}

	#Remove from student file if necessary
	unless($slotholder =~ m/(AVAILABLE\*SLOT)/)
	{
		my $studentFile = "STUDENTCAL" . $slotholder . ".txt";

		open(FH3, $studentFile) || die;
		my @studLessons;
		my $s_line;
		while(<FH3>)
		{
			$s_line = $_;
			chomp($s_line);
			unless($s_line eq $sheet_string)
			{
				push(@studLessons, $s_line);
			}
		}
		close(FH3);
		open (FH4, ">$studentFile") || die;
		for my $s_l(@studLessons)
		{
			print FH4 $s_l . "\n";
		}
		close(FH4);
		
		print"<html><p>Please email $slotholder that you canceled the lesson.</p></html>";		
	}
	
}

###############################################################################

#This method checks for if the month has shifted over to
#the next month. In such a case, the lessons for what was
#calendar 1 - the month that has passed - are removed from
#the lesson sheet. This is done to ensure that lessons from only the two current
#month calendars (this month and next) are stored in the lesson sheet.

sub refreshLessonSheet
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
			if($line =~ m/($month2)(\s)(\d+)(\s)([a-zA-Z0-9_\-\.\*]+)(\s)(\d+)(\.)(\d+)(\s)(\d+)(\.)(\d+)/)
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

#This method prints out a textfield for embedding a youtube video link

sub videoField
{
print <<END_OF_PRINTING;
<html>
<br><br>
<h1>Upload a Video</h1>
<p>Please copy and paste a YouTube video link from your browser</p>
<form action= "viewmycalendar.pl.cgi" method=POST>
<textarea name = "vidlink" rows=1 cols=30></textarea><br>
<input type=submit name ="addLink" value= "Embed">
</form></html>
END_OF_PRINTING
}

###############################################################################

#This method checks to see if a lesson sheet already contains a video

sub containsVideo
{
	my $sheet = $_[0];
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

###############################################################################

#This method adds a video to the lesson sheet

sub addVideo
{
	my $sh = $_[0]; # lesson sheet
	my $l = $_[1]; #link URL
	my $edit_l;
	if($l =~ m/(http:\/\/)(www\.)(youtube)(\.com\/)(watch\?v=)([a-zA-Z0-9_\-=&]+)/)
	{
		$edit_l = $1 . $2 . $3 . $4 . "embed\/" . $6;
		#print"<html><p>Modified: $edit_l</p></html>";
	}
	open(FH, ">>$sh") || die "Couldn't open $sh.";
	print FH $edit_l . "\n";
	close (FH);
}

###############################################################################

#This method prints the remove video button

sub removeVideoField
{
print <<END_OF_PRINTING;
<html>
<br>
<form action= "viewmycalendar.pl.cgi" method=POST>
<br>Remove Video:<br>
<input type=submit name ="removeLink" value= "Remove">
</form></html>
END_OF_PRINTING
}

###############################################################################

#This method removes a video from the lesson sheet

sub removeVideo
{
	my $sh = $_[0]; #Lesson sheet
	my @info;
	my $line;
	open (FH, $sh) || die "Could not open $sh";
	while(<FH>)
	{
		$line = $_;
		chomp($line);
		unless($line =~ m/(http:\/\/)(www\.)(youtube)(\.com\/)(embed\/)([a-zA-Z0-9_\-]+)/)
		{
			push(@info, $line)
		}
	}
	close FH;
	open(FH2, ">$sh") || die "Could not open $sh";
	for my $i(@info)
	{
		print FH2 $i . "\n";
	}
}


###############################################################################

sub printVideo
{
my $l = $_[0];
print<<END_OF_PRINTING;
<html>
<body>
<br><br>
My Video:
<br>
<iframe width="420" height="345"
src="$l">
</iframe>
</body>
</html>
END_OF_PRINTING
}

###############################################################################

#Makes PDF of today's lessons

sub makePDF
{
    my $file = $_[0];
    my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) =
        localtime(time);

    $mon++; #shift index
    my $cal = calToEdit($mon);

    my $lessons = $cal->getcontent($mday+1); #Gets Tomorrow's lessons
    my @lessons_list = split("<br><br>", $lessons); #Gets day's lessons, stored
                                             #in 24-hour time
   
  
    my $title;
    if($file =~ m/(INSTRUCTORCAL)([a-zA-Z0-9_\-\.]+)(\.txt)/)
    {
        $title = $2;
    }

   	my $filename;
    # initialize PDF
      my $pdf = new PDF::Create('filename'     => "tomorrowslessons$title.pdf",
                              'Author'       => "$title",
                              'Title'        => "Today's Lessons",
                              'CreationDate' => [ localtime ], );
      
	$filename = "tomorrowslessons$title.pdf";

                               
      # add a A4 sized page
      my $a4 = $pdf->new_page('MediaBox' => $pdf->get_page_size('A4'));

      # Add a page which inherits its attributes from $a4
      my $page = $a4->new_page;

      # Prepare a font
      my $f1 = $pdf->font('BaseFont' => 'Helvetica');

    my $count = 0;
    my $top = 500;
    for my $l(@lessons_list)
    {
        #print"<html><p>$l</p></html>";
        $page->stringc($f1, 12, 275, $top, $l);
        $top+=15;
    }
    $year +=1900;
    my $d = $mday+1;
    my $date =  $mon. "/" . $d . "/" . $year;
    $page->stringc($f1, 15, 275, $top + 15, $date);
    $page->stringc($f1, 15, 275, $top+40, "Instructor: " .$title);
    $page->stringc($f1, 20, 275, $top+70, "Tomorrow's Lessons");

      # Close the file and write the PDF
      $pdf->close;

	return $filename;
   
}
