#!/usr/bin/perl
    
use CGI; # load CGI routines

use strict;

MakeOptions();

sub MakeOptions()
	{
print "Content-type: text/html\n\n";
print <<EndOfPrinting;
<html>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
	<head>
		<title>InstraSchedule</title>
		<link rel="stylesheet" type="text/css" href="css/main.css" media="screen" />
		<link rel="stylesheet" type="text/css" href="css/print.css" media="print" />
		<!--[if lte IE 6]>
		<link rel="stylesheet" type="text/css" href="css/ie6_or_less.css" />
		<![endif]-->
		<script type="text/javascript" src="js/common.js"></script>
	</head>
	<body id="type-a">
		<div id="wrap">
			<div id="header">
				<div id="site-name"> InstraSchedule </div>
				<ul id="nav">
					<li><a href="./studentlogin.pl.cgi"> Student Login </a></li>
					<li><a href="./studentsignup.pl.cgi"> Student Sign Up </a></li>
					<li><a href="./instructorlogin.pl.cgi"> Instructor Login </a></li>
					<li><a href="./instructorsignup.pl.cgi"> Instructor Sign Up </a></li>
					<li><a href="./sitestatistics.pl.cgi"> Site Statistics </a></li>
				</ul>
			</div>
			<div id="content-wrap">
				<div id="content">
					<h1> Welcome to InstraSchedule!</h1>
					<h3> We are proud to be your one stop shop for music lesson scheduling. </h3>
				</div>
			</div>	
		</div>
	</body></html>
EndOfPrinting
}
