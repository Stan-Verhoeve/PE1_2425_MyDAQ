# -*- coding: utf-8 -*-
"""
Created on Mon Sep  4 14:41:56 2023

@author: Stan_Verhoeve
"""

import nidaqmx as dx
import numpy as np

class DAQ:
    def __init__(self, samplerate):
        self._samplerate = samplerate
    
    @staticmethod
    def addOutputChannels(task, channels):
        if isinstance(channels, str):
            DAQ.addOutputChannels(task, [channels])
        else:
            for chan in channels:
                task.ao_channels.add_ao_voltage_chan(chan)
    
    @staticmethod
    def addInputChannels(task, channels):
        if isinstance(channels, str):
            DAQ.addInputChannels(task, [channels])
        else:
            for chan in channels:
                task.ai_channels.add_ai_voltage_chan(chan)
    
    def setAcquisitionMode(self, task, sampleTime):
        if isinstance(sampleTime, type(None)):
            sampleMode = dx.constants.AcquisitionType.CONTINUOUS
            task.timing.cfg_samp_clk_timing(self.samplerate, sample_mode=sampleMode)
        else:
            sampleMode = dx.constants.AcquisitionType.FINITE
            
            sampsPerChan = int(sampleTime * self.samplerate)
            task.timing.cfg_samp_clk_timing(self.samplerate, sample_mode=sampleMode, samps_per_chan=sampsPerChan)
            