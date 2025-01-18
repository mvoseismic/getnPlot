# getnPlot

Plot seismic waveforms in a number of ways from a number of sources.

## Description

getnPlot will create a plot of one or more waveforms from several sources. It  is used to generate "standard" plots that are easily compared. It can also be used top generate plots that are modified or combined using scripts.

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
	* getnPlot
	* getnPlot.py
	* findWavGet

### Executing program

#### If in python enviroment
```
getnPlot.py
```
#### If not in python enviroment
```
getnPlot
```
## Scripts (as of 2025-01-43)
| Script     | Function                 |
| -----------| -------------------------|
| findWavGet | Locates data files in MVO CONT_ database and merges them if appropriate. |
| getnPlot   | Bash wrapper script to setup Pythn environment for getnPlot.py. |
| getnPlot.py | Main program. |
| getnPlot3c | |
| getnPlotHeli | Example script to create a helicorder-like plot. ||
| getnPlotIrish | Runs getnPlot several times, suitable for events near Irish Ghaut. |
| getnPlotRemote | Runs getnPlot on *opsproc2*. 
| getnPlotRock | Runs getnPlot several times, suitable for rockfalls. |
| getnPlotSpecial | |
| getnPlotSpecial2 | |
| getnPlotSpecial3 | |
| getnPlotSpecial3a | |
| getnPlotSpecial3long | |
| getnPlotSpecial3Montage | |
| getnPlotVT | Runs getnPlot several times, suitable for VTs. |
| getnPlotVtse2 | |
| getnPlotWav | |
| getWaves.py | |
| panPlots.py | |
| select2getnp.pl | |
| vtst2getnp.pl | |

## Help

Any advise for common problems or issues.
```
getnPlot --help
```

## Author

Roderick Stewart, Dormant Services Ltd

rod@dormant.org

https://services.dormant.org/


## Version Histo

* 1.0
    * Crappy first attemptVarious bug fixes and optimizations
    * See [commit change]() or See [release history]()
* 2.0-dev
    * Working version

## License

This project is licensed to Montserrat Volcano Observatory.
