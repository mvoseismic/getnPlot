#!/usr/bin/bash

./getnPlot.py --printdatarange --time 03:00 --pre 0h --dur 2h --kind heli --heliwidth 10 --sta MSS1
./getnPlot.py --printdatarange --time 03:00 --pre 0h --dur 2h --kind heli --heliwidth 10 --sta MBLY
./getnPlot.py --printdatarange --time 03:00 --pre 0h --dur 2h --kind heli --heliwidth 10 --sta MBLG
./getnPlot.py --printdatarange --time 03:00 --pre 0h --dur 2h --kind heli --heliwidth 10 --sta MBFR
./getnPlot.py --printdatarange --time 03:00 --pre 0h --dur 2h --kind heli --heliwidth 10 --sta MBBY
./getnPlot.py --printdatarange --time 03:00 --pre 0h --dur 2h --kind heli --heliwidth 10 --sta MBRY
./getnPlot.py --printdatarange --time 03:00 --pre 0h --dur 2h --kind heli --heliwidth 10 --sta MBRV

#./getnPlot.py --yesterday --time 00:00 --pre 0h --dur 6h --kind Z --sta MSS1 --kind heli --source mseed --heliwidth 15 --heliscale 1.0 --plotfile test01
#./getnPlot.py --yesterday --time 00:00 --pre 0h --dur 6h --kind Z --sta MSS1 --kind heli --source mseed --heliwidth 15 --heliscale 2.0 --plotfile test02
#./getnPlot.py --yesterday --time 00:00 --pre 0h --dur 6h --kind Z --sta MSS1 --kind heli --source mseed --heliwidth 15 --heliscale 0.5 --plotfile test03
#./getnPlot.py --yesterday --time 06:00 --pre 0h --dur 12h --kind Z --sta MBLY --kind heli --source mseed --heliwidth 10 --plotfile test04
#./getnPlot.py --yesterday --time 06:00 --pre 0h --dur 12h --kind Z --sta MBLY --kind heli --source mseed --heliwidth 10 --plotfile test05 --shape square
#./getnPlot.py --yesterday --time 06:00 --pre 0h --dur 12h --kind Z --sta MBLY --kind heli --source mseed --hpfilt 1.0 --heliwidth 10 --plotfile test06 --shape portrait
#./getnPlot.py --date 2025-01-16 --time 00:00 --pre 0h --dur 48h --kind Z --sta MBLY --kind heli --source mseed --hpfilt 5.0 --heliwidth 60 --plotfile test07 --shape square
#./getnPlot.py --date 2025-01-16 --time 00:00 --pre 0h --dur 48h --kind Z --sta MSS1 --kind heli --source mseed --hpfilt 5.0 --heliwidth 60 --plotfile test08 --shape square
