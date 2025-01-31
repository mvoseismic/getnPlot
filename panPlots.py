#!/usr/bin/env python
# panPlots.py
#
# Gets all data for a time window for one channel and creates a panplot
#
# R.C. Stewart, 5-January-2023
#

############  Imports
import os
import sys
import glob
import argparse
import re
import obspy
import warnings
import matplotlib.pyplot as plt
import numpy as np
import statistics
import gc

sys.path.append( '/'.join( [os.path.expanduser('~'), 'src/pythonModules' ] ) )

import rodsPythonThings
import rodsPlotTfr as rodstfr

from datetime import datetime, date, timedelta, time
from dateutil import parser as dparser
from dateutil.rrule import rrule, DAILY
from obspy.clients.earthworm import Client
from obspy.core import UTCDateTime, Stream, Trace
from pathlib import Path
from obspy.signal.tf_misfit import plot_tfr
from obspy.clients.filesystem.sds import Client as sdsClient
from matplotlib.ticker import NullFormatter
from timeit import default_timer as timer
from cycler import cycler
from scipy import signal
from obspy.signal import util



############  plotPanacea: Function to plot a single channel as a panacea plot and return the figure
def plotPanacea( datimBeg, sta, gain, runQuiet ):

    from matplotlib.axis import Axis

    secInDay = 60*60*24
    datimEnd = datimBeg + timedelta(seconds=secInDay)

    ############  Get all waveform data for interval
    st = Stream()

    bits = sta.split('.')
    network = bits[0]
    station = bits[1]
    location = bits[2]
    channel = bits[3]
    if not runQuiet:
        print( bits )

    # First try Waveserver
    wwsIP = "172.17.102.60"
    wwsPort = 16022
    dataSource = 'waveserver ' + str(wwsIP)
    client = Client(wwsIP, wwsPort, clientTimeout)
    info = client.get_availability(network=network, station=station, channel=channel)
    if not runQuiet:
        print( info )
    for n, s, l, c, start, end in info:
        st += client.get_waveforms(n, s, l, c, datimBeg, datimEnd)

    if len(st) == 0:
        # Second try miniseed files
        dataSource = 'continuous miniseed data'
        if runQuiet:
            warnings.filterwarnings("ignore")
        for netw in ["MV", "MC", "CU", "TR"]:
            client = sdsClient(dirnameSeparator.join([pathMseed, netw]))
            client.FMTSTR = '{station}/{year}.{doy:03d}.{network}.{station}.{location}.{channel}.mseed'
            st += client.get_waveforms(netw, '*',
                                           '*', '*', datimBeg, datimEnd)
        if runQuiet:
            warnings.filterwarnings("default")

    if not runQuiet:
        print('  Streams from ' + dataSource + ': ' + str(len(st)))

    ############  Bug out if nothing got
    if len(st) == 0:
        if not runQuiet:
            print('No streams loaded')
        return None


    ############  Print out all streams
    if not runQuiet:
        print(st.__str__(extended=True))


    ############  Process data
    # Detrend
    st.detrend('demean')


    # Data
    tr = st[0]
    data = tr.data
    data = data[0:-1]
    data = data * gain
    npts = tr.stats.npts
    dt = tr.stats.delta
    samprate = tr.stats.sampling_rate
    fnyq = samprate/2.0
    t = np.arange(0, npts / samprate, 1 / samprate)
    t = t[0:-1]
    tday = 24*60*60

    # Free up some memory
    del st
    #del tr
    gc.collect()

    # RMS in chunks
    trFilt = tr.copy()
    trFilt.filter('highpass', freq=1.0, corners=2, zerophase=True)
    dataFilt = trFilt.data
    minutesRMS = 10;
    samplesRMS = int( minutesRMS * 60 * samprate )
    #chunks = np.array_split(dataFilt, 144)
    dataRMS = list()
    timeRMS = list()
    for isamp in np.arange(0,npts,samplesRMS):
        dataChunk = dataFilt[isamp:isamp+samplesRMS-1]
        rms = np.sqrt(np.mean(dataChunk**2))
        dataRMS.append( rms )
        time = isamp/samprate
        time += 0.5*samplesRMS/samprate
        timeRMS.append( time )

    #if not runQuiet:
    #    datamax = int( max(max(data),-min(data)) )
    #    datamed = int( statistics.median(abs(data)) )
    #    datamaxRMS = int( max(dataRMS) )
    #    datamedRMS = int( statistics.median(dataRMS) )

    #    ratioMaxs = datamax/datamaxRMS
    #    print( ': '.join([ '  Max data', str( datamax ) ]) )
    #    print( ': '.join([ '  Median data', str( datamed ) ]) )
    #    print( ': '.join([ '  Max RMS', str( datamaxRMS  ) ]) )
    #    print( ': '.join([ '  Median RMS', str( datamedRMS  ) ]) )
    #    print( ': '.join([ '  Max data / max RMS', str( ratioMaxs  ) ]) )


    dataLimit = 10000.0
    dataRmsLimit = 2000.0

    # Time ticks
    tTicks = np.arange(0, tday+1, 3600)

    # Time labels
    lis = np.arange(0,25)
    tTickLabels = []
    for n in lis:
        n2 = n-4
        if n2 < 0:
            n2 = n2 + 24
        buf = "%02d:00 (%02d:00)" % (n, n2)
        tTickLabels.append(buf)

    ############  Create plot
    x1 = 0.1
    x2 = 0.4
    x3 = 0.7
    x4 = 0.8
    x5 = 0.9
    y1 = 0.05
    y2 = 0.95


    fig = plt.figure()
    fig.set_size_inches(plotSize[0]/100.0, plotSize[1]/100.0)

    fontSize = 24

    xlabelx = 0.5
    xlabely = 1.01
    ylabel = 'UTC (LT)'
    ylabelx = 1.3
    ylabely = 1.005

    # Plot signal
    ax_sig = fig.add_axes([ x3, y1, x4-x3, y2-y1 ] )
    ax_sig.plot( data, t, 'b', linewidth=0.5 )
    ax_sig.xaxis.set_major_formatter(NullFormatter())
    ax_sig.yaxis.set_major_formatter(NullFormatter())
    datamax = max(max(data),-min(data))
    if datamax > dataLimit:
        ax_sig.plot( data*(dataLimit/datamax), t, 'r', linewidth=0.5 )
    ax_sig.set_xlim( -1.0 * dataLimit, dataLimit)
    ax_sig.set_ylim(-600, tday)
    ax_sig.invert_yaxis()
    ax_sig.tick_params(axis='both', direction='in', top=False, bottom=False, left=True, right=True, length=16, width=2)
    ax_sig.grid( visible=True, which='major', axis='y', linewidth=1 )
    ax_sig.set_yticks( tTicks )
    plt.xlabel( 'Seismogram', fontsize=fontSize, fontweight='bold' )
    ax_sig.xaxis.set_label_position('top')
    Axis.set_label_coords(ax_sig.xaxis, xlabelx, xlabely)


    # Plot RMS
    ax_rms = fig.add_axes([ x4, y1, x5-x4, y2-y1 ] )
    ax_rms.plot( dataRMS[0:-1], timeRMS[0:-1], 'b', linewidth=2.0 )
    ax_rms.xaxis.set_major_formatter(NullFormatter())
    #ax_rms.yaxis.set_major_formatter(NullFormatter())
    datamax = max(dataRMS)
    if datamax > dataRmsLimit:
        multBy = dataRmsLimit/datamax
        dataRMS2 = np.array( dataRMS ) * multBy
        ax_rms.plot( dataRMS2[0:-1], timeRMS[0:-1], 'r', linewidth=2.0 )
    ax_rms.set_xlim( 0, dataRmsLimit)
    ax_rms.set_ylim(-600, tday)
    ax_rms.invert_yaxis()
    ax_rms.tick_params(axis='both', direction='inout', top=False, bottom=False, left=True, right=True, labelleft=False, labelright=True, labelsize=fontSize-4, length=16, width=2)
    ax_rms.grid( visible=True, which='major', axis='y', linewidth=1 )
    ax_rms.set_yticks( tTicks )
    tit = "%d min RMS (1Hz HP)" % (minutesRMS)
    plt.xlabel( tit, fontsize=fontSize, fontweight='bold' )
    ax_rms.xaxis.set_label_position('top')
    ax_rms.set_yticklabels( tTickLabels )
    Axis.set_label_coords(ax_rms.xaxis, xlabelx, xlabely)
    plt.ylabel( ylabel, rotation='horizontal', fontsize=fontSize-4 )
    Axis.set_label_coords(ax_rms.yaxis, ylabelx, ylabely)

    fig.text( x4, 0.7*y1, 'Fixed magnification', fontsize=fontSize-4, color='blue', ha='center' )
    fig.text( x4, 0.4*y1, 'Normalized to peak', fontsize=fontSize-4, color='red', ha='center' )


    # Plot helicorder
    minutesLine = 10;
    samplesLine = int( minutesRMS * 60 * samprate )

    data2 = np.reshape( data, (samplesLine, -1), order='F' )
    data2 = data2 / dataLimit
    data2 = data2 * 4.0
    t2 = np.arange(0, samplesLine / samprate, 1 / samprate)
    t2 = t2/60

    ax_hel = fig.add_axes([ x1, y1, x2-x1, y2-y1 ] )

    nrows = len( data2[0] )

    #ax_hel.set_prop_cycle(cycler('color', ['#ff7f0e', '#2ca02c', '#d62728', '#9467bd']) )
    ax_hel.set_prop_cycle(cycler('color', [(0,0,0),(.5,0,0),(0,0,.5),(0,.5,0)] ) )
    for irow in range(0,nrows):
        data3 = data2[:,irow]
        data3 = data3 + nrows - irow
        ax_hel.plot( t2, data3, linewidth=0.5 )
    ax_hel.set_xlim( 0, t2[-1] )
    ax_hel.set_ylim( 0, nrows+1)
    ax_hel.set_xticks( np.arange(0, minutesLine, step=1) )
    ax_hel.set_yticks( np.arange(0, nrows+1, step=6) )
    ax_hel.tick_params(axis='both', direction='out', top=False, bottom=True, left=True, right=True, labelleft=True, labelright=False, labelsize=fontSize-4, length=16, width=2)
    plt.xlabel( 'Helicorder', fontsize=fontSize, fontweight='bold' )
    ax_hel.xaxis.set_label_position('top')
    Axis.set_label_coords(ax_hel.xaxis, xlabelx, xlabely)
    tTickLabels.reverse()
    ax_hel.set_yticklabels( tTickLabels )
    plt.ylabel( ylabel, rotation='horizontal', fontsize=fontSize-4 )
    ylabelx = -0.1
    Axis.set_label_coords(ax_hel.yaxis, ylabelx, ylabely)

    fig.text( 0.5*(x2+x1), 0.4*y1, 'Minutes', fontsize=fontSize-4, ha='center' )


    # Plot spectrogram
    npts = len( data )
    fnyq = samprate/2.0
    nfft = util.next_pow_2(npts) ###### * 4
    #fff, ttt, sss = signal.spectrogram( data, fs=samprate, window='hamming', nperseg=256, noverlap=128, nfft=nfft, detrend='constant' )
    fff, ttt, sss = signal.spectrogram( data, fs=samprate, scaling='spectrum' )
    sss = np.sqrt( np.abs(sss) )
    ssss = sss.transpose()
    ax_sgr = fig.add_axes([ x2, y1, x3-x2, y2-y1 ])
    ax_sgr.pcolormesh( fff, ttt, ssss, shading='gouraud', cmap='jet' )
    ax_sgr.set_yscale("linear")
    ax_sgr.set_xlim(0.0, fnyq)
    ax_sgr.set_ylim(ttt[0], ttt[-1])
    ax_sgr.invert_yaxis()
    ax_sgr.yaxis.set_major_formatter(NullFormatter())
    ax_sgr.tick_params(axis='both', direction='out', top=False, bottom=True, left=False, right=False, labelsize=fontSize-4, length=16, width=2)
    plt.xlabel( 'Spectrogram', fontsize=fontSize, fontweight='bold' )
    ax_sgr.xaxis.set_label_position('top')
    Axis.set_label_coords(ax_sgr.xaxis, xlabelx, xlabely)

    fig.text( 0.5*(x3+x2), 0.4*y1, 'Frequency (Hz)', fontsize=fontSize-4, ha='center' )

    plotTitle = '  '.join([ sta, datimBeg.strftime("%Y-%m-%d") ])
    fig.suptitle( plotTitle, x=0.01, y=0.99, fontsize=fontSize, fontweight='bold', ha='left' )

    return fig


############  Start timer
start = timer()

############  Arguments
parser = argparse.ArgumentParser( prog='panPlots', description='Get seismic data and plot it', usage='%(prog)s [options]',
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                 epilog = 'Example:  panPlots --date yesterday' )

parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.0')

parser.add_argument('-q', '--quiet', action='store_true', help='No screen output')

parser.add_argument('-d', '--date', default='yesterday', help='Date of event (UTC): today | yesterday | yyyy-mm-dd | yyyy.jjj', metavar='')

parser.add_argument('--dir', default='.', help='Directory name for plots and files', metavar='')

args = parser.parse_args()


############  Assign arguments, parsing if necessary
runQuiet = args.quiet
eventDate = args.date
outDir = args.dir


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



############  Sort out dates and times
if eventDate == 'yesterday':
    evDate = UTCDateTime(today.year, today.month, today.day) - secInDay
elif eventDate == 'today':
    evDate = UTCDateTime(today.year, today.month, today.day)
else:
    evDate = dparser.parse(eventDate)

datimBeg = evDate



plotSize = (4740,2963)
fontSize = 32


############  Channels wanted for all plot types
nslcWant = {
    'MV.MBLG.00.HHZ',
    'MV.MBLY.00.HHZ',
    'MV.MBRY..BHZ',
    'MV.MSS1..SHZ',
}


datimEventString = evDate.strftime("%Y%m%d")

numberStations = len( nslcWant )

for sta in nslcWant:

    bits = sta.split('.')
    network = bits[0]
    station = bits[1]
    location = bits[2]
    channel = bits[3]
    if location == '':
        location = '--'
    scnl = '_'.join([ station, channel, network, location ])
    filePlot = filenameSeparator.join([scnl, datimEventString, 'png'])
    filePlot = dirnameSeparator.join([outDir, filePlot])

    if sta == 'MV.MSS1..SHZ':
        gain = 1.0
    elif sta == 'MV.MBRY..BHZ':
        gain = 0.3 
    else:
        gain = 0.1 

    figPan = plotPanacea( datimBeg, sta, gain, runQuiet )

    ############  Save plot as png
    if not runQuiet:
        print('  Plot file: ' + filePlot)
    figPan.savefig(filePlot)


############# End timer
end = timer()
print('  Elapsed time: ' + str( timedelta(seconds=end-start) ) )
