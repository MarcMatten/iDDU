import time
from libs.IDDU import IDDUThread
import serial
import serial.tools.list_ports
import struct


class SteeringWheelComsThread(IDDUThread):
    def __init__(self, rate):
        IDDUThread.__init__(self, rate)
        # connecting to Steering Wheel Arduino
        self.PortList = serial.tools.list_ports.comports()
        self.BPortFound = False
        self.BArduinoConnected = False
        self.COMPort = None
        self.serial = None
        self.rBitePointSent = 0
        for i in range(1, len(self.PortList)):
            if self.PortList[i].device == 'COM13':
                self.COMPort = self.PortList[i].device
                self.BPortFound = True

        if self.BPortFound:
            try:
                self.logger.info('Arduino found! Connecting to {}'.format(self.COMPort))

                self.serial = serial.Serial(self.COMPort, 9600, timeout=0.1)
                time.sleep(2)
                self.rBitePointSent = self.db.config['rBitePoint']/100
                self.serial.write(struct.pack('<f', self.rBitePointSent))

                msg = self.serial.readline()
                if msg:
                    if len(msg) == 1:
                        data = struct.unpack('<b', msg)[0]
                    elif len(msg) == 4:
                        data = struct.unpack('<f', msg)[0]
                    else:
                        data = None

                    if not round(self.rBitePointSent, 3) == round(data, 3):
                        self.logger.error('Could not set Clutch Bite Point!')

                self.BArduinoConnected = True

                self.logger.info('Connection to Steering Wheel established on {}!'.format(self.COMPort))
            except:
                self.BArduinoConnected = False
                self.logger.error('Could not connect to Steering Wheel on {}!'.format(self.COMPort))

    def run(self):
        while True:
            # execute this loop while iRacing is running
            while self.ir.startup():

                # execute this loop while player is on track
                while self.BArduinoConnected and self.db.IsOnTrack:
                    if not self.rBitePointSent == self.db.config['rBitePoint'] / 100:
                        self.rBitePointSent = self.db.config['rBitePoint'] / 100
                        self.serial.write(struct.pack('<f', self.rBitePointSent))

                    msg = self.serial.readline()
                    if msg:
                        if len(msg) == 1:
                            data = struct.unpack('<b', msg)[0]
                        elif len(msg) == 4:
                            data = struct.unpack('<f', msg)[0]
                            if not round(self.rBitePointSent, 3) == round(data, 3):
                                self.logger.error('Could not set Clutch Bite Point!')
                        else:
                            data = None

                        if data == 1 and not self.db.BStartMode:
                            self.db.BStartMode = True
                            self.db.NDDUPage = 4
                        elif data == 0 and self.db.BStartMode:
                            self.db.BStartMode = False
                            self.db.NDDUPage = 1

                time.sleep(0.2)

            time.sleep(1)
