"""
Simple example simulation of a LTI (lowpass filter), and how to use
the Bode() class to extract information for the bode plots
"""
import numpy as np
from span.bode import Bode, plotBode
from scipy.signal import lsim, TransferFunction

# Samplerate and time of simulation
rate = 200_000
samples = 600_000
timeArray = np.linspace(0, samples/rate, samples)

# Create lowpass filter transfer function
wres = 1000
H = TransferFunction([0, wres],[1, wres])
Hfunc = lambda w: wres / (wres + 1j * w)

# Run simulation in the domain [1Hz, 100kHz)
freqs = np.logspace(0, 5, 50)

# Keep track of (simulated) power and phase
powers = np.zeroslike(freqs)
phases = np.zeroslike(freqs)

# Run simulation over range of frequencies
for i, freq in enumerate(freqs):
    print(freq)
    # Input is simple sine, simulate output
    signalIn = np.sin(2*np.pi*freq*timeArray)
    signalOut = lsim(H, signalIn, timeArray)[1]
    
    # Create Bode() instance
    bode = Bode(rate, signalOut, signalIn)
    
    # Get power and phase of freq, with a bandwidth delta=1
    power = bode.getPower(freq, 1)
    phase = bode.getPhase(freq, 1)
    
    # Save power and phase of freq.
    powers[i] = power
    phases[i] = phases

# Analytic solution of transfer function
analytic = Hfunc(2*np.pi*freqs)

# Plot the bode plots
plotBode(2*np.pi*freqs, np.sqrt(powers), phases, analytic=analytic)
