#!/usr/bin/perl

use strict;
use CGI; # load CGI routines
use Digest::MD5 qw(md5 md5_hex md5_base64);

my $l = $ENV{CONTENT_LENGTH};

if($l==0){
	MakeSignup();
}

else{
	read(STDIN, my $form, $ENV{'CONTENT_LENGTH'});
	my @pairs = split(/&/, $form);
	my %F;
	my $pair;
	my $name;
	my $value;
	foreach $pair (@pairs) {
		($name, $value) = split(/=/, $pair);
		$value =~ tr/+/ /;
		$value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
		$F{$name} = $value;
	}
	
	#make sure passwords match
	my $password1 = $F{'p1'};
	my $password2 = $F{'p2'};
	if (!($password1 eq $password2)) {
		MakeUnmatchingPasswords();
	}
	else {
		#in case good email
		my $email = lc($F{'emailinput'});
		if($email =~ /.*@.*\..*/) {
			my $emailexists = CheckForEmail($email);
			if($emailexists==1) {
				MakeExistingEmail();
			}
			else {
				CreateAccount($email,$password1);
				SendMail($email);
				MakeAccountCreateSuccess();
			}
		}
		else {
			MakeInvalidEmail();
		}
	}
}

sub CheckForEmail() {
	my $etocheck = $_[0];

	open (FH, "instructorpasswordlist.txt") || die "Died opening instructorpasswordlist.txt";		
	my $found=0;

	while (<FH>) {
		foreach my $line (split /\n/,$_) {
			if(($line =~ m/$etocheck/))
			{
				$found=1;
			}
		}
	}
	
	close FH;
	return $found;
}

sub CreateAccount() 
	{
	my $user = $_[0];
	my $pass = md5_hex($_[1]);
	my $output = "instructorpasswordlist.txt";
	open(FH,">>$output") || die("This file will not open!");
	print FH "$user = ". $pass ."\n";
	close (FH);

	#create instructorCal
	my $calName = $user;
	$calName =~ s/@//;
	my $filename = "INSTRUCTORCAL". $calName . ".txt";
	open nFH, ">$filename";
	print nFH "$calName\n";
	close nFH;

	#add to BIGInstructorList
	open(GH, ">>BIGInstructorList.txt") || die("BIGInstructorList dead");
	print GH "$user\n";
	close GH;

}

sub SendMail() 
	{
	my $title='Account Confirmation';
	my $to=$_[0];
	my $from= 'tkm2113@columbia.edu';
	my $subject='Instructor Account Confirmation for InstraSchedule';
	open(MAIL, "|/usr/sbin/sendmail -t");
	print MAIL "To: $to\n";
	print MAIL "From: $from\n";
	print MAIL "Subject: $subject\n\n";
	print MAIL "Thank you for creating a instructor account with InstraSchedule.";
	close(MAIL);
}

sub MakeAccountCreateSuccess() {
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
					<li><a href="./studentlogin.pl.cgi"> Student Login </a></li>
					<li><a href="./studentsignup.pl.cgi"> Student Sign Up </a></li>
					<li><a href="./instructorlogin.pl.cgi"> Instructor Login </a></li>
					<li><a href="./instructorsignup.pl.cgi"> Instructor Sign Up </a></li>
				</ul>
			</div>
	<div id="content-wrap">
	<div id = "content">
	<h1> Instructor Account Created Successfully </h1>
	<a href="./instructorlogin.pl.cgi"> Log In With Your New Account </a>
	</div></div></div>
</body></html>
EndOfPrinting
}

sub MakeSignup()
	{
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
					<li><a href="./studentlogin.pl.cgi"> Student Login </a></li>
					<li><a href="./studentsignup.pl.cgi"> Student Sign Up </a></li>
					<li><a href="./instructorlogin.pl.cgi"> Instructor Login </a></li>
					<li><a href="./instructorsignup.pl.cgi"> Instructor Sign Up </a></li>
				</ul>
			</div>
	<div id="content-wrap">
	<div id = "content">
	<h1> Sign Up Below </h1>
	<FORM ACTION="./instructorsignup.pl.cgi" METHOD="POST">
		<input type="text" name="emailinput" placeholder="Email" size="100">
 		<br><br>
		<input type="password" name="p1" placeholder="Desired Password" size="100">
		<br><br>
		<input type="password" name="p2" placeholder="Retype Desired Password" size="100">
		<br><br>
		<INPUT type="submit" name="sub" value="Submit">
	</form>
	</div></div></div>
</body></html>
EndOfPrinting
}

sub MakeUnmatchingPasswords()
	{
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
					<li><a href="./studentlogin.pl.cgi"> Student Login </a></li>
					<li><a href="./studentsignup.pl.cgi"> Student Sign Up </a></li>
					<li><a href="./instructorlogin.pl.cgi"> Instructor Login </a></li>
					<li><a href="./instructorsignup.pl.cgi"> Instructor Sign Up </a></li>
				</ul>
			</div>
	<div id="content-wrap">
	<div id = "content">
	<h1> Sign Up Below </h1>
	<h6> Passwords do not match, please try again. </h6>
	<FORM ACTION="./instructorsignup.pl.cgi" METHOD="POST">
		<input type="text" name="emailinput" placeholder="Email" size="100">
 		<br><br>
		<input type="password" name="p1" placeholder="Desired Password" size="100">
		<br><br>
		<input type="password" name="p2" placeholder="Retype Desired Password" size="100">
		<br><br>
		<INPUT type="submit" name="sub" value="Submit">
	</form>
	</div></div></div>
</body></html>
EndOfPrinting
}

sub MakeInvalidEmail()
	{
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
					<li><a href="./studentlogin.pl.cgi"> Student Login </a></li>
					<li><a href="./studentsignup.pl.cgi"> Student Sign Up </a></li>
					<li><a href="./instructorlogin.pl.cgi"> Instructor Login </a></li>
					<li><a href="./instructorsignup.pl.cgi"> Instructor Sign Up </a></li>
				</ul>
			</div>
	<div id="content-wrap">
	<div id = "content">
	<h1> Sign Up Below </h1>
	<h6> Please enter a valid E-Mail Address. </h6>
	<FORM ACTION="./instructorsignup.pl.cgi" METHOD="POST">
		<input type="text" name="emailinput" placeholder="Email" size="100">
 		<br><br>
		<input type="password" name="p1" placeholder="Desired Password" size="100">
		<br><br>
		<input type="password" name="p2" placeholder="Retype Desired Password" size="100">
		<br><br>
		<INPUT type="submit" name="sub" value="Submit">
	</form>
	</div></div></div>
</body></html>
EndOfPrinting
}

sub MakeExistingEmail()
	{
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
					<li><a href="./studentlogin.pl.cgi"> Student Login </a></li>
					<li><a href="./studentsignup.pl.cgi"> Student Sign Up </a></li>
					<li><a href="./instructorlogin.pl.cgi"> Instructor Login </a></li>
					<li><a href="./instructorsignup.pl.cgi"> Instructor Sign Up </a></li>
				</ul>
			</div>
	<div id="content-wrap">
	<div id = "content">
	<h1> Sign Up Below </h1>
	<h6> Account already exists for this E-Mail Address. Log In or create a new account. </h6>
	<FORM ACTION="./instructorsignup.pl.cgi" METHOD="POST">
		<input type="text" name="emailinput" placeholder="Email" size="100">
 		<br><br>
		<input type="password" name="p1" placeholder="Desired Password" size="100">
		<br><br>
		<input type="password" name="p2" placeholder="Retype Desired Password" size="100">
		<br><br>
		<INPUT type="submit" name="sub" value="Submit">
	</form>
	</div></div></div>
</body></html>
EndOfPrinting
}

