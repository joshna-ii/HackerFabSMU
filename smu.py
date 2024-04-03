from WF_SDK import device, scope, wavegen   # import instruments
 
import matplotlib.pyplot as plt   # needed for plotting

import csv #needed for generating CSV files for graphing later
import ctypes
from sys import platform, path    # this is needed to check the OS type and get the PATH
from os import sep                # OS specific file path separators
 
"""-----------------------------------------------------------------------"""
# assign dwf to be used later
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
 
drain_resistance = 100#float(input("Enter the resistance in Ohms of the resistor in series with the mosfet DRAIN: "))
gate_resistance = 100#float(input("Enter the resistance in Ohms of the resistor in series with the mosfet GATE: "))
chip_number = input("Enter your chip number (ex. 305): ")
device_id = input("Enter the device being tested (ex. 2b1): ")
gate_voltages = input("Enter the gate voltages to test as a comma-separated list (Ex. 1, 1.5, 1.6, 3): ").replace(" ", "").split(",")
# name of csv files
filename_currents = f"csvfiles/{chip_number}_{device_id}_currents.csv"
filename_voltages = f"csvfiles/{chip_number}_{device_id}_voltages.csv"
# connect to the device
ad3_data1 = device.open() #TODO open again to get second device
 
"""-----------------------------------"""

# writing to csv file  
for filename in [filename_currents, filename_voltages]:
    with open(filename, 'w') as csvfile: # opens csv files
        csvwriter = csv.writer(csvfile)  # creating a csv writer object 
        csvwriter.writerow(gate_voltages) # writes header row (gate voltages)
 
# initialize the scope with default settings
scope.open(ad3_data1, sampling_frequency=10e5)

wavegen.generate(ad3_data1, channel=1, function=wavegen.function.sine, offset=5, frequency=10e2, amplitude=5) #generation sine waveform to drain

#set voltage peak to peak input range to 50 V on both channels
dwf.FDwfAnalogInChannelRangeSet(ad3_data1.handle, 0, ctypes.c_double(50.0))
dwf.FDwfAnalogInChannelRangeSet(ad3_data1.handle, 1, ctypes.c_double(50.0))

# generate a 10KHz sine signal with 2V amplitude on channel 1
current_dict = {}
volt_dict = {}
for VG in gate_voltages:
    VG = float(VG)
    wavegen.generate(ad3_data1, channel=2, function=wavegen.function.dc, offset=VG, frequency=10e2, amplitude=1) #generate dc signal to gate voltage at voltage i
    [resistor_voltages, mosfet_voltages] = scope.record2(ad3_data1) # get data with AD3 oscilloscope
    mosfet_currents = []
    for v in resistor_voltages:
        mosfet_currents.append(v/drain_resistance) # calculate current with ohms law
    for filename in [filename_currents, filename_voltages]: #outputs currents and voltages to csv
        with open(filename,'a') as csvfile:
            writer = csv.writer(csvfile)
            if "current" in filename:
                writer.writerow(mosfet_currents)
            elif "voltage" in filename:
                writer.writerow(mosfet_voltages)
    plt.plot(mosfet_voltages, mosfet_currents, label = f"Vg = {VG}") #plot curve of mosfet voltages vs. mosfet currrents    

#plot labels and show
leg = plt.legend(loc='upper center')
plt.xlabel("Voltage (V_DS) [V]")
plt.ylabel("Current (I_D) [A]")
plt.show()

# reset the scope
scope.close(ad3_data1)
 
# reset the wavegen
wavegen.close(ad3_data1)
 
# close the connection
device.close(ad3_data1)