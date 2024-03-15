"""
   DWF Python Example
   Author:  Digilent, Inc.
   Revision:  2023-10-16

   Requires:                       
       Python 2.7, 3
"""

from ctypes import *
import time
from dwfconstants import *
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
version = create_string_buffer(16)
dwf.FDwfGetVersion(version)
print("DWF Version: "+str(version.value))

dwf.FDwfParamSet(DwfParamOnClose, c_int(0)) # 0 = run, 1 = stop, 2 = shutdown

#open device
print("Opening first device...")
dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))

if hdwf.value == hdwfNone.value:
    print("failed to open device")
    quit()

# the device will only be configured when FDwf###Configure is called
dwf.FDwfDeviceAutoConfigureSet(hdwf, c_int(0)) 

hzSignal = 1e3
cPeriods = 5
cDelay = 1
cSamples = 4000

print("Configure Scope")
dwf.FDwfAnalogInFrequencySet(hdwf, c_double(hzSignal*cSamples/(cPeriods+cDelay)))
dwf.FDwfAnalogInChannelEnableSet(hdwf, c_int(0), c_int(1))
dwf.FDwfAnalogInChannelEnableSet(hdwf, c_int(1), c_int(1))
dwf.FDwfAnalogInChannelRangeSet(hdwf, c_int(-1), c_double(2.0))
dwf.FDwfAnalogInBufferSizeSet(hdwf, c_int(cSamples))
dwf.FDwfAnalogInTriggerPositionSet(hdwf, c_double(0.5/hzSignal*(cPeriods+cDelay))) #  T0 at first sample
dwf.FDwfAnalogInTriggerSourceSet(hdwf, trigsrcAnalogOut1)
dwf.FDwfAnalogInConfigure(hdwf, c_int(1), c_int(1))

print("Configure Wavegen")
dwf.FDwfAnalogOutNodeEnableSet(hdwf, c_int(0), AnalogOutNodeCarrier, c_int(1))
dwf.FDwfAnalogOutNodeEnableSet(hdwf, c_int(1), AnalogOutNodeCarrier, c_int(1))
dwf.FDwfAnalogOutNodeFunctionSet(hdwf, c_int(-1), AnalogOutNodeCarrier, funcSine)
dwf.FDwfAnalogOutNodeAmplitudeSet(hdwf, c_int(-1), AnalogOutNodeCarrier, c_double(1.0))
dwf.FDwfAnalogOutNodeFrequencySet(hdwf, c_int(-1), AnalogOutNodeCarrier, c_double(hzSignal))
dwf.FDwfAnalogOutTriggerSourceSet(hdwf, c_int(-1), trigsrcPC)
dwf.FDwfAnalogOutWaitSet(hdwf, c_int(0), c_double(0.000))
dwf.FDwfAnalogOutWaitSet(hdwf, c_int(1), c_double(cDelay/hzSignal)) # W2 one period delay
dwf.FDwfAnalogOutRunSet(hdwf, c_int(-1), c_double(cPeriods/hzSignal)) # 5 periods
dwf.FDwfAnalogOutRepeatSet(hdwf, c_int(-1), c_int(1)) # once
dwf.FDwfAnalogOutConfigure(hdwf, c_int(0), c_int(1))
dwf.FDwfAnalogOutConfigure(hdwf, c_int(1), c_int(1))

time.sleep(0.1) # wait for offset to stabilize after first open or offset adjustment
dwf.FDwfDeviceTriggerPC(hdwf)

while True:
    sts = c_byte()
    if dwf.FDwfAnalogInStatus(hdwf, c_int(1), byref(sts)) == 0:
        szError = create_string_buffer(512)
        dwf.FDwfGetLastErrorMsg(szError)
        print(szError.value)
        quit()

    if sts.value == DwfStateDone.value :
        break
    time.sleep(0.001)

rgdSamples1 = (c_double*cSamples)()
rgdSamples2 = (c_double*cSamples)()
dwf.FDwfAnalogInStatusData(hdwf, 0, rgdSamples1, c_int(cSamples)) # get channel 1 data
dwf.FDwfAnalogInStatusData(hdwf, 1, rgdSamples2, c_int(cSamples)) # get channel 2 data

dwf.FDwfDeviceClose(hdwf)

plt.plot(numpy.fromiter(rgdSamples1, dtype = numpy.float), label="C1")
plt.plot(numpy.fromiter(rgdSamples2, dtype = numpy.float), label="C2")
plt.show()
