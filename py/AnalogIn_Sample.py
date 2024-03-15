"""
   DWF Python Example
   Author:  Digilent, Inc.
   Revision:  2018-07-19

   Requires:                       
       Python 2.7, 3
"""

from ctypes import *
from dwfconstants import *
import time
import sys

if sys.platform.startswith("win"):
    dwf = cdll.dwf
elif sys.platform.startswith("darwin"):
    dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
else:
    dwf = cdll.LoadLibrary("libdwf.so")

#declare ctype variables
hdwf = c_int()
voltage1 = c_double()
voltage2 = c_double()

#print(DWF version
version = create_string_buffer(16)
dwf.FDwfGetVersion(version)
print("DWF Version: "+str(version.value))

#open device
"Opening first device..."
dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))

if hdwf.value == hdwfNone.value:
    szerr = create_string_buffer(512)
    dwf.FDwfGetLastErrorMsg(szerr)
    print(szerr.value)
    print("failed to open device")
    quit()

dwf.FDwfDeviceAutoConfigureSet(hdwf, c_int(0)) # 0 = the device will only be configured when FDwf###Configure is called

print("Preparing to read sample...")
dwf.FDwfAnalogInChannelEnableSet(hdwf, c_int(0), c_int(1)) 
dwf.FDwfAnalogInChannelOffsetSet(hdwf, c_int(0), c_double(0)) 
dwf.FDwfAnalogInChannelRangeSet(hdwf, c_int(0), c_double(5)) 
dwf.FDwfAnalogInConfigure(hdwf, c_int(0), c_int(0))

time.sleep(2)

for i in range(5):
    time.sleep(1)
    dwf.FDwfAnalogInStatus(hdwf, c_int(False), None) # fetch status and samples from device
    dwf.FDwfAnalogInStatusSample(hdwf, c_int(0), byref(voltage1))
    dwf.FDwfAnalogInStatusSample(hdwf, c_int(1), byref(voltage2))
    print("Channel 1:  " + str(voltage1.value)+" V")
    print("Channel 2:  " + str(voltage2.value)+" V")

dwf.FDwfDeviceCloseAll()
