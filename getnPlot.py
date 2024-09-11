#!/usr/bin/env python
# getnPlot.py
#
# Gets all data for a time window, from a variety of sources, and plots in various ways
# Previously called fetchPlot
#
# Version 2: much more logical
# Version 2.0-dev: development
#
# R.C. Stewart, Dec 2022 to Feb 2023
#



############  Imports
import os
import sys
import glob
import subprocess
import argparse
import re
import obspy
import warnings
import matplotlib.pyplot as plt
import numpy as np
import socket
from datetime import datetime, date, timedelta, time
from dateutil import parser as dparser
from dateutil.rrule import rrule, DAILY
from obspy.clients.earthworm import Client
from obspy.core import UTCDateTime, Stream, Trace
from pathlib import Path
from obspy.signal.tf_misfit import plot_tfr
from obspy.clients.filesystem.sds import Client as sdsClient


############  Location of python modules is different on opsproc2
hostname = socket.gethostname()
sys.path.append( '/'.join( [os.path.expanduser('~'), 'src/pythonModules' ] ) )

import rodsPythonThings
import rodsPlotTfr as rodstfr



############  For timer 
startTime = datetime.now()



############  Arguments
parser = argparse.ArgumentParser( prog='getnPlot', description='Get seismic data and plot it', usage='%(prog)s [options]',
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                 epilog = 'Example:  getnPlot --date yesterday --time 12:37 --kind closeZ --pre 20 --dur 90' )

parser.add_argument('-v', '--version', action='version', version='%(prog)s 2.0-dev')

choices = ['getnplot','get','plot','test']
parser.add_argument('--mode', default='getnplot', choices=choices, help='Mode of operation: '+' | '.join(choices), metavar='')
parser.add_argument('-q', '--quiet', action='store_true', help='No screen output')

choices=['auto','wws','mseed','cont', 'event', 'filename']
parser.add_argument('--source', default='auto', help='Data source (auto tries wws then mseed then cont): '+' | '.join(choices), metavar='')
parser.add_argument('--wwsip', default='172.17.102.60', help='Hostname or IP address of winston wave server', metavar='')
parser.add_argument('--wwsport', default=16022, help='Port of winston wave server', metavar='')

choices=['allZ','all3C','closeZ','close3C','radianZ','radian3C','Z','specialZ', 'spectrumZ', '3C','special3C','irishZ','irish3C','lahar','tfr','forAI', 'rockfall', 'partmot', 'all', 'allplusZ', 'strain', 'strainplus', 'infra' ]
parser.add_argument('-k', '--kind', default='allZ', choices=choices, help='Kind of plot (use all for get only): '+' | '.join(choices), metavar='')
parser.add_argument('--sta', default='MSS1', help='Station(s) to be plotted, comma separated) (not used in some kinds of plot).', metavar='')

parser.add_argument('-d', '--date', default='today', help='Date of event (UTC): today | yesterday | yyyy-mm-dd | yyyy.jjj', metavar='')
parser.add_argument('-t', '--time', default='now', help='Time of event (UTC): hh:mm | hh:mm:ss | hh:mm:ss.s | now |now-X | now-Xs | now-Xm', metavar='')
parser.add_argument('--yesterday', action='store_true', help='Set date to yesterday')
parser.add_argument('--today', action='store_true', help='Set date to today')

parser.add_argument('-p', '--pre', default='10', help='Window starts this many seconds before event time, append m or h to input minutes or hours', metavar='')
parser.add_argument('-l', '--dur', default='60', help='Window duration, in seconds: append m or h to input minutes or hours', metavar='')
parser.add_argument('--twin', default='30', help='Duration, in seconds, of window for analysis: append m or h to input minutes or hours', metavar='')

choices=['landscape','portrait','square','long','xlong', 'xxlong', 'xxxlong', 'thin']
parser.add_argument('--shape', default='landscape', choices=choices , help='Shape of plot: '+' | '.join(choices), metavar='')
parser.add_argument('--size', type=int, default=1920, help='Length (pixels) of longest side of plot', metavar='')
choices=['d','s','m','h']
parser.add_argument('--tscale', default='d', choices=choices , help='Time scale units (defaults to s or what window duration is specified in): ' +' | '.join(choices), metavar='')
choices=['linear','log']
parser.add_argument('--fscale', default='linear', choices=choices, help='Frequency scale for analysis and plotting: '+' | '.join(choices), metavar='')
choices=['amp','power','log','sqrt']
parser.add_argument('--zscale', default='sqrt', choices=choices, help='Z scale for plotting: '+' | '.join(choices), metavar='')
parser.add_argument('--plotspec', action='store_true', help='No spectrum in TFR plot')
parser.add_argument('--plotnorms', action='store_true', help='No RMS in lahar plot')
parser.add_argument('--show', action='store_true', help='Show plot on screen as well as saving it')
parser.add_argument('--grid', action='store_true', help='Add time-axis grid to seismograms')
parser.add_argument('--title', help='Title for plot, defaults gives all information.', metavar='')
parser.add_argument('--bigtitle', action='store_true', help='Big bold title.')
parser.add_argument('--nogreen', action='store_true', help='Do not plot green line for arrival/event time.')
parser.add_argument('--linewidth', type=float, default=0.5, help='Thickness of plotted line', metavar='')

parser.add_argument('--fmin', type=float, default=0, help='Minimum frequency for analysis and plotting', metavar='')
parser.add_argument('--fmax', type=float, default=100.0, help='Maximum frequency for analysis and plotting', metavar='')
parser.add_argument('--hpfilt', type=float, default=0.0, help='High-pass filter corner frequency', metavar='')
parser.add_argument('--lpfilt', type=float, default=0.0, help='Low-pass filter corner frequency', metavar='')
choices=['no','yes','3c']
parser.add_argument('--norm', default='3c', choices=choices, help='Normalise data: '+' | '.join(choices), metavar='')
parser.add_argument('--mult', default=1.0, help='Multiply data by this much', metavar='')
parser.add_argument('--integrate', action='store_true', help='Integrate seismic data')

parser.add_argument('--dir', default='.', help='Directory name for plots and files', metavar='')
parser.add_argument('--tag', default='', help='String (no spaces) used in output file names', metavar='')
parser.add_argument('--plotfile', default='', help='Plot file name, no extension, default is based on arguments', metavar='')
parser.add_argument('--datafile', default='', help='Data file name, no extension, default is based on arguments', metavar='')
parser.add_argument('--datimtag', default=4, help='Number of characters in time bit of datim tag', metavar='')

parser.add_argument('--downsample', type=int, default=1, help='Downsampling factor', metavar='')

parser.add_argument('rest', nargs=argparse.REMAINDER)

args = parser.parse_args()



############  Assign arguments, parsing if necessary
runQuiet = args.quiet
runMode = args.mode
dataSource= args.source
wwsIP = args.wwsip
wwsPort = args.wwsport
plotKind = args.kind.lower()
dataStation = args.sta
if plotKind == '3c' and dataStation == 'MSS1':
    dataStation = "MBLY"
elif plotKind == "strainplus":
    dataStation = "MBLY"
eventDate = args.date
eventTime = args.time
eventTimeArg = ''.join( args.rest )
if eventTimeArg:
    eventTime = eventTimeArg
plotTscale= args.tscale
wpre = args.pre
if wpre[-1] == 's':
    windowPre = float( wpre[:-1] )
elif wpre[-1] == 'm':
    windowPre = 60 * float( wpre[:-1] )
elif wpre[-1] == 'h':
    windowPre = 3600 * float( wpre[:-1] )
else:
    windowPre = float( wpre )
wdur = args.dur
if wdur[-1] == 's':
    windowDur = float( wdur[:-1] )
elif wdur[-1] == 'm':
    windowDur = 60 * float( wdur[:-1] )
    if plotTscale == 'd':
        plotTscale = 'm'
elif wdur[-1] == 'h':
    windowDur = 3600 * float( wdur[:-1] )
    if plotTscale == 'd':
        plotTscale = 'h'
else:
    windowDur = float( wdur )
twin = args.twin
if twin[-1] == 's':
    windowAnal = float( twin[:-1] )
elif twin[-1] == 'm':
    windowAnal = 60 * float( twin[:-1] )
elif twin[-1] == 'h':
    windowAnal = 3600 * float( twin[:-1] )
else:
    windowAnal = float( twin )
plotShape = args.shape
plotSize = args.size
plotFscale= args.fscale
plotZscale= args.zscale
plotSpec = args.plotspec
plotRms = not args.plotnorms
plotShow = args.show
plotGrid = args.grid
plotFmax = args.fmax
plotFmin = args.fmin
dataHPfilt = args.hpfilt
dataLPfilt = args.lpfilt
dataIntegrate = args.integrate
dataNormalize = args.norm
dataMult= args.mult
outDir = args.dir
filenameTag = args.tag
filePlot = args.plotfile
fileMseedOut = args.datafile
setToday = args.today
setYesterday = args.yesterday
plotTitleArg = args.title
plotTitleBig = args.bigtitle
plotNogreen = args.nogreen
plotLineWidth= args.linewidth
filenameDatimN = float( args.datimtag )
dataDownsample = args.downsample

if plotTscale == 'd':
    plotTscale = 's'



############ Suppress all output if required
if runQuiet:
    fd = os.open('/dev/null',os.O_WRONLY)
    os.dup2(fd,2)
    os.dup2(fd,1)



############  Constants
secInDay = 60*60*24
filenameSeparator = "."
filenameSeparator2 = "-"
dirnameSeparator = "/"
clientTimeout = 20
today = datetime.utcnow().date()
datimNow = datetime.utcnow()



############  Directories
pathWAV1 = '/mnt/mvofls2/Seismic_Data/WAV/MVOE_'
#    pathWAV2 = '/mnt/mvofls2/Seismic_Data/WAV/ROD__'
pathMseed = '/mnt/mvohvs3/MVOSeisD6/mseed'



############  Files
if runMode == 'plot' and dataSource == '':
    dataSource = 'dataTmp.mseed'



############  Sort out dates and times
if eventDate == 'yesterday' or setYesterday:
    evDate = UTCDateTime(today.year, today.month, today.day) - secInDay
elif eventDate == 'today' or setToday:
    evDate = UTCDateTime(today.year, today.month, today.day)
else:
    #evDate = dparser.parse(eventDate, dayfirst=True)
    evDate = dparser.parse(eventDate)

if eventTime[0:3] == 'now':
    evDatim = datimNow
    if eventTime[0:4] == 'now-':
        charNow = eventTime[-1]
        if charNow == 's' or charNow == 'm' or charNow == 'h':
            numberNow = int( eventTime[4:-1] )
            if charNow == 'm':
                numberNow = numberNow * 60
            if charNow == 'h':
                numberNow = numberNow * 3600
        else:
            numberNow = int( eventTime[4:] )
    else:
        numberNow = windowPre
    evDatim = evDatim - timedelta(seconds=numberNow)
else:
    if eventTime.count(':') == 1:
        [hours, minutes] = [float(x) for x in eventTime.split(':')]
        seconds = 0.0
    else:
        [hours, minutes, seconds] = [float(x) for x in eventTime.split(':')]
    evDatim = evDate + \
        timedelta(hours=hours, minutes=minutes, seconds=seconds)

datimBeg = UTCDateTime(evDatim - timedelta(seconds=windowPre))
datimEnd = UTCDateTime(datimBeg + timedelta(seconds=windowDur))



############  Plot sizes
if plotShape == "portrait":
    plotSize2 = (int(plotSize/1.5), plotSize)
elif plotShape == "landscape":
    plotSize2 = (plotSize, int(plotSize/1.5))
elif plotShape == "square":
    plotSize2 = (plotSize, plotSize)
elif plotShape == "long":
    plotSize2 = (plotSize, int(plotSize/2.4))
elif plotShape == "xlong":
    plotSize2 = (plotSize, int(plotSize/3.0))
elif plotShape == "xxlong":
    plotSize2 = (plotSize, int(plotSize/5.0))
elif plotShape == "xxxlong":
    plotSize2 = (2*plotSize, 2*int(plotSize/7.5))
elif plotShape == "thin":
    plotSize2 = (int(plotSize/2.5), plotSize)



############  Frequency ranges
if plotFscale == 'log' and plotFmin == 0.0:
    plotFmin = 0.5
if plotKind == 'tfr' and plotFmin == 0.0:
    plotFmin = 0.5
### These lines are temporary
dataFmin = plotFmin
dataFmax = plotFmax
if plotKind =='tfr' and dataStation == 'MSS1':
    plotFmax = 50.0;
if plotKind =='forai' and dataStation == 'MSS1':
    plotFmax = 50.0;



############  Channels wanted for all plot types
nslcWant = {
    'MV.MBBY.00.HH1', 'MV.MBBY.00.HH2', 'MV.MBBY.00.HHZ',
    'MV.MBBY..BHE', 'MV.MBBY..BHN', 'MV.MBBY..BHZ',
    'MV.MBFL.00.HH1', 'MV.MBFL.00.HH2', 'MV.MBFL.00.HHZ',
    'MV.MBFL..BHE', 'MV.MBFL..BHN', 'MV.MBFL..BHZ',
    'MV.MBFL..SHZ',
    'MV.MBFL.00.HDF',
    'MV.MBFR.00.HH1', 'MV.MBFR.00.HH2', 'MV.MBFR.00.HHZ',
    'MV.MBFR..BHE', 'MV.MBFR..BHN', 'MV.MBFR..BHZ',
    'MV.MBGA..SHZ',
    'MV.MBGB.00.HH1', 'MV.MBGB.00.HH2', 'MV.MBGB.00.HHZ',
    'MV.MBGB..BHE', 'MV.MBGB..BHN', 'MV.MBGB..BHZ',
    'MV.MBGB..SHZ',
    'MV.MBGH.00.HH1', 'MV.MBGH.00.HH2', 'MV.MBGH.00.HHZ',
    'MV.MBGH..BHE', 'MV.MBGH..BHN', 'MV.MBGH..BHZ',
    'MV.MBGH..SHZ',
    'MV.MBHA..BHE', 'MV.MBHA..BHN', 'MV.MBHA..BHZ',
    'MV.MBHA..SHZ',
    'MV.MBLG.00.HH1', 'MV.MBLG.00.HH2', 'MV.MBLG.00.HHZ',
    'MV.MBLG..BHE', 'MV.MBLG..BHN', 'MV.MBLG..BHZ',
    'MV.MBLG..SHZ',
    'MV.MBLY.00.HH1', 'MV.MBLY.00.HH2', 'MV.MBLY.00.HHZ',
    'MV.MBLY..BHE', 'MV.MBLY..BHN', 'MV.MBLY..BHZ',
    'MV.MBRV..BHE', 'MV.MBRV..BHN', 'MV.MBRV..BHZ',
    'MV.MBRV..SHZ',
    'MV.MBRY..BHE', 'MV.MBRY..BHN', 'MV.MBRY..BHZ',
    'MV.MBWH..BHE', 'MV.MBWH..BHN', 'MV.MBWH..BHZ',
    'MV.MBWH..SHZ',
    'MV.MRYT..SHZ',
    'MV.MSS1..SHZ',
    'MC.AIRS..BLZ', 'MC.OlV1..BLZ', 'MC.TRNT..BLZ',
    'CU.GRGR.00.BHZ', 'CU.GRGR.00.BH1', 'CU.GRGR.00.BH2',
    'CU.ANWB.00.BHZ', 'CU.ANWB.00.BH1', 'CU.ANWB.00.BH2',
    'CU.BBGH.00.BHZ', 'CU.BBGH.00.BH1', 'CU.BBGH.00.BH2',
    'WI.ABD.00.HHZ', 'WI.ABD.00.HHN', 'WI.ABD.00.HHE',
    'WI.DHS.00.HHZ', 'WI.DHS.00.HHN', 'WI.DHS.00.HHE',
    'NA.SABA..BHZ', 'NA.SABA..BHN', 'NA.SABA..BHE',
    'TR.SVT..HHZ', 'TR.SVT..HHN', 'TR.SVT..HHE',
    'TR.DSLB..HHZ', 'TR.DSLB..HHN', 'TR.DSLB..HHE'
}
#    'MC.OLV1..BHZ', 'MC.OLV1..BHE', 'MC.OLV1..BHN',
#    'MC.TRNT..BHZ', 'MC.TRNT..BHE', 'MC.TRNT..BHN',



############  Channels wanted for different plots types
if plotKind[-2:] == "3c":
    chas = "3c"
elif plotKind[-1] == "z":
    chas = "z"
    if dataNormalize == "3c":
        dataNormalize = "no"

if plotKind[0:5] == "close":
    stas = ["MSS1", "MBFR", "MBLG", "MBLY", "MBRY"]
elif plotKind[0:6] == "radian":
    stas = ["MBFR", "MBLG", "MBLY", "MBBY", "MBGH", "MBFL", "MBGB"]
elif plotKind == "tfr":
    stas = dataStation.split(",")
    chas = "z"
elif plotKind == "irish3c":
    stas = ["MBLG", "MBHA", "MSS1"]
elif plotKind == "irishz":
    stas = ["MBLG", "MBHA", "MSS1", "MBLY", "MBRY"]
elif plotKind == "all3c":
    stas = ["MBFR", "MBLY", "MBLG", "MBRY", "MBBY",
            "MBGH", "MBWH", "MBFL", "MBGB", "MBRV"]
elif plotKind == "3c":
    stas = dataStation.split(",")
elif plotKind == "z":
    stas = dataStation.split(",")
elif plotKind == "special3c":
    stas = dataStation.split(",")
elif plotKind == "specialz":
    stas = dataStation.split(",")
elif plotKind == "spectrumz":
    stas = dataStation.split(",")
    chas = "z"
elif plotKind == "lahar":
    stas = [ "MSS1", "MBFR", "MBLY", "MBBY" ]
    chas = "z"
elif plotKind == "rockfall":
    stas = [ "MSS1", "MBRY", "MBLY", "MBLG", "MBGH", "MBBY", "MBFR" ]
    chas = "z"
    if dataNormalize == "3c":
        dataNormalize = "no"
    if filenameTag =="":
        filenameTag = "Rockfall"
elif plotKind == "forai":
    stas = dataStation.split(",")
    chas = "z"
elif plotKind == "partmot":
    stas = dataStation.split(",")
    chas = "3c"
elif plotKind == "all":
    stas = ["MSS1", "MBFR", "MBLY", "MBLG", "MBRY", "MBBY",
            "MBHA", "MBGH", "MBWH", "MBFL", "MBGB", "MBRV"]
    chas = "3c"
elif plotKind == "strain":
    stas = ["AIRS", "OLV1", "TRNT"]
    chas = "z"
elif plotKind == "strainplus":
    stas = ["AIRS", "OLV1", "TRNT"]
    stas.append( dataStation )
    chas = "3c"
elif plotKind == "infra":
    stas =["MBFL"] 
    chas = "h"
elif plotKind == "allplusZ":
    stas = ["MSS1", "MBFR", "MBLY", "MBLG", "MBRY", "MBBY",
            "MBHA", "MBGH", "MBWH", "MBFL", "MBGB", "TRNT", "OLV1", "MBRV"]
    chas = "z"
else:
    # "allZ"
    stas = ["MSS1", "MBFR", "MBLY", "MBLG", "MBRY", "MBBY",
            "MBHA", "MBGH", "MBWH", "MBFL", "MBGB", "MBRV"]
    chas = "z"



if chas == '3c' and dataNormalize != 'no':
    dataNormalize = "3c"

fileStaTag = '-'.join( ['_'.join( stas ), chas.upper()] )

numberStations = len( stas )



############  File names and plot title
if plotTscale == 'h':
    windowString = str(int(windowDur/3600))+"h"+str(int(windowPre/3600))
elif plotTscale == 'm':
    windowString = str(int(windowDur/60))+"m"+str(int(windowPre/60))
else:
    windowString = str(int(windowDur))+"s"+str(int(windowPre))

if filePlot == "":
    if filenameTag in ("MSS1_trigger", "MBFR_trigger", "MBLG_trigger", "MBLY_trigger"): 
        filenameDatimN = 6
    elif filenameTag== "VT_string_event":
        filenameDatimN = 7

    if filenameDatimN == 7:
        datimEventString = evDatim.strftime("%Y%m%d-%H%M%S%f")[:-5]
    elif filenameDatimN == 6:
        datimEventString = evDatim.strftime("%Y%m%d-%H%M%S")
    else:
        datimEventString = evDatim.strftime("%Y%m%d-%H%M")

    if plotKind == "allz":
        filePlot = filenameSeparator2.join([datimEventString,
            '-'+filenameTag, plotKind, windowString])
    elif plotKind == "all3c":
        filePlot = filenameSeparator2.join([datimEventString,
            '-'+filenameTag, plotKind, windowString])
    elif plotKind == "tfr":
        filePlot = filenameSeparator2.join([datimEventString,
            '-'+filenameTag, fileStaTag, plotKind, windowString])
    elif plotKind == "spectrumz":
        filePlot = filenameSeparator2.join([datimEventString,
            '-'+filenameTag, fileStaTag, 'spectrum', windowString])
    elif plotKind == "forai":
        filePlot = filenameSeparator2.join([datimEventString,
            '-'+filenameTag, fileStaTag, plotKind, windowString])
    elif plotKind == "partmot":
        filePlot = filenameSeparator2.join([datimEventString,
            '-'+filenameTag, fileStaTag, plotKind, windowString])
    elif plotKind == "rockfall":
        filePlot = filenameSeparator2.join([datimEventString,
            '-'+filenameTag, "amplitudes"])
    elif plotKind == "strain":
        filePlot = filenameSeparator2.join([datimEventString,
            '-'+filenameTag, fileStaTag, plotKind, windowString])
    elif plotKind == "strainplus":
        filePlot = filenameSeparator2.join([datimEventString,
            '-'+filenameTag, fileStaTag, plotKind, windowString])
    else:
        filePlot = filenameSeparator2.join([datimEventString,
            '-'+filenameTag, fileStaTag, windowString])
    if dataHPfilt > 0.0:
        filePlot = filenameSeparator2.join([filePlot, 'hp'+ str(dataHPfilt)+'Hz'])
    if dataLPfilt > 0.0:
        filePlot = filenameSeparator2.join([filePlot, 'lp'+ str(dataLPfilt)+'Hz'])
    if dataIntegrate:
        filePlot = filenameSeparator2.join([filePlot, 'integrated'])
    plotTitle = filePlot
else:
    plotTitle = filePlot + '  ' + evDatim.strftime( "%Y-%m-%d %H:%M:%S" )

if fileMseedOut == "":
    fileMseedOut = filePlot

plotTitle2 = evDatim.strftime("%Y-%m-%d %H:%M:%S.%f")[:-5]
index = plotTitle.find('--')
plotTitle = plotTitle[index:]
plotTitle = plotTitle.replace( "-", "  " )
plotTitle = plotTitle.replace( "_", " " )
plotTitle = "  ".join( [plotTitle2, plotTitle] )

if plotTitleArg:
    plotTitle = plotTitleArg

filePlot = filenameSeparator.join([filePlot, 'png'])
filePlot = dirnameSeparator.join([outDir, filePlot])
fileMseedOut = filenameSeparator.join([fileMseedOut, 'mseed'])
fileMseedOut = dirnameSeparator.join([outDir, fileMseedOut])


############  Values for forAI plot
if plotKind == "forai":
    #windowPre = 5
    #windowDur = 60
    plotSize = 800
    plotSize2 = (plotSize, plotSize )


############  Print out arguments, changed, and calculated things

if not runQuiet:

    print( startTime )
    print( "Hostname: " + hostname )

    print( 'Script running' )
    print(' Mode:            ' + runMode)
    print(' Quiet:           ' + str(runQuiet))

    print( 'Data' )
    print(' Source:          ' + dataSource)
    print(' WWS IP:          ' + wwsIP)
    print(' WWS port:        ' + str(wwsPort))
    print(' Station:         ' + dataStation)
    print(' N stations:      ' + str( numberStations))
    print(' Event date:      ' + eventDate)
    print(' Event time:      ' + eventTime)
    print(' Window pre:      ' + str(windowPre) + ' seconds')
    print(' Window dur:      ' + str(windowDur) + ' seconds')
    print(' Analysis window: ' + str(windowAnal) + ' seconds')
    print(' Data begins:     ' + datimBeg.strftime("%Y-%m-%d %H:%M:%S"))
    print(' Data ends:       ' + datimEnd.strftime("%Y-%m-%d %H:%M:%S"))

    print( 'Plot' )
    print(' Plot kind:       ' + plotKind)
    print(' Plot shape:      ' + plotShape)
    print(' Plot size:       ' + str(plotSize))
    print(' Plot size (2):   ' + str(plotSize2))
    print(' Plot timescale:  ' + plotTscale)
    print(' Plot freq scale: ' + plotFscale)
    print(' Plot Z scale:    ' + plotZscale)
    print(' Max plot freq:   ' + str(plotFmax))
    print(' Min plot freq:   ' + str(plotFmin))
    print(' Max data freq:   ' + str(dataFmax))
    print(' Min data freq:   ' + str(dataFmin))
    print(' Plot title:      ' + plotTitle)
    print(' Big title:       ' + str(plotTitleBig))
    print(' Plot grid:       ' + str(plotGrid))
    print(' Plot line width: ' + str(plotLineWidth))
    print(' No green line:   ' + str(plotNogreen))

    print( 'Data processing' )
    print(' Max frequency:   ' + str(dataFmax))
    print(' Min frequency:   ' + str(dataFmin))
    print(' HP filter:       ' + str(dataHPfilt))
    print(' LP filter:       ' + str(dataLPfilt))
    print(' Normalize:       ' + dataNormalize)
    print(' Integrate:       ' + str(dataIntegrate))

    print( 'Output' )
    print(' Output dir:      ' + outDir)
    print(' Filename tag:    ' + filenameTag)
    print(' Stations tag:    ' + fileStaTag)
    print(' Plot file:       ' + filePlot)
    print(' Data file:       ' + fileMseedOut)
    print(' Spec in TFR:     ' + str(plotSpec))
    print(' RMS in lahar:    ' + str(plotRms))
    print(' Show plot:       ' + str(plotShow))

    print(' Downsampling:    ' + str(dataDownsample))


############  Exit when testing
if runMode == 'test':
    exit(0)



############  Get all waveform data for interval
st = Stream()

if dataSource == 'auto':
    # First try Waveserver
    dataSource = 'waveserver ' + str(wwsIP)
    client = Client(wwsIP, wwsPort, clientTimeout)
    info = client.get_availability(network='*', station='*', channel='*')
    #info = client.get_availability(network='MV', station='*', channel='*')
    sys.stdout = open(os.devnull, "w")
    sys.stderr = open(os.devnull, "w")
    for net, sta, loc, cha, start, end in info:
        st += client.get_waveforms(net, sta, loc, cha, datimBeg, datimEnd)
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__

    if len(st) == 0:
        # Second try miniseed files
        dataSource = 'continuous miniseed data'
        warnings.filterwarnings("ignore")
        for netw in ["MV", "MC", "CU", "TR"]:
            client = sdsClient(dirnameSeparator.join([pathMseed, netw]))
            client.FMTSTR = '{station}/{year}.{doy:03d}.{network}.{station}.{location}.{channel}.mseed'
            st += client.get_waveforms(netw, '*',
                                           '*', '*', datimBeg, datimEnd)
        warnings.filterwarnings("default")

    if not runQuiet:
        print('  Streams from ' + dataSource + ': ' + str(len(st)))

elif dataSource == 'wws':
    # Waveserver
    # Define wave server
    client = Client(wwsIP, wwsPort, clientTimeout)
    # Fetch all data from waveserver
    info = client.get_availability(network='MV', station='M*', channel='*')
    for net, sta, loc, cha, start, end in info:
        st += client.get_waveforms(net, sta, loc, cha, datimBeg, datimEnd)

elif dataSource == "mseed":
    client = sdsClient(pathMseed)
    client.FMTSTR = '{network}/{station}/{year}.{doy:03d}.{network}.{station}.{location}.{channel}.mseed'
    st = client.get_waveforms('*', '*', '*', '*', datimBeg, datimEnd)

elif dataSource == "cont":
    if not runQuiet:
        print( 'source ' + dataSource + ' not implemented' )

elif dataSource == "event":
    if not runQuiet:
        print( 'source ' + dataSource + ' not implemented' )

else:
    # Event file
    if not os.path.isfile(dataSource):
        if not runQuiet:
            print('  No file in local directory')
        # If file doesnt exist, search in WAV/MVOE_ or WAV/ROD__
        try:
            dataSource = find(dataSource, pathWAV1)
        except:
            if not runQuiet:
                print('  No file in', pathWAV1)
            exit(0)
            #try:
            #    dataSource = find(dataSource, pathWAV2)
            #except:
            #    print('  No file in', pathWAV2)
            #    exit(0)
    if os.path.isfile(dataSource):
        if not runQuiet:
            print(' Data file.: ' + dataSource)
        st = obspy.read(dataSource)
    else:
        st = []



############  Bug out if nothing got
if len(st) == 0:
    if not runQuiet:
        print('No streams loaded')
    exit(0)



############  Check if SCNL is nasty thing returned by SEISAN files
tr = st[0]
chunks = tr.id.split('.')
if chunks[0] == "":
    sttemp = Stream()
    for tr in st:
        chunks = tr.id.split('.')
        if chunks[0] == "":
            if chunks[1] == "MBGA":
                idNew = "MV." + chunks[1] + ".." + 'SHZ'
            elif chunks[3] == "S Z":
                idNew = "MV." + chunks[1] + ".." + 'SHZ'
            else:
                idNew = "MV." + chunks[1] + ".." + chunks[3] + chunks[2]
            if not runQuiet:
                print("Changing code from " + tr.id + " to " + idNew)
            tr.id = idNew
        sttemp += tr
    st = sttemp



############  Extract time window
st.trim(starttime=datimBeg, endtime=datimEnd)
stWant = Stream()
for idWant in nslcWant:
    stWant += st.select(id=idWant)
#nslc = set(tr.id for tr in stWant)
#print( nslc )



############  Create stream with only the wanted channels
st2 = Stream()
icha = 0
if chas == "z":
    # Loop round wanted stations
    for sta in stas:
        icha += 1
        # Get wanted channels
        try:
            stt = stWant.select(station=sta, component=chas)
            tr = stt[0]
        except:
            tr = Trace(data=np.zeros(2))
            tr.stats.npts = 2
            tr.stats.starttime = datimBeg
            tr.stats.station = sta
            tr.stats.sampling_rate = 100.0
        netf = f'{icha:02d}'
        tr.stats.network = netf
        st2 += tr
elif chas == "h":
    # Loop round wanted stations
    for sta in stas:
        icha += 1
        # Get wanted channels
        try:
            stt = stWant.select(station=sta, channel='HDF')
            tr = stt[0]
        except:
            tr = Trace(data=np.zeros(2))
            tr.stats.npts = 2
            tr.stats.starttime = datimBeg
            tr.stats.station = sta
            tr.stats.sampling_rate = 100.0
        netf = f'{icha:02d}'
        tr.stats.network = netf
        st2 += tr
elif chas == "3c":
    # Loop round wanted stations
    for sta in stas:
        stt = stWant.select(station=sta, channel='HH*')
        if len(stt) == 3:
            for i in range(3):
                tr = stt[i]
                if tr.stats.channel.endswith('Z'):
                    ichat = icha + 1
                elif tr.stats.channel.endswith('1'):
                    ichat = icha + 2
                elif tr.stats.channel.endswith('2'):
                    ichat = icha + 3
                elif tr.stats.channel.endswith('E'):
                    ichat = icha + 2
                elif tr.stats.channel.endswith('N'):
                    ichat = icha + 3
                netf = f'{ichat:02d}'
                tr.stats.network = netf
                st2 += tr
            icha += 3
        else:
            stt = stWant.select(station=sta, channel='BH*')
            if len(stt) == 3:
                for i in range(3):
                    tr = stt[i]
                    if tr.stats.channel.endswith('Z'):
                        ichat = icha + 1
                    elif tr.stats.channel.endswith('E'):
                        ichat = icha + 2
                    elif tr.stats.channel.endswith('N'):
                        ichat = icha + 3
                    netf = f'{ichat:02d}'
                    tr.stats.network = netf
                    st2 += tr
                icha += 3
            else:
                stt = stWant.select(station=sta, channel='SHZ')
                if len(stt) == 1:
                    tr = stt[0]
                    icha += 1
                    netf = f'{icha:02d}'
                    tr.stats.network = netf
                    st2 += tr
                else:
                    stt = stWant.select(station=sta, channel='BLZ')
                    if len(stt) == 1:
                        tr = stt[0]
                        icha += 1
                        netf = f'{icha:02d}'
                        tr.stats.network = netf
                        st2 += tr
elif chas == "all":
    # Loop round wanted stations
    for sta in stas:
        stt = stWant.select(station=sta, channel='HH*')
        if len(stt) == 3:
            for i in range(3):
                tr = stt[i]
                if tr.stats.channel.endswith('Z'):
                    ichat = icha + 1
                elif tr.stats.channel.endswith('1'):
                    ichat = icha + 2
                elif tr.stats.channel.endswith('2'):
                    ichat = icha + 3
                netf = f'{ichat:02d}'
                tr.stats.network = netf
                st2 += tr
            icha += 3
        else:
            stt = stWant.select(station=sta, channel='BH*')
            if len(stt) == 3:
                for i in range(3):
                    tr = stt[i]
                    if tr.stats.channel.endswith('Z'):
                        ichat = icha + 1
                    elif tr.stats.channel.endswith('E'):
                        ichat = icha + 2
                    elif tr.stats.channel.endswith('N'):
                        ichat = icha + 3
                    netf = f'{ichat:02d}'
                    tr.stats.network = netf
                    st2 += tr
                icha += 3
            else:
                stt = stWant.select(station=sta, channel='SHZ')
                if len(stt) == 1:
                    tr = stt[0]
                    icha += 1
                    netf = f'{icha:02d}'
                    tr.stats.network = netf
                    st2 += tr


if not runQuiet:
    print('  Streams extracted for plot: ' + str(len(st2)))



############  Process data
# Detrend
st2.detrend('demean')
if dataLPfilt > 0.0:
    st2.filter("lowpass", freq=dataLPfilt)
st2.detrend('demean')
if dataHPfilt > 0.0:
    st2.filter("highpass", freq=dataHPfilt)
if dataIntegrate:
    st2.filter( "bandpass", freqmax=0.1, freqmin=0.003 )
    st2.integrate
if dataDownsample > 1:
    st2.decimate(factor=dataDownsample, strict_length=False)
st2.detrend('demean')



############  Save data as miniseed and exit
if runMode== "get":
    for trace in st2:
        trace.data = trace.data.astype(np.int32)
        trace.stats.network = "MV"
    st2.write( fileMseedOut, "MSEED" )
    exit(0)



############  Plot signal normalization
if dataNormalize == 'yes':
    equalScale = True
elif dataNormalize == '3c':
    sttemp = Stream()
    for sta in stas:
        sttemp2 = st2.select( station=sta )
        if len(sttemp2) > 0:
            sttemp2.normalize( global_max=True )
            sttemp += sttemp2
    st2 = sttemp
    equalScale = True
else:
    equalScale = False

plotFuncs = 'obspy'

############  Create plot
if plotKind == "tfr":
    thisFig = rodstfr.plot_tfr(tr.data, dt=tr.stats.delta, fmin=plotFmin,
        mode='sqrt', fmax=plotFmax, w0=16., nf=128, fft_zero_pad_fac=4, cmap='jet', show=False )
    thisFig.set_size_inches(plotSize2[0]/100.0, plotSize2[1]/100.0)

elif plotKind == "forai" and numberStations == 1:
    thisFig = rodsPythonThings.plotZforai( st2, windowPre, plotFmin, plotFmax )
    plotFuncs = 'rods'

elif plotKind == "specialz" and numberStations == 1:
    thisFig = rodsPythonThings.plotZManyWays( st2, windowPre, plotSpec, plotFscale, plotZscale, plotFmin, plotFmax )
    plotFuncs = 'rods'

elif plotKind == "spectrumz" and numberStations == 1:
    thisFig = rodsPythonThings.plotZSpectrum( st2, windowPre, plotSpec, plotFscale, plotZscale, plotFmin, plotFmax )
    plotFuncs = 'rods'

elif plotKind == "special3c" and numberStations == 1:
    thisFig = rodsPythonThings.plot3CManyWays( st2, windowPre, plotFscale, plotZscale, plotFmin, plotFmax  )
    plotFuncs = 'rods'

elif plotKind == "partmot" and numberStations == 1:
    thisFig = rodsPythonThings.plot3CPartMot( st2, windowPre, windowAnal  )
    plotFuncs = 'rods'

elif plotKind == "lahar":
    thisFig = rodsPythonThings.plotLahar( st2, windowPre, plotRms, plotFscale, plotZscale, plotFmin, plotFmax )
    plotFuncs = 'rods'
    thisFig.set_size_inches(plotSize2[0]/100.0, plotSize2[1]/100.0)

elif plotKind == "rockfall":
    thisFig = rodsPythonThings.plotRockfall( st2, windowPre, datimEventString )
    plotFuncs = 'rods'

else:
    if plotGrid:
        thisFig = st2.plot(starttime=datimBeg, endtime=datimEnd,
                       equal_scale=equalScale, linewidth=plotLineWidth, show=False, size=plotSize2)
    else:
        thisFig = st2.plot(starttime=datimBeg, endtime=datimEnd,
                       equal_scale=equalScale, linewidth=plotLineWidth, show=False, size=plotSize2)



############  Add title to plot
if plotKind == 'tfr':
    if plotTitleBig:
        thisFig.axes[1].set_title( plotTitle, fontsize='xx-large', fontweight='bold' )
    else:
        thisFig.axes[1].set_title( plotTitle )
else:
    if plotTitleBig:
        thisFig.axes[0].set_title( plotTitle, fontsize='xx-large', fontweight='bold' )
    else:
        thisFig.axes[0].set_title( plotTitle )

# Remove existing title from plot
thisFig.suptitle( '' )



############  Draw event time as vertical green line on plot
if plotNogreen:
    tmp = 'tmp'
elif plotFuncs == 'obspy' and plotKind != 'tfr':
    theseAxes = thisFig.get_axes()
    for thisAxes in theseAxes:
        xLimits = thisAxes.get_xlim()
        yLimits = thisAxes.get_ylim()
        xPlot = xLimits[0] + windowPre/(60*60*24)
        thisAxes.vlines( xPlot, yLimits[0], yLimits[1], colors='g', linewidth= 0.2 )
elif plotFuncs == 'obspy':
    theseAxes = thisFig.get_axes()
    xLimits = theseAxes[0].get_xlim()
    yLimits = theseAxes[0].get_ylim()
    xPlot = xLimits[0] + windowPre
    theseAxes[0].vlines( xPlot, yLimits[0], yLimits[1], colors='g', linewidth= 0.2 )



############  Save plot as png
if not runQuiet:
    print('  Plot file: ' + filePlot)
thisFig.savefig(filePlot)



############  Show plot on screen
if plotShow:
    #thisFig.show()
    subprocess.Popen([ "eog", filePlot ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT)
    # When feh was used in above call, it made the terminal characters invisible, so had to reset terminal
    #subprocess.run( "reset" )



############  End timer
endTime = datetime.now()
elapsed = endTime - startTime
print( "Elapsed time: ", elapsed )



############  find: Function to recursively search for a file and return the full path
def find(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)
