"""
   DWF Python Example
   Author:  Digilent, Inc.
   Revision:  2023-06-23

   Requires:                       
       Python 2.7, 3
"""

from ctypes import *
from dwfconstants import *
import time
import matplotlib.pyplot as plt
import sys
import numpy

if sys.platform.startswith("win"):
    dwf = cdll.dwf
elif sys.platform.startswith("darwin"):
    dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
else:
    dwf = cdll.LoadLibrary("libdwf.so")

# DIO 0 -> Trig 1
# DIO 1 -> Trig 2 and Scope 1
hzClock = 1e6
hzTrig = 5e3
cSamples = 200

hdwf = c_int()
sts = c_byte()
rgdSamples = (c_double*cSamples)()

version = create_string_buffer(16)
dwf.FDwfGetVersion(version)
print("DWF Version: "+str(version.value))

#open device
print("Opening first device")
dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))

if hdwf.value == hdwfNone.value:
    szerr = create_string_buffer(512)
    dwf.FDwfGetLastErrorMsg(szerr)
    print(szerr.value)
    print("failed to open device")
    quit()
    

dwf.FDwfDeviceAutoConfigureSet(hdwf, c_int(0)) # 0 = the device will only be configured when FDwf###Configure is called

hzSys = c_double()
dwf.FDwfDigitalOutInternalClockInfo(hdwf, byref(hzSys))
# clock on DIO-0
dwf.FDwfDigitalOutEnableSet(hdwf, c_int(0), c_int(1))
dwf.FDwfDigitalOutDividerSet(hdwf, c_int(0), c_int(int(hzSys.value/hzClock/2)))
dwf.FDwfDigitalOutCounterSet(hdwf, c_int(0), c_int(1), c_int(1))

# trigger signal on DIO-1
dwf.FDwfDigitalOutEnableSet(hdwf, c_int(1), c_int(1))
dwf.FDwfDigitalOutDividerSet(hdwf, c_int(1), c_int(int(hzSys.value/hzTrig/2)))
dwf.FDwfDigitalOutCounterSet(hdwf, c_int(1), c_int(1), c_int(1))

dwf.FDwfDigitalOutConfigure(hdwf, c_int(1))

print("Starting DIOs")

#set up acquisition
dwf.FDwfAnalogInFrequencySet(hdwf, c_double(hzClock))
dwf.FDwfAnalogInBufferSizeSet(hdwf, c_int(cSamples)) 
dwf.FDwfAnalogInTriggerSourceSet(hdwf, trigsrcExternal2)
dwf.FDwfAnalogInTriggerConditionSet(hdwf, DwfTriggerSlopeRise)
dwf.FDwfAnalogInTriggerPositionSet(hdwf, c_double(cSamples/hzClock/2)) # on the left

dwf.FDwfAnalogInChannelEnableSet(hdwf, c_int(0), c_int(1))
dwf.FDwfAnalogInChannelRangeSet(hdwf, c_int(0), c_double(10))

dwf.FDwfAnalogInSamplingSlopeSet(hdwf, DwfTriggerSlopeRise)
dwf.FDwfAnalogInSamplingSourceSet(hdwf, trigsrcExternal1)

print("Starting oscilloscope")
dwf.FDwfAnalogInConfigure(hdwf, c_int(1), c_int(1))

while True:
    dwf.FDwfAnalogInStatus(hdwf, c_int(1), byref(sts))
    if sts.value == DwfStateDone.value :
        break
    time.sleep(0.1)
print("Acquisition done")

dwf.FDwfAnalogInStatusData(hdwf, 0, rgdSamples, cSamples) # get channel 1 data
dwf.FDwfDeviceCloseAll()

plt.plot(numpy.fromiter(rgdSamples, dtype = numpy.float))
plt.show()


