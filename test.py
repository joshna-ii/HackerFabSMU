import ctypes                     # import the C compatible data types
from sys import platform, path    # this is needed to check the OS type and get the PATH
from os import sep                # OS specific file path separators
import dwfconstants as constants
 
# load the dynamic library, get constants path (the path is OS specific)
if platform.startswith("win"):
    # on Windows
    dwf = ctypes.cdll.dwf
    constants_path = "C:" + sep + "Program Files (x86)" + sep + "Digilent" + sep + "WaveFormsSDK" + sep + "samples" + sep + "py"
elif platform.startswith("darwin"):
    # on macOS
    lib_path = sep + "Library" + sep + "Frameworks" + sep + "dwf.framework" + sep + "dwf"
    dwf = ctypes.cdll.LoadLibrary(lib_path)
    constants_path = sep + "Applications" + sep + "WaveForms.app" + sep + "Contents" + sep + "Resources" + sep + "SDK" + sep + "samples" + sep + "py"
else:
    # on Linux
    dwf = ctypes.cdll.LoadLibrary("libdwf.so")
    constants_path = sep + "usr" + sep + "share" + sep + "digilent" + sep + "waveforms" + sep + "samples" + sep + "py"
 
# import constants
path.append(constants_path)

class data:
    """
        stores the device handle and the device name
    """
    handle = ctypes.c_int(0)
    name = ""
 
def open():
    """
        open the first available device
    """
    # this is the device handle - it will be used by all functions to "address" the connected device
    device_handle = ctypes.c_int()
    # connect to the first available device
    dwf.FDwfDeviceOpen(ctypes.c_int(-1), ctypes.byref(device_handle))
    data.handle = device_handle
    return data

def close(device_data):
    """
        close a specific device
    """
    dwf.FDwfDeviceClose(device_data.handle)
    return

from WF_SDK import device       # import instruments
 
"""-----------------------------------------------------------------------"""
 
# connect to the device
device_data = device.open()
 
"""-----------------------------------"""
 
# use instruments here
 
 
"""-----------------------------------"""
 
# close the connection
device.close(device_data)