#!/usr/bin/perl

use PDF::Create;

my $filename = "BIGStudentList.txt";

makePDF($filename);

sub makePDF
{
	my $studListFile = $_[0]; #Takes in list of student users
	open(FH, $studListFile) || die;
	my @students;
	my $line;
	while(<FH>)
	{
		$line = $_;
		chomp($line);
		$line =~ s/@//;
		$line = "STUDENTCAL" . $line . ".txt";
		push(@students, $line);
	}
	close(FH);
	
	my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) =
		localtime(time);
	$mon++; #Adjust for index

	my @todays_lessons;

	for my $f(@students)
	{
		open (FH, $f) || die;
		my $less;
		while(<FH>)
		{
			$less = $_;
			chomp($less);
			if($less =~ m/($mon)(\s)($mday)(\s)([a-zA-Z0-9_\-\.\*]+)(\s)(\d+)(\.)(\d+)(\s)(\d+)(\.)(\d+)/)
			{
				push(@todays_lessons, $less);
			}
		}
		close(FH);
	}
	# initialize PDF
	$year +=1900;
  	my $pdf = new PDF::Create('filename'     => "todayslesson-$mon-$mday-$year.pdf",
                              'Author'       => 'Alison and Trevor',
                              'Title'        => 'Lessons for Today',
                              'CreationDate' => [ localtime ], );
                                        
  	# add a A4 sized page
  	my $a4 = $pdf->new_page('MediaBox' => $pdf->get_page_size('A4'));

  	# Add a page which inherits its attributes from $a4
  	my $page = $a4->new_page;

  	# Prepare a font
  	my $f1 = $pdf->font('BaseFont' => 'Helvetica');

	my $count = 0;
	$my_top = 750;
	for($count = 1; $count <= 30; $count++)
	{
		$page->stringc($f1, 12, 10, $my_top, $todays_lessons[$count]);
		$my_top+=15;
	}

  	# Close the file and write the PDF
  	$pdf->close;
	
		
}
