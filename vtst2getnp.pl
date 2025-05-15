#!/usr/bin/env perl
#
# Draws one figure per event in event list file.

use strict;
use warnings;

if( scalar @ARGV == 0 ) {
    print "Need an input file.\n";
    exit;
}

my $inputFile= $ARGV[0];
my $outputFile="doIt";

open my $fho, '>', $outputFile or die $!;
open my $fhi, '<', $inputFile or die $!;

my @chunks = split /\//, $inputFile;


my $tag = $chunks[-1] =~ m/\-\-(.*)\.txt$/; 

my $bash = `which bash`;
chomp $bash;
print $fho "#!$bash\n";

while (my $line = readline($fhi)) {

    chomp $line;

    my @chunks = split /\s/, $line;
    my $dateEvent = join( '-', $chunks[0], $chunks[1], $chunks[2] );
    my $timeEvent = join( ':', $chunks[3], $chunks[4], $chunks[5] );

    print $fho "getnPlot --tag $tag --date $dateEvent --time $timeEvent\n";
    print $fho "getnPlot --kind tfr --pre 5 --dur 35 --tag $tag --date $dateEvent --time $timeEvent\n";

}

close($fhi);
close($fho);


system( 'chmod +x doIt' );
