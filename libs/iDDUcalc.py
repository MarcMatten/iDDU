import irsdk
from libs import iDDUhelper, Track, Car
import csv
import math
import numpy as np
import os
import glob
from datetime import datetime
import winsound
import time


class IDDUCalc:
    white = (255, 255, 255)
    red = (255, 0, 0)
    green = (0, 255, 0)
    blue = (0, 0, 255)
    yellow = (255, 255, 0)
    orange = (255, 133, 13)
    grey = (141, 141, 141)
    black = (0, 0, 0)
    cyan = (0, 255, 255)

    def __init__(self, db):
        self.db = db

        self.FlagCallTime = 0
        self.init = False

        self.Yaw = []
        self.YawNorth = []
        self.VelocityX = []
        self.VelocityY = []
        self.dist = []
        self.time = []
        self.dx = []
        self.dy = []
        self.Logging = False
        self.logLap = 0
        self.timeLogingStart = 0
        self.BCreateTrack = False
        self.BRecordtLap = False

        self.ir = irsdk.IRSDK()

        self.DRSList = ['formularenault35', 'mclarenmp430']
        self.P2PList = ['dallaradw12', 'dallarair18']

        self.dir = None
        self.trackdir = None
        self.trackList = None
        self.carDir = None
        self.carList = None

        self.x = None
        self.y = None
        self.snapshot = False

        self.getTrackFiles2()
        self.loadTrack2('default')

        self.getCarFiles()
        self.loadCar('default')

    def calc(self):
        # Check if DDU is initialised
        if not self.db.BDDUexecuting:
            # initialise
            if not self.db.BWaiting:
                print(self.db.timeStr + ': Waiting for iRacing')
                self.db.BWaiting = True

        # Check if iRacing Service is running
        if self.db.startUp:
            # iRacing is running
            if not self.db.BDDUexecuting:
                print(self.db.timeStr + ': Connecting to iRacing')

            if self.db.oldSessionNum < self.db.SessionNum or self.db.WeekendInfo['SubSessionID'] is not self.db.SubSessionIDOld:
                print(self.db.timeStr + ':\tNew Session: ' + self.db.SessionInfo['Sessions'][self.db.SessionNum][
                    'SessionType'])
                self.initSession()

            if self.db.SessionTime < 10 + self.db.GreenTime:
                self.db.CarIdxPitStops = [0] * 64

            if self.db.SessionInfo['Sessions'][self.db.SessionNum]['ResultsPositions']:
                for i in range(0, len(self.db.SessionInfo['Sessions'][self.db.SessionNum]['ResultsPositions'])):
                    if self.db.SessionInfo['Sessions'][self.db.SessionNum]['ResultsPositions'][i]['CarIdx'] == self.db.DriverCarIdx:
                        self.db.NClassPosition = self.db.SessionInfo['Sessions'][self.db.SessionNum]['ResultsPositions'][i]['ClassPosition'] + 1
                        self.db.NPosition = self.db.SessionInfo['Sessions'][self.db.SessionNum]['ResultsPositions'][i]['Position']
                        self.db.BResults = True

            if self.db.BResults:
                self.db.PosStr = str(self.db.NClassPosition) + '/' + str(self.db.NDriversMyClass)
            else:
                self.db.PosStr = '-/' + str(self.db.NDriversMyClass)

            if self.db.OnPitRoad or self.db.CarIdxTrackSurface[self.db.DriverCarIdx] == 1 or self.db.CarIdxTrackSurface[self.db.DriverCarIdx] == 2:
                pitSpeedLimit = self.db.WeekendInfo['TrackPitSpeedLimit']
                deltaSpeed = [self.db.Speed * 3.6 - float(pitSpeedLimit.split(' ')[0])]

                r = np.interp(deltaSpeed, [-10, -1, 0, 1, 10, 30, 40],
                              [self.black[0], self.black[0], self.green[0], self.green[0], self.yellow[0],
                               self.orange[0], self.red[0]])
                g = np.interp(deltaSpeed, [-10, -1, 0, 1, 10, 30, 40],
                              [self.black[1], self.black[1], self.green[1], self.green[1], self.yellow[1],
                               self.orange[1], self.red[1]])
                b = np.interp(deltaSpeed, [-10, -1, 0, 1, 10, 30, 40],
                              [self.black[2], self.black[2], self.green[2], self.green[2], self.yellow[2],
                               self.orange[2], self.red[2]])

                self.db.backgroundColour = tuple([r, g, b])
                self.db.textColour = self.white
            else:
                if not (self.db.SessionFlags == self.db.oldSessionFlags):
                    self.FlagCallTime = self.db.SessionTime
                    self.db.FlagExceptionVal = 0
                    if self.db.SessionFlags & 0x80000000:  # startGo
                        self.db.backgroundColour = self.green
                        self.db.GreenTime = self.db.SessionTime
                        self.db.CarIdxPitStops = [0] * 64
                    if self.db.SessionFlags & 0x2:  # white
                        self.db.backgroundColour = self.white
                        self.db.textColour = self.black
                    if self.db.SessionFlags & 0x20 and self.db.SessionTime > 20 + self.db.GreenTime:  # blue
                        self.db.backgroundColour = self.blue
                    if self.db.SessionFlags & 0x1:  # checkered
                        self.db.textColour = self.grey
                        self.db.FlagExceptionVal = 1
                        self.db.FlagException = True
                    if self.db.SessionFlags & 0x100000:  # repair
                        self.db.FlagException = True
                        self.db.FlagExceptionVal = 2
                        self.db.backgroundColour = self.black
                    if self.db.SessionFlags & 0x10000 or self.db.SessionFlags & 0x20000:  # disqualified
                        self.db.textColour = self.grey
                        self.db.FlagException = True
                        self.db.FlagExceptionVal = 4
                    if self.db.SessionFlags & 0x40:  # debry
                        self.db.FlagExceptionVal = 5
                    if self.db.SessionFlags & 0x80000:  # warning
                        self.db.FlagException = True
                        self.db.textColour = self.grey
                        self.db.FlagExceptionVal = 6
                    if self.db.SessionFlags & 0x8 or self.db.SessionFlags & 0x100:  # yellow
                        self.db.backgroundColour = self.yellow
                        self.db.textColour = self.black
                    if self.db.SessionFlags & 0x4000 or self.db.SessionFlags & 0x8000:  # SC
                        self.db.FlagException = True
                        self.db.backgroundColour = self.yellow
                        self.db.textColour = self.black
                        self.db.FlagExceptionVal = 3
                    if self.db.SessionFlags & 0x10:  # red
                        self.db.backgroundColour = self.red

                    self.db.oldSessionFlags = self.db.SessionFlags

                elif self.db.SessionTime > (self.FlagCallTime + 3):
                    self.db.backgroundColour = self.black
                    self.db.textColour = self.white
                    self.db.FlagException = False
                    self.db.FlagExceptionVal = 0

            if self.db.IsOnTrack:
                # do if car is on track #############################################################################################
                if not self.db.WasOnTrack:
                    self.db.WasOnTrack = True
                    print(self.db.timeStr + ':\tIsOnTrack')

                self.db.Alarm[0:6] = [0] * 6

                if self.db.RX:
                    self.db.JokerLapsRequired = self.db.WeekendInfo['WeekendOptions']['NumJokerLaps']
                    NumDrivers = len(self.db.DriverInfo['Drivers'])
                    if self.db.SessionInfo['Sessions'][self.db.SessionNum]['ResultsPositions'] is not None:
                        NumResults = len(self.db.SessionInfo['Sessions'][self.db.SessionNum]['ResultsPositions'])
                    else:
                        NumResults = 0
                    self.db.JokerLaps = [0] * NumDrivers
                    self.db.textColourJoker = self.db.textColour
                    for n in range(0, NumResults):
                        self.db.JokerLaps[
                            self.db.SessionInfo['Sessions'][self.db.SessionNum]['ResultsPositions'][n]['CarIdx']] = \
                            self.db.SessionInfo['Sessions'][self.db.SessionNum]['ResultsPositions'][n][
                                'JokerLapsComplete']

                    if not self.db.JokerLapsRequired == 0:
                        self.db.JokerStr = str(self.db.JokerLaps[self.db.DriverCarIdx]) + '/' + str(
                            self.db.JokerLapsRequired)
                    else:
                        self.db.JokerStr = str(self.db.JokerLaps[self.db.DriverCarIdx])

                    if self.db.JokerLaps[self.db.JokerLaps[self.db.DriverCarIdx]] < self.db.JokerLapsRequired:
                        if self.db.LapsToGo == self.db.JokerLapsRequired + 1:
                            self.db.Alarm[6] = 2
                        elif self.db.LapsToGo <= self.db.JokerLapsRequired:
                            self.db.Alarm[6] = 3
                    else:
                        if self.db.JokerLapsRequired > 0:
                            self.db.textColourJoker = self.green

                if self.db.init:  # do when getting into the car
                    print(self.db.timeStr + ':\tGetting into car')
                    self.db.init = False
                    self.db.OutLap = True
                    self.db.LastFuelLevel = self.db.FuelLevel
                    self.db.FuelConsumptionList = []
                    self.db.RunStartTime = self.db.SessionTime
                    self.db.Run = self.db.Run + 1

                    self.ir.pit_command(7)

                if self.db.OnPitRoad:
                    self.db.onPitRoad = True
                elif (not self.db.OnPitRoad) and self.db.onPitRoad:  # pit exit
                    self.db.onPitRoad = False
                    self.db.OutLap = True

                # check if new lap
                if self.db.Lap > self.db.oldLap and self.db.SessionState == 4 and self.db.SessionTime > self.db.newLapTime + 10:
                    self.db.BNewLap = True
                    self.newLap()
                else:
                    self.db.BNewLap = False

                # Create Track Map
                if (self.BCreateTrack or self.BRecordtLap) and not self.db.OutLap and self.db.StintLap > 0:
                    # Logging track data
                    if not self.Logging:
                        self.logLap = self.db.Lap
                        self.Logging = True
                        self.timeLogingStart = self.db.SessionTime

                    self.Yaw.append(self.db.Yaw)
                    self.YawNorth.append(self.db.YawNorth)
                    self.VelocityX.append(self.db.VelocityX)
                    self.VelocityY.append(self.db.VelocityY)
                    self.dist.append(self.db.LapDistPct * 100)
                    self.time.append(self.db.SessionTime - self.timeLogingStart)

                    self.dx.append(math.cos(self.db.Yaw) * self.db.VelocityX * 0.033 - math.sin(
                        self.db.Yaw) * self.db.VelocityY * 0.033)
                    self.dy.append(math.cos(self.db.Yaw) * self.db.VelocityY * 0.033 + math.sin(
                        self.db.Yaw) * self.db.VelocityX * 0.033)

                # fuel consumption -----------------------------------------------------------------------------------------
                if len(self.db.FuelConsumptionList) >= 1:
                    self.db.FuelAvgConsumption = iDDUhelper.meanTol(self.db.FuelConsumptionList, 0.2)
                    self.db.NLapRemaining = self.db.FuelLevel / self.db.FuelAvgConsumption
                    if self.db.NLapRemaining < 3:
                        self.db.Alarm[3] = 2
                    if self.db.NLapRemaining < 1:
                        self.db.Alarm[3] = 3
                    if self.db.BNewLap and not self.db.onPitRoad:
                        fuelNeed = self.db.FuelAvgConsumption * (self.db.LapsToGo - 1 + 0.5)
                        self.db.VFuelAdd = min(max(fuelNeed - self.db.FuelLevel + self.db.FuelAvgConsumption, 0),
                                               self.db.DriverInfo['DriverCarFuelMaxLtr'] * self.db.DriverInfo[
                                                   'DriverCarMaxFuelPct'])
                        if self.db.VFuelAdd == 0:
                            self.ir.pit_command(2, 1)
                            self.ir.pit_command(11)
                            self.db.BTextColourFuelAddOverride = False
                        else:
                            if not round(self.db.VFuelAdd) == round(self.db.VFuelAddOld):
                                self.ir.pit_command(2, round(self.db.VFuelAdd + 1 + 1e-10))
                            if self.db.VFuelAdd < self.db.DriverInfo['DriverCarFuelMaxLtr'] * self.db.DriverInfo['DriverCarMaxFuelPct'] - self.db.FuelLevel + self.db.FuelAvgConsumption:
                                self.db.textColourFuelAddOverride = self.green
                                self.db.BTextColourFuelAddOverride = True
                            elif self.db.VFuelAdd < self.db.DriverInfo['DriverCarFuelMaxLtr'] * self.db.DriverInfo['DriverCarMaxFuelPct'] - self.db.FuelLevel + 2 * self.db.FuelAvgConsumption:
                                self.db.textColourFuelAddOverride = self.yellow
                                self.db.BTextColourFuelAddOverride = True
                            elif self.db.VFuelAdd < self.db.DriverInfo['DriverCarFuelMaxLtr'] * self.db.DriverInfo['DriverCarMaxFuelPct'] - self.db.FuelLevel + 3 * self.db.FuelAvgConsumption:
                                self.db.textColourFuelAddOverride = self.red
                                self.db.BTextColourFuelAddOverride = True
                            else:
                                self.db.BTextColourFuelAddOverride = False
                        self.db.VFuelAddOld = self.db.VFuelAdd
                else:
                    self.db.FuelAvgConsumption = 0
                    self.db.NLapRemaining = 0
                    self.db.VFuelAdd = 0

                if self.db.BTextColourFuelAddOverride:
                    self.db.textColourFuelAdd = self.db.textColourFuelAddOverride
                else:
                    self.db.textColourFuelAdd = self.db.textColour

                # DRS
                if self.db.DRS:
                    if self.db.DRSCounter >= self.db.DRSActivations > 0:
                        self.db.textColourDRS = self.red
                    else:
                        if not self.db.DRS_Status == self.db.old_DRS_Status:
                            if self.db.DRS_Status == 2:
                                self.db.DRSCounter = self.db.DRSCounter + 1
                            else:
                                self.db.textColourDRS = self.db.textColour
                        if self.db.DRS_Status == 1:
                            self.db.textColourDRS = self.green

                    self.db.DRSRemaining = (self.db.DRSActivations - self.db.DRSCounter)
                    if self.db.DRSRemaining == 1 and not self.db.DRS_Status == 2:
                        self.db.Alarm[5] = 2
                    if self.db.DRS_Status == 2:
                        self.db.Alarm[5] = 1

                    self.db.old_DRS_Status = self.db.DRS_Status

                # P2P
                if self.db.P2P:
                    if self.db.P2PCounter >= self.db.P2PActivations > 0:
                        self.db.textColourP2P = self.red
                    elif (self.db.P2PCounter + 1) == self.db.P2PActivations:
                        self.db.textColourP2P = self.orange
                    else:
                        self.db.textColourP2P = self.db.textColour
                    if not self.db.PushToPass == self.db.old_PushToPass:
                        if self.db.PushToPass:
                            self.db.P2PTime = self.db.SessionTime
                            self.db.Alarm[4] = 1
                            self.db.P2PCounter = self.db.P2PCounter + 1

                    if self.db.SessionTime < self.db.P2PTime + 3:
                        self.db.Alarm[4] = 1

                    self.db.old_PushToPass = self.db.PushToPass

                # alarm
                if self.db.dcTractionControlToggle:
                    self.db.Alarm[1] = 3

                if type(self.db.FuelLevel) is float:
                    if self.db.FuelLevel <= 5:
                        self.db.Alarm[2] = 3
            else:
                if self.db.WasOnTrack:
                    print(self.db.timeStr + ':\tGetting out of car')
                    print(self.db.timeStr + ': Run: ' + str(self.db.Run))
                    print(self.db.timeStr + ':\tFuelAvgConsumption: ' + iDDUhelper.roundedStr2(
                        self.db.FuelAvgConsumption))
                    self.db.WasOnTrack = False
                    self.db.init = True
                # do if car is not on track but don't do if car is on track ------------------------------------------------
                self.init = True

            # do if sim is running after updating data ---------------------------------------------------------------------
            if not self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionLaps'] == 'unlimited':
                self.db.RemLapValue = max(
                    min(self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionLaps'] - self.db.Lap + 1,
                        self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionLaps']), 0)
                self.db.RemLapValueStr = str(self.db.RemLapValue)
            else:
                self.db.RemLapValue = 0
                self.db.RemLapValueStr = '0'

            for i in range(0, len(self.db.CarIdxOnPitRoad)):
                if self.db.CarIdxOnPitRoad[i] and not self.db.CarIdxOnPitRoadOld[i]:
                    self.db.CarIdxPitStops[i] = self.db.CarIdxPitStops[i] + 1
            self.db.CarIdxOnPitRoadOld = self.db.CarIdxOnPitRoad

            # change in driver controls
            if self.db.SessionTime > self.db.RunStartTime + 1:
                if not self.db.dcBrakeBias == self.db.dcBrakeBiasOld and self.db.dcBrakeBias is not None:
                    self.db.dcBrakeBiasChange = True
                    self.db.dcChangeTime = self.db.SessionTime
                if not self.db.dcABS == self.db.dcABSOld and self.db.dcABS is not None:
                    self.db.dcABSChange = True
                    self.db.dcChangeTime = self.db.SessionTime
                if not self.db.dcTractionControlToggle == self.db.dcTractionControlToggleOld and self.db.dcTractionControlToggle is not None:
                    self.db.dcTractionControlToggleChange = True
                    self.db.dcChangeTime = self.db.SessionTime
                if not self.db.dcTractionControl == self.db.dcTractionControlOld and self.db.dcTractionControl is not None:
                    self.db.dcTractionControlChange = True
                    self.db.dcChangeTime = self.db.SessionTime
                if not self.db.dcTractionControl2 == self.db.dcTractionControl2Old and self.db.dcTractionControl2 is not None:
                    self.db.dcTractionControl2Change = True
                    self.db.dcChangeTime = self.db.SessionTime
                if not self.db.dcThrottleShape == self.db.dcThrottleShapeOld and self.db.dcThrottleShape is not None:
                    self.db.dcThrottleShapeChange = True
                    self.db.dcChangeTime = self.db.SessionTime
                if not self.db.dcFuelMixture == self.db.dcFuelMixtureOld and self.db.dcFuelMixture is not None:
                    self.db.dcFuelMixtureChange = True
                    self.db.dcChangeTime = self.db.SessionTime

                if self.db.SessionTime > self.db.dcChangeTime + 0.75:
                    self.db.dcBrakeBiasChange = False
                    self.db.dcABSChange = False
                    self.db.dcTractionControlToggleChange = False
                    self.db.dcTractionControlChange = False
                    self.db.dcTractionControl2Change = False
                    self.db.dcThrottleShapeChange = False
                    self.db.dcFuelMixtureChange = False

            self.db.dcBrakeBiasOld = self.db.dcBrakeBias
            self.db.dcABSOld = self.db.dcABS
            self.db.dcTractionControlToggleOld = self.db.dcTractionControlToggle
            self.db.dcTractionControlOld = self.db.dcTractionControl
            self.db.dcTractionControl2Old = self.db.dcTractionControl2
            self.db.dcThrottleShapeOld = self.db.dcThrottleShape
            self.db.dcFuelMixtureOld = self.db.dcFuelMixture

            if self.db.SessionTime > self.db.RunStartTime + 1:
                if not self.db.dcHeadlightFlash == self.db.dcHeadlightFlashOld and self.db.dcHeadlightFlash is not None:
                    self.db.BdcHeadlightFlash = True
                    self.db.tdcHeadlightFlash = self.db.SessionTime

                if self.db.SessionTime > self.db.tdcHeadlightFlash + 0.5:
                    self.db.BdcHeadlightFlash = False


            self.db.BDDUexecuting = True
        else:
            # iRacing is not running
            if self.db.BDDUexecuting:  # necssary?
                self.db.BDDUexecuting = False
                self.db.BWaiting = True
                self.db.oldSessionNum = -1
                self.db.SessionNum = 0
                self.db.StopDDU = True
                print(self.db.timeStr + ': Lost connection to iRacing')

    def initSession(self):
        print(self.db.timeStr + ': Initialising Session ==========================')
        time.sleep(3)
        self.getTrackFiles2()
        self.db.init = True
        self.db.BResults = False
        self.db.weatherStr = 'TAir: ' + iDDUhelper.roundedStr0(self.db.AirTemp) + '°C     TTrack: ' + iDDUhelper.roundedStr0(self.db.TrackTemp) + '°C     pAir: ' + iDDUhelper.roundedStr2(self.db.AirPressure * 0.0338639*1.02) + ' bar    rHum: ' + iDDUhelper.roundedStr0(self.db.RelativeHumidity * 100) + ' %     rhoAir: ' + iDDUhelper.roundedStr2(self.db.AirDensity) + ' kg/m³     vWind: '
        self.db.FuelConsumptionList = []
        self.db.FuelLastCons = 0
        self.db.newLapTime = 0
        self.db.oldLap = self.db.Lap
        self.db.TrackLength = float(self.db.WeekendInfo['TrackLength'].split(' ')[0])
        self.db.JokerLapsRequired = 0
        self.db.PitStopsRequired = 0
        self.db.MapHighlight = False
        self.db.Alarm = [0]*10

        nan = float('nan')

        if self.db.startUp:
            self.db.StartDDU = True
            self.db.oldSessionNum = self.db.SessionNum
            self.db.DriverCarFuelMaxLtr = self.db.DriverInfo['DriverCarFuelMaxLtr'] * self.db.DriverInfo[
                'DriverCarMaxFuelPct']
            self.db.DriverCarIdx = self.db.DriverInfo['DriverCarIdx']

            # track
            if self.db.WeekendInfo['TrackName'] + '.json' in self.trackList:
                self.loadTrack2(self.db.WeekendInfo['TrackName'])
                self.BCreateTrack = False
            else:
                self.loadTrack2('default')
                self.BCreateTrack = True
                self.BRecordtLap = True
                print(self.db.timeStr + ':\tCreating Track')

            # car
            carName = self.db.DriverInfo['Drivers'][self.db.DriverInfo['DriverCarIdx']]['CarScreenNameShort']
            if carName + '.json' in self.carList:
                self.loadCar(carName)
                if self.db.WeekendInfo['TrackName'] in self.db.car.tLap:
                    self.BRecordtLap = False
                    self.db.time = self.db.car.tLap[self.db.WeekendInfo['TrackName']]
                else:
                    self.BRecordtLap = True
            else:
                self.loadCar('default')
                self.db.car = Car.Car(carName)
                self.db.car.createCar(self.db)
                self.db.car.saveJson(self.db.dir)
                self.BRecordtLap = True

                print(self.db.timeStr + ':\tCreated Car ' + carName)

            print(self.db.timeStr + ':\tTrackName: ' + self.db.WeekendInfo['TrackDisplayName'])
            print(self.db.timeStr + ':\tEventType: ' + self.db.WeekendInfo['EventType'])
            print(self.db.timeStr + ':\tCategory: ' + self.db.WeekendInfo['Category'])
            print(self.db.timeStr + ':\tSessionType: ' + self.db.SessionInfo['Sessions'][self.db.SessionNum][
                'SessionType'])

            if self.db.WeekendInfo['Category'] == 'DirtRoad':
                self.db.__setattr__('RX', True)
                self.db.__setattr__('JokerLapsRequired', self.db.WeekendInfo['WeekendOptions']['NumJokerLaps'])
                self.db.MapHighlight = True
                self.db.RenderLabel[17] = True
                print(self.db.timeStr + ':\tDirt Racing')
            else:
                self.db.__setattr__('RX', False)
                self.db.RenderLabel[17] = False
                print(self.db.timeStr + ':\tRoad Racing')

            # unlimited laps
            if self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionLaps'] == 'unlimited':
                self.db.RaceLaps = self.db.UserRaceLaps
                self.db.LapLimit = False
                self.db.RenderLabel[20] = False
                self.db.RenderLabel[21] = False
                print(self.db.timeStr + ':\t' + self.db.SessionInfo['Sessions'][self.db.SessionNum][
                    'SessionLaps'] + ' laps')
                if self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionType'] == 'Race':
                    print(self.db.timeStr + ':\t' + 'RaceLaps: ' + str(self.db.RaceLaps))
                    self.db.LapLimit = True
                    self.db.RenderLabel[20] = True

                # unlimited time
                if self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionTime'] == 'unlimited':
                    self.db.SessionLength = 86400
                    self.db.RenderLabel[15] = False
                    self.db.RenderLabel[16] = True
                    self.db.TimeLimit = False
                    print(self.db.timeStr + ':\t' + self.db.SessionInfo['Sessions'][self.db.SessionNum][
                        'SessionTime'] + ' time')
                    print(self.db.timeStr + ':\tRace mode 0')
                # limited time
                else:
                    self.db.RenderLabel[15] = True
                    self.db.RenderLabel[16] = False
                    self.db.TimeLimit = True
                    tempSessionLength = self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionTime']
                    self.db.SessionLength = float(tempSessionLength.split(' ')[0])
                    if self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionType'] == 'Race':
                        if self.db.SessionLength > 2100:
                            self.db.PitStopsRequired = 1
                            self.db.MapHighlight = True
                    print(self.db.timeStr + ':\tRace mode 1')
                    print(self.db.timeStr + ':\tSession length :' + self.db.SessionInfo['Sessions'][self.db.SessionNum][
                        'SessionTime'])
                    if self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionType'] == 'Race':
                        self.db.RenderLabel[21] = True
                    else:
                        self.db.RenderLabel[21] = False
            else:  # limited laps
                self.db.RaceLaps = int(self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionLaps'])
                self.db.LapLimit = True
                self.db.RenderLabel[20] = True
                self.db.RenderLabel[21] = False
                if self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionType'] == 'Race':
                    if (self.db.TrackLength*self.db.RaceLaps) > 145:
                        self.db.PitStopsRequired = 1
                        self.db.MapHighlight = True
                # unlimited time
                if self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionTime'] == 'unlimited':
                    self.db.SessionLength = 86400
                    self.db.TimeLimit = False
                    self.db.RenderLabel[15] = False
                    self.db.RenderLabel[16] = True
                    print(self.db.timeStr + ':\tRace mode 4')
                    print(self.db.timeStr + ':\t' + self.db.SessionInfo['Sessions'][self.db.SessionNum][
                        'SessionTime'] + ' time')
                # limited time
                else:
                    self.db.RenderLabel[15] = True
                    self.db.RenderLabel[16] = False
                    self.db.TimeLimit = True
                    print(self.db.timeStr + ':\tRace mode 5')
                    print(self.db.timeStr + ':\tSession length :' + self.db.SessionInfo['Sessions'][self.db.SessionNum][
                        'SessionTime'])

            if self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionType'] == 'Race' and not self.db.LapLimit and self.db.TimeLimit:
                self.db.BEnableRaceLapEstimation = True
            else:
                self.db.BEnableRaceLapEstimation = False

            CarNumber = len(self.db.DriverInfo['Drivers']) + 2
            if not self.db.LapLimit:
                LapNumber = int(self.db.SessionLength/(self.db.TrackLength*13)) + 2
            else:
                if self.db.TimeLimit:
                    LapNumber = int(self.db.SessionLength / (self.db.TrackLength * 13)) + 2
                else:
                    LapNumber = 500

            print(LapNumber)
            print(CarNumber)

            CarIdxtLap_temp = [[] * LapNumber] * CarNumber
            for x in range(0, CarNumber):
                CarIdxtLap_temp[x] = [nan] * LapNumber

            self.db.CarIdxtLap = CarIdxtLap_temp

            self.db.BUpshiftToneInitRequest = True

            print(self.db.timeStr + ':\tinit LapNumber: ' + str(LapNumber))
            print(self.db.timeStr + ':\tinit CarNumber: ' + str(CarNumber))

            print(self.db.timeStr + ':\tRaceLaps: ' + str(self.db.RaceLaps))
            print(self.db.timeStr + ':\tSessionLength: ' + str(self.db.SessionLength))

            # DRS
            if self.db.DriverInfo['Drivers'][self.db.DriverCarIdx]['CarPath'] in self.DRSList:
                self.db.DRS = True
                if not self.db.WeekendInfo['Category'] == 'Oval':
                    self.db.RenderLabel[18] = True
                self.db.DRSCounter = 0
                if not self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionType'] == 'Race':
                    self.db.DRSActivations = 1000
                else:
                    self.db.DRSActivations = self.db.DRSActivationsGUI
            else:
                self.db.DRS = False
                self.db.RenderLabel[18] = False

            # P2P
            if self.db.DriverInfo['Drivers'][self.db.DriverCarIdx]['CarPath'] in self.P2PList:
                self.db.P2P = True
                self.db.P2PCounter = 0
                if not self.db.WeekendInfo['Category'] == 'Oval':
                    self.db.RenderLabel[19] = True
                if not self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionType'] == 'Race':
                    self.db.P2PActivations = 1000
                else:
                    self.db.P2PActivations = self.db.P2PActivationsGUI
            else:
                self.db.P2P = False
                self.db.RenderLabel[19] = False

        if self.db.SessionInfo['Sessions'][self.db.SessionNum]['ResultsPositions']:
            self.db.classStruct = {}

            for i in range(0, len(self.db.DriverInfo['Drivers'])):
                if not str(self.db.DriverInfo['Drivers'][i]['UserName']) == 'Pace Car':
                    if i == 0:
                        self.db.classStruct[str(self.db.DriverInfo['Drivers'][i]['CarClassShortName'])] = {'ID': self.db.DriverInfo['Drivers'][i]['CarClassID'], 'CarClassRelSpeed': self.db.DriverInfo['Drivers'][i]['CarClassRelSpeed'],
                                                                                           'CarClassColor': self.db.DriverInfo['Drivers'][i]['CarClassColor'],
                                                                                           'Drivers': [{'Name': self.db.DriverInfo['Drivers'][i]['UserName'], 'IRating': self.db.DriverInfo['Drivers'][i]['IRating']}]}
                    else:
                        if str(self.db.DriverInfo['Drivers'][i]['CarClassShortName']) in self.db.classStruct:
                            self.db.classStruct[str(self.db.DriverInfo['Drivers'][i]['CarClassShortName'])]['Drivers'].append({'Name': self.db.DriverInfo['Drivers'][i]['UserName'],
                                                                                                                           'IRating': self.db.DriverInfo['Drivers'][i]['IRating']})
                        else:
                            self.db.classStruct[str(self.db.DriverInfo['Drivers'][i]['CarClassShortName'])] = {'ID': self.db.DriverInfo['Drivers'][i]['CarClassID'], 'CarClassRelSpeed': self.db.DriverInfo['Drivers'][i]['CarClassRelSpeed'],
                                                                                               'CarClassColor': self.db.DriverInfo['Drivers'][i]['CarClassColor'],
                                                                                               'Drivers': [{'Name': self.db.DriverInfo['Drivers'][i]['UserName'], 'IRating': self.db.DriverInfo['Drivers'][i]['IRating']}]}


            self.db.NClasses = len(self.db.classStruct)
            classNames = list(self.db.classStruct.keys())
            self.db.NDrivers = 0
            tempSOF = 0
            for j in range(0, self.db.NClasses):
                self.db.classStruct[classNames[j]]['NDrivers'] = len(self.db.classStruct[classNames[j]]['Drivers'])
                tempSOFClass = 0

                for k in range(0, self.db.classStruct[classNames[j]]['NDrivers']):
                    tempSOFClass = tempSOFClass + self.db.classStruct[classNames[j]]['Drivers'][k]['IRating']

                self.db.classStruct[classNames[j]]['SOF'] = tempSOFClass / self.db.classStruct[classNames[j]]['NDrivers']
                self.db.NDrivers = self.db.NDrivers + self.db.classStruct[classNames[j]]['NDrivers']
                tempSOF = tempSOF + tempSOFClass

            self.db.SOF = tempSOF / self.db.NDrivers

            self.db.SOFMyClass = self.db.classStruct[str(self.db.DriverInfo['Drivers'][self.db.DriverCarIdx]['CarClassShortName'])]['SOF']
            self.db.NDriversMyClass = self.db.classStruct[str(self.db.DriverInfo['Drivers'][self.db.DriverCarIdx]['CarClassShortName'])]['NDrivers']

        self.db.SubSessionIDOld = self.db.WeekendInfo['SubSessionID']

    def loadTrack(self, name):
        print(self.db.timeStr + ':\tLoading track: ' + r"track/" + name + '.csv')

        self.db.__setattr__('map', [])
        self.db.__setattr__('x', [])
        self.db.__setattr__('y', [])
        self.db.__setattr__('dist', [])
        self.db.__setattr__('time', [])

        with open(r"track/" + name + '.csv') as csv_file:
            csv_reader = csv.reader(csv_file)
            for line in csv_reader:
                self.db.dist.append(float(line[0]))
                self.db.x.append(float(line[1]))
                self.db.y.append(float(line[2]))
                self.db.time.append(float(line[3]))

                self.db.map.append([float(line[1]), float(line[2])])

        self.db.aOffsetTrack = iDDUhelper.angleVertical(self.db.x[5] - self.db.x[0], self.db.y[5] - self.db.y[0])
        print(self.db.timeStr + ':\tTrack has been loaded successfully.')

    def loadTrack2(self, name):
        print(self.db.timeStr + ':\tLoading track: ' + r"track/" + name + '.json')

        # self.db.track = Track.Track(name)
        # self.db.track.loadFromCSV("track/" + name + '.csv')
        self.db.track = Track.Track(name)
        self.db.track.loadJson("track/" + name + '.json')

        print(self.db.timeStr + ':\tTrack has been loaded successfully.')

    def loadCar(self, name):
        print(self.db.timeStr + ':\tLoading car: ' + r"car/" + name + '.json')

        # self.db.track = Track.Track(name)
        # self.db.track.loadFromCSV("track/" + name + '.csv')
        self.db.car = Car.Car(name)
        self.db.car.loadJson("car/" + name + '.json')

        print(self.db.timeStr + ':\tCar has been loaded successfully.')

    def getTrackFiles(self):
        print(self.db.timeStr + ':\tCollecting Track files...')
        self.dir = os.getcwd()
        self.trackdir = self.dir + r"\track"
        self.trackList = []

        # get list of trackfiles
        os.chdir(self.trackdir)
        for file in glob.glob("*.csv"):
            self.trackList.append(file)
        os.chdir(self.dir)

    def getTrackFiles2(self):
        print(self.db.timeStr + ':\tCollecting Track files...')
        self.dir = os.getcwd()
        self.trackdir = self.dir + r"\track"
        self.trackList = []

        # get list of trackfiles
        os.chdir(self.trackdir)
        for file in glob.glob("*.json"):
            self.trackList.append(file)
        os.chdir(self.dir)

    def getCarFiles(self):
        print(self.db.timeStr + ':\tCollecting Car files...')
        self.dir = os.getcwd()
        self.carDir = self.dir + r"\car"
        self.carList = []

        # get list of trackfiles
        os.chdir(self.carDir)
        for file in glob.glob("*.json"):
            self.carList.append(file)
        os.chdir(self.dir)

    def newLap(self):
        # Lap Counting
        winsound.Beep(200, 200)
        self.db.newLapTime = self.db.SessionTime

        # Fuel Calculations
        self.db.FuelLastCons = self.db.LastFuelLevel - self.db.FuelLevel
        # self.db.FuelConsumptionList.extend([self.db.FuelLastCons])
        if (not self.db.OutLap) and (not self.db.onPitRoad):
            self.db.FuelConsumptionList.extend([self.db.FuelLastCons])
        else:
            self.db.OutLap = False

        self.db.LastFuelLevel = self.db.FuelLevel

        # Logging for race lap estimation
        now = datetime.now()
        date_time = now.strftime("%Y-%m-%d_%H-%M-%S")

        LapStr = date_time + '_Run_'"{:02d}".format(self.db.Run) + '_Lap_'"{:03d}".format(self.db.StintLap) + '.laplog'
        f = open('laplog/' + LapStr, 'x')
        f.write('Lap = ' + repr(self.db.Lap) + '\n')
        f.write('StintLap = ' + repr(self.db.StintLap) + '\n')
        f.write('RaceLaps = ' + repr(self.db.RaceLaps) + '\n')
        f.write('FuelConsumptionList = ' + repr(self.db.FuelConsumptionList) + '\n')
        f.write('TimeLimit = ' + repr(self.db.TimeLimit) + '\n')
        f.write('SessionInfo = ' + repr(self.db.SessionInfo) + '\n')
        f.write('SessionTime = ' + repr(self.db.SessionTime) + '\n')
        f.write('GreenTime = ' + repr(self.db.GreenTime) + '\n')
        f.write('SessionTimeRemain = ' + repr(self.db.SessionTimeRemain) + '\n')
        f.write('DriverCarIdx = ' + repr(self.db.DriverCarIdx) + '\n')
        f.write('CarIdxF2Time = ' + repr(self.db.CarIdxF2Time) + '\n')
        f.write('LapLastLapTime = ' + repr(self.db.LapLastLapTime) + '\n')
        f.write('PitStopsRequired = ' + repr(self.db.PitStopsRequired) + '\n')
        f.write('CarIdxPitStops = ' + repr(self.db.CarIdxPitStops) + '\n')
        f.write('SessionNum = ' + repr(self.db.SessionNum) + '\n')
        f.write('ResultsPositions = ' + repr(self.db.SessionInfo['Sessions'][self.db.SessionNum]['ResultsPositions']) + '\n')
        f.write('DriverInfo = ' + repr(self.db.DriverInfo) + '\n')
        f.write('CarIdxtLap = ' + repr(self.db.CarIdxtLap) + '\n')
        f.write('NLapRaceTime = ' + repr(self.db.NLapRaceTime) + '\n')
        f.write('NLapWinnerRaceTime = ' + repr(self.db.NLapWinnerRaceTime) + '\n')
        f.write('TFinishPredicted = ' + repr(self.db.TFinishPredicted) + '\n')
        f.write('WinnerCarIdx = ' + repr(self.db.WinnerCarIdx) + '\n')
        f.write('NLapDriver = ' + repr(self.db.NLapDriver) + '\n')
        f.write('TimeLimit = ' + repr(self.db.TimeLimit) + '\n')
        f.write('LapLimit = ' + repr(self.db.LapLimit) + '\n')
        f.write('SessionLength = ' + repr(self.db.SessionLength) + '\n')
        f.write('PitStopDelta = ' + repr(self.db.PitStopDelta) + '\n')
        f.write('CarIdxOnPitRoad = ' + repr(self.db.CarIdxOnPitRoad) + '\n')
        f.write('CarIdxLapDistPct = ' + repr(self.db.CarIdxLapDistPct) + '\n')
        f.write('PaceCarIdx = ' + repr(self.db.DriverInfo['PaceCarIdx']) + '\n')
        f.write('FuelLevel = ' + repr(self.db.FuelLevel) + '\n')
        f.write('SessionFlags = ' + repr(self.db.SessionFlags) + '\n')

        f.close()

        self.db.StintLap = self.db.StintLap + 1
        self.db.oldLap = self.db.Lap
        self.db.LapsToGo = self.db.RaceLaps - self.db.Lap + 1

        self.db.weatherStr = 'TAir: ' + iDDUhelper.roundedStr0(self.db.AirTemp) + '°C     TTrack: ' + iDDUhelper.roundedStr0(self.db.TrackTemp) + '°C     pAir: ' + iDDUhelper.roundedStr2(
            self.db.AirPressure*0.0338639*1.02) + ' bar    rHum: ' + iDDUhelper.roundedStr0(self.db.RelativeHumidity * 100) + ' %     rhoAir: ' + iDDUhelper.roundedStr2(self.db.AirDensity) + ' kg/m³     vWind: '

        if (self.BCreateTrack or self.BRecordtLap) and self.Logging and self.logLap < self.db.Lap and self.db.BNewLap:
            self.createTrackFile(self.BCreateTrack, self.BRecordtLap)

    def createTrackFile(self, BCreateTrack, BRecordtLap):

        time.sleep(1)

        index = np.unique(self.time, return_index=True)[1]
        self.time = np.array(self.time)[index]
        self.dist = np.array(self.dist)[index]

        self.time = np.append(self.time, self.db.LapLastLapTime)
        self.dist = np.append(self.dist, 100)

        if BCreateTrack:
            tempx = np.cumsum(self.dx, dtype=float).tolist()
            tempy = np.cumsum(self.dy, dtype=float).tolist()

            dx = tempx[-1] - tempx[0]
            dy = tempy[-1] - tempy[0]

            self.x = np.cumsum(np.array(self.dx) - dx / len(tempx), dtype=float)[index]
            self.y = np.cumsum(np.array(self.dy) - dy / len(tempy), dtype=float)[index]

            # width = np.max(self.x) - np.min(self.x)
            # height = np.max(self.y) - np.min(self.y)

            # scalingFactor = min(400 / height, 720 / width)
            #
            # self.x = 400 + (scalingFactor * self.x - (min(scalingFactor * self.x) + max(scalingFactor * self.x)) / 2)
            # self.y = -(240 + (
            #         scalingFactor * self.y - (min(scalingFactor * self.y) + max(scalingFactor * self.y)) / 2)) + 480

            self.x = np.append(self.x, self.x[0])
            self.y = np.append(self.y, self.y[0])

            self.db.track = Track.Track(self.db.WeekendInfo['TrackName'])

            # aNorth = float(self.db.WeekendInfo['TrackNorthOffset'].split(' ')[0])
            aNorth = np.mean(self.YawNorth[0:5])

            self.db.track.createTrack(self.x, self.y, self.dist, aNorth, self.db.TrackLength*1000)
        # self.db.track.saveJson(self.db.dir + "/track/" + self.db.WeekendInfo['TrackName'] + ".json")
            self.db.track.saveJson(self.db.dir)

            self.db.dist = self.db.track.dist

            print(self.db.timeStr + ':\tTrack has been successfully created')
            print(self.db.timeStr + ':\tSaved track as: ' + r"track/" + self.db.track.name + ".json")

        if BRecordtLap:
            self.db.car.addLapTime(self.db.WeekendInfo['TrackName'], self.time, self.dist, self.db.track.dist)
            self.db.car.saveJson(self.db.dir)
            self.db.time = self.db.car.tLap[self.db.WeekendInfo['TrackName']]

            print(self.db.timeStr + ':\tLap time has been recorded successfully!')
            print(self.db.timeStr + ':\tSaved car as: ' + r"car/" + self.db.car.name + ".json")

        # with open(r"track/" + self.db.WeekendInfo['TrackName'] + ".csv", 'w', newline='') as f:
        #     thewriter = csv.writer(f)
        #     NTrackElements = len(self.dist)
        #     for l in range(0, NTrackElements):
        #         if l > 2:
        #             if not self.dist[l - 1] >= self.dist[l]:
        #                 thewriter.writerow([self.dist[l], self.x[l], self.y[l], self.time[l]])
        #
        # self.db.map = []
        # self.db.x = []
        # self.db.y = []
        # for i in range(0, NTrackElements):
        #     self.db.map.append([float(self.x[i]), float(self.y[i])])
        # self.db.dist = self.dist[0:NTrackElements]
        # self.db.time = self.time[0:NTrackElements]
        # self.db.x = self.x[0:NTrackElements]
        # self.db.y = self.y[0:NTrackElements]
        #
        # self.db.aOffsetTrack = iDDUhelper.angleVertical(self.db.x[5] - self.db.x[0], self.db.y[5] - self.db.y[0])

        self.BCreateTrack = False
        self.BRecordtLap = False
        self.Logging = False

    def SOFstring(self):
        if self.db.NClasses > 1:
            temp = 'SOF: ' + iDDUhelper.roundedStr0(self.db.SOFMyClass) + '('
            keys = self.db.classStruct.keys()
            for i in range(0, self.db.NClasses):
                temp = temp + self.db.classStruct[keys[i]] + ': ' + iDDUhelper.roundedStr0(self.db.classStruct[keys[i]]['SOF'])
            self.db.SOFstr = temp + ')'
        else:
            self.db.SOFstr = 'SOF: ' + iDDUhelper.roundedStr0(self.db.SOF)
