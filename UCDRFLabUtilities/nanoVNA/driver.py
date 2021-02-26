#!python3

import serial
from typing import Dict, Tuple, Callable
import numpy as np
from serial import SerialException

class NanoVNA():
    def __init__(self, port:str, baudrate:int=115200, timeout:float=1.0, write_timeout:float=1.0):
        # Open serial port to VNA
        self.vnaPort = serial.Serial(port=port, baudrate=baudrate, timeout=timeout, write_timeout=write_timeout)

        # Configuration values
        self.sweepPoints = None
        self.sweepStart = None
        self.sweepStep = None

        # Data
        self.sweepData = None
        self.s11 = None
        self.s21 = None

    def __del__(self):
        self.disconnect()

    def connect(self) -> None:
        self.vnaPort.open()

    def disconnect(self) -> None:
        self.vnaPort.close()

    def ping(self) -> bool:
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

    def setSweepConfig(self, sweepPoints:np.uint16, sweepStart:np.uint64, sweepStep:np.uint64) -> None:
        self.sweepPoints = np.uint16(sweepPoints)
        self.sweepStart = np.uint64(sweepStart)
        self.sweepStep = np.uint64(sweepStep)

        if not self.vnaPort.is_open:
            raise SerialException('VNA port not open.')

        # Clear serial buffers
        self.vnaPort.reset_output_buffer()
        self.vnaPort.reset_input_buffer()

        # Set sweepPoints on VNA
        # 21 - WRITE2
        # 20 - Starting at address 0x20
        command = bytes.fromhex('21 20') + self.sweepPoints.tobytes()
        self.vnaPort.write(command)
        # Set sweepStart on VNA
        # 23 - WRITE8
        # 00 - Starting at address 0x00
        command = bytes.fromhex('23 00') + self.sweepStart.tobytes()
        self.vnaPort.write(command)
        # Set sweepStep on VNA
        # 23 - WRITE8
        # 10 - Starting at address 0x10
        command = bytes.fromhex('23 10') + self.sweepStep.tobytes()
        self.vnaPort.write(command)

        # Allocate sweepData and calculate frequencies
        # Row0 - Frequencies
        # Row1 - Re(fwd0)
        # Row2 - Im(fwd0)
        # Row3 - Re(rev0)
        # Row4 - Im(rev0)
        # Row5 - Re(rev1)
        # Row6 - Im(rev1)
        self.sweepData = np.zeros((7,self.sweepPoints), dtype=np.int32)
        self.sweepData[0,:] = np.linspace(0, self.sweepPoints - 1, self.sweepPoints)
        np.multiply(self.sweepData[0,:], self.sweepStep, out=self.sweepData[0,:])
        np.add(self.sweepData[0,:], self.sweepStart, out=self.sweepData[0,:])

        # Allocate S-parameter matrix
        self.s11 = np.zeros(self.sweepPoints, dtype=np.complex128)
        self.s21 = np.zeros(self.sweepPoints, dtype=np.complex128)

    def readSweepConfig(self) -> Tuple[np.uint16, np.uint64, np.uint64]:
        # Clear serial buffers
        self.vnaPort.reset_output_buffer()
        self.vnaPort.reset_input_buffer()

        # Read sweepPoints from VNA
        # 11 - READ2
        # 20 - Starting at address 0x20
        command = bytes.fromhex('11 20')
        self.vnaPort.write(command)
        reply = self.vnaPort.read_until(size=2)
        sweepPoints = np.uint32(int.from_bytes(reply, byteorder='little'))

        # Read sweepStart from VNA
        # 12 - READ4
        # 00 - Starting at address 0x00
        # 12 - READ4
        # 04 - Starting at address 0x04
        command = bytes.fromhex('12 00 12 04')
        self.vnaPort.write(command)
        reply = self.vnaPort.read_until(size=8)
        sweepStart = np.uint64(int.from_bytes(reply, byteorder='little'))

        # Read sweepStep from VNA
        # 12 - READ4
        # 10 - Starting at address 0x10
        # 12 - READ4
        # 14 - Starting at address 0x14
        command = bytes.fromhex('12 10 12 14')
        self.vnaPort.write(command)
        reply = self.vnaPort.read_until(size=8)
        sweepStep = np.uint64(int.from_bytes(reply, byteorder='little'))

        return (sweepPoints, sweepStart, sweepStep)

    def readNextPoint(self, s11Calc:Callable[[np.ndarray, np.ndarray, np.uint16], None],
                            s21Calc:Callable[[np.ndarray, np.ndarray, np.uint16], None]) -> None:
        # Clear serial buffers
        self.vnaPort.reset_output_buffer()
        self.vnaPort.reset_input_buffer()

        # Request next frequency from VNA (FIFO)
        # 18 - READFIFO
        # 30 - FIFO at address 0x30
        # 32 - Read 32 bytes
        command = bytes.fromhex('18 30 32')
        self.vnaPort.write(command)
        pointData = self.vnaPort.read_until(size=32)

        # Store freqency in pointData
        # Row0 - Frequencies
        # Row1 - Re(fwd0)
        # Row2 - Im(fwd0)
        # Row3 - Re(rev0)
        # Row4 - Im(rev0)
        # Row5 - Re(rev1)
        # Row6 - Im(rev1)
        freqIndex = np.uint16(int.from_bytes(pointData[0x18:0x1a], byteorder='little', signed=False))
        self.sweepData[1, freqIndex] = np.int32(int.from_bytes(pointData[0x00:0x04], byteorder='little', signed=True))
        self.sweepData[2, freqIndex] = np.int32(int.from_bytes(pointData[0x04:0x08], byteorder='little', signed=True))
        self.sweepData[3, freqIndex] = np.int32(int.from_bytes(pointData[0x08:0x0c], byteorder='little', signed=True))
        self.sweepData[4, freqIndex] = np.int32(int.from_bytes(pointData[0x0c:0x10], byteorder='little', signed=True))
        self.sweepData[5, freqIndex] = np.int32(int.from_bytes(pointData[0x10:0x14], byteorder='little', signed=True))
        self.sweepData[6, freqIndex] = np.int32(int.from_bytes(pointData[0x14:0x18], byteorder='little', signed=True))

        # Calculate S-parameters (possibly apply calibration)
        s11Calc(self.sweepData, self.s11, freqIndex)
        s21Calc(self.sweepData, self.s21, freqIndex)

    def captureSweep(self, s11Calc:Callable[[np.ndarray, np.ndarray, np.uint16], None],
                            s21Calc:Callable[[np.ndarray, np.ndarray, np.uint16], None]) -> Dict[str,np.ndarray]:
        # Clear serial buffers
        self.vnaPort.reset_output_buffer()
        self.vnaPort.reset_input_buffer()

        # Flush VNA FIFO
        # 20 - WRITEFIFO
        # 30 - valuesFIFO (sweep data FIFO)
        # 00 - Random data (writing anything to the FIFO flushes the FIFO)
        command = bytes.fromhex('20 30 00')
        self.vnaPort.write(command)

        # Get all data points for one sweep from VNA
        for i in range(self.sweepPoints):
            self.readNextPoint(s11Calc, s21Calc)

        return {'freqs':self.sweepData[0,:], 'S11':self.s11, 'S21':self.s21}
