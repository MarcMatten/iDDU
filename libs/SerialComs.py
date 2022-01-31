import time
from libs.IDDU import IDDUThread
import serial
import serial.tools.list_ports
import struct
import numpy as np

RPMLEDPattern = [0, 3, 6, 7, 8]


class SerialComsThread(IDDUThread):
    def __init__(self, rate):
        IDDUThread.__init__(self, rate)
        # connecting to Arduino which controlls the fans
        self.PortList = serial.tools.list_ports.comports()
        self.BPortFound = False
        self.BArduinoConnected = False
        self.COMPort = None
        self.serial = None
        for i in range(1, len(self.PortList)):
            if self.PortList[i].description[0:16] == 'Arduino Leonardo':
                self.COMPort = self.PortList[i].device
                self.BPortFound = True

        if self.BPortFound:
            try:
                self.logger.info('Arduino found! Connecting to {}'.format(self.COMPort))

                self.serial = serial.Serial(self.COMPort, 9600, timeout=1)
                time.sleep(2)
                self.serial.write(struct.pack('>bbbbbbb', 0, 0, 0, 0, 0, 0, 1))

                self.BArduinoConnected = True

                self.logger.info('Connection to Arduino Leonardo established on {}!'.format(self.COMPort))
            except:
                self.BArduinoConnected = False
                self.logger.error('Could not connect to Arduino Leonardo established on {}!'.format(self.COMPort))

    def run(self):
        while True:
            # execute this loop while iRacing is running
            while self.ir.startup():

                # execute this loop while player is on track
                while self.BArduinoConnected:
                    t = time.perf_counter()

                    vCar = 0 #np.int8(min(max(3.06 * abs(self.db.Speed)-128, -128), 127))
                    BInitLEDs = 0
                    # ShiftLEDs = np.int8(max(min(RPMLEDPattern[self.db.Alarm[7]], 8), 0))
                    ShiftLEDs = np.int8(max(min(self.db.NShiftLEDState, 8), 0))
                    SlipLEDsFL = 0
                    SlipLEDsFR = 0
                    SlipLEDsRL = 0
                    SlipLEDsRR = 0

                    if self.db.BLEDsInit:
                        BInitLEDs = 1
                        self.db.BLEDsInit = False

                    # ABS Activation
                    if 'dcABS' in self.db.car.dcList:
                        SlipLEDsFL = np.int8(min(max(self.db.rABSActivity[0], 0), 4))
                        SlipLEDsFR = np.int8(min(max(self.db.rABSActivity[1], 0), 4))
                        SlipLEDsRL = np.int8(min(max(self.db.rABSActivity[2], 0), 4))
                        SlipLEDsRR = np.int8(min(max(self.db.rABSActivity[3], 0), 4))
                    elif self.db.rRearLocking:
                        SlipLEDsRL = np.int8(min(max(self.db.rRearLocking, 0), 4))
                        SlipLEDsRR = np.int8(min(max(self.db.rRearLocking, 0), 4))

                    # Wheel spin
                    if self.db.rWheelSpin:
                        SlipLEDsRL = np.int8(min(max(self.db.rWheelSpin, 0), 4))
                        SlipLEDsRR = np.int8(min(max(self.db.rWheelSpin, 0), 4))

                    if self.BArduinoConnected:
                        t2 = time.perf_counter()
                        msg = struct.pack('>bbbbbbb', ShiftLEDs, SlipLEDsFL, SlipLEDsFR, SlipLEDsRL, SlipLEDsRR, BInitLEDs, vCar)
                        # bits = bin(int(ShiftLEDs)) + bin(int(SlipLEDsFL))[2:] + bin(int(SlipLEDsFR))[2:] + bin(int(SlipLEDsRL))[2:] + bin(SlipLEDsRR)[2:] + bin(vCar)[2:] + bin(int(BInitLEDs))[2:]
                        # RPM - format(8, '#006b')
                        # slip - format(4, '#005b')
                        # vcar - format(255, '#010b')
                        # init - bin()
                        self.serial.write(msg)
                        # self.serial.write(struct.pack('>bbbbbbb', 0, 0, 0, 0, 0, 0, 0))
                        self.db.tExecuteSerialComs2 = (time.perf_counter() - t2) * 1000
                        # if self.db.tExecuteSerialComs2 >= 50:
                            # self.logger.warning(msg)
                            # self.logger.warning(ShiftLEDs)
                            # self.logger.warning(SlipLEDsFL)
                            # self.logger.warning(SlipLEDsFR)
                            # self.logger.warning(SlipLEDsRL)
                            # self.logger.warning(SlipLEDsRR)
                            # self.logger.warning(vCar)
                            # self.logger.warning(BInitLEDs)


                    self.db.tExecuteSerialComs = (time.perf_counter() - t) * 1000

                    time.sleep(self.rate)

                time.sleep(0.2)

            time.sleep(1)
