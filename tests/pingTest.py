#!python3

from UCDRFLabUtilities.nanoVNA.driver import NanoVNA

if __name__=='__main__':
    vna = NanoVNA('COM5')
    print(vna.ping())