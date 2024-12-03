"""
Simple example measurement of a LTI, and how to use
the Bode() class to extract information for the bode plots
"""

import numpy as np
from span.bode import Bode, plotBode
from span.daq import MyDAQ

# Create daq object
daq = MyDAQ()
daq.samplerate = 200_000
daq.name = "myDAQ"
print(daq)

# Generate array of white noise
timeArray, white = daq.generateWaveform("white", daq.samplerate, frequency=1)

# Write to channel AO0, read on channel AI0, AI1
signalOut, signalIn = daq.readwrite(white, ["AI0", "AI1"], "AO0")

# Create Bode() instance
bode = Bode(daq.samplerate, signalOut, signalIn)
freqs, welchIn, welchOut = bode.getWelchSpectrum()

plotBode(2 * np.pi * freqs, welchOut, np.zeros_like(welchOut))

# Measure over range of frequencies
# for i, freq in enumerate(freqs):
#     print(freq)
# 
#     # Create sinusoidal waveform
#     timeArray, signalWrite = daq.generateWaveform("sine", daq.samplerate, frequency=freq)
# 
#     # Write to channel AO0 and read on channel AI0
#     signalOut, signalIn = daq.readwrite(signalWrite, ["AI0", "AI1"], "AO0")
# 
#     # Create Bode() instance
#     bode = Bode(daq.samplerate, signalOut, signalIn)
# 
#     # Get power and phase of freq, with a bandwidth delta=1
#     power = bode.getPower(freq, 1)
#     phase = bode.getPhase(freq, 0)
# 
#     # Save power and phase of freq.
#     powers[i] = power
#     phases[i] = phase
# 
# # Plot the bode plots
# plotBode(2 * np.pi * freqs, np.sqrt(powers), phases)
