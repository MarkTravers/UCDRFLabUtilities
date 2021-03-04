#!python3

import numpy as np
from UCDRFLabUtilities.nanoVNA.driver import NanoVNA
from UCDRFLabUtilities.signalutilities.sparameters import NoCalibration

import matplotlib.pyplot as plt

if __name__=='__main__':
    vna = NanoVNA('COM5')
    
    # Sweep Parameters
    sweepPoints = 100
    sweepStart = 1.0e9
    sweepStop = 3.0e9
    sweepStep = (sweepStop - sweepStart) / sweepPoints

    # Configure VNA sweep
    vna.setSweepConfig(sweepPoints=sweepPoints, sweepStart=sweepStart, sweepStep=sweepStep)

    # Read sweep from VNA
    sweepData = vna.captureSweep(NoCalibration.calcS11, NoCalibration.calcS21)

    plt.plot(sweepData['S11'].real)
    # plt.plot(sweepData['freqs'], sweepData['S11'], sweepData['freqs'], sweepData['S21'])
    plt.show()
    
    print('done.')