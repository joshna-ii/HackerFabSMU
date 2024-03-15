from WF_SDK import device       # import instruments
 
"""-----------------------------------------------------------------------"""
 
# connect to the device
device_data = device.open()
print(device_data)
 
"""-----------------------------------"""
 
# use instruments here
 
 
"""-----------------------------------"""
 
# close the connection
device.close(device_data)