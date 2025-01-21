# -*- coding: utf-8 -*-
"""
Created on Tue Dec 24 02:44:24 2024

@author: s_ver
"""
import numpy as np


class PIDController:
    def __init__(self, kp=0, ki=0, kd=0, setpoint=0):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.setpoint = setpoint
        self.I = 0
        self.__clipFunction = None
        self.previous = 0

    @property
    def clipFunction(self):
        return self.__clipFunction

    @clipFunction.setter
    def clipFunction(self, newClipFunction):
        assert callable(newClipFunction), "clipFunction should be callable"
        self.__clipFunction = newClipFunction

    # ONLY CALL TO COMPLETELY RESET FEEDBACK!!!
    def resetFeedback(self):
        self.kp = 0.0
        self.ki = 0.0
        self.kp = 0.0
        self.__clipFunction = None
        self.I = 0.0

    def compute(self, data, dt):
        assert not (self.clipFunction is None), ""
        data = abs(np.asarray(data))
        error = self.setpoint - data
        # print(error)

        if error.size > 1:
            P = self.kp * error.mean()
            self.I += np.trapezoid(error, dx=dt)
            D = self.kd * np.gradient(error, dt).mean()
        else:
            P = self.kp * error
            self.I += error * dt
            D = self.kd * (error - self.previous) / dt

        I = self.ki * self.I

        feedback = P + I + D

        clipped = self.clipFunction(feedback)
        self.previous = clipped

        return clipped
