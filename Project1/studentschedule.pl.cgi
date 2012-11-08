#!/usr/bin/perl

#This script runs the student profile capabilities, which include viewing
#the instructors' available lesson slots, adding and removing lessons, and
#viewing their upcoming lesson schedule. 

use strict;

use HTML::CalendarMonthSimple;
use CGI::Cookie;

my $calendar_1;
my $calendar_2;
my $lessonFile;
my $chosenInFile;
my $inListFile;

print "Content-type: text/html\n\n";

###############################################################################
#Methods used above

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
	if(scalar @i_list == 0) #Nothing valid to remove
	{
	 	$message = "Cannot remove a lesson";
	 	push(@i_list, $message);
	}

print <<END_OF_PRINTING;
<html>
<body>
<h1>Select an Instructor</h1>
<form action="studentschedule.pl.cgi" method=POST>
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

###############################################################################

#This generates the calendars of the selected instructor

sub selectedInstructorSched
{
	my $instructorFile = $_[0];
	my $inCal1;
	my $inCal2;
	my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) =
		localtime(time);
    $year += 1900; #Gets correct year
    $mon++; #Adjusts month index
    #Makes 1st calendar (empty)
	$inCal1 = new HTML::CalendarMonthSimple('year'=>$year,'month'=>$mon);
	$inCal1->bgcolor('#3BB9FF');
	$inCal1->border(10);
	#Makes 2nd calendar (empty)
	if($mon == 12) #if December
	{
		$year++;
	}
	$mon++;
	my $nextMonth = $mon % 12;
	
	$inCal2 = new HTML::CalendarMonthSimple('year'=>$year,'month'=>$nextMonth);
	$inCal2->border(10);
	$inCal2->bgcolor('#3BB9FF');

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

   while(<FH>)
   {
		$line = $_;
		chomp($line);
		if($line =~ m/(\d+)(\s)(\d+)(\s)(AVAILABLE*SLOT)(\s)(\d+)(\.)(\d+)(\s)(\d+)(\.)(\d+)/)
		{
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
					$inCal1->addcontent($day, $lesson_string);
				}
				elsif($month == $month_2) #Second calendar
				{
					$inCal2->addcontent($day, $lesson_string);
				}
			}#End of if
		}
	}#End of file reading
	close(FH);
	my @instructorCals;
	push(@instructorCals, $inCal1);
	push(@instructorCals, $inCal2);
}


###############################################################################

#This prints a button to show the student their upcoming lessons

sub viewUpcoming
{
}

###############################################################################

#This prints the upcoming lessons

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

#This makes a return home button

sub returnHome
{
	print "<html><form action=\"studentschedule.pl.cgi\" method=POST></html>";
	print "<html><br><input type=\"submit\" name =\"returnHome\"value=\"Return Home\">";
}

###############################################################################

#This prints a drop down of available lessons, from which the student can pick
#and schedule a lesson

sub addLessonMenu
{
}

###############################################################################

#This adds the lesson to the lesson sheet, modifying the instructor's lesson
#sheet and the student's lesson sheet

sub addStudentLesson
{
}

###############################################################################

#This prints a drop down of lessons to remove. Those listed start from tomorrow
#onward

sub removeLessonMenu
{
}

###############################################################################

#This removes the lesson from the lesson sheet, modifying the instructor's
#sheet and the student's lesson sheet. The instructor's sheet is modified to
#make it an available slot again

sub removeStudentLesson
{
}


