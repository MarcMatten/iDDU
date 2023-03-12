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
        for i in range(0, len(self.PortList)):
            if self.PortList[i].device == 'COM8':  # self.PortList[i].description[0:16] == 'Serielles USB-Ge' and
                self.COMPort = self.PortList[i].device
                self.BPortFound = True

        if self.BPortFound:
            try:
                self.logger.info('Arduino found! Connecting to {}'.format(self.COMPort))
                self.serial = serial.Serial(self.COMPort, 9600, timeout=1)
                self.serial.write(struct.pack('>bbbbbbb', 0, 0, 0, 0, 0, 0, 1))
                self.BArduinoConnected = True
                self.logger.info('Connection to Arduino Leonardo established on COM8!')
            except:
                self.BArduinoConnected = False
                self.logger.error('Could not connect to COM8!')
        else:
            self.logger.error('Did not find Arduino Leonardo (COM8)!')

    def run(self):
        while self.running:
            # execute this loop while iRacing is running
            while self.ir.startup():

                # execute this loop while player is on track
                while self.BArduinoConnected and self.db.IsOnTrack:
                    t = time.perf_counter()
                    self.tic()

                    # Shift LEDs
                    vCar = 0  # np.int8(min(max(3.06 * abs(self.db.Speed)-128, -128), 127))
                    BInitLEDs = 0

                    if self.db.config['BEnableShiftLEDs']:
                        ShiftLEDs = np.int8(max(min(self.db.NShiftLEDState, 8), 0))
                    else:
                        ShiftLEDs = 0

                    if self.db.BLEDsInit:
                        BInitLEDs = 1
                        self.db.BLEDsInit = False

                    # Slip LEDS
                    #   0      1     2                 3           4                     5                6
                    # ['Off', 'On', 'Traction + ABS', 'ABS only', 'Traction + Braking', 'Traction only', 'Braking only']

                    SlipLEDsFL = 0
                    SlipLEDsFR = 0
                    SlipLEDsRL = 0
                    SlipLEDsRR = 0

                    # ABS Activation
                    if self.db.config['NSlipLEDMode'] in [1, 2, 3] and ('dcABS' in self.db.car.dcList or self.db.car.name in self.CarsWithABS):
                        SlipLEDsFL = np.int8(min(max(self.db.rABSActivity[0], 0), 4))
                        SlipLEDsFR = np.int8(min(max(self.db.rABSActivity[1], 0), 4))
                        SlipLEDsRL = np.int8(min(max(self.db.rABSActivity[2], 0), 4))
                        SlipLEDsRR = np.int8(min(max(self.db.rABSActivity[3], 0), 4))

                    # rear locking
                    if self.db.config['NSlipLEDMode'] in [1, 4, 6] and self.db.rRearLocking:
                        SlipLEDsRL = np.int8(min(max(self.db.rRearLocking, 0), 4))
                        SlipLEDsRR = np.int8(min(max(self.db.rRearLocking, 0), 4))

                    # Wheel spin
                    if self.db.config['NSlipLEDMode'] in [1, 2, 4, 5] and self.db.rWheelSpin:
                        SlipLEDsRL = np.int8(min(max(self.db.rWheelSpin, 0), 4))
                        SlipLEDsRR = np.int8(min(max(self.db.rWheelSpin, 0), 4))

                    t2 = time.perf_counter()
                    msg = struct.pack('>bbbbbbb', ShiftLEDs, SlipLEDsFL, SlipLEDsFR, SlipLEDsRL, SlipLEDsRR, BInitLEDs, vCar)
                    self.serial.write(msg)
                    self.db.tExecuteSerialComs2 = (time.perf_counter() - t2) * 1000

                    self.db.tExecuteSerialComs = (time.perf_counter() - t) * 1000
                    self.toc()
                    time.sleep(self.rate)

                    msg = struct.pack('>bbbbbbb', 0, 0, 0, 0, 0, 0, 0)
                    self.serial.write(msg)
                time.sleep(0.2)

            time.sleep(1)
        
        self.serial.close()
