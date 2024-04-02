from WF_SDK import device, scope, wavegen   # import instruments
 
import matplotlib.pyplot as plt   # needed for plotting

import csv #needed for generating CSV files for graphing later
 
"""-----------------------------------------------------------------------"""
 
drain_resistance = float(input("Enter the resistance in Ohms of the resistor in series with the mosfet DRAIN: "))
gate_resistance = float(input("Enter the resistance in Ohms of the resistor in series with the mosfet GATE: "))
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
    plt.plot(mosfet_voltages, mosfet_currents) #plot curve of mosfet voltages vs. mosfet currrents    

#plot labels and show
plt.xlabel("Voltage (V_DS) [V]")
plt.ylabel("Current (I_D) [A]")
plt.show()

# reset the scope
scope.close(ad3_data1)
 
# reset the wavegen
wavegen.close(ad3_data1)
 
# close the connection
device.close(ad3_data1)