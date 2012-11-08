#!/usr/bin/perl
    
use CGI; # load CGI routines

use Digest::MD5 qw(md5 md5_hex md5_base64);
    
use CGI::Cookie;

use strict;

my $l = $ENV{CONTENT_LENGTH};

if($l==0){
	MakeLogin();
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

	my $username = lc($F{'email'});
	my $password = $F{'pass'};
	my $found = Validate($username,$password);
	
	if($found==1) {
	        my $c = CGI::Cookie->new(-name    =>  "InstraScheduleinstructorloginfo=$username",
                            );
		$c->bake;
		MakeLoginSuccess($username);
	}
	else {
		MakeLoginAgain($username);
	}
	
	close FH
}

sub Validate() {
	my $etocheck = $_[0];
	my $ptocheck = md5_hex($_[1]);
	my $query = $etocheck . " = " . $ptocheck;
	open (FH, "instructorpasswordlist.txt") || die "Died opening instructorpasswordlist.txt";
	my $found=0;
	while (<FH>) {
		foreach my $line (split /\n/,$_) {
			if(($line =~ m/$query/))
			{
				$found=1;
			}
		}
	}

	return $found;
	close FH;
}

sub MakeLoginSuccess() 
	{
	my $user = $_[0];
	$user =~ s/@//;
	my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
	my $stat = "LOGIN;" . $user . "(" . $min . ":" . $hour . ":" . $mday . ":" . (++$mon) . ":" . ($year+1900) . ")\n";
	open (FH, ">>BIGInstructorStats.txt") || die "Died opening BIGInstructorStats.txt";
	print FH $stat;
	close FH;
	
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
InstraSchedule Log In</title></head>
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
		<h1> Log In Successful! </h1>

		</div></div></div>
EndOfPrinting
}

sub MakeLogin()
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
InstraSchedule Log In</title></head>
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
		<h1> Log In to InstraSchedule </h1>
		<FORM ACTION="./instructorlogin.pl.cgi" METHOD="POST">
		<input type="text" name="email" placeholder="Email" size="100">
		<input type="password" name="pass" placeholder="Password" size="100">
		<br><br>
		<INPUT type="submit" name="sub" value="Submit">
		</form>
		</div></div></div>
	</body></html>
EndOfPrinting
}

sub MakeLoginAgain()
	{
	my $user = $_[0];
	$user =~ s/@//;
	my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
	my $stat = "FAILEDL;" . $user . "(" . $min . ":" . $hour . ":" . $mday . ":" . (++$mon) . ":" . ($year+1900) . ")\n";
	open (FH, ">>BIGInstructorStats.txt") || die "Died opening BIGInstructorStats.txt";
	print FH $stat;
	close FH;

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
InstraSchedule Log In</title></head>
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
		<h1> Log In to InstraSchedule </h1>
		<h6> Authentication failed, try again. </h6>
		<FORM ACTION="./instructorlogin.pl.cgi" METHOD="POST">
		<input type="text" name="email" placeholder="Email" size="100">
		<input type="password" name="pass" placeholder="Password" size="100">
		<br><br>
		<INPUT type="submit" name="sub" value="Submit">
		</form>
		<FORM ACTION="./resetpassword.pl.cgi" METHOD="POST">
		<input type="submit" name="instructorReset" value="Reset Password">
		</FORM>
		</div></div></div>
	</body></html>
EndOfPrinting
}
