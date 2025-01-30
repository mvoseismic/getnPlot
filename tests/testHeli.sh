#!/usr/bin/bash

./getnPlot.py --date 2025-01-16 --time 16:00 --pre 0h --dur 48h --kind Z --sta MBLY --kind heli --source mseed --hpfilt 5.0 --heliwidth 60 --shape square --heliscale 1.5
./getnPlot.py --date 2025-01-16 --time 16:00 --pre 0h --dur 48h --kind Z --sta MSS1 --kind heli --source mseed --hpfilt 5.0 --heliwidth 60 --shape square --heliscale 1.5
./getnPlot.py --date 2025-01-16 --time 16:00 --pre 0h --dur 48h --kind Z --sta MBLG --kind heli --source mseed --hpfilt 5.0 --heliwidth 60 --shape square --heliscale 1.5
./getnPlot.py --date 2025-01-16 --time 16:00 --pre 0h --dur 48h --kind Z --sta MBFR --kind heli --source mseed --hpfilt 5.0 --heliwidth 60 --shape square --heliscale 1.5
