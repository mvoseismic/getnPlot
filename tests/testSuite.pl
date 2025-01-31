#!/usr/bin/perl
#
# Tests getnPlot as thouroughly as can be.
# R.C.Stewart, 2025-01-31
#

use strict;
use warnings;

# Which version to test
my $executable = '../getnPlot.py';
print "Which version to test, b (~/bin) or l (.): ";
my $choice= <STDIN>;
chomp $choice;
if( $choice eq 'b' ) {
    $executable = '~/bin/getnPlot';
}

my $testCmd;
my $testTag;
my $testNumber;
my $testGroup;
my $testWhat;
my $testDate = '2019-12-30';
my $testTime = '01:10:00.0';

my @shapes = ('landscape','portrait','square','long','xlong','xxlong','xxxlong','xxxxlong','thin');
#my @sources = ('auto', 'wws', 'mseed', 'cont', 'event', 'filename');
my @sources = ('auto', 'wws', 'mseed', 'cont', 'filename');
my @kinds = ('allZ','all3C','closeZ','close3C','radianZ','radian3C','Z','specialZ','spectrumZ','3C','special3C','irishZ','irish3C','lahar','tfr','forAI','rockfall','partmot','all','allplusZ','strain','strainplus','infra','heli','longsgram','stringthing');
my @dates = ( 'today', 'yesterday', 'yyyy-mm-dd', 'yyyy.jjj' );
my @times = ( 'hh:mm', 'hh:mm:ss', 'hh:mm:ss.s', 'now', 'now-X', 'now-Xs', 'now-Xm' );


print "0  ALL tests\n";
print "1  BASIC tests\n";
print "2  DATE tests\n";
print "3  TIME tests\n";
print "4  SHAPE tests\n";
print "5  SIZE tests\n";
print "6  SOURCE tests\n";
print "7  KIND tests\n";
print "Which tests to run: ";
my $testsToRun = <STDIN>;
chomp $testsToRun;

# Remove previous tests
system( 'rm *.png' );
system( 'rm *.txt' );

$testNumber = 0;

# BASIC tests
if( $testsToRun eq "0" || $testsToRun eq "1" ){
    $testNumber++;
    $testGroup = 'basic';
    $testTag = sprintf( "test_%03d_%s", $testNumber, $testGroup );
    $testCmd = join( ' ', $executable, '--plotfile', $testTag, '--today --time 01:00:00.0' );
    doTest( $testNumber, $testTag, $testCmd);
}


# DATE tests
if( $testsToRun eq "0" || $testsToRun eq "2" ){
    $testGroup = 'date';
    foreach my $testDate (@dates){
        $testNumber++;
        $testTag = sprintf( "test_%03d_%s_%s", $testNumber, $testGroup, $testDate);
        my $testDateString;
        if( $testDate eq 'yyyy-mm-dd' ) {
            $testDateString = '2025-01-18';
        } elsif( $testDate eq 'yyyy.jjj' ) {
            $testDateString = '2025.018';
        } else {
            $testDateString = $testDate;
        }
        $testCmd = join( ' ', $executable, '--plotfile', $testTag, '--time 01:00:00.0 --date', $testDateString);
        doTest( $testNumber, $testTag, $testCmd );
    }
}


# TIME tests
if( $testsToRun eq "0" || $testsToRun eq "3" ){
    $testGroup = 'time';
    foreach my $testTime (@times){
        $testNumber++;
        $testTag = sprintf( "test_%03d_%s_%s", $testNumber, $testGroup, $testTime);
        my $testTimeString;
        my $testDateString = '--yesterday';
        if( $testTime eq 'hh:mm' ) {
            $testTimeString = '13:12';
        } elsif( $testTime eq 'hh:mm:ss' ) {
            $testTimeString = '13:12:12';
        } elsif( $testTime eq 'hh:mm:ss.s' ) {
            $testTimeString = '13:12:12.2';
        } elsif( $testTime eq 'now-X' ) {
            $testDateString = '';
            $testTimeString = 'now-60';
        } elsif( $testTime eq 'now-Xs' ) {
            $testDateString = '';
            $testTimeString = 'now-60s';
        } elsif( $testTime eq 'now-Xm' ) {
            $testDateString = '';
            $testTimeString = 'now-6m';
        } else {
            $testDateString = '';
            $testTimeString = $testTime;
        }
        $testCmd = join( ' ', $executable, '--plotfile', $testTag, $testDateString, '--time', $testTimeString);
        doTest( $testNumber, $testTag, $testCmd );
    }
}


# SHAPE tests
if( $testsToRun eq "0" || $testsToRun eq "4" ){
    $testGroup = 'shape';
    foreach my $testShape (@shapes){
        $testNumber++;
        $testTag = sprintf( "test_%03d_%s_%s", $testNumber, $testGroup, $testShape );
        $testCmd = join( ' ', $executable, '--plotfile', $testTag, '--today --time 01:00:00.0 --shape', $testShape );
        doTest( $testNumber, $testTag, $testCmd );
    }
}


# SIZE tests
if( $testsToRun eq "0" || $testsToRun eq "5" ){
    $testGroup = 'size';
    my $testSize = 2800;
    foreach my $testShape (@shapes){
        $testNumber++;
        $testTag = sprintf( "test_%03d_%s_%s", $testNumber, $testGroup, $testShape );
        $testCmd = join( ' ', $executable, '--plotfile', $testTag, '--today --time 01:00:00.0 --shape', $testShape, '--size', $testSize );
        doTest( $testNumber, $testTag, $testCmd );
    }
}


# SOURCE tests
if( $testsToRun eq "0" || $testsToRun eq "6" ){
    $testGroup = 'source';
    foreach my $testSource (@sources){
        $testNumber++;
        $testTag = sprintf( "test_%03d_%s_%s", $testNumber, $testGroup, $testSource);
        if( $testSource eq 'cont' ) {
            $testCmd = join( ' ', $executable, '--plotfile', $testTag, '--date', $testDate,  '--time', $testTime, '--source', $testSource );
        } elsif( $testSource eq 'event' ) {
            my $testDate = '2025-01-02';
            my $testTime = '16:53:24.0';
            $testCmd = join( ' ', $executable, '--plotfile', $testTag, '--date', $testDate,  '--time', $testTime, '--source', $testSource );
        } elsif( $testSource eq 'filename' ){
            $testCmd = join( ' ', $executable, '--plotfile', $testTag, '--date 2025-01-13 --time 06:29 --source 2025_01_13_0620_00.msd' );
        } else {
            $testCmd = join( ' ', $executable, '--plotfile', $testTag, '--yesterday --time', $testTime, '--source', $testSource );
        }
        doTest( $testNumber, $testTag, $testCmd );
    }

    # SOURCE CONT when data traverses 20-minute files
    $testNumber++;
    my $testSource = 'cont';
    $testWhat = 'cont_2_files';
    $testTag = sprintf( "test_%03d_%s_%s", $testNumber, $testGroup, $testWhat);
    $testTime = '01:19:30';
    $testCmd = join( ' ', $executable, '--plotfile', $testTag, '--date', $testDate,  '--time', $testTime, '--source', $testSource );
    doTest( $testNumber, $testTag, $testCmd );

}


# KIND tests
if( $testsToRun eq "0" || $testsToRun eq "7" ){
    $testGroup = 'kind';
    $testTime = '01:10:00.0';
    foreach my $testKind(@kinds){
        $testNumber++;
        $testTag = sprintf( "test_%03d_%s_%s", $testNumber, $testGroup, $testKind);
        if( $testKind eq 'heli' ){
            $testCmd = join( ' ', $executable, '--plotfile', $testTag, '--yesterday --time 00:00 --dur 120m --pre 0m --kind', $testKind );
        } else {
            $testCmd = join( ' ', $executable, '--plotfile', $testTag, '--today --time', $testTime, '--kind', $testKind );
        }
        doTest( $testNumber, $testTag, $testCmd );
    }
}





sub doTest {

    my ($testNumber, $testTag, $cmd) = @_;
    my $testNumberString = sprintf( "%03d", $testNumber );

    my $fileOut = sprintf( "test_%03d.txt", $testNumber );
    open(FH, '>', $fileOut) or die $!;

    print "\nTest $testNumberString:    $cmd\n";
    print FH "Test $testNumberString:\n$cmd\n\n";
    close( FH );

    $cmd = join( " ", $cmd, '2>&1 | tee -a', $fileOut );
    system( $cmd );

}
