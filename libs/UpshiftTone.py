import time
import winsound
from libs.IDDU import IDDUThread
import numpy as np
from scipy.interpolate import interp1d


class ShiftToneThread(IDDUThread):
    def __init__(self, rate):
        IDDUThread.__init__(self, rate)
        self.FirstRPM = 20000
        self.ShiftRPM = 20000
        self.LastRPM = 20000
        self.BlinkRPM = 20000
        self.DriverCarName = ''
        self.BInitialised = False
        self.IsOnTrack = False
        self.tBeep = 0
        self.BShiftTone = False
        self.oldGear = 0
        self.rSlipRMax = 6
        self.nMotorLED = np.zeros([10, 8])
        self.nMotorLEDLUT = [interp1d([0, 10000], [0, 1], kind='nearest')]*10
        self.LEDToAlarm = interp1d([0, 1, 4, 7, 8], [0, 1, 2, 3, 4], kind='previous')
        self.AlarmToLED = interp1d([0, 1, 2, 3, 4], [0, 1, 4, 7, 8], kind='previous')

    def run(self):
        while 1:
            # execute this loop while iRacing is running
            while self.ir.startup():
                if not self.BInitialised or self.db.BUpshiftToneInitRequest:
                    self.initialise()

                # execute this loop while player is on track
                while self.ir['IsOnTrack'] and (self.db.config['ShiftToneEnabled'] or self.db.config['NFuelTargetMethod']):
                    t = time.perf_counter()

                    if self.db.config['NFuelTargetMethod'] and self.ir['Throttle'] > 0.9:
                        if self.db.BLiftToneRequest:
                            self.vjoy.set_button(63, 1)
                            winsound.Beep(self.db.config['fFuelBeep'], self.db.config['tFuelBeep'])
                            self.vjoy.set_button(63, 0)
                            self.db.BLiftToneRequest = False
                            # self.db.Alarm[7] = 0
                            continue  # no shift beep when lift beep
                        if self.db.tNextLiftPoint < self.db.tLiftTones[0] + 0.5 and len(self.db.LapDistPctLift) > 0:
                            time.sleep(self.rate)
                            # self.db.Alarm[7] = 0
                            continue  # no shift beep when close to lift beep

                    if self.db.config['UpshiftStrategy'] == 5 and self.ir['Gear'] in range(1, self.db.car.NGearMax + 1):

                        if self.ir['EngineWarnings'] & 0x20:
                            self.db.NShiftLEDState = 8
                            self.db.Alarm[7] = 4
                        else:
                            self.db.NShiftLEDState = self.nMotorLEDLUT[max(self.ir['Gear'], 0)](self.ir['RPM'])
                            self.db.Alarm[7] = self.LEDToAlarm( self.db.NShiftLEDState)

                        # if self.ir['RPM'] >= self.db.car.iRShiftRPM[3]:
                        #     self.db.Alarm[7] = 4
                        # elif self.ir['RPM'] >= self.db.car.UpshiftSettings['nMotorShiftLEDs'][self.ir['Gear'] - 1][2]:
                        #     self.db.Alarm[7] = 3
                        #     print(60)
                        # elif self.ir['RPM'] >= self.db.car.UpshiftSettings['nMotorShiftLEDs'][self.ir['Gear'] - 1][1]:
                        #     self.db.Alarm[7] = 2
                        # elif self.ir['RPM'] >= self.db.car.UpshiftSettings['nMotorShiftLEDs'][self.ir['Gear'] - 1][0]:
                        #     self.db.Alarm[7] = 1
                        # else:
                        #     self.db.Alarm[7] = 0
                    else:
                        if self.ir['RPM'] >= self.db.car.iRShiftRPM[3]:
                            self.db.Alarm[7] = 4
                        elif self.ir['RPM'] >= self.db.car.iRShiftRPM[2]:
                            self.db.Alarm[7] = 3
                        elif self.ir['RPM'] >= self.db.car.iRShiftRPM[1]:
                            self.db.Alarm[7] = 2
                        elif self.ir['RPM'] >= self.db.car.iRShiftRPM[0]:
                            self.db.Alarm[7] = 1
                        else:
                            self.db.Alarm[7] = 0
                        self.db.NShiftLEDState = self.AlarmToLED(self.db.Alarm[7])

                    if self.db.config['ShiftToneEnabled']:
                        if self.ir['Gear'] > 0 and self.ir['Throttle'] > 0.9 and self.ir['Speed'] > 20 and self.db.rSlipR < self.rSlipRMax:
                            if self.db.config['UpshiftStrategy'] < 4:  # iRacing shift rpm
                                if self.ir['RPM'] >= self.db.iRShiftRPM[self.db.config['UpshiftStrategy']] and self.db.config['UserShiftFlag'][self.ir['Gear'] - 1]:
                                    self.beep()
                                # else:
                                    # self.db.Alarm[7] = 0
                            elif self.db.config['UpshiftStrategy'] == 4:  # user shift rpm
                                if self.ir['RPM'] >= self.db.config['UserShiftRPM'][self.ir['Gear'] - 1] and self.db.config['UserShiftFlag'][self.ir['Gear'] - 1]:
                                    self.beep()
                                # else:
                                    # self.db.Alarm[7] = 0
                            elif self.db.config['UpshiftStrategy'] == 5:  # optimised shift rpm from car file
                                if self.db.car.UpshiftSettings['BShiftTone'][self.ir['Gear'] - 1] and \
                                        self.ir['RPM'] >= self.db.car.UpshiftSettings['nMotorShiftTarget'][self.ir['Gear'] - 1] and \
                                        (self.db.car.UpshiftSettings['vCarShiftTarget'][self.ir['Gear'] - 1] - 5) <= \
                                        self.ir['Speed'] < (self.db.car.UpshiftSettings['vCarShiftTarget'][self.ir['Gear'] - 1] + 5):
                                    self.beep()
                                # else:
                                    # self.db.Alarm[7] = 0
                        # else:
                            # self.db.Alarm[7] = 0

                    if (not self.oldGear == self.ir['Gear']) and self.BShiftTone:
                        tShiftReaction = max(time.time() - self.tBeep + self.db.config['tShiftBeep'] / 1000, 0)
                        if tShiftReaction > 1:
                            self.db.tShiftReaction = float('nan')
                        else:
                            self.db.tShiftReaction = tShiftReaction

                        self.BShiftTone = False

                    if self.ir['Gear'] > 0:
                        self.oldGear = self.ir['Gear']

                    self.db.tExecuteUpshiftTone = (time.perf_counter() - t) * 1000

                    time.sleep(self.rate)

                time.sleep(0.2)

            time.sleep(1)

            self.BInitialised = False

    def beep(self):
        # self.db.Alarm[7] = 3
        if time.time() > (self.tBeep + 0.75):
            self.vjoy.set_button(63, 1)
            winsound.Beep(self.db.config['fShiftBeep'], self.db.config['tShiftBeep'])
            self.tBeep = time.time()
            self.vjoy.set_button(63, 0)

            if (not self.BShiftTone) and self.oldGear == self.ir['Gear']:
                self.BShiftTone = True

    def initialise(self):
        time.sleep(0.1)
        self.tBeep = 0

        # get optimal shift RPM from iRacing and display message
        self.FirstRPM = self.db.DriverInfo['DriverCarSLFirstRPM']
        self.ShiftRPM = self.db.DriverInfo['DriverCarSLShiftRPM']
        self.LastRPM = self.db.DriverInfo['DriverCarSLLastRPM']
        self.BlinkRPM = self.db.DriverInfo['DriverCarSLBlinkRPM']
        self.DriverCarName = self.db.DriverInfo['Drivers'][self.db.DriverCarIdx]['CarScreenNameShort']

        self.db.iRShiftRPM = [self.FirstRPM, self.ShiftRPM, self.LastRPM, self.BlinkRPM]

        # play three beep sounds as notification
        winsound.Beep(500, 150)
        time.sleep(0.3)
        winsound.Beep(600, 150)
        time.sleep(0.3)
        winsound.Beep(800, 150)

        self.BInitialised = True
        self.db.BUpshiftToneInitRequest = False

        # shift LEDs
        self.nMotorLED = np.ones([self.db.car.NGearMax + 1, 8]) * 100000

        self.nMotorLED[0, :] = np.concatenate((np.linspace(self.FirstRPM, self.ShiftRPM, 4)[0:3],
                                               np.linspace(self.ShiftRPM, self.LastRPM, 4),
                                               np.array(self.BlinkRPM)),
                                              axis=None)

        for i in range(0, self.db.car.NGearMax-1):
            self.nMotorLED[i + 1, :] = np.concatenate((np.linspace(self.db.car.UpshiftSettings['nMotorShiftLEDs'][i][0], self.db.car.UpshiftSettings['nMotorShiftLEDs'][i][1], 4)[0:3],
                                                       np.linspace(self.db.car.UpshiftSettings['nMotorShiftLEDs'][i][1], self.db.car.UpshiftSettings['nMotorShiftLEDs'][i][2], 4),
                                                       np.array(self.BlinkRPM)),
                                                      axis=None)

            print(i)
        print(self.nMotorLED)

        self.nMotorLED[self.db.car.NGearMax, :] = self.nMotorLED[self.db.car.NGearMax - 1, :]

        # avoid case where BlinkRPM < nMotorShift causes limiter to flash too early
        self.nMotorLED[:, -1] = np.maximum(self.nMotorLED[:, -1], self.nMotorLED[:, -2] + (self.nMotorLED[:, -2] - self.nMotorLED[:, -3]))


        print('===========================')
        print(self.nMotorLED)
        print(len(self.nMotorLED))
        print(np.size(self.nMotorLED))
        print('===========================')

        for i in range(0, len(self.nMotorLED)):
            self.nMotorLEDLUT[i] = interp1d(np.concatenate((0, self.nMotorLED[i, :], 100000), axis=None), [0, 1, 2, 3, 4, 5, 6, 7, 8, 8], kind='previous')
            print(i)
            print(np.concatenate((0, self.nMotorLED[i, :], 100000), axis=None))

        print('===========================')
        print(self.nMotorLEDLUT)


        # self.nMotorLED[self.db.car.NGearMax, :] = np.concatenate((np.linspace(self.FirstRPM, self.ShiftRPM, 4)[0:3],
        #                                                               np.linspace(self.ShiftRPM, self.LastRPM, 4),
        #                                                               np.array(self.BlinkRPM)),
        #                                                              axis=None)






