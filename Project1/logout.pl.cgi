#!/usr/bin/perl
    
use CGI::Cookie;

use strict;

my %cookies = CGI::Cookie->fetch;
for (keys %cookies)
{
       my $current = $cookies{$_};
       if($current->name =~ m/InstraSchedule([a-z]+)loginfo/)
       {Expire($current->name);}
}
sub Expire()
{
       my $cookieString = $_;
	my $c = CGI::Cookie->new(-name =>  "$cookieString", -expires => '-1D');
	$c->bake;
}

system("/usr/bin/perl ./home.pl.cgi");

