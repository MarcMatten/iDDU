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
        self.GearID = 'base'

    def run(self):
        while self.running:
            # execute this loop while iRacing is running
            while self.db.startUp:
                if not self.BInitialised or self.db.BUpshiftToneInitRequest:
                    self.initialise()

                # execute this loop while player is on track
                while self.db.IsOnTrack and (self.db.config['ShiftToneEnabled'] or self.db.config['NFuelTargetMethod']):
                    self.tic()
                    t = time.perf_counter()

                    # pit speed approch beeps
                    if self.db.BRequestPitSpeedBeep:
                        self.beepQuick()
                        self.db.BRequestPitSpeedBeep = False

                    if self.db.config['NFuelTargetMethod'] and self.db.Throttle > 0.9:
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

                    if self.db.config['UpshiftStrategy'] == 5 and self.db.Gear in range(1, self.db.car.NGearMax + 1):

                        if self.db.EngineWarnings & 0x20:
                            self.db.NShiftLEDState = 8
                            self.db.Alarm[7] = 4
                        else:
                            self.db.NShiftLEDState = self.nMotorLEDLUT[max(self.db.Gear, 0)](self.db.RPM)
                            self.db.Alarm[7] = self.LEDToAlarm(self.db.NShiftLEDState)

                        # if self.db.RPM >= self.db.car.iRShiftRPM[3]:
                        #     self.db.Alarm[7] = 4
                        # elif self.db.RPM >= self.db.car.UpshiftSettings['nMotorShiftLEDs'][self.db.Gear - 1][2]:
                        #     self.db.Alarm[7] = 3
                        #     print(60)
                        # elif self.db.RPM >= self.db.car.UpshiftSettings['nMotorShiftLEDs'][self.db.Gear - 1][1]:
                        #     self.db.Alarm[7] = 2
                        # elif self.db.RPM >= self.db.car.UpshiftSettings['nMotorShiftLEDs'][self.db.Gear - 1][0]:
                        #     self.db.Alarm[7] = 1
                        # else:
                        #     self.db.Alarm[7] = 0
                    else:
                        if self.db.RPM >= self.db.car.iRShiftRPM[3]:
                            self.db.Alarm[7] = 4
                        elif self.db.RPM >= self.db.car.iRShiftRPM[2]:
                            self.db.Alarm[7] = 3
                        elif self.db.RPM >= self.db.car.iRShiftRPM[1]:
                            self.db.Alarm[7] = 2
                        elif self.db.RPM >= self.db.car.iRShiftRPM[0]:
                            self.db.Alarm[7] = 1
                        else:
                            self.db.Alarm[7] = 0
                        self.db.NShiftLEDState = self.AlarmToLED(self.db.Alarm[7])

                    if self.db.config['ShiftToneEnabled']:
                        if self.db.Gear > 0 and self.db.Throttle > 0.5 and self.db.Speed > 20 and self.db.rSlipR < self.rSlipRMax:
                            if self.db.config['UpshiftStrategy'] < 4:  # iRacing shift rpm
                                if self.db.RPM >= self.db.iRShiftRPM[self.db.config['UpshiftStrategy']] and self.db.config['UserShiftFlag'][self.db.Gear - 1]:
                                    self.beep()
                                # else:
                                    # self.db.Alarm[7] = 0
                            elif self.db.config['UpshiftStrategy'] == 4:  # user shift rpm
                                if self.db.RPM >= self.db.config['UserShiftRPM'][self.db.Gear - 1] and self.db.config['UserShiftFlag'][self.db.Gear - 1]:
                                    self.beep()
                                # else:
                                    # self.db.Alarm[7] = 0
                            elif self.db.config['UpshiftStrategy'] == 5:  # optimised shift rpm from car file
                                if self.db.car.UpshiftSettings[self.GearID]['BShiftTone'][self.db.Gear - 1] and \
                                        self.db.RPM >= self.db.car.UpshiftSettings[self.GearID]['nMotorShiftTarget'][self.db.Gear - 1] and \
                                        (self.db.car.UpshiftSettings[self.GearID]['vCarShiftTarget'][self.db.Gear - 1] - 1) <= \
                                        self.db.Speed < (self.db.car.UpshiftSettings[self.GearID]['vCarShiftTarget'][self.db.Gear - 1] + 1):
                                    self.beep()
                                # else:
                                    # self.db.Alarm[7] = 0
                        # else:
                            # self.db.Alarm[7] = 0

                    if (not self.oldGear == self.db.Gear) and self.BShiftTone:
                        tShiftReaction = max(time.time() - self.tBeep + self.db.config['tShiftBeep'] / 1000, 0)
                        if tShiftReaction > 1:
                            self.db.tShiftReaction = float('nan')
                        else:
                            self.db.tShiftReaction = tShiftReaction

                        self.BShiftTone = False

                    if self.db.Gear > 0:
                        self.oldGear = self.db.Gear

                    # # pit speed approch beeps
                    # if self.db.BRequestPitSpeedBeep:
                    #     self.beepQuick()
                    #     self.db.BRequestPitSpeedBeep = False


                    self.db.tExecuteUpshiftTone = (time.perf_counter() - t) * 1000
                    self.toc()

                    time.sleep(self.rate)

                time.sleep(0.2)

            time.sleep(1)

            self.BInitialised = False

    def beep(self):
        # self.db.Alarm[7] = 3
        if not self.db.AM.PSLARMED.BActive and not self.db.BEnteringPits and time.time() > (self.tBeep + 0.75):
            self.vjoy.set_button(64, 1)
            winsound.Beep(self.db.config['fShiftBeep'], self.db.config['tShiftBeep'])
            self.tBeep = time.time()
            self.vjoy.set_button(64, 0)

            if (not self.BShiftTone) and self.oldGear == self.db.Gear:
                self.BShiftTone = True

    def beepQuick(self):
        # self.db.Alarm[7] = 3
        if time.time() > (self.tBeep + 0.25):
            self.vjoy.set_button(64, 1)
            winsound.Beep(self.db.config['fShiftBeep'], self.db.config['tShiftBeep'])
            self.tBeep = time.time()
            self.vjoy.set_button(64, 0)

    def initialise(self):
        time.sleep(0.1)
        self.tBeep = 0

        GearID = self.db.car.getGearID(self.db.CarSetup)
        if GearID == '' or GearID not in self.db.car.UpshiftSettings:
            GearID = 'base'
        self.GearID = GearID
        self.logger.info('Loaded Upshift config: {}'.format(GearID))

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
            self.nMotorLED[i + 1, :] = np.concatenate((np.linspace(self.db.car.UpshiftSettings[self.GearID]['nMotorShiftLEDs'][i][0], self.db.car.UpshiftSettings[self.GearID]['nMotorShiftLEDs'][i][1], 4)[0:3],
                                                       np.linspace(self.db.car.UpshiftSettings[self.GearID]['nMotorShiftLEDs'][i][1], self.db.car.UpshiftSettings[self.GearID]['nMotorShiftLEDs'][i][2], 4),
                                                       np.array(self.BlinkRPM)),
                                                      axis=None)

        # self.nMotorLED[self.db.car.NGearMax, :] = self.nMotorLED[self.db.car.NGearMax - 1, :]
        # self.nMotorLED[self.db.car.NGearMax, :] = np.concatenate((np.linspace(self.db.iRShiftRPM[0], self.db.iRShiftRPM[1], 4)[0:3],
        #                                                           np.linspace(self.db.iRShiftRPM[1], self.db.iRShiftRPM[2], 4),
        #                                                           np.array(self.BlinkRPM)),
        #                                                          axis=None)
        self.nMotorLED[self.db.car.NGearMax, :] = np.concatenate((np.linspace((self.FirstRPM+self.ShiftRPM)/2, self.ShiftRPM, 4)[0:3],
                                                                  np.linspace(self.ShiftRPM, (self.LastRPM+self.BlinkRPM)/2, 4),
                                                                  np.array(self.BlinkRPM)),
                                                                 axis=None)



        # avoid case where BlinkRPM < nMotorShift causes limiter to flash too early
        self.nMotorLED[:, -1] = np.maximum(self.nMotorLED[:, -1], self.nMotorLED[:, -2] + (self.nMotorLED[:, -2] - self.nMotorLED[:, -3]))


        for i in range(0, len(self.nMotorLED)):
            self.nMotorLEDLUT[i] = interp1d(np.concatenate((0, self.nMotorLED[i, :], 100000), axis=None), [0, 1, 2, 3, 4, 5, 6, 7, 8, 8], kind='previous')


        # self.nMotorLED[self.db.car.NGearMax, :] = np.concatenate((np.linspace(self.FirstRPM, self.ShiftRPM, 4)[0:3],
        #                                                               np.linspace(self.ShiftRPM, self.LastRPM, 4),
        #                                                               np.array(self.BlinkRPM)),
        #                                                              axis=None)






