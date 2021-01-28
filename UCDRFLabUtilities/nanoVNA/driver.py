#!python3

import serial
from serial import SerialException

class NanoVNA():
    def __init__(self, port:str, baudrate:int=115200, timeout=1.0):
        self.vnaPort = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)
        self.freqSteps = None
        self.freqStart = None
        self.freqStop = None

    def connect(self):
        self.vnaPort.open()

    def disconnect(self):
        self.vnaPort.close()

    def ping(self):
        self.vnaPort.reset_output_buffer()
        self.vnaPort.reset_input_buffer()
        self.vnaPort.write(bytes.fromhex('0d'))
        if self.vnaPort.inWaiting() > 1:
            raise SerialException('Failed to clear input buffer or VNA transmitting data.')
        reply = self.vnaPort.read_until(size=1)
        if reply is None:
            raise SerialException('VNA failed to respond.')
        elif int(reply) != 0x2:
            raise SerialException('Unexpected reply from VNA.')
        else:
            return True
