from WF_SDK import device, scope, wavegen   # import instruments
 
import matplotlib.pyplot as plt   # needed for plotting

import csv #needed for generating CSV files for graphing later
 
"""-----------------------------------------------------------------------"""
 
#resistance = float(input("Enter the resistance in Ohms of the resistor in series with the mosfet: "))
resistance = 100
gate_voltages = [0, 1, 2, 3, 4, 5] #gate voltages to sweep across
# name of csv files
filename_currents = "chip_currents.csv"
filename_voltages = "chip_voltages.csv"
# connect to the device
device_data = device.open() #TODO open again to get second device
 
"""-----------------------------------"""

# writing to csv file  
for filename in [filename_currents, filename_voltages]:
    with open(f'csvfiles/{filename}', 'w') as csvfile: # opens csv files
        csvwriter = csv.writer(csvfile)  # creating a csv writer object 
        csvwriter.writerow(gate_voltages) # writes header row (gate voltages)
 
# initialize the scope with default settings
scope.open(device_data, sampling_frequency=10e5)

# generate a 10KHz sine signal with 2V amplitude on channel 1
current_dict = {}
volt_dict = {}
for VG in gate_voltages:
    wavegen.generate(device_data, channel=2, function=wavegen.function.dc, offset=VG, frequency=10e2, amplitude=1) #generate dc signal to gate voltage at voltage i
    wavegen.generate(device_data, channel=1, function=wavegen.function.sine, offset=2.5, frequency=10e2, amplitude=2.5) #generation sine waveform to drain
    [mosfet_voltages, resistor_voltages] = scope.record2(device_data) # get data with AD3 oscilloscope
    mosfet_currents = []
    for v in resistor_voltages:
        mosfet_currents.append(v/resistance) # calculate current with ohms law
    for filename in [filename_currents, filename_voltages]: #outputs currents and voltages to csv
        with open(filename,'a') as csvfile:
            writer = csv.writer(csvfile)
            if "current" in filename:
                writer.writerow(mosfet_currents)
            elif "voltage" in filename:
                writer.writerow(mosfet_voltages)
    plt.plot(mosfet_voltages, mosfet_currents) #plot curve of mosfet voltages vs. mosfet currrents    

#plot labels and show
plt.xlabel("Voltage (V_DS) [V]")
plt.ylabel("Current (I_D) [A]")
plt.show()

# reset the scope
scope.close(device_data)
 
# reset the wavegen
wavegen.close(device_data)
 
# close the connection
device.close(device_data)