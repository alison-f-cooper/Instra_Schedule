#!/usr/bin/perl
    
use CGI; # load CGI routines

use Digest::MD5 qw(md5 md5_hex md5_base64);
    
use CGI::Cookie;
use String::Random qw(random_regex random_string);

use strict;

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

if($F{'instructorReset'})
{
	my $instructorFile = "instructorpasswordlist.txt";
	MakeResetPage($instructorFile);
}

elsif($F{'studentReset'})
{
	my $studentFile = "studentpasswordlist.txt";
	MakeResetPage($studentFile);
}

elsif($F{'checkEmail'})
{
	my $usr = $F{'checkEmail'};
	my $file = $F{'checkFile'};
	ValidateReseter($file,$usr);
}

elsif($F{'tempPass'})
{
	my $newP1 = $F{'newP1'};
	my $newP2 = $F{'newP2'};
	my $user = $F{'user'};
	my $tempPass = $F{'tempPass'};
	my $checkFile = $F{'checkFile'};

	if(!($newP1 eq $newP2)) {MakeMailNewPasswordAgainPassUnmatch($checkFile, $user);}

	my $valid = Validate($user,$tempPass,$checkFile);

	if($valid==0) {MakeMailNewPasswordAgainIncorrectTemp($checkFile, $user);}

	else {MakePasswordResetSuccess($user,$newP1,$checkFile);}

}

sub MakePasswordResetSuccess() {
	my $user = $_[0];
	my $ptoreplace = md5_hex($_[1]);
	my $checkFile = $_[2];

    	open(FILE,"<$checkFile") || die "Died opening ".$checkFile;
    	my @LINES = <FILE>;
    	close(FILE);
    	open(FILE,">$checkFile");
    	foreach my $LINE (@LINES) {
    		my @array = split(/\s/,$LINE);
    		print FILE $LINE unless ($array[0] eq "$user");
    	}
	print FILE "$user = ". $ptoreplace ."\n";
    	close(FILE); 


	my $usertype;
	
	if($checkFile =~ m/instructor/) {$usertype = 'instructor';}
	else {$usertype = 'student';}

	my $loginDirect = "./".$usertype."login.pl.cgi"; 

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
	<h1> Password Successfully Reset </h1>
	<a href="$loginDirect"> Log In With Your New Password </a>
	</div></div></div>
</body></html>
EndOfPrinting

	close FH;
}

sub ValidateReseter {
	my $checkFile = $_[0];
	my $user = $_[1];
	open (FH, "$checkFile") || die "Died opening ". $checkFile;
	my $found=0;
	while (<FH>) {
		foreach my $line (split /\n/,$_) {
			if(($line =~ m/$user/))
			{
				$found=1;
			}
		}
	}

	if ($found==1)
		{MakeMailNewPassword($checkFile,$user);}
	else
		{MakeResetPageAgain($checkFile);}

	close FH;
}

sub Validate() {
	my $etocheck = $_[0];
	my $ptocheck = md5_hex($_[1]);
	my $checkFile = $_[2];
	my $query = $etocheck . " = " . $ptocheck;
	open (FH, $checkFile) || die "Died opening ". $checkFile;
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

sub MakeResetPage() {

	my $checkFile = $_[0];
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
InstraSchedule Password Reset </title></head>
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
		<h1> Enter Account E-Mail for Reset </h1>
		<FORM ACTION="./resetpassword.pl.cgi" METHOD="POST">
		<input type="text" name="checkEmail" placeholder="E-Mail" size="100">
		<input type="text" name="checkFile" id="hiddenfield" value = "$checkFile">
		<br><br>
		<INPUT type="submit" name="sub" value="Submit">
		</form>
		</div></div></div>
	</body></html>
EndOfPrinting
	
}

sub MakeResetPageAgain() {

	my $checkFile = $_[0];
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
InstraSchedule Password Reset </title></head>
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
		<h1> Enter Account E-Mail for Reset </h1>
		<h6> No account exists for this E-Mail. </h6>
		<FORM ACTION="./resetpassword.pl.cgi" METHOD="POST">
		<input type="text" name="checkEmail" placeholder="E-Mail" size="100">
		<input type="text" name="checkFile" id="hiddenfield" value = "$checkFile">
		<br><br>
		<INPUT type="submit" name="sub" value="Submit">
		</form>
		</div></div></div>
	</body></html>
EndOfPrinting
}

sub MakeMailNewPassword {
	my $checkFile = $_[0];
	my $user = $_[1];
	my $tempPass = random_string("ccCccCccCcc");
	SendPassword($user,$tempPass);
	my $mdTemp = md5_hex($tempPass);	

    	open(FILE,"<$checkFile") || die "Died opening ".$checkFile;
    	my @LINES = <FILE>;
    	close(FILE);
    	open(FILE,">$checkFile");
    	foreach my $LINE (@LINES) {
    		my @array = split(/\s/,$LINE);
    		print FILE $LINE unless ($array[0] eq "$user");
    	}
	print FILE "$user = ". $mdTemp ."\n";
    	close(FILE); 

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
InstraSchedule Password Reset </title></head>
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
		<h1> Temporary Password Sent To $user </h1>
		<h6> Enter temporary password and new desired password below. </h6>
		<FORM ACTION="./resetpassword.pl.cgi" METHOD="POST">

		<input type="text" name="tempPass" placeholder="Temporary Password" size="100">
		<input type="password" name="newP1" placeholder="New Password" size="100">
		<input type="password" name="newP2" placeholder="Confirm New Password" size="100">

		<input type="text" name="checkFile" id="hiddenfield" value = "$checkFile">
		<input type="text" name="user" id="hiddenfield" value = "$user">
		<br><br>
		<INPUT type="submit" name="sub" value="Submit">
		</form>
		</div></div></div>
	</body></html>
EndOfPrinting
	
}

sub SendPassword {
	my $to = $_[0];
	my $pass = $_[1];
	my $title='Account Confirmation';
	my $from = 'tkm2113@columbia.edu';
	my $subject='InstraSchedule Password Reset';
	open(MAIL, "|/usr/sbin/sendmail -t");
	print MAIL "To: $to\n";
	print MAIL "From: $from\n";
	print MAIL "Subject: $subject\n\n";
	print MAIL "Your temporary password for InstraSchedule is $pass";
	close(MAIL);
}

sub MakeMailNewPasswordAgainPassUnmatch() {

	my $checkFile = $_[0];
	my $user = $_[1];
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
InstraSchedule Password Reset </title></head>
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
		<h1> Temporary Password Sent To $user </h1>
		<h6> New passwords do not match, try again. </h6>
		<FORM ACTION="./resetpassword.pl.cgi" METHOD="POST">

		<input type="text" name="tempPass" placeholder="Temporary Password" size="100">
		<input type="text" name="newP1" placeholder="New Password" size="100">
		<input type="text" name="newP2" placeholder="Confirm New Password" size="100">

		<input type="text" name="checkFile" id="hiddenfield" value = "$checkFile">
		<input type="text" name="user" id="hiddenfield" value = "$user">
		<br><br>
		<INPUT type="submit" name="sub" value="Submit">
		</form>
		</div></div></div>
	</body></html>
EndOfPrinting
	
}

sub MakeMailNewPasswordAgainIncorrectTemp() {

	my $checkFile = $_[0];
	my $user = $_[1];
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
InstraSchedule Password Reset </title></head>
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
		<h1> Temporary Password Sent To $user </h1>
		<h6> Incorrect temporary password, check E-Mail again. </h6>
		<FORM ACTION="./resetpassword.pl.cgi" METHOD="POST">

		<input type="text" name="tempPass" placeholder="Temporary Password" size="100">
		<input type="text" name="newP1" placeholder="New Password" size="100">
		<input type="text" name="newP2" placeholder="Confirm New Password" size="100">

		<input type="text" name="checkFile" id="hiddenfield" value = "$checkFile">
		<input type="text" name="user" id="hiddenfield" value = "$user">
		<br><br>
		<INPUT type="submit" name="sub" value="Submit">
		</form>
		</div></div></div>
	</body></html>
EndOfPrinting
}
