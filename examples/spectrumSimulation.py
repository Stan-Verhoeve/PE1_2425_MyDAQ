"""
Simple example simulation of a LTI (lowpass filter), and how to use
the Bode() class to extract information for the bode plots
"""

import numpy as np
from span.bode import Bode, plotBode
from scipy.signal import lsim, TransferFunction
from span.daq import MyDAQ
from tqdm import tqdm

# Create daq object
daq = MyDAQ()
daq.samplerate = 200_000
daq.name = "myDAQ1"
print(daq)

# Samplerate and time of simulation
rate = 200_000
T = 2

# Create lowpass filter transfer function
wres = 1000
Transfer = TransferFunction([0, wres], [1, wres])
Hfunc = lambda w: wres / (wres + 1j * w)


# =============================================================================
# = There are two methods to measure the transfer function using SPAN         =
# = The first method is quick but less accurate, and uses a white noise       =
# = spectrum to immediately determine the transfer function                   =
# =============================================================================

# Generate array of white noise
timeArray, white = MyDAQ.generateWaveform("white", rate, 1, duration=T)

# Write to channel AO0, read on channel AI0, AI1
signalOut = lsim(Transfer, white, timeArray)[1]

# Create Bode() instance and extract transfer function
bode = Bode(daq.samplerate, signalOut, white)
freqs, H = bode.getTransfer(nperseg=int(white.size / 10))


# Analytic solution of transfer function
analytic = Hfunc(2 * np.pi * freqs)

# Plot transfer function
plotBode(2*np.pi*freqs, np.abs(H), np.angle(H), analytic=analytic,
         xlim=(10, 1e5), mag_ylim=(-60, 10))


# =============================================================================
# = There are two methods to measure the transfer function using SPAN         =
# = The second method is slow but more accurate, and uses a sweep over        =
# = different frequencies to determine the transfer function at each          =
# = frequency individually                                                    =
# =============================================================================


# Run simulation in the domain [1Hz, 100kHz)
freqs = np.logspace(1, 4, 50)

# Keep track of (simulated) power and phase
powers = np.zeros_like(freqs)
phases = np.zeros_like(freqs)

# Run simulation over range of frequencies
for i, freq in enumerate(tqdm(freqs)):
    # Input is simple sine, simulate output
    timeArray, signalIn = MyDAQ.generateWaveform("sine", rate, freq, duration=T)
    signalOut = lsim(Transfer, signalIn, timeArray)[1]

    # Create Bode() instance
    bode = Bode(rate, signalOut, signalIn)

    # Get power and phase of freq, with a bandwidth delta=1
    power = bode.getPower(freq, 1)
    phase = bode.getPhase(freq, 0)

    # Save power and phase of freq.
    powers[i] = power
    phases[i] = phase
    
    
# Analytic solution of transfer function
analytic = Hfunc(2 * np.pi * freqs)

# Plot the bode plots
plotBode(2 * np.pi * freqs, np.sqrt(powers), phases, analytic=analytic)


# =============================================================================
# = There are two methods to measure the transfer function using SPAN         =
# = The second method is slow but more accurate, and uses a sweep over        =
# = different frequencies to determine the transfer function at each          =
# = frequency individually                                                    =
# = Here, we are using the `getTranfer` function of SPAN.bode, which          =
# = returns the Welch power spectrum. We thus have to extract only at         =
# = those points closest to the frequency of interest.                        =
# = This and the previous method are equivalent.                              =
# =============================================================================


# Run simulation in the domain [1Hz, 100kHz)
freqs = np.logspace(1, 4, 50)

# Keep track of (simulated) magnitude and phase
mags = np.zeros_like(freqs)
phases = np.zeros_like(freqs)

# Run simulation over range of frequencies
for i, freq in enumerate(tqdm(freqs)):
    # Input is simple sine, simulate output
    timeArray, signalIn = MyDAQ.generateWaveform("sine", rate, freq, duration=T)
    signalOut = lsim(Transfer, signalIn, timeArray)[1]

    # Create Bode() instance
    bode = Bode(rate, signalOut, signalIn)

    # Get power and phase of freq, with a bandwidth delta=1
    Hfreqs, H = bode.getTransfer(nperseg = int(signalIn.size) / 10)
    index = np.argmin(abs(Hfreqs - freq))
    
    # plotBode(2 * np.pi * freqs, np.abs(H), np.angle(H))
    
    mag = abs(H)[index]
    phase = np.angle(H)[index]
    # Save power and phase of freq.
    mags[i] = mag
    phases[i] = phase
    
    
# Analytic solution of transfer function
analytic = Hfunc(2 * np.pi * freqs)

# Plot the bode plots
plotBode(2 * np.pi * freqs, mags, phases, analytic=analytic)
