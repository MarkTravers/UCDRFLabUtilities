#!python3

import serial
import numpy as np
from serial import SerialException

class NanoVNA():
    def __init__(self, port:str, baudrate:int=115200, timeout=1.0):
        self.vnaPort = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)
        self.sweepPoints = None
        self.sweepStart = None
        self.sweepStop = None

    def __del__(self):
        self.disconnect()

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
        elif int(reply) != 0x02:
            raise SerialException('Unexpected reply from VNA.')
        else:
            return True

    def configureSweep(self, sweepPoints:np.uint16, sweepStart:np.uint64, sweepStop:np.uint64):
        self.sweepPoints = np.uint16(sweepPoints)
        self.sweepStart = np.uint64(sweepStart)
        self.sweepStop = np.uint64(sweepStop)
        self.sweepStep = np.uint64(abs(sweepStop - sweepStart) / sweepPoints)

        if not self.vnaPort.is_open:
            raise SerialException('VNA port not open.')

        # Clear serial buffers
        self.vnaPort.reset_output_buffer()
        self.vnaPort.reset_input_buffer()

        # Set sweepPoints on VNA
        command = bytes.fromhex('21 20') + bytearray(self.sweepPoints)
        self.vnaPort.write(command)
        # Set sweepStart on VNA
        command = bytes.fromhex('23 00') + bytearray(self.sweepStart)
        self.vnaPort.write(command)
        # Set sweepStop on VNA
        command = bytes.fromhex('23 10') + bytearray(self.sweepStep)
        self.vnaPort.write(command)
