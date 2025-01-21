# -*- coding: utf-8 -*-
"""
Created on Tue Jan 21 20:28:10 2025

@author: s_ver
"""
import matplotlib.pyplot as plt
import numpy as np

from span.feedback import PIDController

# Simulation parameters
kp = 0.1
kd = 0.0
dt = 0.1
simTime = 150

fig = plt.figure()
ax = fig.add_subplot()

for ki in [
    0.001,
    0.01,
    0.5,
]:
    setpoint = 20
    timeData = []
    tempData = []
    feedbackData = []
    setpointData = []

    # Initial conditions and tracking
    temp = 20.0
    ambient = 20.0
    coolCoef = 0.01
    heatCoef = 0.7

    pid = PIDController(kp, ki, kd, setpoint)
    pid.clipFunction = lambda data: data

    for t in np.arange(0, simTime, dt):
        if t > 10.0:
            pid.setpoint = 50
        feedback = pid.compute(temp, dt)
        heating_rate = feedback * heatCoef
        cooling_rate = coolCoef * (temp - ambient)

        temp += (heating_rate - cooling_rate) * dt
        timeData.append(t)
        tempData.append(temp)
        feedbackData.append(feedback)
        setpointData.append(pid.setpoint)

    ax.plot(timeData, tempData, label=f"ki = {ki}")

ax.set_xlabel("Time [s]")
ax.set_ylabel("Temperature [C]")

ax.plot(timeData, setpointData, c="gray", ls="--", label="setpoint")
ax.legend()
plt.show()
