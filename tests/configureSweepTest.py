#!python3

import numpy as np
from UCDRFLabUtilities.nanoVNA.driver import NanoVNA

if __name__=='__main__':
    vna = NanoVNA('COM5')
    
    # Sweep Parameters
    sweepPoints = 100
    sweepStart = 1.0e9
    sweepStop = 3.0e9
    sweepStep = (sweepStop - sweepStart) / sweepPoints

    # Configure VNA sweep
    vna.setSweepConfig(sweepPoints=sweepPoints, sweepStart=sweepStart, sweepStep=sweepStep)

    # Confirm sweep configuration
    config = vna.readSweepConfig()
    print('sweepPoints = %d; sweepStart = %d; sweepStep = %d' % config)