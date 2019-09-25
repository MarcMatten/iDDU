import irsdk
from libs import iDDUhelper
import csv
import math
import numpy as np
import os
import glob
import time
from datetime import datetime

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

        self.DRSList = ['formularenault35', 'mclarenmp430']
        self.P2PList = ['dallaradw12', 'dallarair18']

    def calc(self):
        # Check if DDU is initialised
        if self.db.BDDUexecuting == False:
            # initialise
            if not self.db.BWaiting:
                print(self.db.timeStr+': Waiting for iRacing')
                self.db.BWaiting = True

        # Check if iRacing Service is running
        if self.db.startUp:
            # iRacing is running
            if self.db.BDDUexecuting == False:
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
                    self.db.JokerLapsRequired = self.db.WeekendInfo['WeekendOptions']['NumJokerLaps']
                    NumDrivers = len(self.db.DriverInfo['Drivers'])
                    if self.db.SessionInfo['Sessions'][self.db.SessionNum]['ResultsPositions'] is not None:
                        NumResults = len(self.db.SessionInfo['Sessions'][self.db.SessionNum]['ResultsPositions'])
                    else:
                        NumResults = 0
                    self.db.JokerLaps = [0] * NumDrivers
                    self.db.textColorJoker = self.db.textColour
                    for n in range(0, NumResults):
                        self.db.JokerLaps[self.db.SessionInfo['Sessions'][self.db.SessionNum]['ResultsPositions'][n]['CarIdx']] = self.db.SessionInfo['Sessions'][self.db.SessionNum]['ResultsPositions'][n]['JokerLapsComplete']

                    if not self.db.JokerLapsRequired == 0:
                        self.db.JokerStr = str(self.db.JokerLaps[self.db.DriverCarIdx]) + '/' + str(self.db.JokerLapsRequired)
                    else:
                        self.db.JokerStr = str(self.db.JokerLaps[self.db.DriverCarIdx])

                    if self.db.JokerLaps[self.db.JokerLaps[self.db.DriverCarIdx]] < self.db.JokerLapsRequired:
                        if self.db.LapsToGo == self.db.JokerLapsRequired + 1:
                            self.db.Alarm.extend([8])
                        elif self.db.LapsToGo <= self.db.JokerLapsRequired:
                            self.db.Alarm.extend([9])
                    else:
                        self.db.textColorJoker = self.green

                if self.db.init:  # do when getting into the car
                    print(self.db.timeStr+':\tGetting into car')
                    self.db.init = False
                    self.db.OutLap = True
                    self.db.LastFuelLevel = self.db.FuelLevel
                    self.db.FuelConsumption = []
                    self.db.RunStartTime = self.db.SessionTime
                    self.db.Run = self.db.Run + 1

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
                    now = datetime.now()
                    date_time = now.strftime("%Y-%m-%d_%H-%M-%S")

                    LapStr = date_time + '_Run_'"{:02d}".format(self.db.Run) + '_Lap_'"{:03d}".format(self.db.Lap)
                    f = open(LapStr, 'x')
                    f.write('self.db.Lap = ' + repr(self.db.Lap) + '\n')
                    f.write('self.db.FuelConsumption = ' + repr(self.db.FuelConsumption) + '\n')
                    f.write('self.db.TimeLimit = ' + repr(self.db.TimeLimit) + '\n')
                    f.write('self.db.SessionInfo = ' + repr(self.db.SessionInfo) + '\n')
                    f.write('self.db.SessionTime = ' + repr(self.db.SessionTime) + '\n')
                    f.write('self.db.SessionTimeRemain = ' + repr(self.db.SessionTimeRemain) + '\n')
                    f.write('self.db.DriverCarIdx = ' + repr(self.db.DriverCarIdx) + '\n')
                    f.write('self.db.CarIdxF2Time = ' + repr(self.db.CarIdxF2Time) + '\n')
                    f.write('self.db.LapLastLapTime = ' + repr(self.db.LapLastLapTime) + '\n')
                    f.write('self.db.PitStopsRequired = ' + repr(self.db.PitStopsRequired) + '\n')
                    f.write('self.db.CarIdxPitStops = ' + repr(self.db.CarIdxPitStops) + '\n')
                    f.write('self.db.SessionTime = ' + repr(self.db.SessionTime) + '\n')
                    f.write('self.db.SessionNum = ' + repr(self.db.SessionNum) + '\n')
                    f.write('self.db.ResultsPositions = ' + repr(self.db.SessionInfo['Sessions'][self.db.SessionNum]['ResultsPositions']) + '\n')
                    f.write('self.db.DriverInfo = ' + repr(self.db.DriverInfo) + '\n')
                    f.close()

                    # Race Lap Estimation
                    # if self.db.TimeLimit and self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionType'] == 'Race' and self.db.Lap > 2:
                    #     myLineCrossingTime = self.db.SessionTime - self.db.SessionTimeRemain
                    #     meBehind = self.db.CarIdxF2Time[self.db.DriverCarIdx]
                    #     LeaderLineCrossingTime = myLineCrossingTime - meBehind
                    #     self.db.LapTimes.extend(self.db.LapLastLapTime)
                    #     avgLapTime = iDDUhelper.smartAverageMax(self.db.LapTimes, 0.03)
                    #
                    #     estLapsToGo = (self.db.SessionTimeRemain - self.db.PitStopDelta*max(0,self.db.PitStopsRequired-self.db.CarIdxPitStops[self.db.DriverCarIdx]))/avgLapTime
                    #
                    #     for i in range(int(estLapsToGo)-2, int(estLapsToGo)+3):
                    #         finishTime = myLineCrossingTime + self.db.PitStopDelta*max(0,self.db.PitStopsRequired-self.db.CarIdxPitStops[self.db.DriverCarIdx]) + avgLapTime * i
                    #         finishLap = i
                    #         if finishTime >= self.db.SessionTime:
                    #             break
                    #
                    #     CarIdxBehind = [0] * 64
                    #     CarIdxAvgLapTime = [0] * 64
                    #     CarIdxEstLapsToGo = [0] * 64
                    #     for i in range(0, len(self.db.SessionInfo['Sessions'][self.db.SessionNum]['ResultsPositions'])):
                    #         Idx = self.db.SessionInfo['Sessions'][self.db.SessionNum]['ResultsPositions'][i]['CarIdx']
                    #         self.db.CarIdxLapTimes[Idx].extend = self.db.SessionInfo['Sessions'][self.db.SessionNum]['ResultsPositions'][i]['LastTime']
                    #         CarIdxBehind[Idx] = self.db.SessionInfo['Sessions'][self.db.SessionNum]['ResultsPositions'][i]['Time']
                    #         CarIdxAvgLapTime[Idx] = iDDUhelper.smartAverageMax(self.db.CarIdxLapTimes[Idx], 0.03)
                    #
                    #         CarIdxEstLapsToGo = (self.db.SessionTime - LeaderLineCrossingTime + CarIdxBehind[Idx] - self.db.PitStopDeltaFastetClass * max(0, self.db.PitStopsRequired -self.db.CarIdxPitStops[Idx])) / CarIdxAvgLapTime[Idx]
                    #
                    #         finishTimes = [] * 64
                    #         for i in range(int(estLapsToGo) - 2, int(estLapsToGo) + 3):
                    #             temp = myLineCrossingTime + self.db.PitStopDelta * max(0, self.db.PitStopsRequired - self.db.CarIdxPitStops[self.db.DriverCarIdx]) + avgLapTime * i
                    #             finishTimes.extend([(i, temp)])
                    #
                    #     find minimum of all finish time but for maximum lap number
                    #     where am i relative to it?
                    #     that's the time i'm lokking for!

                else:
                    newLap = False

                if self.createTrack and not self.db.OutLap and self.db.StintLap > 1:

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

                # DRS
                if self.db.DRS:
                    if self.db.DRSCounter >= self.db.DRSActivations and self.db.DRSActivations > 0:
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
                        self.db.Alarm.extend([6])
                    
                    if self.db.DRS_Status == 2:
                        self.db.Alarm.extend([7])

                    self.db.old_DRS_Status = self.db.DRS_Status

                # P2P
                if self.db.P2P:
                    if self.db.P2PCounter >= self.db.P2PActivations and self.db.P2PActivations > 0:
                        self.db.textColourP2P = self.red
                    elif (self.db.P2PCounter + 1) == self.db.P2PActivations:
                        self.db.textColourP2P = self.orange
                    else:
                        self.db.textColourP2P = self.db.textColour
                    if not self.db.PushToPass == self.db.old_PushToPass:
                        if self.db.PushToPass == True:
                            self.db.P2PTime = self.db.SessionTime
                            self.db.Alarm.extend([5])
                            self.db.P2PCounter = self.db.P2PCounter + 1
                    
                    if self.db.SessionTime < self.db.P2PTime + 3:
                        self.db.Alarm.extend([5])
                    
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

                r = np.interp(Dv, [-10, -5, -1, 1, 15, 30, 40],
                                 [self.black[0], self.black[0], self.green[0], self.green[0], self.yellow[0], self.orange[0], self.red[0]])
                g = np.interp(Dv, [-10, -5, -1, 1, 15, 30, 40],
                                 [self.black[1], self.black[1], self.green[1], self.green[1], self.yellow[1], self.orange[1], self.red[1]])
                b = np.interp(Dv, [-10, -5, -1, 1, 15, 30, 40],
                                 [self.black[2], self.black[2], self.green[2], self.green[2], self.yellow[2], self.orange[2], self.red[2]])
                self.db.backgroundColour = (r, g, b)
                self.db.textColour = self.grey
            else:
                if not (self.db.SessionFlags == self.db.oldSessionFlags):
                    self.FlagCallTime = self.db.SessionTime
                    self.db.FlagExceptionVal = 0
                    if self.db.SessionFlags & 0x8000000: # startGo
                        self.db.backgroundColour = self.green
                        self.db.GreenTime = self.db.SessionTimeRemain
                        self.db.CarIdxPitStops = [0] * 64
                    if self.db.SessionFlags & 0x2: # white
                        self.db.backgroundColour = self.white
                        self.db.textColour = self.black
                    if self.db.SessionFlags & 0x20: # blue
                        self.db.backgroundColour = self.blue
                    if self.db.SessionFlags & 0x1: # checkered
                        self.db.textColour = self.grey
                        self.db.FlagExceptionVal = 1
                        self.db.FlagException = True
                    if self.db.SessionFlags & 0x100000: # repair
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
                    if self.db.SessionFlags & 0x8 or self.db.SessionFlags & 0x100: # yellow
                        self.db.backgroundColour = self.yellow
                        self.db.textColour = self.black
                    if self.db.SessionFlags & 0x4000 or self.db.SessionFlags & 0x8000:  # SC
                        self.db.FlagException = True
                        self.db.backgroundColour = self.yellow
                        self.db.textColour = self.black
                        self.db.FlagExceptionVal = 3
                    if self.db.SessionFlags & 0x10: # red
                        self.db.backgroundColour = self.red

                    self.db.oldSessionFlags = self.db.SessionFlags

                elif self.db.SessionTime > (self.FlagCallTime + 3):
                    self.db.backgroundColour = self.black
                    self.db.textColour = self.grey
                    self.db.FlagException = False
                    self.db.FlagExceptionVal = 0

            # change in driver controls
            if self.db.SessionTime > self.db.RunStartTime + 1:
                if not self.db.dcBrakeBias == self.db.dcBrakeBiasOld:
                    self.db.dcBrakeBiasChange = True
                    self.db.dcChangeTime = self.db.SessionTime
                if not self.db.dcABS == self.db.dcABSOld:
                    self.db.dcABSChange = True
                    self.db.dcChangeTime = self.db.SessionTime
                if not self.db.dcTractionControlToggle == self.db.dcTractionControlToggleOld:
                    self.db.dcTractionControlToggleChange = True
                    self.db.dcChangeTime = self.db.SessionTime
                if not self.db.dcTractionControl == self.db.dcTractionControlOld:
                    self.db.dcTractionControlChange = True
                    self.db.dcChangeTime = self.db.SessionTime
                if not self.db.dcTractionControl2 == self.db.dcTractionControl2Old:
                    self.db.dcTractionControl2Change = True
                    self.db.dcChangeTime = self.db.SessionTime
                if not self.db.dcThrottleShape == self.db.dcThrottleShapeOld:
                    self.db.dcThrottleShapeChange = True
                    self.db.dcChangeTime = self.db.SessionTime
                if not self.db.dcFuelMixture == self.db.dcFuelMixtureOld:
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

            self.db.BDDUexecuting = True
        else:
            # iRacing is not running
            if self.db.BDDUexecuting == True: # necssary?
                self.db.BDDUexecuting = False
                self.db.BWaiting = True
                self.db.oldSessionNum = -1
                self.db.SessionNum = 0
                self.db.StopDDU = True
                # self.reinit()
                print(self.db.timeStr+': Lost connection to iRacing')
                print(self.db.timeStr+': Last Lap Fuel Consumption: ', self.db.FuelLastConsStr)
                print(self.db.timeStr+': Average Fuel Consumption: ', self.db.FuelConsStr)

    def reinit(self):
        print(self.db.timeStr+': Starting RTDB reinitialisation.')
        self.db.reinitialise()
        # helpData = {'done': False, 'timeStr': 0, 'BWaiting': False, 'LabelSessionDisplay': [1, 1, 1, 0, 1, 1]}
        # # data from iRacing
        # iRData = {'LapBestLapTime': 0,
        #           'LapLastLapTime': 0,
        #           'LapDeltaToSessionBestLap': 0,
        #           'dcFuelMixture': 0,
        #           'dcThrottleShape': 0,
        #           'dcTractionControl': 0,
        #           'dcTractionControl2': 0,
        #           'dcTractionControlToggle': 0,
        #           'dcABS': 0,
        #           'dcBrakeBias': 0,
        #           'FuelLevel': 0,
        #           'Lap': 0,
        #           'IsInGarage': 0,
        #           'LapDistPct': 0,
        #           'OnPitRoad': 0,
        #           'PlayerCarClassPosition': 0,
        #           'PlayerCarPosition': 0,
        #           'SessionLapsRemain': 0,
        #           'Throttle': 0,
        #           'SessionTimeRemain': 0,
        #           'SessionTime': 0,
        #           'SessionFlags': 0,
        #           'SessionNum': 0,
        #           'IsOnTrack': False,
        #           'Gear': 0,
        #           'Speed': 0,
        #           'DriverInfo': {
        #               'DriverCarIdx': 0,
        #               'DriverCarFuelMaxLtr': 0,
        #               'DriverCarMaxFuelPct': 1,
        #               'Drivers': [],
        #               'DriverPitTrkPct': 0},
        #           'CarIdxLapDistPct': [0],
        #           'CarIdxOnPitRoad': [True]*64,
        #           'SessionInfo': {'Sessions':
        #                               [{'SessionType': 'Session',
        #                                 'SessionTime': 'unlimited',
        #                                 'SessionLaps': 0,
        #                                 'ResultsPositions':
        #                                     [{'CarIdx': 0,
        #                                       'JokerLapsComplete': 0}]}]},
        #           'Yaw': 0,
        #           'VelocityX': 0,
        #           'VelocityY': 0,
        #           'YawNorth': 0,
        #           'WeekendInfo': [],
        #           'RPM': 0,
        #           'LapCurrentLapTime': 0,
        #           'EngineWarnings': 0,
        #           'CarIdxTrackSurface': 0,
        #           'CarLeftRight': 0,
        #           'DRS_Status': 0,
        #           'PushToPass': False,
        #           'CarIdxF2Time': [],
        #           'LapLastLapTime': 0}
        # # calculated data
        # calcData = {'LastFuelLevel': 0,
        #             'GearStr': '-',
        #             'SessionInfoAvailable': False,
        #             'SessionNum': 0,
        #             'init': True,
        #             'onPitRoad': True,
        #             'BDDUexecuting': False,
        #             'WasOnTrack': False,
        #             'StintLap': 0,
        #             'oldSessionNum': -1,
        #             'oldLap': 0.1,
        #             'FuelConsumption': [],
        #             'FuelLastCons': 0,
        #             'OutLap': True,
        #             'oldSessionlags': 0,
        #             'LapsToGo': 27,
        #             'SessionLapRemain': 0,
        #             'FuelConsumptionStr': '0.00',
        #             'RemLapValueStr': '10',
        #             'FuelLapStr': '0',
        #             'FuelAddStr': '0.0',
        #             'ToGoStr': '100',
        #             'FlagCallTime': 0,
        #             'FlagException': False,
        #             'FlagExceptionVal': 0,
        #             'Alarm': [],
        #             'oldFuelAdd': 1,
        #             'GreenTime': 0,
        #             'RemTimeValue': 0,
        #             'RaceLaps': 100000,
        #             'JokerStr': '-/-',
        #             'dist': [],
        #             'x': [],
        #             'y': [],
        #             'map': [],
        #             'RX': False,
        #             'createTrack': True,
        #             'dx': [],
        #             'dy': [],
        #             'logLap': 0,
        #             'Logging': False,
        #             'tempdist': -1,
        #             'StartUp': False,
        #             'oldSessionFlags': 0,
        #             'backgroundColour': (0, 0, 0),
        #             'textColourFuelAdd': (141, 141, 141),
        #             'textColour': (141, 141, 141),
        #             'FuelLaps': 1,
        #             'FuelAdd': 1,
        #             'PitStopDelta': 61,
        #             'time': [],
        #             'Run': 0,
        #             'UpshiftStrategy': 0,
        #             'UserShiftRPM': [100000, 100000, 100000, 100000, 100000, 100000, 100000],
        #             'UserShiftFlag': [1, 1, 1, 1, 1, 1, 1],
        #             'iRShiftRPM': [100000, 100000, 100000, 100000],
        #             'ShiftToneEnabled': True,
        #             'StartDDU': False,
        #             'StopDDU': False,
        #             'DDUrunning': False,
        #             'UserRaceLaps': 0,
        #             'SessionLength': 86400,
        #             'CarIdxPitStops': [0] * 64,
        #             'CarIdxOnPitRoadOld': [True]*64,
        #             'PitStopsRequired': 1,
        #             'old_DRS_Status': 0,
        #             'DRSActivations': 8,
        #             'P2PActivations': 12,
        #             'DRSActivationsGUI': 8,
        #             'P2PActivationsGUI': 12,
        #             'JokerLapDelta': 2,
        #             'JokerLaps': 1,
        #             'MapHighlight': True,
        #             'old_PushToPass': False,
        #             'textColourDRS': (141, 141, 141),
        #             'textColourP2P': (141, 141, 141),
        #             'textColorJoker': (141, 141, 141),
        #             'DRSCounter': 0,
        #             'P2PCounter': 0,
        #             'RenderLabel': [
        #                 True,   # Best
        #                 True,   # Last
        #                 True,   # Delta
        #                 True,   # FuelLevel
        #                 True,   # FuelCons
        #                 True,   # FuelLastCons
        #                 True,   # FuelLaps
        #                 True,   # FuelAdd
        #                 True,   # ABS
        #                 True,   # BBias
        #                 True,   # Mix
        #                 True,   # TC1
        #                 True,   # TC2
        #                 True,   # Lap
        #                 True,   # Clock
        #                 True,   # Remain
        #                 False,  # Elapsed
        #                 False,  # Joker
        #                 False,  # DRS
        #                 False,  # P2P
        #                 True,  # ToGo
        #             ],
        #             'P2P': False,
        #             'DRS': False,
        #             'LapLimit': False,
        #             'TimeLimit': False,
        #             'P2PTime': 0,
        #             'DRSRemaining': 0,
        #             'dcFuelMixtureOld': 0,
        #             'dcThrottleShapeOld': 0,
        #             'dcTractionControlOld': 0,
        #             'dcTractionControl2Old': 0,
        #             'dcTractionControlToggleOld': 0,
        #             'dcABSOld': 0,
        #             'dcBrakeBiasOld': 0,
        #             'RunStartTime': 0,
        #             'changeLabelsOn': True,
        #             'dcChangeTime': 0,
        #             'dcFuelMixtureChange': False,
        #             'dcThrottleShapeChange': False,
        #             'dcTractionControlChange': False,
        #             'dcTractionControl2Change': False,
        #             'dcTractionControlToggleChange': False,
        #             'dcABSChange': False,
        #             'dcBrakeBiasChange': False,
        #             'BUpshiftToneInitRequest': False
        #             }
        #
        # self.db.StopDDU = True
        # self.db.initialise(helpData)
        # self.db.initialise(iRData)
        # self.db.initialise(calcData)
        # # print(self.db.timeStr+': RTDB reinitialisied')
        # self.db.timeStr = time.strftime("%H:%M:%S", time.localtime())
        # self.db.StartDDU = True
        print(self.db.timeStr + ':RTDB reinitialisied')

    def initSession(self):
        print(self.db.timeStr+': Initialising Session ==========================')

        # self.reinit()

        self.getTrackFiles()

        self.db.BUpshiftToneInitRequest = True

        if self.db.startUp:
            self.db.StartDDU = True
            self.db.oldSessionNum = self.db.SessionNum
            self.SessionInfo = True
            #self.db.WeekendInfo = self.db.WeekendInfo
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
                self.db.RenderLabel[17] = True
                print(self.db.timeStr+':\tDirt Racing')
            else:
                self.db.__setattr__('RX', False)
                self.db.RenderLabel[17] = False
                print(self.db.timeStr+':\tRoad Racing')

            # unlimited laps
            if self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionLaps'] == 'unlimited':
                self.db.RaceLaps = self.db.UserRaceLaps
                self.db.LapLimit = False
                self.db.RenderLabel[20] = False
                print(self.db.timeStr + ':\t' + self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionLaps'] + ' laps')
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
                    print(self.db.timeStr + ':\t' + self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionTime'] + ' time')
                    print(self.db.timeStr + ':\tRace mode 0')
                # limited time
                else:
                    self.db.RenderLabel[15] = True
                    self.db.RenderLabel[16] = False
                    self.db.TimeLimit = True
                    tempSessionLength = self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionTime']
                    self.db.SessionLength = float(tempSessionLength.split(' ')[0])
                    print(self.db.timeStr + ':\tRace mode 1')
                    print(self.db.timeStr + ':\tSession length :' + self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionTime'])
            else:
                self.db.RaceLaps = int(self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionLaps'])
                self.db.LapLimit = True
                self.db.RenderLabel[20] = True
                # unlimited time
                if self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionTime'] == 'unlimited':
                    self.db.SessionLength = 86400
                    self.db.TimeLimit = False
                    self.db.RenderLabel[15] = False
                    self.db.RenderLabel[16] = True
                    print(self.db.timeStr + ':\tRace mode 4')
                    print(self.db.timeStr + ':\t' + self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionTime'] + ' time')
                # limited time
                else:
                    #tempSessionLength = self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionTime']
                    #self.db.SessionLength = float(tempSessionLength.split(' ')[0])
                    #SpeedLimit = (self.db.WeekendInfo['TrackLength']*1000*self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionLaps']/self.db.SessionLength)
                    #print(SpeedLimit)
##                    if SpeedLimit < 33:
##                        self.db.RaceLaps = int(self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionLaps'])
##                        self.db.LapLimit = True
##                        tempSessionLength = self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionTime']
##                        self.db.SessionLength = float(tempSessionLength.split(' ')[0])
##                        self.db.RenderLabel[15] = False
##                        self.db.RenderLabel[16] = True
##                        self.db.TimeLimit = True
##                        print(self.db.timeStr + ':\tRace mode 3')
##                        printnt(self.db.timeStr + ':\tSession length :' + self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionTime'])
##                    else:
                    self.db.RenderLabel[15] = True
                    self.db.RenderLabel[16] = False
                    self.db.TimeLimit = True
                        # if self.db.SessionLength > (800*self.db.RaceLaps):
                        #     self.db.TimeLimit = False
                        # else:
                        #     self.db.TimeLimit = False
                    print(self.db.timeStr + ':\tRace mode 5')
                    print(self.db.timeStr + ':\tSession length :' + self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionTime'])

            print(self.db.timeStr + ':\tRaceLaps: ' + str(self.db.RaceLaps))
            print(self.db.timeStr + ':\tSessionLength: ' + str(self.db.SessionLength))

            # DRS
            if self.db.DriverInfo['Drivers'][self.db.DriverCarIdx]['CarPath'] in self.DRSList:
                self.db.DRS = True
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
                self.db.RenderLabel[19] = True
                self.db.P2PCounter = 0
                if not self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionType'] == 'Race':
                    self.db.P2PActivations = 1000
                else:
                    self.db.P2PActivations = self.db.P2PActivationsGUI
            else:
                self.db.P2P = False
                self.db.RenderLabel[19] = False
        
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

    def newLap(self):
        return 0