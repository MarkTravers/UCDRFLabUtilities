#!python3

from UCDRFLabUtilities.nanoVNA.driver import NanoVNA

if __name__=='__main__':
    vna = NanoVNA('COM5')
    vna.configureSweep(sweepPoints=100, sweepStart=1000000, sweepStop=3000000)