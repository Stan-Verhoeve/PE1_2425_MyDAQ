"""
===============================================================================
                        Functionality: basics
===============================================================================
"""
from matplotlib import pyplot as plt
from span.daq import MyDAQ

# Create MyDAQ instance
daq = MyDAQ() 
print(daq)

# Give DAQ a name and samplerate
daq.name = "myDAQ1"
daq.samplerate = 200_000  # Hz
print()
print(daq)


"""
===============================================================================
                        Functionality: waveforms
===============================================================================
"""
# Generate some waveforms
timeArray, sine = daq.generateWaveform("sine", daq.samplerate, frequency=5)
__, square = daq.generateWaveform("square", daq.samplerate, frequency=10, amplitude=0.5, phase=90)

"""
===============================================================================
                        Functionality: writing
===============================================================================
"""
# Write a single waveform on channel 1, then the other on channel 2 (succesively)
daq.write(sine, "AO0")
daq.write(square, "AO1")

# Write both waveform simultaneously on 2 channels
# Also swap channels for good measure
daq.write(np.asarray([square, sine]), "AO0", "AO1")

plt.figure()
plt.plot(timeArray, square, label = "Channel 1")
plt.plot(timeArray, sine, label = "Channel 2")
plt.xlabel("Time [s]")
plt.ylabel("Amplitude [V]")
plt.show()

"""
===============================================================================
                        Functionality: reading
===============================================================================
"""

# Read on channel 1 for 2 seconds, then on channel 2 for 1 second (succesively)
data1 = daq.read(2, "AI0")
data2 = daq.read(1, "AI1")
time1 = daq.getTimeArray(2, daq.samplerate)
time2 = daq.getTimeArray(1, daq.samplerate)

plt.figure()
plt.plot(time1, data1, label = "Channel 1")
plt.plot(time2, data2, label = "Channel 2")
plt.xlabel("Time [s]")
plt.ylabel("Amplitude [V]")
plt.show()

# Now read both channels simultaneously for 1 second
data = daq.read(1, "AI0", "AI1")
timeArray = daq.getTimeArray(1, daq.samplerate)

plt.figure()
plt.plot(timeArray, data[0])
plt.plot(timeArray, data[1])
plt.xlabel("Time [s]")
plt.ylabel("Amplitude [V]")
plt.show()

"""
===============================================================================
                        Functionality: reading + writing
===============================================================================
"""
# Write sine on channel 1 and simultaneously read channel 2
data1 = daq.readwrite(sine, "AI1", "AO0")
time1 = daq.getTimeArray(1, daq.samplerate)

# Write square on channel 2 and simultaneously read channel 1
data2 = daq.readwrite(square, "AI0", "AO1")
time2 = daq.getTImeArray(1, daq.samplerate)

plt.figure()
plt.plot(time1, data1, label = "Channel 2")
plt.plot(time2, data2, label = "Channel 1")
plt.xlabel("Time [s]")
plt.ylabel("Amplitude [V]")
plt.show()

# Write on channels 1 and 2, and read on channels 1 and 2
data = daq.readwrite(np.asarray([sine, square]), ["AI0", "AI1"], ["AO0", "AO1"])
timeArray = daq.getTimeArray(1, daq.samplerate)

plt.figure()
plt.plot(timeArray, data[0])
plt.plot(timeArray, data[1])
plt.xlabel("Time [s]")
plt.ylabel("Amplitude [V]")
plt.show()
