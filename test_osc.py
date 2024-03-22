from WF_SDK import device, scope, wavegen   # import instruments
 
import matplotlib.pyplot as plt   # needed for plotting
 
"""-----------------------------------------------------------------------"""
 
#resistance = float(input("Enter the resistance in Ohms of the resistor in series with the mosfet: ")) TODO user inputs
resistance = 5
# connect to the device
device_data = device.open() #TODO open again to get second device
 
"""-----------------------------------"""
 
# initialize the scope with default settings
scope.open(device_data, sampling_frequency=10e5)

# generate a 10KHz sine signal with 2V amplitude on channel 1
for i in range(0.8, 5, 0.2):
    wavegen.generate(device_data, channel=2, function=wavegen.function.dc, offset=i, frequency=10e2, amplitude=1) #generate dc signal to gate voltage at voltage i
    for j in range(0, 5, 0.1):
        wavegen.generate(device_data, channel=1, function=wavegen.function.dc, offset=j, frequency=10e2, amplitude=2.5)
        [resistor_voltages, mosfet_voltages] = scope.record2(device_data) #functions outputs [resistor_voltages, mosfet_voltages]
        mosfet_currents = []
        for v in resistor_voltages:
            mosfet_currents.append(v/resistance)
        plt.plot(mosfet_voltages, mosfet_currents)

n = len(mosfet_voltages)

time = []
for t in range(0,n):
    time.append(0.4*t/n)      

#plt.plot(time, mosfet_voltages)
#plt.plot(time, mosfet_voltages5)
#plt.plot(time, resistor_voltages)
#plt.plot(time, mosfet_currents)
#plt.plot(resistor_voltages, mosfet_currents)
#plt.plot(resistor_voltages5, mosfet_currents5)
#plt.plot(mosfet_voltages, mosfet_currents)
#plt.plot(mosfet_voltages5, mosfet_currents5)
plt.xlabel("Voltage (V_DS) [V]")
plt.ylabel("Current (I_D) [A]")
plt.show()


# reset the scope
scope.close(device_data)
 
# reset the wavegen
wavegen.close(device_data)
 
# close the connection
device.close(device_data)