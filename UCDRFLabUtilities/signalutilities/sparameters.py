#!python3

import numpy as np

class SOLTCalibration:
    pass

class NoCalibration:
    @staticmethod
    def calcS11(sweepData:np.ndarray, s11:np.ndarray, freqIndex)