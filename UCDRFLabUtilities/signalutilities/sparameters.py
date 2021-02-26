#!python3

import numpy as np

class SOLTCalibration:
    pass

class NoCalibration:
    @staticmethod
    def calcS11(sweepData:np.ndarray, s11:np.ndarray, freqIndex:np.uint16):
        # Row0 - Frequencies
        # Row1 - Re(fwd0)
        # Row2 - Im(fwd0)
        # Row3 - Re(rev0)
        # Row4 - Im(rev0)
        # Row5 - Re(rev1)
        # Row6 - Im(rev1)
        s11[freqIndex] = np.complex128(sweepData[3,freqIndex] + 1j*sweepData[4,freqIndex]) / np.complex128(sweepData[1,freqIndex] + 1j*sweepData[2,freqIndex])

    @staticmethod
    def calcS21(sweepData:np.ndarray, s21:np.ndarray, freqIndex:np.uint16):
        # Row0 - Frequencies
        # Row1 - Re(fwd0)
        # Row2 - Im(fwd0)
        # Row3 - Re(rev0)
        # Row4 - Im(rev0)
        # Row5 - Re(rev1)
        # Row6 - Im(rev1)
        s21[freqIndex] = np.complex128(sweepData[5,freqIndex] + 1j*sweepData[6,freqIndex]) / np.complex128(sweepData[1,freqIndex] + 1j*sweepData[2,freqIndex])