#!/usr/bin/env python

import obspy
fileIn = "mseed_files/2020_11_08_0340_00.msd"
fileOut = "test.mseed"

st = obspy.read(fileIn)
print( st[0].stats )

st.write(fileOut, format='MSEED')


st2 = obspy.read(fileOut)
print( st2[0].stats )
