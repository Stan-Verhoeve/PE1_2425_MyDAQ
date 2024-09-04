import numpy as np
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
    def samplerate(self, newSamplerate):
        assert newSamplerate > 0 and type(newSamplerate) == int, "Samplerate should be a positive integer!"
        self.__samplerate = newSamplerate
    
    @property
    def name(self):
        return self.__name
    
    @name.setter
    def name(self, newName):
        assert type(newName) == str, "Name should be a string!"
        self.__name = newName
    
    def _addOutputChannels(self, task, channels):
        """
        Add output channels to the DAQ
        """
        assert self.name, "Name should be set first!"
        
        # Make sure channels can be iterated over
        if isinstance(channels, str):
            channels = [channels]
            
        # Iterate over all channels and add to task
        for channel in channels:
            if self.__name in channel:
                task.ao_channels.add_ao_voltage_chan(channel)
            else:
                task.ao_channels.add_ao_voltage_chan(self.__name + f"{channel}")
    
    def _addInputChannels(self, task, channels):
        """
        Add input channels to the DAQ
        """
        assert self.name, "Name should be set first!"
        
        # Make sure channels can be iterated over
        if isinstance(channels, str):
            channels = [channels]
            
        # Iterate over all channels and add to task
        for channel in channels:
            task.ai_channels.add_ai_voltage_chan(channel)
    
    
    def _configureChannelTimings(self, task, samples):
        """
        Set the correct timings for task based on number of samples
        """
        assert self.samplerate, "Samplerate should be set first!"

        task.timing.cfg_samp_clk_timing(self.samplerate, 
                                        sample_mode=dx.constants.AcquisitionType.FINITE,
                                        samps_per_chan=samples)
    
    def _convertDurationToSamples(self, duration):
        assert self.samplerate, "Samplerate should be set first!"
        
        samples = duration * self.samplerate
        
        # Round down to nearest integer
        return int(samples)
        
    
    def read(self, duration, *channels):
        """
        Read from user-specified channels for `duration` seconds
        """
        
        # Convert duration to samples
        samples = self._convertDurationToSamples(duration)
        
        # Create read task
        with dx.Task("readOnly") as readTask:
            self._addInputChannels(readTask, channels)
            self._configureChannelTimings(readTask, samples)
            
            # Now read in data. Use WAIT_INFINITELY to assure ample reading time
            data = readTask.read(number_of_samples_per_channel=samples, 
                                 timeout=dx.constants.WAIT_INFINITELY)
            
            return np.asarray(data)
    
    def write(self, voltages, *channels):
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
            sleep(samples / self.samplerate + 1/1000)
            writeTask.stop()
    
    def readwrite(self, voltages, readChannels, writeChannels):
        samples = max(voltages.shape)
        
        with dx.Task("read") as readTask, dx.Task("write") as writeTask:
            self._addOutputChannels(writeTask, writeChannels)
            self._addInputChannels(readTask, readChannels)
            
            self._configureChannelTimings(writeTask, samples)
            self._configureChannelTimings(readTask, samples)
            
            # Start writing. Since reading is a blocking function, there
            # is no need to sleep and wait for writing to finish. 
            writeTask.write(voltages, auto_start=True)
            data = readTask.read(number_of_samples_per_channel=samples, timeout=dx.constants.WAIT_INFINITELY)
            
            return np.asarray(data)
    
    @staticmethod
    def generateWaveform(self, form, frequency, samplerate, amplitude=1, phase=0, duration=1):
        """
        Geneate a waveform from the 4 basic wave parameters

        Parameters
        ----------
        form : str
            Type of waveform. 
            Must be in ["sine", "square", "sawtooth", "isawtooth", "triangle"].
        frequency : int or float
            Frequency of the waveform.
        samplerate: int
            Samplerate with which to sample waveform.
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
        arg = 2*np.pi * frequency * timeArray + np.deg2rad(phase)
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
        return timeArray, wave
    
    @staticmethod
    def getTimeArray(duration, samplerate):
        return np.arange(1/samplerate, duration, 1/samplerate)
    
    def __str__(self):
        """
        Only used for pretty printing of class
        E.g. using `print(MyDAQ)` will neatly print the most important
        properties
        """
        title = f"MyDAQ instance"
        
        return title + f"\n{'=' * len(title)}" + \
               f"\nBase name: {self.name}" + \
               f"\nSample rate: {self.samplerate}"
