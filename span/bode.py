from dataclasses import dataclass
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.gridspec import GridSpec
from scipy.integrate import trapezoid
from scipy.signal import welch, csd


@dataclass
class Bode:
    """
    Data class to extract bode plot information from
    an output voltage. If no input voltage is provided,
    assumes input to be 1 (i.e. power and phase will be
    of the output only, NOT the ratio)
    """

    samplerate: int
    voltageOut: np.ndarray
    voltageIn: np.ndarray = None

    def __post_init__(self):
        self.timeArray = np.linspace(
            1 / self.samplerate,
            self.voltageOut.size / self.samplerate,
            self.voltageOut.size,
        )

    @staticmethod
    def integral(x: np.ndarray, y: np.ndarray) -> float | np.ndarray:
        return trapezoid(y, x)

    @staticmethod
    def FFT(voltage: np.ndarray) -> np.ndarray:
        return np.fft.fftshift(np.fft.fft(voltage))

    @staticmethod
    def freqs(voltage: np.ndarray, samplerate: int) -> np.ndarray:
        return np.fft.fftshift(np.fft.fftfreq(voltage.size, d=1 / samplerate))

    @staticmethod
    def restrictPiPi(angle):
        return np.mod(angle + np.pi, 2 * np.pi) - np.pi

    def getTransfer(self, nperseg: int = 1024) -> np.ndarray:
        """
        Calculate the transfer function using Welch's method.
        If `voltageIn` is white noise, this returns the full transfer function.
        If `voltageIn` is coloured noise (1/f^n), this returns the uncorrected
        full transfer function.
        If `voltageIn` is sinusoidal, the return is only physical for the input
        frequency, and post-processing care should be taken to extract from the
        return only the transfer function at this input frequency. This is
        equivalent to calling `getPower` and `getPhase`.
        """
        if self.voltageIn is not None:
            # Compute cross power spectral density (CSD) and power spectral density (PSD)
            freqs, Pxy = csd(
                self.voltageIn, self.voltageOut, fs=self.samplerate, nperseg=nperseg
            )
            _, Pxx = welch(self.voltageIn, fs=self.samplerate, nperseg=nperseg)
            H = Pxy / Pxx
        else:
            print("No input given; cannot calculate phase information.")
            print("Will return power spectral density of output instead.")
            freqs, H = welch(self.voltageOut, fs=self.samplerate, nperseg=nperseg)

        return freqs, H

    def getPower(self, f: float, delta: float) -> float:
        """
        Calculate the power (ratio) using Parserval theorem
        """

        # Get Fourier frequencies in the interval 2*delta around f
        freqs = Bode.freqs(self.voltageOut, self.samplerate)
        interval = (freqs > f - delta) & (freqs < f + delta)

        # Get Fourier transform of output, and calculate power
        FFTOUT = Bode.FFT(self.voltageOut)
        powerOut = Bode.integral(freqs[interval], np.abs(FFTOUT[interval]) ** 2)

        # Calculate power of input if provided, else set to 1.
        if self.voltageIn is not None:
            FFTIN = Bode.FFT(self.voltageIn)
            powerIn = Bode.integral(freqs[interval], np.abs(FFTIN[interval]) ** 2)
        else:
            powerIn = 1.0

        return powerOut / powerIn

    def getPhase(self, f: float, offset: float = 0) -> float:
        """
        Calculate the phase (ratio)
        """

        # Get the positive Fourier frequencies (discard 0)
        freqs = Bode.freqs(self.voltageOut, self.samplerate)

        positiveIndex = freqs > 0
        closestIndex = abs(freqs[positiveIndex] - f).argmin()

        # Get Fourier transform of output, and calculate phase
        FFTOUT = Bode.FFT(self.voltageOut)
        phaseOut = np.angle(FFTOUT[positiveIndex][closestIndex])

        # Calculate phase of input if provided, else set to 0.
        if self.voltageIn is not None:
            FFTIN = Bode.FFT(self.voltageIn)
            phaseIn = np.angle(FFTIN[positiveIndex][closestIndex])
        else:
            phaseIn = 0.0

        phase = phaseOut - phaseIn
        # We are not interested in angles outside (-pi, pi]
        return Bode.restrictPiPi(phase)


def plotBode(
    freqs: np.ndarray,
    mag: np.ndarray,
    phase: np.ndarray,
    save: str = None,
    analytic: np.ndarray = None,
    **kwargs,
) -> None:

    # Use GridSpec to nicely center subplots
    gs = GridSpec(2, 4)

    # Create figure and axes
    fig = plt.figure(figsize=(10, 7))
    magAx = fig.add_subplot(gs[0, :2])
    phaseAx = fig.add_subplot(gs[0, 2:])
    polarAx = fig.add_subplot(gs[1, 1:3], projection="polar")

    # If provided, convert magnitude error to decibels
    if not (kwargs.get("merr") is None):
        logErr = 20 / np.log(10) * kwargs.get("merr") / abs(mag)
    else:
        logErr = None

    # Plot data
    magAx.errorbar(
        freqs,
        20 * np.log10(abs(mag)),
        yerr=logErr,
        markersize=4,
        fmt=".",
        c="k",
        label="Measured",
        zorder=0,
    )
    phaseAx.errorbar(
        freqs, phase, yerr=kwargs.get("perr"), markersize=4, fmt=".", c="k", zorder=0
    )
    polarAx.errorbar(
        phase,
        mag,
        xerr=kwargs.get("perr"),
        yerr=kwargs.get("merr"),
        markersize=4,
        fmt=".",
        c="k",
        zorder=0,
    )

    # Add labels
    magAx.set_xlabel("Frequency [rad s$^{-1}$]")
    magAx.set_ylabel("log$_{10}$|H($\omega$)|")
    phaseAx.set_xlabel("Frequency [rad s$^{-1}$]")
    phaseAx.set_ylabel("Arg(H($\omega$)")
    polarAx.set_xlabel("$\phi$")
    polarAx.set_ylabel("$\omega$")

    # Add grid
    magAx.grid(alpha=0.5)
    phaseAx.grid(alpha=0.5)
    polarAx.grid(alpha=0.5)

    # Add analytic if provided
    if not (analytic is None):
        magAx.plot(freqs, 20 * np.log10(abs(analytic)), c="r", label="Analytic")
        phaseAx.plot(freqs, np.angle(analytic), c="r")
        polarAx.plot(np.angle(analytic), abs(analytic), c="r")

        magAx.legend()

    # Convert to logarithmic axes
    magAx.set_xscale("log")
    phaseAx.set_xscale("log")

    # Set limits if provided
    kwargs.get("xlim") and magAx.set_xlim(kwargs["xlim"])
    kwargs.get("xlim") and phaseAx.set_xlim(kwargs["xlim"])
    kwargs.get("mag_ylim") and magAx.set_ylim(kwargs["mag_ylim"])
    kwargs.get("phase_ylim") and phaseAx.set_ylim(kwargs["phase_ylim"])

    plt.tight_layout()
    plt.show()
