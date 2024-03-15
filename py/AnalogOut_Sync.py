"""
   DWF Python Example
   Author:  Digilent, Inc.
   Revision:  2018-07-19

   Requires:                       
       Python 2.7, 3
"""

from ctypes import *
import time
from dwfconstants import *
import sys

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

# continue running after device close, prevent temperature drifts
dwf.FDwfParamSet(DwfParamOnClose, c_int(0)) # 0 = run, 1 = stop, 2 = shutdown

#open device
print("Opening first device...")
dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))

if hdwf.value == hdwfNone.value:
    print("failed to open device")
    quit()

# the device will only be configured when FDwf###Configure is called
dwf.FDwfDeviceAutoConfigureSet(hdwf, c_int(0)) 

# enable two channels
dwf.FDwfAnalogOutNodeEnableSet(hdwf, c_int(0), AnalogOutNodeCarrier, c_int(True))
dwf.FDwfAnalogOutNodeEnableSet(hdwf, c_int(1), AnalogOutNodeCarrier, c_int(True))
# for second channel set master the first channel
dwf.FDwfAnalogOutMasterSet(hdwf, c_int(1), c_int(0));
# slave channel is controlled by the master channel
# it is enough to set trigger, wait, run and repeat paramters for master channel

# configure enabled channels
dwf.FDwfAnalogOutNodeFunctionSet(hdwf, c_int(-1), AnalogOutNodeCarrier, funcSine)
dwf.FDwfAnalogOutNodeFrequencySet(hdwf, c_int(-1), AnalogOutNodeCarrier, c_double(1000.0))
dwf.FDwfAnalogOutNodeAmplitudeSet(hdwf, c_int(-1), AnalogOutNodeCarrier, c_double(1.0))

#set phase for second channel
dwf.FDwfAnalogOutNodePhaseSet(hdwf, c_int(1), AnalogOutNodeCarrier, c_double(180.0))

print("Generating sine wave")
# start signal generation, 
# the second, slave channel will start too
dwf.FDwfAnalogOutConfigure(hdwf, c_int(0), c_int(1))

dwf.FDwfAnalogOutReset(hdwf, c_int(-1))
dwf.FDwfDeviceClose(hdwf)
