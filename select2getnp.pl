#!/usr/bin/env perl
#
## UNDER CONSTRUCTION

use strict;
use warnings;

if( scalar @ARGV == 0 ) {
    print "Need an input file.\n";
    exit;
}

my $inputFile= $ARGV[0];
my $outputFile="doIt.sh";

my $cmdOpts = $ARGV[1];
if( !$cmdOpts ){
    $cmdOpts = '';
}

my $sta = $ARGV[2];
if( !$sta ){
    $sta = '';
} else {
    $cmdOpts = join( ' ', $cmdOpts, '--sta', $sta );    
}

open my $fho, '>', $outputFile or die $!;
open my $fhi, '<', $inputFile or die $!;

my $bash = `which bash`;
chomp $bash;
print $fho "#!$bash\n";

my $cmdStub = 'getnPlot -q';
my $cmd = '';

my $evType;
my $evVolcType;
my $evDate;
my $evTime;
my $evTag;
my $evFile;
my $evFileDir;
my $evFileDirStub = '/mnt/mvofls2/Seismic_Data/WAV/MVOE_';

while (my $line = readline($fhi)) {

    chomp $line;

    if( substr($line,-1) eq '1' ) {

        my $strYr = substr( $line, 1, 4 );
        my $strMo = substr( $line, 6, 2 );
        $strMo =~ s/\s/0/;
        my $strDa = substr( $line, 8, 2 );
        $strDa =~ s/\s/0/;
        my $strHr = substr( $line, 11, 2 );
        $strHr =~ s/\s/0/;
        my $strMi = substr( $line, 13, 2 );
        $strMi =~ s/\s/0/;
        my $strSe = substr( $line, 16, 4 );
        $strSe =~ s/\s/0/;
        $evDate = join( '-', $strYr, $strMo, $strDa );
        $evTime = join( ':', $strHr, $strMi, $strSe );
        $evType = substr( $line, 21, 2 );
        $evType =~ s/^\s+//;
        $evType =~ s/\s+$//;
        $evFileDir = join( '/', $strYr, $strMo );

    } elsif( substr($line,-1) eq '3' && substr($line,1,9) eq 'VOLC MAIN' ) {

        $evVolcType = substr( $line, 11, 1 );

    } elsif( substr($line,-1) eq '6' ) {

        my @bits = split ' ', $line;
        $evFile = $bits[0];
        $evFile = join( '/', $evFileDirStub, $evFileDir, $evFile );

    } elsif( substr($line,1,4) eq $sta ) {
        if( substr( $line, 7, 1) eq 'Z' ){
            my $pickTime = substr($line,18,10);
            $pickTime =~ s/ /0/g;
                 $evTime = join( ':', substr($pickTime,0,2), substr($pickTime,2,2), substr($pickTime,4,6) );
        }


    } elsif( $line =~ /^ *$/ ) {

        if( $evVolcType eq 't' ){
            $evTag = 'VT';
        } elsif( $evVolcType eq 'l' ){
            $evTag = 'LP';
        } elsif( $evVolcType eq 'h' ){
            $evTag = 'Hybrid';
        } elsif( $evVolcType eq 'r' ){
            $evTag = 'Rockfall';
        } elsif( $evVolcType eq 'e' ){
            $evTag = 'LP_rockfall';
        } elsif( $evVolcType eq 'x' ){
            $evTag = 'Explosion';
        } elsif( $evVolcType eq 's' ){
            $evTag = 'Swarm';
        } elsif( $evVolcType eq 'n' ){
            $evTag = 'Noise';
        } elsif( $evVolcType eq 'm' ){
            $evTag = 'Monochromatic';
        } elsif( $evType eq 'L' ){
            $evTag = 'Local';
        } elsif( $evType eq 'R' ){
            $evTag = 'Regional';
        } elsif( $evType eq 'D' ){
            $evTag = 'Distant';
        }
        # HACK TO USE MSEED FILES INSTEAD OF SEISAN FILE
        $evFile = "mseed";
        if( $cmdOpts =~ /tag/ ) {
            $cmd = join( ' ', $cmdStub, $cmdOpts, '--date', $evDate, '--time', $evTime, '--source', $evFile , '--pre 30 --dur 120 --kind close3C --shape long' );
        } else {
            $cmd = join( ' ', $cmdStub, $cmdOpts, '--date', $evDate, '--time', $evTime, '--tag', $evTag, '--source', $evFile , '--pre 30 --dur 120 --kind close3C --shape long' );
        }
        if( substr($evDate,0,4)+0 >= 2022 ) {
           $cmd = join( ' ', $cmd, "--source mseed" );
       } else {
           $cmd = join( ' ', $cmd, "--source cont" );
       } 
        print join( '|', $evDate,$evTime,$evType,$evVolcType,$evFile), "\n";
        if( $evDate ){
            print $cmd, "\n";
            print $fho "$cmd\n";
        }

        $evType = '';
        $evVolcType = '';
        $evDate = '';
        $evTime = '';
        $evTag = '';
        $evFile = '';
        $evFileDir = '';

    }
}

close($fhi);
close($fho);


system( 'chmod +x doIt.sh' );
