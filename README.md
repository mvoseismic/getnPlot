# getnPlot

Plot seismic waveforms in a number of ways from a number of sources.

## Description

getnPlot will create a plot of one or more waveforms from several sources. It  is used to generate "standard" plots that are easily compared. It can also be used to generate plots that are modified or combined using scripts.

## Getting Started

### Dependencies

* Python
* obspy
* Python modules: https://github.com/dormant/pythonModules
* findwavget
* imagemagick needed for some scripts

### Installing

* Edit location of Python modules in *getnPlot.py*.
* Edit *getnPlot* for local Python environment.
* Copy these scripts to *~/bin*.
	* *getnPlot*
	* *getnPlot.py*
	* *findWavGet*

### Executing program

#### If in python enviroment
```
getnPlot.py
```
#### If not in python enviroment
```
getnPlot
```

## Options

```
  -h, --help        show this help message and exit
  -v, --version     show program's version number and exit
  --mode            Mode of operation: getnplot | get | plot | test (default: getnplot)
  -q, --quiet       No screen output (default: False)
  --source          Data source (auto tries wws then mseed then cont): auto | wws | mseed | cont | event | filename (default: auto)
  --wwsip           Hostname or IP address of winston wave server (default: 172.17.102.60)
  --wwsport         Port of winston wave server (default: 16022)
  -k , --kind       Kind of plot (use all for get only): allZ | all3C | closeZ | close3C | radianZ | radian3C | Z | specialZ | spectrumZ | 3C | special3C | irishZ | irish3C | lahar | tfr | forAI | rockfall | partmot | all | allplusZ | strain | strainplus | infra | heli | longsgram | stringthing (default: allZ)
  --sta             Station(s) to be plotted, comma separated) (not used in some kinds of plot). (default: MSS1)
  -d , --date       Date of event (UTC): today | yesterday | yyyy-mm-dd | yyyy.jjj (default: today)
  -t , --time       Time of event (UTC): hh:mm | hh:mm:ss | hh:mm:ss.s | now |now-X | now-Xs | now-Xm (default: now)
  --yesterday       Set date to yesterday (default: False)
  --today           Set date to today (default: False)
  -p , --pre        Window starts this many seconds before event time, append m or h to input minutes or hours (default: 10)
  -l , --dur        Window duration, in seconds: append m or h to input minutes or hours (default: 60)
  --twin            Duration, in seconds, of window for analysis: append m or h to input minutes or hours (default: 30)
  --shape           Shape of plot: landscape | portrait | square | long | xlong | xxlong | xxxlong | xxxxlong | thin (default: landscape)
  --size            Length (pixels) of longest side of plot (default: 1920)
  --tscale          Time scale units (defaults to s or what window duration is specified in): d | s | m | h (default: d)
  --ylim            Limits of Y axis for plot (+/- this number) (default: 0)
  --fscale          Frequency scale for analysis and plotting: linear | log (default: linear)
  --zscale          Z scale for plotting: amp | power | log | sqrt (default: sqrt)
  --plotspec        No spectrum in TFR plot (default: False)
  --plotnorms       No RMS in lahar plot (default: False)
  --show            Show plot on screen as well as saving it (default: False)
  --grid            Add time-axis grid to seismograms (default: False)
  --title           Title for plot, defaults gives all information. Special arguments: sta, datetime, date, time, tag (default: None)
  --bigtitle        Big bold title. (default: False)
  --nogreen         Do not plot green line for arrival/event time. (default: False)
  --linewidth       Thickness of plotted line (default: 0.5)
  --fmin            Minimum frequency for analysis and plotting (default: 0)
  --fmax            Maximum frequency for analysis and plotting (default: 100.0)
  --hpfilt          High-pass filter corner frequency (default: 0.0)
  --lpfilt          Low-pass filter corner frequency (default: 0.0)
  --norm            Normalise data: no | yes | 3c (default: 3c)
  --mult            Multiply data by this much (default: 1.0)
  --integrate       Integrate seismic data (default: False)
  --abs             Use absolute value of data (default: False)
  --sqrt            Use square-root value of data (default: False)
  --log             Use logarithinc value of data (default: False)
  --env             Use signal envelope (default: False)
  --vec             Replaces 3C sets with vector sum (default: False)
  --dir             Directory name for plots and files (default: .)
  --tag             String (no spaces) used in output file names (default: )
  --plotfile        Plot file name, no extension, default is based on arguments (default: )
  --datafile        Data file name, no extension, default is based on arguments (default: )
  --datimtag        Number of characters in time bit of datim tag (default: 4)
  --downsample      Downsampling factor (default: 1)
  --saverms         Save RMS of signals in a text file (default: False)
  --nochaff         Remove all labelling, titles (default: False)
  --noscnl          Remove scnl label in panel (default: False)
  --heliwidth       Width (minutes) of helicorder plot (default: 15.0)
  --heliscale       Scaling of helicorder plot (default: 0.0)
  --printdatarange  Print out range of data for each channel (default: False)
```

## Scripts (as of 2025-02-10)
| Script       | Function |
| -------------| -------------------|
| *findWavGet* | Locates data files in MVO CONT_ database and merges them if appropriate. |
| *getnPlot*   | Bash wrapper script to setup Python environment for *getnPlot.py*. |
| *getnPlot*.py | Main program. |
| *getnPlot3c* | Generates a 3C plot for each of 10 stations.|
| *getnPlotHeli* | Runs *getnPlot* many times to create a helicorder-like plot. ||
| *getnPlotIrish* | Runs *getnPlot* several times, suitable for events near Irish Ghaut. |
| *getnPlotRemote* | Runs *getnPlot* on *opsproc2*. 
| *getnPlotRock* | Runs getnPlot several times, suitable for rockfalls. |
| *getnPlotRockAmps* | Runs getnPlot for rockfalls to get envelope amplitudes. |
| *getnPlotSpecial* | Creates composite plot useful for comparing events.|
| *getnPlotSpecial2* | Like *getnPlotSpecial* but without the bottom panel.|
| *getnPlotSpecial3* | Creates thin composite plot that can be montaged with *getnPlotSpecial3Montage*.|
| *getnPlotSpecial3a* | Like *getnPlotSpecial3* but with fewer stations.|
| *getnPlotSpecial3long* | Like *getnPlotSpecial3* but with more data.|
| *getnPlotSpecial3Montage* | Shell script to create montage of *getnPlotSpecial3* or *getnPlotspecial3a* images.|
| *getnPlotVT* | Runs *getnPlot* several times, suitable for VTs. |
| *getnPlotTiledTfr* | Runs *getnPlot* to get a tiled plot of TFR from the six closest stations. |
| *getnPlotVtse2* | Runs *getnPlot* for each time in a text file, passed as argument. The text file can be generated by *mulplt2vtse*.|
| *getnPlotWav* | |
| *getWaves.py* |  |
| *panPlots.py* | Standalone script to generate "panacea" plots. Testbed for *--kind pan* option.|
| *select2getnp.pl* | |
| *vtst2getnp.pl* | |

## Examples
Plot all default Z channels for a 60-second window with 10 seconds before time given.
```
getnPlot 21:23
getnPlot 01:12:59.1
getnPlot 20250123-1220
```
Plot all default Z channels for a 120-second window with 40 seconds before time given.
```
getnPlot --time 01:12:59.1 --pre 40s --dur 120s
```
Plot three Z channels for a 20-minute window with two minutes before time given.
```
getnPlot --time 01:12:59.1 --pre 2m --dur 20m --kind Z --sta MSS1,MBFR,MBLG
```
Plot a two-day helicorder (slow)
```
getnPlot --date 2025-01-16 --time 16:00 --pre 0h --dur 48h --kind Z --sta MSS1 --kind heli --source mseed --hpfilt 5.0 --heliwidth 60 --shape square --heliscale 1.5
```
## Author

Roderick Stewart, Dormant Services Ltd

rod@dormant.org

https://services.dormant.org/

## Version History

* 1.0
    * Crappy first attempt
* 2.0-dev
    * Working version

## License

This project is licensed to Montserrat Volcano Observatory.
