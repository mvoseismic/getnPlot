#!/usr/bin/env python
# getWaves.py
#
# Gets all data for a time window from wws and saves as mseed file.
#
# R.C. Stewart, 2023-06-10
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
if hostname == 'opsproc2':
    sys.path.append( '/'.join( [os.path.expanduser('~'), 'src/pythonModules' ] ) )
else:
    sys.path.append( '/'.join( [os.path.expanduser('~'), 'STUFF/src/pythonModules' ] ) )

import rodsPythonThings
import rodsPlotTfr as rodstfr

############  For timer 
startTime = datetime.now()



############  Arguments
parser = argparse.ArgumentParser( prog='getWaves', description='Get seismic data and save as mseed file', usage='%(prog)s [options]',
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                 epilog = 'Example:  getnPlot --date yesterday --time 12:37 --pre 20 --dur 90' )

parser.add_argument('-v', '--version', action='version', version='%(prog)s 2.0-dev')

parser.add_argument('-d', '--date', default='today', help='Date of event (UTC): today | yesterday | yyyy-mm-dd | yyyy.jjj', metavar='')
parser.add_argument('-t', '--time', default='now', help='Time of event (UTC): hh:mm | hh:mm:ss | hh:mm:ss.s | now |now-X | now-Xs | now-Xm', metavar='')

parser.add_argument('-p', '--pre', default='10', help='Window starts this many seconds before event time, append m or h to input minutes or hours', metavar='')
parser.add_argument('-l', '--dur', default='60', help='Window duration, in seconds: append m or h to input minutes or hours', metavar='')

args = parser.parse_args()



############  Assign arguments, parsing if necessary
eventDate = args.date
eventTime = args.time
wpre = args.pre
plotTscale = 's'
if wpre[-1] == 's':
    windowPre = int( wpre[:-1] )
elif wpre[-1] == 'm':
    windowPre = 60 * int( wpre[:-1] )
elif wpre[-1] == 'h':
    windowPre = 3600 * int( wpre[:-1] )
else:
    windowPre = int( wpre )
wdur = args.dur
if wdur[-1] == 's':
    windowDur = int( wdur[:-1] )
elif wdur[-1] == 'm':
    windowDur = 60 * int( wdur[:-1] )
    if plotTscale == 'd':
        plotTscale = 'm'
elif wdur[-1] == 'h':
    windowDur = 3600 * int( wdur[:-1] )
    if plotTscale == 'd':
        plotTscale = 'h'
else:
    windowDur = int( wdur )



############  Constants
secInDay = 60*60*24
filenameSeparator = "."
filenameSeparator2 = "-"
dirnameSeparator = "/"
clientTimeout = 20
today = datetime.utcnow().date()
datimNow = datetime.utcnow()
wwsIP = '172.17.102.60'
wwsPort = 16022




############  Sort out dates and times
if eventDate == 'yesterday':
    evDate = UTCDateTime(today.year, today.month, today.day) - secInDay
elif eventDate == 'today':
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

datimEventString = evDatim.strftime("%Y%m%d-%H%M")

if plotTscale == 'h':
    windowString = str(int(windowDur/3600))+"h"+str(int(windowPre/3600))
elif plotTscale == 'm':
    windowString = str(int(windowDur/60))+"m"+str(int(windowPre/60))
else:
    windowString = str(windowDur)+"s"+str(windowPre)

fileMseedOut = filenameSeparator2.join([datimEventString, 'allChannels', windowString])
fileMseedOut = filenameSeparator.join([fileMseedOut, 'mseed'])


############  Get all waveform data for interval
st = Stream()

# Waveserver
# Define wave server
client = Client(wwsIP, wwsPort, clientTimeout)
# Fetch all data from waveserver
info = client.get_availability(network='*', station='*', channel='*')
for net, sta, loc, cha, start, end in info:
    st += client.get_waveforms(net, sta, loc, cha, datimBeg, datimEnd)


############  Save data as miniseed and exit
st.write( fileMseedOut, "MSEED" )


