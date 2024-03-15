from WF_SDK import device, scope, wavegen   # import instruments
 
import matplotlib.pyplot as plt   # needed for plotting
 
"""-----------------------------------------------------------------------"""
 
#resistance = float(input("Enter the resistance in Ohms of the resistor in series with the mosfet: "))
resistance = 5100
# connect to the device
device_data = device.open()
 
"""-----------------------------------"""
 
# initialize the scope with default settings
scope.open(device_data, sampling_frequency=10e5)

# generate a 10KHz sine signal with 2V amplitude on channel 1
wavegen.generate(device_data, channel=1, function=wavegen.function.sine, offset=1, frequency=10e2, amplitude=2)
'''
mosfet_voltages = scope.record(device_data, channel=1)
wavegen.close(device_data)

wavegen.generate(device_data, channel=1, function=wavegen.function.sine, offset=1, frequency=10e2, amplitude=2)
resistor_voltages = scope.record(device_data, channel=2)
wavegen.close(device_data)
'''
[mosfet_voltages, resistor_voltages] = scope.record2(device_data)
wavegen.close(device_data)

mosfet_currents = []
for v in resistor_voltages:
    mosfet_currents.append(v/resistance)

added_voltages = []
for i in range(len(resistor_voltages)):
    added_voltages.append(mosfet_voltages[i] + resistor_voltages[i])
print("mosfet voltages")
print(mosfet_voltages)
print("resistor voltages")
print(resistor_voltages)
print("added voltages")
print(added_voltages)
print("mosfet currents")
print(mosfet_currents)

n = len(mosfet_voltages)

time = []
for t in range(0,n):
    time.append(0.4*t/n)      

#plt.plot(time, mosfet_voltages)
#plt.plot(time, resistor_voltages)
#plt.plot(time, mosfet_currents)
plt.plot(mosfet_voltages, mosfet_currents)
#plt.plot(resistor_voltages, mosfet_currents)
#plt.xlabel("Voltage [V]")
#plt.ylabel("Current [A]")
plt.show()
print("here")


'''
# plot
time = [moment * 1e03 for moment in time]   # convert time to ms
plt.plot(time, buffer)
plt.xlabel("time [ms]")
plt.ylabel("voltage [V]")
plt.show()
'''
# reset the scope
scope.close(device_data)
 
# reset the wavegen
#wavegen.close(device_data)
 
"""-----------------------------------"""
 
# close the connection
device.close(device_data)