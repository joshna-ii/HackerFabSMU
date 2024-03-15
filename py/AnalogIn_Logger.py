"""
   DWF Python Example
   Author:  Digilent, Inc.
   Revision:  2018-07-19

   Requires:                       
       Python 2.7, 3
   Description:
   Generates AM modulated signal on AWG1 channel
   Scope performs scan shift acquisition and logs DC and AC/DC-RMS values
"""

from ctypes import *
import math
import time
import matplotlib.pyplot as plt
import sys

if sys.platform.startswith("win"):
    dwf = cdll.dwf
elif sys.platform.startswith("darwin"):
    dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
else:
    dwf = cdll.LoadLibrary("libdwf.so")

hdwf = c_int()
sts = c_byte()
secLog = 1.0 # logging rate in seconds
nSamples = 8000
rgdSamples = (c_double*nSamples)()
cValid = c_int(0)

version = create_string_buffer(16)
dwf.FDwfGetVersion(version)
print("DWF Version: "+str(version.value))

print("Opening first device")
dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))

if hdwf.value == 0:
    szerr = create_string_buffer(512)
    dwf.FDwfGetLastErrorMsg(szerr)
    print(str(szerr.value))
    print("failed to open device")
    quit()

dwf.FDwfDeviceAutoConfigureSet(hdwf, c_int(0)) # 0 = the device will only be configured when FDwf###Configure is called

print("Generating AM sine wave...")
dwf.FDwfAnalogOutNodeEnableSet(hdwf, c_int(0), c_int(0), c_int(1)) # carrier
dwf.FDwfAnalogOutNodeFunctionSet(hdwf, c_int(0), c_int(0), c_int(1)) # sine
dwf.FDwfAnalogOutNodeFrequencySet(hdwf, c_int(0), c_int(0), c_double(50))
dwf.FDwfAnalogOutNodeAmplitudeSet(hdwf, c_int(0), c_int(0), c_double(1))
dwf.FDwfAnalogOutNodeOffsetSet(hdwf, c_int(0), c_int(0), c_double(0.5))
dwf.FDwfAnalogOutNodeEnableSet(hdwf, c_int(0), c_int(2), c_int(1)) # AM
dwf.FDwfAnalogOutNodeFunctionSet(hdwf, c_int(0), c_int(2), c_int(3)) # triangle
dwf.FDwfAnalogOutNodeFrequencySet(hdwf, c_int(0), c_int(2), c_double(0.1))
dwf.FDwfAnalogOutNodeAmplitudeSet(hdwf, c_int(0), c_int(2), c_double(50))
dwf.FDwfAnalogOutConfigure(hdwf, c_int(0), c_int(1))

#set up acquisition
dwf.FDwfAnalogInChannelEnableSet(hdwf, c_int(0), c_int(1))
dwf.FDwfAnalogInChannelRangeSet(hdwf, c_int(0), c_double(5))
dwf.FDwfAnalogInAcquisitionModeSet(hdwf, c_int(1)) #acqmodeScanShift
dwf.FDwfAnalogInFrequencySet(hdwf, c_double(nSamples/secLog))
dwf.FDwfAnalogInBufferSizeSet(hdwf, c_int(nSamples))
dwf.FDwfAnalogInConfigure(hdwf, c_int(1), c_int(0))

#wait at least 2 seconds for the offset to stabilize
time.sleep(1)

#begin acquisition
dwf.FDwfAnalogInConfigure(hdwf, c_int(0), c_int(1))

print("Press Ctrl+C to stop")
try:
    while True:
        time.sleep(secLog)
        dwf.FDwfAnalogInStatus(hdwf, c_int(1), byref(sts))
        dwf.FDwfAnalogInStatusSamplesValid(hdwf, byref(cValid))
        for iChannel in range(2):
            dwf.FDwfAnalogInStatusData(hdwf, c_int(iChannel), byref(rgdSamples), cValid) # get channel 1 data
            dc = 0
            for i in range(nSamples):
                dc += rgdSamples[i]
            dc /= nSamples
            dcrms = 0
            acrms = 0
            for i in range(nSamples):
                dcrms += rgdSamples[i] ** 2
                acrms += (rgdSamples[i]-dc) ** 2
            dcrms /= nSamples
            dcrms = math.sqrt(dcrms)
            acrms /= nSamples
            acrms = math.sqrt(acrms)
            print(f"CH:{iChannel+1} DC:{dc:.3f}V DCRMS:{dcrms:.3f}V ACRMS:{acrms:.3f}V")
except KeyboardInterrupt:
    pass

dwf.FDwfAnalogOutConfigure(hdwf, c_int(0), c_int(0))
dwf.FDwfDeviceCloseAll()

