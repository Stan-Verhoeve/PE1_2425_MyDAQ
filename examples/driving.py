"""
===============================================================================
                        Functionality: basics
===============================================================================
"""

from matplotlib import pyplot as plt
from span.daq import MyDAQ
from numpy import random, arange

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
__, square = daq.generateWaveform(
    "square", daq.samplerate, frequency=10, amplitude=0.5, phase=90
)

"""
===============================================================================
                        Functionality: writing
===============================================================================
"""
# Plot the waveforms
plt.figure()
plt.plot(timeArray, sine, label="Channel 1")
plt.plot(timeArray, square, label="Channel 2")
plt.title("Arrays written to MyDAQ")
plt.xlabel("Time [s]")
plt.ylabel("Amplitude [V]")
plt.legend()
plt.show()

# Write a single waveform on channel 1, then the other on channel 2 (succesively)
daq.write(sine, "AO0")
daq.write(square, "AO1")

# Write both waveforms simultaneously on 2 channels
daq.write(np.asarray([sine, square]), "AO0", "AO1")

# In principle, timeArray was formed because when we made the waveforms, we
# provided a duration. However, in the situation where you create a signal
# that is to be written, without knowing its duration, we can still get a
# timeArray

# Create array of random duration
randomDuration = random.uniform(1, 5)
randomSamples = arange(0, randomDuration, 1 / daq.samplerate)

# Reconstruct duration using class functionality
reconstructedDuration = daq.convertSamplesToDuration(daq.samplerate, randomSamples.size)
timeArray = daq.getTimeArray(reconstructedDuration, daq.samplerate)

# Check results to 4 digits
print(f"Random duration        : {randomDuration:.4f}")
print(f"Reconstructed duration : {reconstructedDuration:.4f}")

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
plt.plot(time1, data1, label="Channel 1")
plt.plot(time2, data2, label="Channel 2")
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
plt.plot(time1, data1, label="Channel 2")
plt.plot(time2, data2, label="Channel 1")
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
