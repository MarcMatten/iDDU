import irsdk
import iDDUhelper
import csv
import math
import numpy as np
import os
import glob
import time


class IDDUCalc:
    def __init__(self, db):
        self.db = db

        self.white = (255, 255, 255)
        self.red = (255, 0, 0)
        self.green = (0, 255, 0)
        self.blue = (0, 0, 255)
        self.yellow = (255, 255, 0)
        self.orange = (255, 133, 13)
        self.grey = (141, 141, 141)
        self.black = (0, 0, 0)
        self.cyan = (0, 255, 255)

        self.FlagCallTime = 0

        self.Yaw = []
        self.YawNorth = []
        self.VelocityX = []
        self.VelocityY = []
        self.dist = []
        self.time = []
        self.dx = []
        self.dy = []
        self.Logging = False

        self.ir = irsdk.IRSDK()

        self.getTrackFiles()
        self.loadTrack('cota gp')

    def calc(self):
        # t = time.time()
        if self.db.isRunning == False:
            # initialise
            if not self.db.waiting:
                print(self.db.timeStr+': Waiting for iRacing')
                self.db.waiting = True

        if self.db.startUp:
            if self.db.isRunning == False:
                print(self.db.timeStr+': Connecting to iRacing')

            if self.db.oldSessionNum < self.db.SessionNum:
                print(self.db.timeStr+':\tNew Session: ' + self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionType'])
                self.initSession()

            if self.db.IsOnTrack:
                # do if car is on track ------------------------------------------------------------------------------------
                if self.db.WasOnTrack == False:
                    self.db.WasOnTrack = True

                self.db.Alarm = []

                if self.db.RX:
                    self.db.JokerLaps = []
                    if self.db.SessionInfo['Sessions'][self.db.SessionNum]['ResultsPositions'] is not None:
                        length = len(self.db.SessionInfo['Sessions'][self.db.SessionNum]['ResultsPositions'])
                    else:
                        length = 0
                    for n in range(0, length):
                        self.db.JokerLaps[self.db.SessionInfo['Sessions'][self.db.SessionNum]['ResultsPositions'][n]['CarIdx']] = self.db.SessionInfo['Sessions'][self.db.SessionNum]['ResultsPositions'][n]['JokerLapsComplete']

                    if not self.db.JokerLapsRequired == 0:
                        self.db.JokerStr = str(self.db.JokerLaps[self.db.DriverCarIdx]) + '/' + str(self.db.JokerLapsRequired)
                    else:
                        self.db.JokerStr = str(self.db.JokerLaps[self.db.DriverCarIdx])
                else:
                    self.db.JokerStr = '-'

                if self.db.init:  # do when getting into the car
                    print(self.db.timeStr+':\tGetting into car')
                    self.db.init = False
                    self.db.OutLap = True
                    self.db.LastFuelLevel = self.db.FuelLevel
                    self.db.FuelConsumption = []

                    self.ir.pit_command(7)

                if self.db.OnPitRoad:
                    self.db.onPitRoad = True
                elif (not self.db.OnPitRoad) and self.db.onPitRoad == True:  # pit exit
                    self.db.onPitRoad = False
                    self.db.OutLap = True

                # check if new lap
                if self.db.Lap > self.db.oldLap:
                    newLap = True
                    self.db.StintLap = self.db.StintLap + 1
                    self.db.oldLap = self.db.Lap
                    self.db.LapsToGo = self.db.RaceLaps - self.db.Lap + 1

                    self.db.FuelLastCons = self.db.LastFuelLevel - self.db.FuelLevel

                    if (not self.db.OutLap) and (not self.db.onPitRoad):
                        self.db.FuelConsumption.extend([self.db.FuelLastCons])
                    else:
                        self.db.OutLap = False

                    self.db.LastFuelLevel = self.db.FuelLevel

                else:
                    newLap = False

                if self.createTrack and not self.db.OutLap:

                    if not self.Logging:
                        self.logLap = self.db.Lap
                        self.Logging = True
                        self.timeLogingStart = self.db.SessionTime

                    self.Yaw.append(self.db.Yaw)
                    self.YawNorth.append(self.db.YawNorth)
                    self.VelocityX.append(self.db.VelocityX)
                    self.VelocityY.append(self.db.VelocityY)
                    self.dist.append(self.db.LapDistPct*100)
                    self.time.append(self.db.SessionTime-self.timeLogingStart)

                    self.dx.append(math.cos(self.db.Yaw)*self.db.VelocityX*0.033 - math.sin(self.db.Yaw)*self.db.VelocityY*0.033)
                    self.dy.append(math.cos(self.db.Yaw)*self.db.VelocityY*0.033 + math.sin(self.db.Yaw)*self.db.VelocityX*0.033)

                if self.createTrack and self.Logging and self.logLap < self.db.Lap and newLap:
                    tempx = np.cumsum(self.dx, dtype=float)
                    tempy = np.cumsum(self.dy, dtype=float)

                    dx = tempx[-1] - tempx[0]
                    dy = tempy[-1] - tempy[0]

                    self.x = np.cumsum(self.dx - dx/len(tempx), dtype=float)
                    self.y = np.cumsum(self.dy - dy/len(tempy), dtype=float)

                    width = max(self.x)-min(self.x)
                    height = max(self.y)-min(self.y)

                    scalingFactor = min(400/height,  720/width)

                    self.x = 400 + (scalingFactor * self.x - (min(scalingFactor * self.x) + max(scalingFactor * self.x))/2)
                    self.y = -(240 + (scalingFactor * self.y - (min(scalingFactor * self.y) + max(scalingFactor * self.y))/2)) + 480

                    with open(r"track/" + self.db.WeekendInfo['TrackName'] + ".csv", 'w', newline='') as f:
                        thewriter = csv.writer(f)
                        for l in range(0, len(self.dist)):
                            if l > 2:
                                if not self.dist[l-1] >= self.dist[l]:
                                    thewriter.writerow([self.dist[l], self.x[l], self.y[l], self.time[l]])

                    self.db.map = []
                    self.db.x = []
                    self.db.y = []
                    for i in range(0, l):
                        self.db.map.append([float(self.x[i]), float(self.y[i])])
                    self.db.dist = self.dist[0:l]
                    self.db.time = self.time[0:l]
                    self.db.x = self.x[0:l]
                    self.db.y = self.y[0:l]

                    self.createTrack = False
                    self.Logging = False

                    print(self.db.timeStr+':\tTrack has been successfully created')
                    print(self.db.timeStr+':\tSaved track as: ' + r"track/" + self.db.WeekendInfo['TrackName'] + ".csv")

                # fuel consumption -----------------------------------------------------------------------------------------
                if len(self.db.FuelConsumption) >= 1:
                    avg = sum(self.db.FuelConsumption) / len(self.db.FuelConsumption)
                    self.db.FuelConsumptionStr = iDDUhelper.roundedStr2(avg)
                    LapRem = self.db.FuelLevel / avg
                    if LapRem < 3:
                        self.db.Alarm.extend([3])
                    if LapRem < 1:
                        self.db.Alarm.extend([4])
                    self.db.FuelLapStr = iDDUhelper.roundedStr1(LapRem)
                    if newLap and not self.db.onPitRoad:
                        fuelNeed = avg * (self.db.LapsToGo - 1)
                        fuelAdd = min(max(fuelNeed - self.db.FuelLevel + avg, 0), self.db.DriverInfo['DriverCarFuelMaxLtr'] * self.db.DriverInfo['DriverCarMaxFuelPct'])
                        self.db.FuelAddStr = iDDUhelper.roundedStr1(fuelAdd)
                        if fuelAdd == 0:
                            self.ir.pit_command(2, 1)
                            self.ir.pit_command(11)
                            self.db.textColourFuelAdd = self.db.textColour
                        else:
                            if not round(fuelAdd) == round(self.db.oldFuelAdd):
                                self.ir.pit_command(2, round(fuelAdd + 1 + 1e-10))
                            if fuelAdd < self.db.DriverInfo['DriverCarFuelMaxLtr'] * self.db.DriverInfo['DriverCarMaxFuelPct'] - self.db.FuelLevel + avg:
                                self.db.textColourFuelAdd = self.green
                            elif fuelAdd < self.db.DriverInfo['DriverCarFuelMaxLtr'] * self.db.DriverInfo['DriverCarMaxFuelPct'] - self.db.FuelLevel + 2*avg:
                                self.db.textColourFuelAdd = self.yellow
                            elif fuelAdd < self.db.DriverInfo['DriverCarFuelMaxLtr'] * self.db.DriverInfo['DriverCarMaxFuelPct'] - self.db.FuelLevel + 3*avg:
                                self.db.textColourFuelAdd = self.red
                            else:
                                self.db.textColourFuelAdd = self.db.textColour
                        self.db.oldFuelAdd = fuelAdd
                else:
                    self.db.FuelConsumptionStr = '0'
                    self.db.FuelLapStr = '0'
                    self.db.FuelAddStr = '0'

                # DRS and P2P
                if self.db.DRSCounter == self.db.DRSActivations:
                    self.db.textColourDRS = self.red
                else:
                    if not self.db.DRS_Status == self.db.old_DRS_Status:
                        if self.db.DRS_Status == 1:
                            self.db.textColourDRS = self.green
                        elif self.db.DRS_Status == 0:
                            self.db.textColourDRS = self.red
                        elif self.db.DRS_Status == 2:
                            self.db.textColourDRS = self.black
                            self.db.DRSCounter = self.db.DRSCounter + 1
                        else:
                            self.db.textColourDRS = self.db.textColour
                        self.db.old_DRS_Status = self.db.DRS_Status

                if self.db.P2PCounter == self.db.P2PActivations:
                    self.db.textColourP2P = self.red
                elif (self.db.P2PCounter + 1) == self.db.P2PActivations:
                    self.db.textColourP2P = self.orange
                else:
                    if not self.db.PushToPass == self.db.old_PushToPass:
                        if not self.db.PushToPass:
                            self.db.textColourP2P = self.green
                        elif self.db.PushToPass:
                            self.db.textColourP2P = self.black
                            self.db.P2PCounter = self.db.P2PCounter + 1
                        self.db.old_PushToPass = self.db.PushToPass

                # alarm
                if self.db.dcTractionControlToggle:
                    self.db.Alarm.extend([1])

                if type(self.db.FuelLevel) is float:
                    if self.db.FuelLevel <= 5:
                        self.db.Alarm.extend([2])
            else:
                if self.db.WasOnTrack:
                    print(self.db.timeStr+':\tGetting out of car')
                    self.db.WasOnTrack = False
                    self.db.init = True
                # do if car is not on track but don't do if car is on track ------------------------------------------------
                self.init = True

            # do if sim is running after updating data ---------------------------------------------------------------------
            if not self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionLaps'] == 'unlimited':
                self.db.RemLapValue = max(min(self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionLaps'] - self.db.Lap + 1,
                                                   self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionLaps']), 0)
                self.db.RemLapValueStr = str(self.db.RemLapValue)
            else:
                self.db.RemLapValue = 0
                self.db.RemLapValueStr = '0'
            RemTimeValue = iDDUhelper.convertTimeHHMMSS(self.db.SessionTimeRemain)

            for i in range(0, len(self.db.CarIdxOnPitRoad)):
                if self.db.CarIdxOnPitRoad[i] and not self.db.CarIdxOnPitRoadOld[i]:
                    self.db.CarIdxPitStops[i] = self.db.CarIdxPitStops[i] + 1
            self.db.CarIdxOnPitRoadOld = self.db.CarIdxOnPitRoad


            if self.db.OnPitRoad or self.db.CarIdxTrackSurface[self.db.DriverCarIdx] == 1 or self.db.CarIdxTrackSurface[self.db.DriverCarIdx] == 2:
                pitSpeedLimit = self.db.WeekendInfo['TrackPitSpeedLimit']
                Dv = self.db.Speed*3.6 - float(pitSpeedLimit.split(' ')[0])

                r = np.interp(Dv, [-10, -5, -1, 1, 5, 10, 15],
                                 [self.black[0], self.black[0], self.green[0], self.green[0], self.yellow[0], self.orange[0], self.red[0]])
                g = np.interp(Dv, [-10, -5, -1, 1, 5, 10, 15],
                                 [self.black[1], self.black[1], self.green[1], self.green[1], self.yellow[1], self.orange[1], self.red[1]])
                b = np.interp(Dv, [-10, -5, -1, 1, 5, 10, 15],
                                 [self.black[2], self.black[2], self.green[2], self.green[2], self.yellow[2], self.orange[2], self.red[2]])
                self.db.backgroundColour = (r, g, b)
                self.db.textColour = self.grey
            else:
                if not (self.db.SessionFlags == self.db.oldSessionFlags):
                    self.FlagCallTime = self.db.SessionTime
                    Flags = str(("0x%x" % self.db.SessionFlags)[2:11])
                    self.db.FlagExceptionVal = 0
                    if Flags[0] == '8':  # Flags[7] == '4' or Flags[0] == '1':
                        self.db.backgroundColour = self.green
                        self.db.GreenTime = self.db.SessionTimeRemain
                        self.db.CarIdxPitStops = [0] * 64
                    if Flags[7] == '2':
                        self.db.backgroundColour = self.white
                        self.db.textColour = self.black
                    if Flags[6] == '2':
                        self.db.backgroundColour = self.blue
                    if Flags[7] == '1':  # checkered
                        self.db.textColour = self.grey
                        self.db.FlagExceptionVal = 1
                        self.db.FlagException = True
                    if Flags[2] == '1':  # repair
                        self.db.FlagException = True
                        self.db.FlagExceptionVal = 2
                        self.db.backgroundColour = self.black
                    if Flags[3] == '1' or Flags[3] == '2' or Flags[3] == '5':  # disqualified or Flags[3] == '4'
                        self.db.textColour = self.grey
                        self.db.FlagException = True
                        self.db.FlagExceptionVal = 4
                    if Flags[6] == '4':  # debry
                        self.db.FlagExceptionVal = 5
                    if Flags[3] == '8' or Flags[3] == 'c':  # warning
                        self.db.FlagException = True
                        self.db.textColour = self.grey
                        self.db.FlagExceptionVal = 6
                    if Flags[7] == '8' or Flags[5] == '1' or Flags[4] == '4' or Flags[4] == '8':
                        self.db.backgroundColour = self.yellow
                        self.db.textColour = self.black
                    if Flags[4] == '4' or Flags[4] == '8':  # SC
                        self.db.FlagException = True
                        self.db.backgroundColour = self.yellow
                        self.db.textColour = self.black
                        self.db.FlagExceptionVal = 3
                    if Flags[7] == '1':  # or Flags[0] == '4'
                        self.db.backgroundColour = self.red

                    self.db.oldSessionFlags = self.db.SessionFlags

                elif self.db.SessionTime > (self.FlagCallTime + 3):
                    self.db.backgroundColour = self.black
                    self.db.textColour = self.grey
                    self.db.FlagException = False
                    self.db.FlagExceptionVal = 0
            self.db.isRunning = True
        else:
            # do if sim is not running -------------------------------------------------------------------------------------
            if self.db.isRunning == True:
                self.db.isRunning = False
                self.db.waiting = True
                self.db.oldSessionNum = -1
                self.db.SessionNum = 0
                self.reinit()
                print(self.db.timeStr+': Lost connection to iRacing')

        # print((time.time()-t)*1000)

    def reinit(self):
        print(self.db.timeStr+': Starting RTDB reinitialisation.')
        helpData = {'done': False, 'timeStr': 0, 'waiting': False, 'LabelSessionDisplay': [1, 1, 1, 0, 1, 1]}
        # data from iRacing
        iRData = {'LapBestLapTime': 0, 'LapLastLapTime': 0, 'LapDeltaToSessionBestLap': 0, 'dcFuelMixture': 0,
                  'dcThrottleShape': 0, 'dcTractionControl': 0, 'dcTractionControl2': 0, 'dcTractionControlToggle': 0,
                  'dcABS': 0, 'dcBrakeBias': 0, 'FuelLevel': 0, 'Lap': 0, 'IsInGarage': 0, 'LapDistPct': 0,
                  'OnPitRoad': 0,
                  'PlayerCarClassPosition': 0, 'PlayerCarPosition': 0, 'SessionLapsRemain': 0, 'Throttle': 0,
                  'SessionTimeRemain': 0, 'SessionTime': 0, 'SessionFlags': 0, 'SessionNum': 0, 'IsOnTrack': False,
                  'Gear': 0,
                  'Speed': 0, 'DriverInfo': {'DriverCarIdx': 0, 'DriverCarFuelMaxLtr': 0, 'DriverCarMaxFuelPct': 1,
                                             'Drivers': [], 'DriverPitTrkPct': 0}, 'CarIdxLapDistPct': [0],
                  'CarIdxOnPitRoad': [True]*64,
                  'SessionInfo': {'Sessions':
                                      [{'SessionType': 'Session', 'SessionTime': 'unlimited', 'SessionLaps': 0,
                                        'ResultsPositions':
                                            [{'CarIdx': 0, 'JokerLapsComplete': 0}]}]}, 'Yaw': 0, 'VelocityX': 0,
                  'VelocityY': 0,
                  'YawNorth': 0,
                  'WeekendInfo': [],
                  'RPM': 0,
                  'LapCurrentLapTime': 0,
                  'EngineWarnings': 0,
                  'CarIdxTrackSurface': 0,
                  'CarLeftRight': 0,
                  'DRS_Status': 0,
                  'PushToPass': False}
        # calculated data
        calcData = {'LastFuelLevel': 0,
                    'GearStr': '-',
                    'SessionInfoAvailable': False,
                    'SessionNum': 0,
                    'init': True,
                    'onPitRoad': True,
                    'isRunning': False,
                    'WasOnTrack': False,
                    'StintLap': 0,
                    'oldSessionNum': -1,
                    'oldLap': 0.1,
                    'FuelConsumption': [],
                    'FuelLastCons': 0,
                    'OutLap': True,
                    'oldSessionlags': 0,
                    'LapsToGo': 27,
                    'SessionLapRemain': 0,
                    'FuelConsumptionStr': '0.00',
                    'RemLapValueStr': '10',
                    'FuelLapStr': '0',
                    'FuelAddStr': '0.0',
                    'FlagCallTime': 0,
                    'FlagException': False,
                    'FlagExceptionVal': 0,
                    'Alarm': [],
                    'oldFuelAdd': 1,
                    'GreenTime': 0,
                    'RemTimeValue': 0,
                    'RaceLaps': 100000,
                    'JokerStr': '-/-',
                    'dist': [],
                    'x': [],
                    'y': [],
                    'map': [],
                    'RX': False,
                    'createTrack': True,
                    'dx': [],
                    'dy': [],
                    'logLap': 0,
                    'Logging': False,
                    'tempdist': -1,
                    'StartUp': False,
                    'oldSessionFlags': 0,
                    'backgroundColour': (0, 0, 0),
                    'textColourFuelAdd': (141, 141, 141),
                    'textColour': (141, 141, 141),
                    'FuelLaps': 1,
                    'FuelAdd': 1,
                    'PitStopDelta': 61,
                    'time': [],
                    'UpshiftStrategy': 0,
                    'UserShiftRPM': [100000, 100000, 100000, 100000, 100000, 100000, 100000],
                    'UserShiftFlag': [1, 1, 1, 1, 1, 1, 1],
                    'iRShiftRPM': [100000, 100000, 100000, 100000],
                    'ShiftToneEnabled': True,
                    'StartDDU': False,
                    'StopDDU': False,
                    'DDUrunning': False,
                    'UserRaceLaps': 0,
                    'SessionLength': 86400,
                    'CarIdxPitStops': [0] * 64,
                    'CarIdxOnPitRoadOld': [True]*64,
                    'PitStopsRequired': 1,
                    'old_DRS_Status': 0,
                    'DRSActivations': 8,
                    'P2PActivations': 12,
                    'JokerLapDelta': 2,
                    'JokerLaps': 1,
                    'MapHighlight': True,
                    'old_PushToPass': False,
                    'textColourDRS': (141, 141, 141),
                    'textColourP2P': (141, 141, 141),
                    'DRSCounter': 0,
                    'P2PCounter': 0}

        self.db.StopDDU = True
        self.db.initialise(helpData)
        self.db.initialise(iRData)
        self.db.initialise(calcData)
        # print(self.db.timeStr+': RTDB reinitialisied')
        self.db.timeStr = time.strftime("%H:%M:%S", time.localtime())
        self.db.StartDDU = True
        print(self.db.timeStr + ':RTDB reinitialisied')

    def initSession(self):
        print(self.db.timeStr+': Initialising Session')
        self.getTrackFiles()
        if self.db.startUp:
            self.db.oldSessionNum = self.db.SessionNum
            self.SessionInfo = True
            self.db.WeekendInfo = self.db.WeekendInfo
            self.db.DriverCarFuelMaxLtr = self.db.DriverInfo['DriverCarFuelMaxLtr'] * \
                                          self.db.DriverInfo['DriverCarMaxFuelPct']
            self.db.DriverCarIdx = self.db.DriverInfo['DriverCarIdx']

            if self.db.WeekendInfo['TrackName'] + '.csv' in self.trackList:
                self.loadTrack(self.db.WeekendInfo['TrackName'])
                self.createTrack = False
            else:
                self.loadTrack('cota gp')
                self.createTrack = True
                print(self.db.timeStr+':\tCreating Track')

            print(self.db.timeStr + ':\tTrackName: ' + self.db.WeekendInfo['TrackDisplayName'])
            print(self.db.timeStr + ':\tEventType: ' + self.db.WeekendInfo['EventType'])
            print(self.db.timeStr + ':\tCategory: ' + self.db.WeekendInfo['Category'])
            print(self.db.timeStr + ':\tSessionType: ' + self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionType'])

            if self.db.WeekendInfo['Category'] == 'DirtRoad':
                self.db.__setattr__('RX', True)
                self.db.__setattr__('JokerLapsRequired', self.db.WeekendInfo['WeekendOptions']['NumJokerLaps'])
                print(self.db.timeStr+':\tDirt Racing')
            else:
                self.db.__setattr__('RX', False)
                print(self.db.timeStr+':\tRoad Racing')

            # unlimited laps
            if self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionLaps'] == 'unlimited':
                self.db.LabelSessionDisplay[4] = 0  # ToGo
                self.db.RaceLaps = self.db.UserRaceLaps
                print(self.db.timeStr + ':\t' + self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionLaps'] + ' laps')
                # unlimited time
                if self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionTime'] == 'unlimited':
                    self.db.LabelSessionDisplay[2] = 0  # Remain
                    self.db.LabelSessionDisplay[3] = 1  # Elapsed
                    self.db.SessionLength = 86400
                    print(self.db.timeStr + ':\t' + self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionTime'] + ' time')
                    print(self.db.timeStr + ':\tRace mode 0')
                # limited time
                else:
                    self.db.LabelSessionDisplay[2] = 1  # Remain
                    self.db.LabelSessionDisplay[3] = 0  # Elapsed
                    tempSessionLength = self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionTime']
                    self.db.SessionLength = float(tempSessionLength.split(' ')[0])
                    print(self.db.timeStr + ':\tRace mode 1')
                    print(self.db.timeStr + ':\tSession length :' + self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionTime'])
            # limited laps
            elif int(self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionLaps']) >= 2000: # alternative
                self.db.LabelSessionDisplay[4] = 0  # ToGo
                self.db.RaceLaps = self.db.UserRaceLaps
                print(self.db.timeStr + ':\t' + self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionLaps'] + ' laps')
                if self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionTime'] == 'unlimited':
                    self.db.LabelSessionDisplay[2] = 0  # Remain
                    self.db.LabelSessionDisplay[3] = 1  # Elapsed
                    self.db.SessionLength = 86400
                    print(self.db.timeStr + ':\t' + self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionTime'] + ' time')
                    print(self.db.timeStr + ':\tRace mode 0')
                else:
                    self.db.LabelSessionDisplay[2] = 1  # Remain
                    self.db.LabelSessionDisplay[3] = 0  # Elapsed
                    tempSessionLength = self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionTime']
                    self.db.SessionLength = float(tempSessionLength.split(' ')[0])
                    print(self.db.timeStr + ':\tRace mode 1')
                    print(self.db.timeStr + ':\tSession length :' + self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionTime'])
            # limited laps
            else:
                self.db.RaceLaps = int(self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionLaps'])
                self.db.LabelSessionDisplay[4] = 1  # ToGo
                # print(self.db.timeStr + ':\t' + self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionLaps'] + ' laps')
                # unlimited time
                if self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionTime'] == 'unlimited':
                    self.db.LabelSessionDisplay[3] = 1  # Elapsed
                    self.db.LabelSessionDisplay[4] = 0  # ToGo
                    self.db.SessionLength = 86400
                    print(self.db.timeStr + ':\tRace mode 2')
                    print(self.db.timeStr + ':\t' + self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionTime'] + ' time')
                # limited time
                else:
                    tempSessionLength = self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionTime']
                    self.db.SessionLength = float(tempSessionLength.split(' ')[0])
                    if self.db.SessionLength > (800*self.db.RaceLaps):
                        self.db.LabelSessionDisplay[4] = 0  # ToGo
                        self.db.LabelSessionDisplay[3] = 1  # Elapsed
                    else:
                        self.db.LabelSessionDisplay[4] = 1  # ToGo
                        self.db.LabelSessionDisplay[3] = 0  # Elapsed
                    print(self.db.timeStr + ':\tRace mode 3')
                    print(self.db.timeStr + ':\tSession length :' + self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionTime'])

            print(self.db.timeStr + ':\tRaceLaps: ' + str(self.db.RaceLaps))
            print(self.db.timeStr + ':\tSessionLength: ' + str(self.db.SessionLength))

            if self.db.WeekendInfo['Category'] == 'DirtRoad':
                self.db.LabelSessionDisplay[5] = 1  # Joker
            else:
                self.db.LabelSessionDisplay[5] = 0  # Joker
        
    def loadTrack(self, name):
        print(self.db.timeStr+':\tLoading track: ' + r"track/" + name + '.csv')

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
        print(self.db.timeStr+':\tTrack has been loaded successfully.')

    def getTrackFiles(self):
        print(self.db.timeStr+':\tCollecting Track files...')
        self.dir = cwd = os.getcwd()
        self.trackdir = self.dir + r"\track"

        self.trackList = []

        # get list of trackfiles
        os.chdir(self.trackdir)
        for file in glob.glob("*.csv"):
            self.trackList.append(file)
            # print(self.db.timeStr+':\t- ' + str(file))
        os.chdir(self.dir)
