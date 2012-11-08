#!/usr/bin/perl

#This script runs the student profile capabilities removing lessons, and
#viewing their upcoming lesson schedule. 

use strict;

use HTML::CalendarMonthSimple;
use CGI::Cookie;

my $calendar_1;
my $calendar_2;
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
					<li><a href="./editstudentschedule.pl.cgi"> View Available Instructors </a></li>
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
	genCalendars($studFile);
	refCalendars($studFile);
	genCalendars($studFile);
	print"<html><h1>Upcoming Lessons</h1></html>";
	printSchedule();
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

