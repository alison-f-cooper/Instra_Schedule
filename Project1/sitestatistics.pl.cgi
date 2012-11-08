#!/usr/bin/perl 

use strict;

#Main method

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
					<li><a href="./logout.pl.cgi"> Home </a></li>
				</ul>
			</div>
	<div id="content-wrap">
	<div id = "content">
EndOfPrinting

open(SS,"BIGStudentStats.txt")|| die "Died opening BIGStudentStats.txt";
open(IS,"BIGInstructorStats.txt") || die "Died opening BIGInstructorStats.txt";

#calculate distinct users, #logins per user

my %instructorLoginCount;
my %instructorDateLogins;
my %instructorFailedTally;
my $instructorFailedLogins="";

while (<IS>) {
	foreach my $line (split /\n/,$_) {
		$line =~ m/([A-Z]+)(;)([a-z_\-@\.]+)(\()([0-9:]+)(\))/;
		my $statType = $1;
		my $user = $3;
		my $time = $5;
		$time =~ m/([0-9]+)(:)([0-9]+)(:)([0-9]+)(:)([0-9]+)(:)([0-9]+)/;
		my $minhour = $3 . ":" . $1;
		my $date = $5 .":". $7 .":". $9; #day:month:year
		if ($statType eq "LOGIN")
		{
			if(defined $instructorLoginCount{$user}) {$instructorLoginCount{$user}++;}
			else {$instructorLoginCount{$user}=1;}

			if(defined $instructorDateLogins{$date}){$instructorDateLogins{$date}++;}
			else{$instructorDateLogins{$date}=1;}
		}
		elsif($statType eq "FAILEDL")
		{
			if(defined $instructorFailedTally{$user}) {$instructorFailedTally{$user}++;}
			else {$instructorFailedTally{$user}=1;}

			$instructorFailedLogins = $instructorFailedLogins . "$user failed at $minhour on $date.<br>";
		}
	}
}


my %studentLoginCount;
my %studentDateLogins;
my %studentFailedTally;
my $studentFailedLogins="";
my $totalLessons=0;
my %lessonTally;

while (<SS>) {
	foreach my $line (split /\n/,$_) {
		$line =~ m/([A-Z]+)(;)([a-z0-9_\-@\.]+)(\()([0-9:]+)(\))/;
		my $statType = $1;
		my $user = $3;
		my $time = $5;
		$time =~ m/([0-9]+)(:)([0-9]+)(:)([0-9]+)(:)([0-9]+)(:)([0-9]+)/;
		my $minhour = $3 . ":" . $1;
		my $date = $5 .":". $7 .":". $9; #day:month:year
		if ($statType eq 'LOGIN'){
			if(defined $studentLoginCount{$user}) {$studentLoginCount{$user}++;}
			else {$studentLoginCount{$user}=1;}
			
			if(defined $studentDateLogins{$date}) {$studentDateLogins{$date}++;}
			else {$studentDateLogins{$date}=1;}
		}
		elsif($statType eq 'FAILEDL')
		{
			if(defined $studentFailedTally{$user}) {$studentFailedTally{$user}++;}
			else {$studentFailedTally{$user}=1;}

			$studentFailedLogins = $studentFailedLogins . "$user failed at $minhour on $date.<br>";
		}
		elsif($statType eq 'LESSONADD')
		{

			if(defined $lessonTally{$user}) {$lessonTally{$user}++;}
			else {$lessonTally{$user}=1;}

			$totalLessons++;
		}
	}
}

close SS;

my $numberOfInstructors = keys %instructorLoginCount;
my $numberOfStudents = keys %studentLoginCount;

my $maxInstructorLogins = 0;
my $mostActiveInstructor;
while ((my $key, my $value) = each(%instructorLoginCount)){
     if ($value>$maxInstructorLogins) {$maxInstructorLogins = $value; $mostActiveInstructor = $key;}
}

my $maxStudentLogins = 0;
my $mostActiveStudent;
while ((my $key, my $value) = each(%studentLoginCount)){
     if ($value>$maxStudentLogins) {$maxStudentLogins = $value; $mostActiveStudent = $key;}
}

my $mostActiveDayLogins = 0;
my $mostActiveDay;

#check days with two while loops in case a ton of student/instructor activity on a day with none of the other.
while ((my $key, my $value) = each(%instructorDateLogins)){
	my $loginsToday = $value + $studentDateLogins{$key};
     if ($loginsToday>$mostActiveDayLogins) {$mostActiveDayLogins = $loginsToday; $mostActiveDay = $key;}
}

while ((my $key, my $value) = each(%studentDateLogins)){
	my $loginsToday = $value + $instructorDateLogins{$key};
     if ($loginsToday>$mostActiveDayLogins) {$mostActiveDayLogins = $loginsToday; $mostActiveDay = $key;}
}

$mostActiveDay =~ m/([0-9]+)(:)([0-9]+)(:)([0-9]+)/;
my$aDay=$1;
my$aMonth=$3-1;
my$aYear=$5;

my @month_abbr = qw( Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec );
(my $sec,my $min,my $hour,my $mday,my $mon,my $year,my $wday,my $yday,my $isdst) =
localtime(time);
$year = $year+1900;
my $output0 = "$month_abbr[$mon] $mday, $year InstraSchedule Stats<br>";
my $output1 = "There are $numberOfInstructors instructors and $numberOfStudents students using InstraSchedule.";
my $output2 = "The most active Instructor is $mostActiveInstructor with $maxInstructorLogins logins and the most active student is $mostActiveStudent with $maxStudentLogins logins.";
my $output3 = "The most active day in InstraSchedule history occured on $month_abbr[$aMonth] $aDay, $aYear. On that day, InstraSchedule was logged into $mostActiveDayLogins times.";
my $output4 = "Failed instructor logins log:<br>$instructorFailedLogins";
my $output5 = "Failed student logins log:<br>$studentFailedLogins";
my $output6 = "Instructor failed login tally:<br>";
while ((my $key, my $value) = each(%instructorFailedTally)){
     $output6 = $output6 . $key." has ".$value." failed logins. <br>";
}
my $output7 = "Student failed login tally:<br>";
while ((my $key, my $value) = each(%studentFailedTally)){
     $output7 = $output7 . $key." has ".$value." failed logins. <br>";
}
my $output8 = "Lesson tally:<br>";
while ((my $key, my $value) = each(%lessonTally)){
     $output8 = $output8 . $key." has scheduled ".$value." lessons. <br>";
}
my $output9 = "InstraSchedule is proud to have helped schedule " . $totalLessons . " lessons.";

print "<html>$output0<br>$output1<br>$output2<br>$output3<br><br>$output4<br>$output5<br>$output6<br>$output7<br>$output8<br>$output9<br></html>";

open (FH, ">webthumbStatisticsFile.txt") || die "Died opening webthumbStatisticsFile.txt";
print FH $output0. "\n" . $output1 . "\n" . $output2 . "\n" . $output3;
close FH;
