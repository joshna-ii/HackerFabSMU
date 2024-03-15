"""
   DWF Python Example
   Author:  Digilent, Inc.
   Revision:  2022-03-08

   Requires:                       
       Python 2.7, 3
"""

from ctypes import *
from dwfconstants import *
import math
import time
import sys
import matplotlib.pyplot as plt
import numpy


if sys.platform.startswith("win"):
    dwf = cdll.dwf
elif sys.platform.startswith("darwin"):
    dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
else:
    dwf = cdll.LoadLibrary("libdwf.so")

hdwf = c_int()
sts = c_byte()

version = create_string_buffer(16)
dwf.FDwfGetVersion(version)
print("DWF Version: "+str(version.value))

dwf.FDwfParamSet(DwfParamOnClose, c_int(0)) # 0 = run, 1 = stop, 2 = shutdown

print("Opening first device")
dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))

if hdwf.value == hdwfNone.value:
    szError = create_string_buffer(512)
    dwf.FDwfGetLastErrorMsg(szError)
    print("failed to open device\n"+str(szError.value))
    quit()

dwf.FDwfDeviceAutoConfigureSet(hdwf, c_int(0)) # 0 = the device will only be configured when FDwf###Configure is called

cReal = c_int()
cFitler = c_int()
cTotal = c_int()

cFir = c_int()
cIir = c_int()

dwf.FDwfAnalogInChannelCounts(hdwf, byref(cReal), byref(cFitler), byref(cTotal))
print("Oscilloscope channels: Real:"+str(cReal.value)+" Filter: "+str(cFitler.value)+" Total: "+str(cTotal.value))

if cFitler.value == 0 :
    quit()
    
# channel  order is real, filters and AWG-loopback, first filter channel index is cReal
dwf.FDwfAnalogInChannelFiirInfo(hdwf, c_int(cReal.value+0), byref(cFir), byref(cIir))
print("Filter support: FIR:"+str(cFir.value)+" IIR: "+str(cIir.value))

if cFir.value == 0 :
    quit()
    
cSamples = 400

print("Generating square wave...")
#                                    AWG 1     carrier
dwf.FDwfAnalogOutNodeEnableSet(hdwf, c_int(0), c_int(0), c_int(1))
dwf.FDwfAnalogOutNodeFunctionSet(hdwf, c_int(0), c_int(0), funcSquare)
dwf.FDwfAnalogOutNodeFrequencySet(hdwf, c_int(0), c_int(0), c_double(400e3))
dwf.FDwfAnalogOutNodeAmplitudeSet(hdwf, c_int(0), c_int(0), c_double(1.0))
dwf.FDwfAnalogOutConfigure(hdwf, c_int(0), c_int(1))

#set up acquisition
dwf.FDwfAnalogInFrequencySet(hdwf, c_double(100e6))
dwf.FDwfAnalogInBufferSizeSet(hdwf, c_int(cSamples)) 

dwf.FDwfAnalogInChannelEnableSet(hdwf, c_int(0), c_int(1))
dwf.FDwfAnalogInChannelRangeSet(hdwf, c_int(0), c_double(4.0))

dwf.FDwfAnalogInChannelEnableSet(hdwf, c_int(cReal.value+0), c_int(1))
dwf.FDwfAnalogInChannelRangeSet(hdwf, c_int(cReal.value+0), c_double(4.0))
dwf.FDwfAnalogInChannelWindowSet(hdwf, c_int(cReal.value+0), DwfWindowBlackman, cFir, c_double(0))
# FIR, low pass, cutoff 0.01X of system frequency with DwfFiirRaw or sample rate
dwf.FDwfAnalogInChannelFiirSet(hdwf, c_int(cReal.value+0), DwfFiirRaw, DwfFiirFir, DwfFiirLowPass, cFir, c_double(0.01), c_double(0), c_double(0))

#set up trigger
dwf.FDwfAnalogInTriggerAutoTimeoutSet(hdwf, c_double(1)) 
dwf.FDwfAnalogInTriggerSourceSet(hdwf, trigsrcDetectorAnalogIn) #one of the analog in channels
dwf.FDwfAnalogInTriggerTypeSet(hdwf, trigtypeEdge)
dwf.FDwfAnalogInTriggerChannelSet(hdwf, c_int(0)) # first channel
dwf.FDwfAnalogInTriggerLevelSet(hdwf, c_double(0.0)) # V
dwf.FDwfAnalogInTriggerConditionSet(hdwf, DwfTriggerSlopeRise) 

dwf.FDwfAnalogInConfigure(hdwf, c_int(1), c_int(0))
time.sleep(0.1)

print("Starting repeated acquisitions")
dwf.FDwfAnalogInConfigure(hdwf, c_int(1), c_int(1))

rgdSamples1 = (c_double*cSamples)()
rgdSamples2 = (c_double*cSamples)()

while True:
    dwf.FDwfAnalogInStatus(hdwf, c_int(1), byref(sts))
    if sts.value == DwfStateDone.value :
        break
    time.sleep(0.001)

dwf.FDwfAnalogInStatusData(hdwf, c_int(0), rgdSamples1, c_int(cSamples)) # get channel 1 data
dwf.FDwfAnalogInStatusData(hdwf, c_int(cReal.value+0), rgdSamples2, c_int(cSamples)) # get channel 2, filter channel 1 data

dwf.FDwfDeviceCloseAll()

plt.plot(numpy.fromiter(rgdSamples1, dtype = numpy.float), label='C1')
plt.plot(numpy.fromiter(rgdSamples2, dtype = numpy.float), label='F1')
plt.show()


