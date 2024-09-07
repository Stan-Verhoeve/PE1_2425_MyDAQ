import numpy as np
from numpy import ndarray
import nidaqmx as dx
from scipy.signal import sawtooth, square
from time import sleep


class MyDAQ:
    def __init__(self):
        self.__samplerate = None
        self.__name = None

    @property
    def samplerate(self):
        return self.__samplerate

    @samplerate.setter
    def samplerate(self, newSamplerate: int) -> None:
        assert (
            newSamplerate > 0 and type(newSamplerate) == int
        ), "Samplerate should be a positive integer!"
        self.__samplerate = newSamplerate

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, newName: str) -> None:
        assert type(newName) == str, "Name should be a string!"
        self.__name = newName

    def _addOutputChannels(self, task: dx.Task, channels: str | list[str]) -> None:
        """
        Add output channels to the DAQ
        """
        assert self.name, "Name should be set first!"

        # Make sure channels can be iterated over
        if isinstance(channels, str):
            channels = [channels]

        # Iterate over all channels and add to task
        for channel in channels:
            if self.name in channel:
                task.ao_channels.add_ao_voltage_chan(channel)
            else:
                task.ao_channels.add_ao_voltage_chan(self.name + f"/{channel}")

    def _addInputChannels(self, task: dx.Task, channels: str | list[str]) -> None:
        """
        Add input channels to the DAQ
        """
        assert self.name, "Name should be set first!"

        # Make sure channels can be iterated over
        if isinstance(channels, str):
            channels = [channels]

        # Iterate over all channels and add to task
        for channel in channels:
            if self.name in channel:
                task.ai_channels.add_ai_voltage_chan(channel)
            else:
                task.ai_channels.add_ai_voltage_chan(self.name + f"/{channel}")

    def _configureChannelTimings(self, task: dx.Task, samples: int) -> None:
        """
        Set the correct timings for task based on number of samples
        """
        assert self.samplerate, "Samplerate should be set first!"

        task.timing.cfg_samp_clk_timing(
            self.samplerate,
            sample_mode=dx.constants.AcquisitionType.FINITE,
            samps_per_chan=samples,
        )

    @staticmethod
    def convertDurationToSamples(samplerate: int, duration: int | float) -> int:
        samples = duration * samplerate

        # Round down to nearest integer
        return int(samples)

    @staticmethod
    def convertSamplesToDuration(samplerate: int, samples: int) -> int | float:
        duration = samples / samplerate

        return duration

    def read(self, duration: int | float, *channels: str) -> ndarray:
        """
        Read from user-specified channels for `duration` seconds
        """

        # Convert duration to samples
        samples = MyDAQ.convertDurationToSamples(self.samplerate, duration)

        # Create read task
        with dx.Task("readOnly") as readTask:
            self._addInputChannels(readTask, channels)
            self._configureChannelTimings(readTask, samples)

            # Now read in data. Use WAIT_INFINITELY to assure ample reading time
            data = readTask.read(
                number_of_samples_per_channel=samples,
                timeout=dx.constants.WAIT_INFINITELY,
            )

            return np.asarray(data)

    def write(self, voltages: ndarray, *channels: str) -> None:
        """
        Write `voltages` to user-specified channels.
        """
        samples = max(voltages.shape)

        # Create write task
        with dx.Task("writeOnly") as writeTask:
            self._addOutputChannels(writeTask, channels)
            self._configureChannelTimings(writeTask, samples)

            # Now write the data
            writeTask.write(voltages, auto_start=True)

            # Wait for writing to finish
            sleep(samples / self.samplerate + 1 / 1000)
            writeTask.stop()

    def readwrite(
        self,
        voltages: ndarray,
        readChannels: str | list[str],
        writeChannels: str | list[str],
    ) -> ndarray:
        samples = max(voltages.shape)

        with dx.Task("read") as readTask, dx.Task("write") as writeTask:
            self._addOutputChannels(writeTask, writeChannels)
            self._addInputChannels(readTask, readChannels)

            self._configureChannelTimings(writeTask, samples)
            self._configureChannelTimings(readTask, samples)

            # Start writing. Since reading is a blocking function, there
            # is no need to sleep and wait for writing to finish.
            writeTask.write(voltages, auto_start=True)
            data = readTask.read(
                number_of_samples_per_channel=samples,
                timeout=dx.constants.WAIT_INFINITELY,
            )

            return np.asarray(data)

    @staticmethod
    def generateWaveform(
        form: str,
        samplerate: int,
        frequency: int | float,
        amplitude: int | float = 1,
        phase: int | float = 0,
        duration: int | float = 1,
    ) -> tuple[ndarray, ndarray]:
        """
        Geneate a waveform from the 4 basic wave parameters

        Parameters
        ----------
        form : str
            Type of waveform.
            Must be in ["sine", "square", "sawtooth", "isawtooth", "triangle"].
        samplerate: int
            Samplerate with which to sample waveform.
        frequency : int or float
            Frequency of the waveform.
        amplitude : int or float, optional
            Amplitude of the waveform in volts. The default is 1.
        phase : int or float, optional
            Phase of the waveform in degrees. The default is 0.
        duration : int or float, optional
            Duration of the waveform in seconds. The default is 1.

        Returns
        -------
        timeArray : ndarray
            ndarray containing the discrete times at which the waveform is evaluated.
        wave : ndarray
            ndarray of the evaluated waveform.

        """
        timeArray = MyDAQ.getTimeArray(duration, samplerate)
        arg = 2 * np.pi * frequency * timeArray + np.deg2rad(phase)

        match form:
            case "sine":
                wave = amplitude * np.sin(arg)
            case "square":
                wave = amplitude * square(arg)
            case "sawtooth":
                wave = amplitude * sawtooth(arg)
            case "isawtooth":
                wave = amplitude * sawtooth(arg, width=0)
            case "triangle":
                wave = amplitude * sawtooth(arg, width=0.5)
            case _:
                raise ValueError(f"{form} is not a recognized wavefront form")
        return timeArray, wave

    @staticmethod
    def getTimeArray(duration: int | float, samplerate: int) -> ndarray:
        return np.arange(1 / samplerate, duration, 1 / samplerate)

    def __str__(self):
        """
        Only used for pretty printing of class
        E.g. using `print(MyDAQ)` will neatly print the most important
        properties
        """
        title = f"MyDAQ instance"

        return (
            title
            + f"\n{'=' * len(title)}"
            + f"\nBase name: {self.name}"
            + f"\nSample rate: {self.samplerate}"
        )
