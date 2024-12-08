"""
Simple example measurement of a LTI, and how to use
the Bode() class to extract information for the bode plots
"""

import numpy as np
from span.bode import Bode, plotBode
from span.daq import MyDAQ
from tqdm import tqdm

# Create daq object
daq = MyDAQ()
daq.samplerate = 200_000
daq.name = "myDAQ1"
print(daq)

# =============================================================================
# = There are two methods to measure the transfer function using SPAN         =
# = The first method is quick but less accurate, and uses a white noise       =
# = spectrum to immediately determine the transfer function                   =
# =============================================================================

# Duration of measurement
T = 2
# Generate array of white noise
timeArray, white = daq.generateWaveform("white", daq.samplerate, frequency=1, duration=T)

# Write to channel AO0, read on channel AI0, AI1
signalOut, signalIn = daq.readwrite(white, ["AI0", "AI1"], "AO0")

# Create Bode() instance and extract transfer function
bode = Bode(daq.samplerate, signalOut, signalIn)
freqs, H = bode.getTransfer(nperseg=int(white.size / 10))

# Plot transfer function
plotBode(2*np.pi*freqs, np.abs(H), np.angle(H), 
         xlim=(1, 1e5))


# =============================================================================
# = There are two methods to measure the transfer function using SPAN         =
# = The second method is slow but more accurate, and uses a sweep over        =
# = different frequencies to determine the transfer function at each          =
# = frequency individually                                                    =
# =============================================================================

# Measure over range of frequencies
freqs = np.logspace(1, 4, 50)
powers = np.zeros_like(freqs)
phases = np.zeros_like(freqs)

for i, freq in enumerate(tqdm(freqs)):
    # Create sinusoidal waveform
    timeArray, signalWrite = daq.generateWaveform("sine", daq.samplerate, frequency=freq)

    # Write to channel AO0 and read on channel AI0
    signalOut, signalIn = daq.readwrite(signalWrite, ["AI0", "AI1"], "AO0")

    # Create Bode() instance
    bode = Bode(daq.samplerate, signalOut, signalIn)

    # Get power and phase of freq, with a bandwidth delta=1
    power = bode.getPower(freq, 1)
    phase = bode.getPhase(freq, 0)

    # Save power and phase of freq.
    powers[i] = power
    phases[i] = phase

# Plot the bode plots
plotBode(2 * np.pi * freqs, np.sqrt(powers), phases)
