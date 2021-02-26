#!python3

import numpy as np
from UCDRFLabUtilities.nanoVNA.driver import NanoVNA
from UCDRFLabUtilities.signalutilities.sparameters import NoCalibration

if __name__=='__main__':
    vna = NanoVNA('COM3')
    
    # Sweep Parameters
    sweepPoints = 100
    sweepStart = 1.0e9
    sweepStop = 3.0e9
    sweepStep = (sweepStop - sweepStart) / sweepPoints

    # Configure VNA sweep
    vna.setSweepConfig(sweepPoints=sweepPoints, sweepStart=sweepStart, sweepStep=sweepStep)

    # Read sweep from VNA
    sweepData = vna.captureSweep(NoCalibration.calcS11, NoCalibration.calcS21)
    
    print('done.')