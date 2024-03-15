"""
   DWF Python Example
   Author:  Digilent, Inc.
   Revision:  2019-02-12

   Requires:                       
       Python 2.7, 3
"""

from ctypes import *
import math
import sys
import time

if sys.platform.startswith("win"):
    dwf = cdll.LoadLibrary("dwf.dll")
elif sys.platform.startswith("darwin"):
    dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
else:
    dwf = cdll.LoadLibrary("libdwf.so")


# continue running after device close
dwf.FDwfParamSet(c_int(4), c_int(0)) # 4 = DwfParamOnClose, 0 = run 1 = stop 2 = shutdown

hdwf = c_int()

print("Opening first device")
dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))
# device configuration of index 3 (4th) for Analog Discovery has 16kS digital-in/out buffer
#dwf.FDwfDeviceConfigOpen(c_int(-1), c_int(3), byref(hdwf)) 

if hdwf.value == 0:
    print("failed to open device")
    szerr = create_string_buffer(512)
    dwf.FDwfGetLastErrorMsg(szerr)
    print(str(szerr.value))
    quit()

# for Digital Discovery:
# set digital voltage between 1.2 and 3.3V
#dwf.FDwfAnalogIOChannelNodeSet(hdwf, c_int(0), c_int(0), c_double(3.3))
# enable VIO output
#dwf.FDwfAnalogIOEnableSet(hdwf, c_int(1))
# pull enable for DIO 39 to 24, bit 15 to 0
#dwf.FDwfAnalogIOChannelNodeSet(hdwf, c_int(0), c_int(2), c_double(0xFFFF)) 
# pull up/down for all DIOs
#dwf.FDwfAnalogIOChannelNodeSet(hdwf, c_int(0), c_int(3), c_double(0xFFFF)) 


print("Configuring I2C...")

iNak = c_int()

dwf.FDwfDigitalI2cReset()
dwf.FDwfDigitalI2cStretchSet(hdwf, c_int(1)) # clock stretching
dwf.FDwfDigitalI2cRateSet(hdwf, c_double(1e5)) # 100kHz
dwf.FDwfDigitalI2cSclSet(hdwf, c_int(0)) # SCL = DIO-0
dwf.FDwfDigitalI2cSdaSet(hdwf, c_int(1)) # SDA = DIO-1
dwf.FDwfDigitalI2cClear(hdwf, byref(iNak))
if iNak.value == 0:
    print("I2C bus error. Check the pull-ups.")
    quit()


adr = 0x69;

dwf.FDwfDigitalI2cWrite(hdwf, c_int(adr<<1), 0, c_int(0), byref(iNak)) # write 0 bytes
if iNak.value != 0:
    print("Device test NAK "+str(iNak.value))
    quit()

rgID = (c_ubyte*1)(0x0F)
dwf.FDwfDigitalI2cWriteRead(hdwf, c_int(adr<<1), rgID, c_int(1), rgID, c_int(1), byref(iNak)) # write 1 byte, restart, read 1 byte
if iNak.value != 0:
    print("Device power NAK "+str(iNak.value))
    quit()
    
if rgID[0] != 0xD3:
    print("Device ID mismatch "+str(rgID[0]))
    quit()

rgReg1 = (c_ubyte*2)(0x20, 0x0F)
dwf.FDwfDigitalI2cWrite(hdwf, c_int(adr<<1), rgReg1, c_int(2), byref(iNak)) # write 2 bytes
if iNak.value != 0:
    print("Device reg1 NAK "+str(iNak.value))
    quit()

for i in range(10):
    time.sleep(0.5);

    rgData = (c_ubyte*1)(0xA8)
    rgAcc = (c_int16*3)()
    dwf.FDwfDigitalI2cWriteRead(hdwf, c_int(adr<<1), rgData, c_int(1), rgAcc, c_int(6), byref(iNak)) # write 1 byte, restart, read 6 bytes
    if iNak.value != 0:
        print("Device Data NAK "+str(iNak.value))
        #quit()

    # convert data bits to signed value relative to gravitational constant
    x = 0.004*rgAcc[0]
    y = 0.004*rgAcc[1] 
    z = 0.004*rgAcc[2]
    a = math.sqrt(math.pow(x,2)+math.pow(y,2)+math.pow(z,2))
    print(f"A: {a:.3f} \tX: {x:.3f} \tY: {y:.3f} \tZ: {z:.3f}")


dwf.FDwfDeviceCloseAll()
