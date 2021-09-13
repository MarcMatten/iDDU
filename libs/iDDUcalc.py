import sys
import os
import time
from datetime import datetime
import numpy as np

from functionalities.libs import maths, convertString, importExport
from libs import Track, Car
from libs.IDDU import IDDUThread

nan = float('nan')  # TODO: add to IDDu object?

# TODO: add more comments
# TODO: try to spread into more nested functions, i.e. approachingPits, inPitStall, exitingPits, ...


class IDDUCalcThread(IDDUThread):
    BError = False
    SError = ''
    Brake = 0
    PitStates = None
    PitStatesOld = None

    def __init__(self, rate):
        IDDUThread.__init__(self, rate)

        self.FlagCallTime = 0
        self.init = False

        self.Yaw = []
        self.YawNorth = []
        self.VelocityX = []
        self.VelocityY = []
        self.LapDistPct = np.array([])
        self.time = np.array([])
        self.dx = np.array(0)
        self.dy = np.array(0)
        self.dt = []
        self.Logging = False
        self.logLap = 0
        self.timeLogingStart = 0
        self.BCreateTrack = False
        self.BRecordtLap = False

        self.DRSList = ['formularenault35', 'mclarenmp430']  # TODO: still required?
        self.P2PList = ['dallaradw12', 'dallarair18']  # TODO: still required?

        self.dir = os.getcwd()
        self.trackList = importExport.getFiles(self.dir + '/data/track', 'json')
        self.carList = importExport.getFiles(self.dir + '/data/car', 'json')

        self.x = None
        self.y = None
        self.snapshot = False

        self.logger.info('Started iDDUcalc')

    def run(self):
        while 1:
            try:
                t = time.perf_counter()
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

                    if self.db.oldSessionNum < self.db.SessionNum or not self.db.WeekendInfo['SubSessionID'] == self.db.SubSessionIDOld:
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

                    if self.db.PlayerTrackSurface == 3:  # on track
                        self.db.BEnteringPits = False
                    elif self.db.PlayerTrackSurfaceOld == 3 and not self.db.BEnteringPits and self.db.PlayerTrackSurface == 2:  # entering pit entry event
                        self.db.BEnteringPits = True

                    self.db.PlayerTrackSurfaceOld = self.db.PlayerTrackSurface

                    if self.db.OnPitRoad and self.db.BEnteringPits and not self.db.PlayerCarPitSvStatus == 2:  # from pit entry end of pit stop
                        self.db.NDDUPage = 3

                    if self.db.OnPitRoad or self.db.BEnteringPits:  # do when in pit entry or in pit lane but not on track
                        pitSpeedLimit = self.db.WeekendInfo['TrackPitSpeedLimit']
                        deltaSpeed = [self.db.Speed * 3.6 - float(pitSpeedLimit.split(' ')[0])]

                        r = np.interp(deltaSpeed, [-10, -5, -2, -1, 0, 2, 5, 20, 40],
                                      [self.black[0], self.black[0], self.blue[0], self.cyan[0], self.green[0], self.green[0], self.yellow[0], self.orange[0], self.red[0]])
                        g = np.interp(deltaSpeed, [-10, -5, -2, -1, 0, 2, 5, 20, 40],
                                      [self.black[1], self.black[1], self.blue[1], self.cyan[1], self.green[1], self.green[1], self.yellow[1], self.orange[1], self.red[1]])
                        b = np.interp(deltaSpeed, [-10, -5, -2, -1, 0, 2, 5, 20, 40],
                                      [self.black[2], self.black[2], self.blue[2], self.cyan[2], self.green[2], self.green[2], self.yellow[2], self.orange[2], self.red[2]])

                        self.db.backgroundColour = tuple([r, g, b])
                        self.db.textColour = self.white
                        self.distance2PitStall()

                        if not self.db.PitstopActive:  # during pitstop
                            if self.db.PitSvFlags & 0x01:
                                self.db.BTyreChangeRequest[0] = True
                            else:
                                self.db.BTyreChangeRequest[0] = False
                            if self.db.PitSvFlags & 0x02:
                                self.db.BTyreChangeRequest[1] = True
                            else:
                                self.db.BTyreChangeRequest[1] = False
                            if self.db.PitSvFlags & 0x04:
                                self.db.BTyreChangeRequest[2] = True
                            else:
                                self.db.BTyreChangeRequest[2] = False
                            if self.db.PitSvFlags & 0x08:
                                self.db.BTyreChangeRequest[3] = True
                            else:
                                self.db.BTyreChangeRequest[3] = False

                            if self.db.PitSvFlags & 0x10:
                                self.db.BFuelRequest = True
                            else:
                                self.db.BFuelRequest = False

                    else:  # do when on track but not when in pits

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

                        elif self.db.SessionTime > (self.FlagCallTime + 3):
                            self.db.backgroundColour = self.black

                            if len(self.db.NLappingCars) > 0 and (self.db.PlayerTrackSurface == 1 or self.db.PlayerTrackSurface == 3) and self.db.IsOnTrack:
                                self.db.backgroundColour = self.blue

                            self.db.textColour = self.white
                            self.db.FlagException = False
                            self.db.FlagExceptionVal = 0

                    self.db.oldSessionFlags = self.db.SessionFlags

                    if self.db.IsOnTrack:
                        # do if car is on track #############################################################################################
                        if not self.db.WasOnTrack:
                            self.db.WasOnTrack = True
                            self.db.StintLap = 0
                            print(self.db.timeStr + ':\tIsOnTrack')

                        self.db.Alarm = [0] * 10

                        # my blue flag
                        if self.db.WeekendInfo['NumCarClasses'] > 1:
                            if self.db.LapDistPct < 0.1:
                                CarIdxLapDistPct = np.array(self.db.CarIdxLapDistPct)
                                CarIdxLapDistPct[(CarIdxLapDistPct > 0) & (CarIdxLapDistPct < 0.1)] = CarIdxLapDistPct[(CarIdxLapDistPct > 0) & (CarIdxLapDistPct < 0.1)] + 1
                                CarIdxDistDiff = (CarIdxLapDistPct - (self.db.LapDistPct + 1)) * self.db.track.sTrack
                            else:
                                CarIdxDistDiff = (np.array(self.db.CarIdxLapDistPct) - self.db.LapDistPct) * self.db.track.sTrack

                            BCarIdxInLappingRange = (-100 <= CarIdxDistDiff) & (CarIdxDistDiff < 0)

                            k = [i for i, x in enumerate(BCarIdxInLappingRange.tolist()) if x]

                            CarClassList = []
                            NLappingCars = []

                            for j in range(0, len(k)):
                                if self.db.CarIdxMap[k[j]] is None:
                                    continue
                                else:
                                    if self.db.DriverInfo['Drivers'][self.db.CarIdxMap[k[j]]]['CarClassRelSpeed'] > self.db.PlayerCarClassRelSpeed and self.db.CarIdxTrackSurface[k[j]] == 3:
                                        name = self.db.DriverInfo['Drivers'][self.db.CarIdxMap[k[j]]]['CarClassShortName'].split(' ')[0]
                                        if name in CarClassList:
                                            NLappingCars[CarClassList.index(name)]['NCars'] += 1
                                            NLappingCars[CarClassList.index(name)]['sDiff'] = max(NLappingCars[CarClassList.index(name)]['sDiff'], CarIdxDistDiff[k[j]])
                                        else:
                                            NLappingCars.append({'Class': name, 'NCars': 1, 'Color': self.bit2RBG(self.db.DriverInfo['Drivers'][self.db.CarIdxMap[k[j]]]['CarClassColor']),
                                                                 'sDiff': CarIdxDistDiff[k[j]]})
                                            CarClassList.append(name)

                            self.db.NLappingCars = sorted(NLappingCars, key=lambda x: x['sDiff'], reverse=True)

                        else:
                            self.db.NLappingCars = []

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
                                self.db.JokerLaps[self.db.SessionInfo['Sessions'][self.db.SessionNum]['ResultsPositions'][n]['CarIdx']] = \
                                    self.db.SessionInfo['Sessions'][self.db.SessionNum]['ResultsPositions'][n]['JokerLapsComplete']

                            if not self.db.JokerLapsRequired == 0:
                                self.db.JokerStr = str(self.db.JokerLaps[self.db.DriverCarIdx]) + '/' + str(self.db.JokerLapsRequired)
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
                            self.db.BMultiInitRequest = True
                            self.db.LastFuelLevel = self.db.FuelLevel
                            self.db.FuelConsumptionList = []
                            self.db.RunStartTime = self.db.SessionTime
                            self.db.Run = self.db.Run + 1
                            if self.db.config['BPitCommandControl']:
                                self.ir.pit_command(0)

                            if self.db.FuelTGTLiftPoints['SFuelConfigCarName'] == self.db.DriverInfo['Drivers'][self.db.DriverCarIdx]['CarScreenNameShort'] \
                                    and self.db.FuelTGTLiftPoints['SFuelConfigTrackName'] == self.db.WeekendInfo['TrackName']:
                                self.db.BFuelSavingConfigLoaded = True
                            else:
                                self.db.BFuelSavingConfigLoaded = False
                                print(self.db.timeStr +
                                      ':\tFuel Saving config loaded ({}, {}) does not match current session ({}, {})'.format(self.db.FuelTGTLiftPoints['SFuelConfigCarName'],
                                                                                                                             self.db.FuelTGTLiftPoints['SFuelConfigTrackName'],
                                                                                                                             self.db.DriverInfo['Drivers'][self.db.DriverCarIdx]['CarScreenNameShort'],
                                                                                                                             self.db.WeekendInfo['TrackDisplayShortName']))
                            if 'dcABS' in self.db.car.dcList:
                                pBrakeLFMax = self.db.LFbrakeLinePress / (self.db.dcBrakeBias / 100) / self.db.Brake
                                pBrakeRFMax = self.db.RFbrakeLinePress / (self.db.dcBrakeBias / 100) / self.db.Brake
                                pBrakeLRMax = self.db.LRbrakeLinePress / (1 - self.db.dcBrakeBias / 100) / self.db.Brake
                                pBrakeRRMax = self.db.RRbrakeLinePress / (1 - self.db.dcBrakeBias / 100) / self.db.Brake

                                self.db.car.setpBrakeMax((pBrakeLFMax + pBrakeRFMax)/2, (pBrakeLRMax+pBrakeRRMax)/2)
                                self.db.car.save(self.db.dir)
                                self.db.car.MotecXMLexport(rootPath=self.dir, MotecPath=self.db.config['MotecProjectPath'])

                        if self.db.OnPitRoad:  # do when on pit road
                            self.db.BWasOnPitRoad = True
                            self.db.BEnteringPits = False
                            if self.db.PitstopActive:  # during pitstop
                                if not self.db.BPitstop:  # pit stop start event
                                    self.db.PitSvFlagsEntry = self.db.PitSvFlags
                                    self.db.VFuelPitStopStart = self.db.FuelLevel
                                    self.db.BPitstop = True
                                self.pitStop()
                                if (not self.db.BPitstopCompleted) and self.db.PlayerCarPitSvStatus == 2:  # pit stop completed event
                                    self.db.BPitstopCompleted = True
                                    self.db.NDDUPage = 2

                        elif (not self.db.OnPitRoad) and self.db.BWasOnPitRoad:  # pit exit event
                            self.db.OutLap = True
                            self.db.FuelConsumptionList = []
                            # self.db.FuelAvgConsumption = 0
                            self.db.sToPitStall = 0
                            self.db.PitSvFlagsEntry = 0
                            self.db.NDDUPage = 1
                            self.db.BPitstop = False
                            self.db.BFuelRequest = False
                            self.db.BFuelCompleted = False
                            self.db.BPitstopCompleted = False
                            self.db.BTyreChangeRequest = [False, False, False, False]
                            self.db.BTyreChangeCompleted = [False, False, False, False]
                            self.db.BWasOnPitRoad = False
                            self.db.BPitCommandUpdate = True

                        # check if new lap
                        if self.db.Lap > self.db.oldLap and self.db.SessionState == 4 and self.db.SessionTime > self.db.newLapTime + 10:
                            self.db.BNewLap = True
                            self.newLap()
                        else:
                            self.db.BNewLap = False

                        # Create Track Map
                        if (self.BCreateTrack or self.BRecordtLap) and not self.db.OutLap and self.db.StintLap > 0:

                            if len(self.time) > 0:
                                if not self.time[-1] == self.db.SessionTime:
                                    self.Yaw.append(self.db.Yaw)
                                    self.YawNorth.append(self.db.YawNorth)
                                    self.VelocityX.append(self.db.VelocityX)
                                    self.VelocityY.append(self.db.VelocityY)
                                    self.LapDistPct = np.append(self.LapDistPct, self.db.LapDistPct * 100)
                                    self.time = np.append(self.time, self.db.SessionTime)
                            else:
                                self.Yaw.append(self.db.Yaw)
                                self.YawNorth.append(self.db.YawNorth)
                                self.VelocityX.append(self.db.VelocityX)
                                self.VelocityY.append(self.db.VelocityY)
                                self.LapDistPct = np.append(self.LapDistPct, self.db.LapDistPct * 100)
                                self.time = np.append(self.time, self.db.SessionTime)

                        # fuel consumption -----------------------------------------------------------------------------------------
                        if not self.db.config['NFuelTargetMethod']:
                            self.db.RenderLabel[4] = True
                            self.db.RenderLabel[5] = True
                            self.db.RenderLabel[28] = False
                            self.db.RenderLabel[29] = False

                        if len(self.db.FuelConsumptionList) >= 1:
                            if self.db.config['NFuelConsumptionMethod'] == 0:
                                self.db.FuelAvgConsumption = maths.meanTol(self.db.FuelConsumptionList, 0.2)
                            elif self.db.config['NFuelConsumptionMethod'] == 1:
                                self.db.FuelAvgConsumption = np.mean(self.db.FuelConsumptionList[-3:])
                            elif self.db.config['NFuelConsumptionMethod'] == 2 and self.db.WeekendInfo['TrackName'] in self.db.car.VFuelLap:
                                self.db.FuelAvgConsumption = self.db.car.VFuelLap[self.db.WeekendInfo['TrackName']]

                            self.db.NLapRemaining = self.db.FuelLevel / self.db.FuelAvgConsumption
                            if self.db.NLapRemaining < 3:
                                self.db.Alarm[3] = 2
                            if self.db.NLapRemaining < 1:
                                self.db.Alarm[3] = 3
                            if self.db.BNewLap and not self.db.OnPitRoad:
                                fuelNeed = self.db.FuelAvgConsumption * (self.db.LapsToGo - 1 + 0.1)
                                self.db.VFuelAdd = min(max(fuelNeed - self.db.FuelLevel + self.db.FuelAvgConsumption, 0),
                                                       self.db.DriverInfo['DriverCarFuelMaxLtr'] * self.db.DriverInfo['DriverCarMaxFuelPct'])
                                if self.db.VFuelAdd == 0:
                                    # self.ir.pit_command(2, 1) # Add fuel, optionally specify the amount to add in liters or pass '0' to use existing amount
                                    # self.ir.pit_command(11) # Uncheck add fuel
                                    self.db.BTextColourFuelAddOverride = False
                                else:
                                    if not round(self.db.VFuelAdd) == round(self.db.VFuelAddOld):
                                        if self.db.config['NFuelSetMethod'] == 1 and self.db.config['BBeginFueling'] and self.db.config['BPitCommandControl']:
                                            self.ir.pit_command(2, round(self.db.VFuelAdd + 1 + 1e-10))  # Add fuel
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
                            # self.db.FuelAvgConsumption = 0
                            # self.db.NLapRemaining = 0
                            self.db.VFuelAdd = 0
                            if self.db.FuelAvgConsumption > 0:
                                self.db.NLapRemaining = self.db.FuelLevel / self.db.FuelAvgConsumption

                        self.db.VFuelUsedLap = self.db.LastFuelLevel - self.db.FuelLevel

                        if self.db.BTextColourFuelAddOverride:
                            self.db.textColourFuelAdd = self.db.textColourFuelAddOverride
                        else:
                            self.db.textColourFuelAdd = self.db.textColour

                        # DRS
                        if self.db.DRS:
                            if self.db.DRSCounter >= self.db.config['DRSActivations'] > 0:
                                self.db.textColourDRS = self.red
                            else:
                                if not self.db.DRS_Status == self.db.old_DRS_Status:
                                    if self.db.DRS_Status == 2:
                                        self.db.DRSCounter = self.db.DRSCounter + 1
                                    else:
                                        self.db.textColourDRS = self.db.textColour
                                if self.db.DRS_Status == 1:
                                    self.db.textColourDRS = self.green

                            self.db.DRSRemaining = (self.db.config['DRSActivations'] - self.db.DRSCounter)
                            if self.db.DRSRemaining == 1 and not self.db.DRS_Status == 2:
                                self.db.Alarm[5] = 2
                            if self.db.DRS_Status == 2:
                                self.db.Alarm[5] = 1

                            self.db.old_DRS_Status = self.db.DRS_Status

                        # P2P
                        if self.db.P2P:
                            if self.db.P2PCounter >= self.db.config['P2PActivations'] > 0:
                                self.db.textColourP2P = self.red
                            elif (self.db.P2PCounter + 1) == self.db.config['P2PActivations']:
                                self.db.textColourP2P = self.orange
                            else:
                                self.db.textColourP2P = self.db.textColour
                            if not self.db.PushToPass == self.db.old_PushToPass:
                                if self.db.PushToPass:
                                    self.db.P2PTime = self.db.SessionTime
                                    self.db.Alarm[4] = 1
                                    self.db.P2PCounter = self.db.P2PCounter + 1

                            if self.db.SessionTime < self.db.P2PTime + 20:
                                self.db.Alarm[4] = 1

                            self.db.old_PushToPass = self.db.PushToPass

                        # alarm
                        if self.db.dcTractionControlToggle or self.db.dcTractionControl == self.db.car.NTC1Disabled:
                            self.db.Alarm[1] = 3
                        if self.db.dcTractionControlToggle or self.db.dcTractionControl2 == self.db.car.NTC2Disabled:
                            self.db.Alarm[9] = 3
                        if self.db.dcABSToggle or self.db.dcABS == self.db.car.NABSDisabled:
                            self.db.Alarm[8] = 3

                        # Lift beeps
                        if self.db.config['NFuelTargetMethod'] and self.db.BFuelSavingConfigLoaded and self.db.Speed > 10:
                            # get fuel data at reference point
                            if self.db.BUpdateVFuelDelta and self.db.LapDistPct * 100 >= self.db.FuelTGTLiftPoints['LapDistPctReference'][self.db.NNextLiftPoint]:
                                if self.db.NNextLiftPoint > 0:
                                    self.db.VFuelDelta = self.db.VFuelUsedLap - self.db.VFuelReference[self.db.NNextLiftPoint]  # positive = overconsumption
                                    self.db.VFuelStartStraight = self.db.FuelLevel
                                    self.db.BUpdateVFuelDelta = False
                                elif self.db.NNextLiftPoint == 0 and self.db.LapDistPct * 100 < self.db.FuelTGTLiftPoints['LapDistPctReference'][1]:
                                    self.db.VFuelDelta = self.db.VFuelUsedLap - self.db.VFuelReference[self.db.NNextLiftPoint]  # positive = overconsumption
                                    self.db.VFuelStartStraight = self.db.FuelLevel
                                    self.db.BUpdateVFuelDelta = False

                            VFuelDelta = np.round(self.db.VFuelDelta, 2)

                            if VFuelDelta > 0.0:
                                self.db.textColourDelta = self.red
                            elif VFuelDelta < 0.0:
                                self.db.textColourDelta = self.green
                            else:
                                self.db.textColourDelta = self.db.textColour

                            self.LiftTone()

                        if type(self.db.FuelLevel) is float:
                            if self.db.FuelLevel <= 5:
                                self.db.Alarm[2] = 3

                        if self.db.SessionTime > self.db.RunStartTime + 3:
                            if not self.db.dc == self.db.dcOld:
                                temp = {k: self.db.dc[k] for k in self.db.dc if k in self.db.dcOld and not self.db.dc[k] == self.db.dcOld[k]}
                                self.db.dcChangedItems = list(temp.keys())
                                self.db.dcChangeTime = time.time()
                                if 'VFuelTgt' in self.db.dcChangedItems or 'VFuelTgtOffset' in self.db.dcChangedItems:
                                    # if np.max(self.db.FuelTGTLiftPoints['VFuelTGT']) == self.db.VFuelTgt and 'VFuelTgt' in self.db.dcChangedItems:
                                    if np.max(self.db.FuelTGTLiftPoints['VFuelTGT']) == self.db.config['VFuelTgt'] and 'VFuelTgt' in self.db.dcChangedItems:
                                        self.db.dcChangedItems[self.db.dcChangedItems.index('VFuelTgt')] = 'Push'
                                    self.setFuelTgt(self.db.config['VFuelTgt'], np.float(self.db.VFuelTgtOffset))

                        self.db.dcOld = self.db.dc.copy()

                        # rear slip ratio
                        if self.db.VelocityX > 10 and not self.db.WeekendInfo['Category'] == 'Oval':
                            if self.db.Gear > 0 and self.db.car.rGearRatios[self.db.Gear] > 0:
                                self.db.rSlipR = (self.db.RPM / 60 * np.pi / self.db.car.rGearRatios[self.db.Gear] * 0.3 / self.db.VelocityX - 1) * 100
                        else:
                            self.db.rSlipR = 0

                        # wheel spin
                        temp = 0
                        if self.db.Throttle > 0.1:
                            for i in range(len(self.db.car.rSlipMapAcc)):
                                if self.db.rSlipR >= self.db.car.rSlipMapAcc[i]:
                                    temp = i+1
                                else:
                                    pass

                        self.db.rWheelSpin = temp

                        # ABS Activity
                        if 'dcABS' in self.db.car.dcList:
                            pBrakeFRef = self.db.car.pBrakeFMax * self.db.dcBrakeBias/100 * self.Brake
                            pBrakeRRef = self.db.car.pBrakeFMax * (1-self.db.dcBrakeBias/100) * self.Brake

                            dpBrake = [self.db.LFbrakeLinePress - pBrakeFRef, self.db.RFbrakeLinePress - pBrakeFRef, self.db.LRbrakeLinePress - pBrakeRRef, self.db.RRbrakeLinePress - pBrakeRRef]

                            self.db.rABSActivity = list(map(self.mapABSActivity, dpBrake))
                        else:  # rear locking
                            temp = 0
                            if self.db.Brake > 0.1:
                                for i in range(len(self.db.car.rSlipMapBrk)):
                                    if self.db.rSlipR <= self.db.car.rSlipMapBrk[i]:
                                        temp = i+1
                                    else:
                                        pass

                            self.db.rRearLocking = temp

                    else:
                        if self.db.WasOnTrack:
                            print(self.db.timeStr + ':\tGetting out of car')
                            print(self.db.timeStr + ': Run: ' + str(self.db.Run))
                            print(self.db.timeStr + ':\tFuelAvgConsumption: ' + convertString.roundedStr2(self.db.FuelAvgConsumption))
                            self.db.NDDUPage = 1
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

                    for i in range(0, len(self.db.CarIdxOnPitRoad)):
                        if self.db.CarIdxOnPitRoad[i] and not self.db.CarIdxOnPitRoadOld[i]:
                            self.db.CarIdxPitStops[i] = self.db.CarIdxPitStops[i] + 1

                    self.db.CarIdxOnPitRoadOld = self.db.CarIdxOnPitRoad

                    # change in driver controls
                    for i in range(0, len(self.db.car.dcList)):
                        self.db.dc[list(self.db.car.dcList.keys())[i]] = self.db.get(list(self.db.car.dcList.keys())[i])

                    for i in range(0, len(self.db.iDDUControls)):
                        self.db.dc[list(self.db.iDDUControls.keys())[i]] = self.db.config[list(self.db.iDDUControls.keys())[i]]

                    if self.db.SessionTime > self.db.RunStartTime + 3:
                        if not self.db.dcHeadlightFlash == self.db.dcHeadlightFlashOld and self.db.dcHeadlightFlash is not None:
                            self.db.BdcHeadlightFlash = True
                            self.db.tdcHeadlightFlash = self.db.SessionTime

                        if self.db.SessionTime > self.db.tdcHeadlightFlash + 1:
                            self.db.BdcHeadlightFlash = False

                    self.db.BDDUexecuting = True
                    self.Brake = self.db.Brake
                else:
                    # iRacing is not running
                    if self.db.BDDUexecuting and not self.db.BSnapshotMode:  # necssary?
                        self.db.BDDUexecuting = False
                        self.db.BWaiting = True
                        self.db.oldSessionNum = -1
                        self.db.SessionNum = 0
                        self.db.StopDDU = True
                        print(self.db.timeStr + ': Lost connection to iRacing')

                self.db.tExecuteCalc = (time.perf_counter() - t) * 1000

                time.sleep(self.rate)

            # except ValueError:
            #     print(self.db.timeStr + ':\tVALUE ERROR in iDDUcalc')
            #     self.db.Exception = 'VALUE ERROR in iDDUcalc'
            #     if not self.BError:
            #         self.db.snapshot()
            #     self.BError = True
            # except NameError:
            #     print(self.db.timeStr + ':\tNAME ERROR in iDDUcalc')
            #     self.db.Exception = 'NAME ERROR in iDDUcalc'
            #     if not self.BError:
            #         self.db.snapshot()
            #     self.BError = True
            # except TypeError as e:
            #     print(self.db.timeStr + ':\tTYPE ERROR in iDDUcalc: ' + str(e))
            #     self.db.Exception = 'TYPE ERROR in iDDUcalc'
            #     if hasattr(e, 'message'):
            #         print(e.message)
            #     else:
            #         print(e)
            #     if not self.BError:
            #         self.db.snapshot()
            #     self.BError = True
            # except KeyError:
            #     print(self.db.timeStr + ':\tKEY ERROR in iDDUcalc')
            #     self.db.Exception = 'KEY ERROR in iDDUcalc'
            #     if not self.BError:
            #         self.db.snapshot()
            #     self.BError = True
            # except IndexError:
            #     print(self.db.timeStr + ':\tINDEX ERROR in iDDUcalc')
            #     self.db.Exception = 'INDEX ERROR in iDDUcalc'
            #     if not self.BError:
            #         self.db.snapshot()
            #     self.BError = True
            # except Exception as e:  # TODO: find a way to handle this
            #     print(self.db.timeStr + ':\tUNEXPECTED ERROR in iDDUcalc: ' + str(e))
            #     self.db.Exception = 'UNEXPECTED ERROR in iDDUcalc: ' + str(e)
            #     if not self.BError:
            #         self.db.snapshot()
            #     self.BError = True

            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                ErrorString = '{} in Line {} of {}'.format(exc_type, exc_tb.tb_lineno, fname)

                if not self.SError == ErrorString:
                    self.logger.error(ErrorString)
                    self.SError = ErrorString
                    print(self.SError)

    def initSession(self):
        print(self.db.timeStr + ': Initialising Session ==========================')
        time.sleep(3)
        print(self.db.timeStr + ':\tNew Session: ' + self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionType'])
        self.trackList = importExport.getFiles(self.dir + '/data/track', 'json')
        self.carList = importExport.getFiles(self.dir + '/data/car', 'json')
        self.db.init = True
        self.db.BResults = False
        self.db.weatherStr = 'TAir: ' + convertString.roundedStr0(self.db.AirTemp) + '°C     TTrack: ' + convertString.roundedStr0(self.db.TrackTemp) + '°C     pAir: ' + convertString.roundedStr2(
            self.db.AirPressure * 0.0338639 * 1.02) + ' bar    rHum: ' + convertString.roundedStr0(self.db.RelativeHumidity * 100) + ' %     rhoAir: ' + convertString.roundedStr2(
            self.db.AirDensity) + ' kg/m³     vWind: '
        self.db.FuelConsumptionList = []
        self.db.FuelLastCons = 0
        self.db.newLapTime = 0
        self.db.oldLap = self.db.Lap
        self.db.TrackLength = float(self.db.WeekendInfo['TrackLength'].split(' ')[0])
        # self.db.JokerLapsRequired = 0
        # self.db.config['PitStopDelta'] = 0
        self.db.config['MapHighlight'] = False
        self.db.Alarm = [0]*10
        self.db.BMultiInitRequest = True

        if self.db.startUp:
            self.db.StartDDU = False
            self.db.oldSessionNum = self.db.SessionNum
            self.db.DriverCarFuelMaxLtr = self.db.DriverInfo['DriverCarFuelMaxLtr'] * self.db.DriverInfo[
                'DriverCarMaxFuelPct']
            self.db.DriverCarIdx = self.db.DriverInfo['DriverCarIdx']
            self.db.PlayerCarClassRelSpeed = self.db.DriverInfo['Drivers'][self.db.DriverCarIdx]['CarClassRelSpeed']

            # track
            if self.db.WeekendInfo['TrackName'] + '.json' in self.trackList:
                self.loadTrack(self.db.WeekendInfo['TrackName'])
                self.BCreateTrack = False
            else:
                self.loadTrack('default')
                self.BCreateTrack = True
                self.BRecordtLap = True
                print(self.db.timeStr + ':\tCreating Track')

            # car
            carName = self.db.DriverInfo['Drivers'][self.db.DriverCarIdx]['CarScreenNameShort']
            carPath = self.db.DriverInfo['Drivers'][self.db.DriverCarIdx]['CarPath']
            if carName + '.json' in self.carList:
                self.loadCar(carName, carPath)  # TODO: required?
                if self.db.WeekendInfo['TrackName'] in self.db.car.tLap:
                    self.BRecordtLap = False
                    self.db.time = self.db.car.tLap[self.db.WeekendInfo['TrackName']]
                else:
                    self.BRecordtLap = True
            else:
                self.loadCar('default', 'default')  # TODO: required?
                self.db.car = Car.Car(Driver=self.db.DriverInfo['Drivers'][self.db.DriverCarIdx])
                self.db.car.createCar(self.db)
                self.db.car.save(self.db.dir)
                self.BRecordtLap = True

                self.db.queryData.extend(list(self.db.car.dcList.keys()))

                print(self.db.timeStr + ':\tCreated Car ' + carName)

            print(self.db.timeStr + ':\tTrackName: ' + self.db.WeekendInfo['TrackDisplayName'])
            print(self.db.timeStr + ':\tEventType: ' + self.db.WeekendInfo['EventType'])
            print(self.db.timeStr + ':\tCategory: ' + self.db.WeekendInfo['Category'])
            print(self.db.timeStr + ':\tSessionType: ' + self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionType'])

            if self.db.WeekendInfo['Category'] == 'DirtRoad':
                self.db.__setattr__('RX', True)
                self.db.__setattr__('JokerLapsRequired', self.db.WeekendInfo['WeekendOptions']['NumJokerLaps'])
                self.db.config['MapHighlight'] = True
                self.db.RenderLabel[17] = True
                print(self.db.timeStr + ':\tDirt Racing')
            else:
                self.db.__setattr__('RX', False)
                self.db.RenderLabel[17] = False
                print(self.db.timeStr + ':\tRoad Racing')

            self.db.config['PitStopsRequired'] = 0
            self.db.config['MapHighlight'] = False

            # unlimited laps
            if self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionLaps'] == 'unlimited':
                self.db.config['RaceLaps'] = self.db.config['UserRaceLaps']
                self.db.LapLimit = False
                self.db.RenderLabel[20] = False
                self.db.RenderLabel[21] = False
                print(self.db.timeStr + ':\t' + self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionLaps'] + ' laps')
                # if self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionType'] == 'Race':
                #     print(self.db.timeStr + ':\t' + 'RaceLaps: ' + str(self.db.config['RaceLaps']))
                #     self.db.LapLimit = True
                #     self.db.RenderLabel[20] = True

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
                            self.db.config['PitStopsRequired'] = 1
                            self.db.config['MapHighlight'] = True
                    print(self.db.timeStr + ':\tRace mode 1')
                    print(self.db.timeStr + ':\tSession length :' + self.db.SessionInfo['Sessions'][self.db.SessionNum][
                        'SessionTime'])
                    if self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionType'] == 'Race':
                        self.db.RenderLabel[21] = True
                        self.db.RenderLabel[20] = True
                    else:
                        self.db.RenderLabel[21] = False
                        self.db.RenderLabel[20] = False
            else:  # limited laps
                self.db.config['RaceLaps'] = int(self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionLaps'])
                self.db.LapLimit = True
                self.db.RenderLabel[20] = True
                self.db.RenderLabel[21] = False
                if self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionType'] == 'Race':
                    if (self.db.TrackLength*self.db.config['RaceLaps']) > 145:
                        self.db.config['PitStopsRequired'] = 1
                        self.db.config['MapHighlight'] = True
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

            if self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionType'] == 'Race' and (not self.db.LapLimit) and self.db.TimeLimit:
                self.db.config['BEnableRaceLapEstimation'] = True
                if self.db.WeekendInfo['TrackName'] in self.db.car.tLap:
                    NLapRaceTime = (self.db.SessionLength - (np.int(self.db.config['PitStopsRequired']) * self.db.config['PitStopDelta'])) / self.db.car.tLap[self.db.WeekendInfo['TrackName']][-1]
                    self.db.NLapDriver = float(NLapRaceTime)
                    self.db.config['RaceLaps'] = int(self.db.NLapDriver + 1)
            else:
                self.db.config['BEnableRaceLapEstimation'] = False

            CarNumber = len(self.db.DriverInfo['Drivers']) + 2
            if not self.db.LapLimit:
                LapNumber = int(self.db.SessionLength/(self.db.TrackLength*13)) + 2
            else:
                if self.db.TimeLimit:
                    LapNumber = int(self.db.SessionLength / (self.db.TrackLength * 13)) + 2
                else:
                    LapNumber = 500

            CarIdxtLap_temp = [[] * LapNumber] * CarNumber
            for x in range(0, CarNumber):
                CarIdxtLap_temp[x] = [nan] * LapNumber

            self.db.CarIdxtLap = CarIdxtLap_temp

            self.db.BUpshiftToneInitRequest = True

            print(self.db.timeStr + ':\tRaceLaps: ' + str(self.db.config['RaceLaps']))
            print(self.db.timeStr + ':\tSessionLength: ' + str(self.db.SessionLength))

            # DRS
            if self.db.DriverInfo['Drivers'][self.db.DriverCarIdx]['CarPath'] in self.DRSList:
                self.db.DRS = True
                if not self.db.WeekendInfo['Category'] == 'Oval':
                    self.db.RenderLabel[18] = True
                self.db.DRSCounter = 0
                if not self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionType'] == 'Race':
                    self.db.config['DRSActivations'] = 1000
                else:
                    self.db.config['DRSActivations'] = self.db.config['DRSActivationsGUI']
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
                    self.db.config['P2PActivations'] = 1000
                else:
                    self.db.config['P2PActivations'] = self.db.config['P2PActivationsGUI']
            else:
                self.db.P2P = False
                self.db.RenderLabel[19] = False

        if self.db.SessionInfo['Sessions'][self.db.SessionNum]['ResultsPositions']:
            self.db.classStruct = {}

            for i in range(0, len(self.db.DriverInfo['Drivers'])):
                if not str(self.db.DriverInfo['Drivers'][i]['UserName']) == 'Pace Car':
                    if i == 0:
                        self.db.classStruct[str(self.db.DriverInfo['Drivers'][i]['CarClassShortName'])] = {'ID': self.db.DriverInfo['Drivers'][i]['CarClassID'],
                                                                                                           'CarClassRelSpeed': self.db.DriverInfo['Drivers'][i]['CarClassRelSpeed'],
                                                                                                           'CarClassColor': self.db.DriverInfo['Drivers'][i]['CarClassColor'],
                                                                                                           'Drivers': [{'Name': self.db.DriverInfo['Drivers'][i]['UserName'],
                                                                                                                        'IRating': self.db.DriverInfo['Drivers'][i]['IRating']}]}
                    else:
                        if str(self.db.DriverInfo['Drivers'][i]['CarClassShortName']) in self.db.classStruct:
                            self.db.classStruct[str(self.db.DriverInfo['Drivers'][i]['CarClassShortName'])]['Drivers'].append({'Name': self.db.DriverInfo['Drivers'][i]['UserName'],
                                                                                                                               'IRating': self.db.DriverInfo['Drivers'][i]['IRating']})
                        else:
                            self.db.classStruct[str(self.db.DriverInfo['Drivers'][i]['CarClassShortName'])] = {'ID': self.db.DriverInfo['Drivers'][i]['CarClassID'],
                                                                                                               'CarClassRelSpeed': self.db.DriverInfo['Drivers'][i]['CarClassRelSpeed'],
                                                                                                               'CarClassColor': self.db.DriverInfo['Drivers'][i]['CarClassColor'],
                                                                                                               'Drivers': [{'Name': self.db.DriverInfo['Drivers'][i]['UserName'],
                                                                                                                            'IRating': self.db.DriverInfo['Drivers'][i]['IRating']}]}

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

        # Display
        if 'dcABS' in self.db.car.dcList:
            self.db.RenderLabel[8] = True
        else:
            self.db.RenderLabel[8] = False

        if 'dcTractionControl' in self.db.car.dcList:
            self.db.RenderLabel[11] = True
        else:
            self.db.RenderLabel[11] = False

        if 'dcTractionControl2' in self.db.car.dcList:
            self.db.RenderLabel[12] = True
        else:
            self.db.RenderLabel[12] = False

        if 'dcFuelMixture' in self.db.car.dcList:
            self.db.RenderLabel[10] = True
        else:
            self.db.RenderLabel[10] = False

        if 'dcBrakeBias' in self.db.car.dcList:
            self.db.RenderLabel[9] = True
        else:
            self.db.RenderLabel[9] = False

        if 'dcAntiRollFront' in self.db.car.dcList:
            self.db.RenderLabel[30] = True
        else:
            self.db.RenderLabel[30] = False

        if 'dcAntiRollRear' in self.db.car.dcList:
            self.db.RenderLabel[31] = True
        else:
            self.db.RenderLabel[31] = False

        if 'dcWeightJackerRight' in self.db.car.dcList and self.db.WeekendInfo['Category'] == 'Oval':
            self.db.RenderLabel[32] = True
        else:
            self.db.RenderLabel[32] = False


    def loadTrack(self, name):
        print(self.db.timeStr + ':\tLoading track: ' + r"track/" + name + '.json')

        self.db.track = Track.Track(name)
        self.db.track.load("data/track/" + name + '.json')

        print(self.db.timeStr + ':\tTrack has been loaded successfully.')

    def loadCar(self, name, carPath):  # TODO: required?
        print(self.db.timeStr + ':\tLoading car: ' + r"car/" + name + '.json')

        self.db.car = Car.Car(name=name, carPath=carPath)
        self.db.car.load("data/car/" + name + '.json')

        self.db.queryData.extend(list(self.db.car.dcList.keys()))

        if self.db.car.UpshiftSettings['BValid']:
            self.db.config['UpshiftStrategy'] = 5
        else:
            self.db.config['UpshiftStrategy'] = self.db.car.UpshiftStrategy

        time.sleep(0.2)

        print(self.db.timeStr + ':\tUpshift strategy: ' + str(self.db.config['UpshiftStrategy']))
        print(self.db.timeStr + ':\tCar has been loaded successfully.')

    def newLap(self):
        # Lap Counting
        self.db.newLapTime = self.db.SessionTime
        # self.db.BLiftBeepPlayed = [0] * len(self.db.FuelTGTLiftPoints['LapDistPct'])

        self.PitStates = (self.db.config['BPitCommandControl'], self.db.config['BChangeTyres'], self.db.config['BBeginFueling'], self.db.config['NFuelSetMethod'], self.db.config['VUserFuelSet'])

        if not self.PitStates == self.PitStatesOld or self.db.BPitCommandUpdate:
            self.setPitCommands()
            self.PitStatesOld = self.PitStates

        if self.db.config['BEnableLapLogging']:  # TODO: still required?
            now = datetime.now()
            date_time = now.strftime("%Y-%m-%d_%H-%M-%S")

            LapStr = date_time + '_Run_'"{:02d}".format(self.db.Run) + '_Lap_'"{:03d}".format(self.db.StintLap) + '.laplog'
            f = open('data/laplog/' + LapStr, 'x')  # TODO: better sturcture of this
            f.write('Lap = ' + repr(self.db.Lap) + '\n')
            f.write('StintLap = ' + repr(self.db.StintLap) + '\n')
            f.write('RaceLaps = ' + repr(self.db.config['RaceLaps']) + '\n')
            f.write('FuelConsumptionList = ' + repr(self.db.FuelConsumptionList) + '\n')
            f.write('TimeLimit = ' + repr(self.db.TimeLimit) + '\n')
            f.write('SessionInfo = ' + repr(self.db.SessionInfo) + '\n')
            f.write('SessionTime = ' + repr(self.db.SessionTime) + '\n')
            f.write('GreenTime = ' + repr(self.db.GreenTime) + '\n')
            f.write('SessionTimeRemain = ' + repr(self.db.SessionTimeRemain) + '\n')
            f.write('DriverCarIdx = ' + repr(self.db.DriverCarIdx) + '\n')
            f.write('CarIdxF2Time = ' + repr(self.db.CarIdxF2Time) + '\n')
            f.write('LapLastLapTime = ' + repr(self.db.LapLastLapTime) + '\n')
            f.write('PitStopsRequired = ' + repr(self.db.config['PitStopsRequired']) + '\n')
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
            f.write('PitStopDelta = ' + repr(self.db.config['PitStopDelta']) + '\n')
            f.write('CarIdxOnPitRoad = ' + repr(self.db.CarIdxOnPitRoad) + '\n')
            f.write('CarIdxLapDistPct = ' + repr(self.db.CarIdxLapDistPct) + '\n')
            f.write('PaceCarIdx = ' + repr(self.db.DriverInfo['PaceCarIdx']) + '\n')
            f.write('FuelLevel = ' + repr(self.db.FuelLevel) + '\n')
            f.write('SessionFlags = ' + repr(self.db.SessionFlags) + '\n')
            f.write('BEnableRaceLapEstimation = ' + repr(self.db.config['BEnableRaceLapEstimation']) + '\n')
            f.write('tNextLiftPoint = ' + repr(self.db.tNextLiftPoint) + '\n')
            f.write('LapDistPct = ' + repr(self.db.LapDistPct) + '\n')
            f.write('BLiftToneRequest = ' + repr(self.db.BLiftToneRequest) + '\n')
            f.write('BLiftBeepPlayed = ' + repr(self.db.BLiftBeepPlayed) + '\n')
            f.close()

        self.db.oldLap = self.db.Lap
        if self.db.config['NRaceLapsSource'] == 0:
            self.db.LapsToGo = self.db.config['RaceLaps'] - self.db.Lap + 1
        elif self.db.config['NRaceLapsSource'] == 1:
            self.db.LapsToGo = self.db.config['UserRaceLaps'] - self.db.Lap + 1

        # Fuel Calculations
        self.db.FuelLastCons = self.db.LastFuelLevel - self.db.FuelLevel
        if (not self.db.OutLap) and (not self.db.OnPitRoad):
            self.db.FuelConsumptionList.extend([self.db.FuelLastCons])
        else:
            self.db.OutLap = False

        FuelLapConsDelta = np.round(self.db.FuelLastCons - self.db.config['VFuelTgt'], 2)

        if FuelLapConsDelta > 0.0 and self.db.config['NFuelTargetMethod'] > 0:
            self.db.textColourLapCons = self.red
        elif FuelLapConsDelta < 0.0 and self.db.config['NFuelTargetMethod'] > 0:
            self.db.textColourLapCons = self.green
        else:
            self.db.textColourLapCons = self.db.textColour

        self.db.LastFuelLevel = self.db.FuelLevel

        VFuelConsumptionTargetFinish = (self.db.FuelLevel - 0.3) / self.db.LapsToGo
        VFuelConsumptionTargetStint = (self.db.FuelLevel - 0.3) / (self.db.config['NLapsStintPlanned'] - self.db.StintLap)

        if self.db.config['NFuelTargetMethod'] == 2:  # Finish
            self.setFuelTgt(VFuelConsumptionTargetFinish, 0)
        elif self.db.config['NFuelTargetMethod'] == 3:  # Stint
            if self.db.config['PitStopsRequired'] > 0 and self.db.config['PitStopsRequired'] <= self.db.CarIdxPitStops[self.db.DriverCarIdx]:
                self.setFuelTgt(VFuelConsumptionTargetFinish, 0)
            else:
                self.setFuelTgt(VFuelConsumptionTargetStint, 0)

        self.db.weatherStr = 'TAir: ' + convertString.roundedStr0(self.db.AirTemp) + '°C     TTrack: ' + convertString.roundedStr0(self.db.TrackTemp) + '°C     pAir: ' + convertString.roundedStr2(
            self.db.AirPressure * 0.0338639 * 1.02) + ' bar    rHum: ' + convertString.roundedStr0(self.db.RelativeHumidity * 100) + ' %     rhoAir: ' + convertString.roundedStr2(
            self.db.AirDensity) + ' kg/m³     vWind: '

        # display fuel consumption information
        self.db.RenderLabel[4] = True
        self.db.RenderLabel[5] = True
        self.db.RenderLabel[28] = False
        self.db.RenderLabel[29] = False

        self.db.StintLap = self.db.StintLap + 1

        if (self.BCreateTrack or self.BRecordtLap) and not self.db.OutLap and self.db.StintLap > 1:
            # Logging track data
            if not self.Logging:
                self.logLap = self.db.Lap
                self.Logging = True
                self.timeLogingStart = self.db.SessionTime

        if (self.BCreateTrack or self.BRecordtLap) and self.Logging and self.logLap < self.db.Lap and self.db.BNewLap:
            self.createTrackFile(self.BCreateTrack, self.BRecordtLap)

    def createTrackFile(self, BCreateTrack, BRecordtLap):

        time.sleep(1)

        index = np.unique(self.time, return_index=True)[1]
        self.time = np.array(self.time)[index]
        self.time = self.time - self.time[0]
        self.LapDistPct = np.array(self.LapDistPct)[index]
        self.YawNorth = np.array(self.YawNorth)[index]
        self.Yaw = np.array(self.Yaw)[index]
        self.VelocityX = np.array(self.VelocityX)[index]
        self.VelocityY = np.array(self.VelocityY)[index]

        # self.time = np.append(self.time, self.db.LapLastLapTime)
        # self.LapDistPct = np.append(self.LapDistPct, [100])

        if BCreateTrack:  # TODO: same code as in fuelSaving Optimiser?
            self.dt = np.diff(self.time)
            self.time = self.time - self.time[0]
            self.time[-1] = self.db.LapLastLapTime

            self.LapDistPct[0] = 0
            self.LapDistPct[-1] = 100

            self.dx = np.append(self.dx, np.cos(self.Yaw[0:-1]) * self.VelocityX[0:-1] * self.dt - np.sin(self.Yaw[0:-1]) * self.VelocityY[0:-1] * self.dt)
            self.dy = np.append(self.dy, np.cos(self.Yaw[0:-1]) * self.VelocityY[0:-1] * self.dt + np.sin(self.Yaw[0:-1]) * self.VelocityX[0:-1] * self.dt)

            tempx = np.cumsum(self.dx, dtype=float).tolist()
            tempy = np.cumsum(self.dy, dtype=float).tolist()

            xError = tempx[-1] - tempx[0]
            yError = tempy[-1] - tempy[0]

            tempdx = np.array(0)
            tempdy = np.array(0)

            tempdx = np.append(tempdx, self.dx[1:len(self.dx)] - xError / (len(self.dx)-1))
            tempdy = np.append(tempdy, self.dy[1:len(self.dy)] - yError / (len(self.dy)-1))

            self.x = np.cumsum(tempdx, dtype=float)
            self.y = np.cumsum(tempdy, dtype=float)

            # self.x = np.cumsum([np.array(self.dx) - xError / len(tempx)], dtype=float)
            # self.y = np.cumsum([np.array(self.dy) - yError / len(tempy)], dtype=float)

            self.x[-1] = 0
            self.y[-1] = 0

            self.db.track = Track.Track(self.db.WeekendInfo['TrackName'])

            aNorth = self.YawNorth[0]

            self.db.track.createTrack(self.x, self.y, self.LapDistPct, aNorth, self.db.TrackLength*1000)
            self.db.track.save(self.db.dir)

            self.db.LapDistPct = self.db.track.LapDistPct

            print(self.db.timeStr + ':\tTrack has been successfully created')
            print(self.db.timeStr + ':\tSaved track as: ' + r"data/track/" + self.db.track.name + ".json")

        if BRecordtLap:
            if maths.strictly_increasing(self.time) and maths.strictly_increasing(self.LapDistPct):
                self.db.car.addLapTime(self.db.WeekendInfo['TrackName'], self.time, self.LapDistPct, self.db.track.LapDistPct, self.db.FuelConsumptionList[-1])
                self.db.car.save(self.db.dir)
                self.db.time = self.db.car.tLap[self.db.WeekendInfo['TrackName']]

                print(self.db.timeStr + ':\tLap time has been recorded successfully!')
                print(self.db.timeStr + ':\tSaved car as: ' + r"data/car/" + self.db.car.name + ".json")
            else:
                print(self.db.timeStr + ':\tRecorded Laptime is not monotonically increasing. Aborted track creation!')

        self.BCreateTrack = False
        self.BRecordtLap = False
        self.Logging = False

    def SOFstring(self):
        if self.db.NClasses > 1:
            temp = 'SOF: ' + convertString.roundedStr0(self.db.SOFMyClass) + '('
            keys = self.db.classStruct.keys()
            for i in range(0, self.db.NClasses):
                temp = temp + self.db.classStruct[keys[i]] + ': ' + convertString.roundedStr0(self.db.classStruct[keys[i]]['SOF'])
            self.db.SOFstr = temp + ')'
        else:
            self.db.SOFstr = 'SOF: ' + convertString.roundedStr0(self.db.SOF)

    def setPitCommands(self):
        # clear = 0  # Clear all pit checkboxes
        # ws = 1  # Clean the windshield, using one tear off
        # fuel = 2  # Add fuel, optionally specify the amount to add in liters or pass '0' to use existing amount
        # lf = 3  # Change the left front tire, optionally specifying the pressure in KPa or pass '0' to use existing pressure
        # rf = 4  # right front
        # lr = 5  # left rear
        # rr = 6  # right rear
        # clear_tires = 7  # Clear tire pit checkboxes
        # fr = 8  # Request a fast repair
        # clear_ws = 9  # Uncheck Clean the winshield checkbox
        # clear_fr = 10  # Uncheck request a fast repair
        # clear_fuel = 11  # Uncheck add fuel

        if self.db.config['BPitCommandControl']:
            if not self.db.config['BChangeTyres']:
                self.ir.pit_command(7)  # clear tires
            else:
                self.ir.pit_command(3)
                self.ir.pit_command(4)
                self.ir.pit_command(5)
                self.ir.pit_command(6)

            if not self.db.config['BBeginFueling']:
                self.ir.pit_command(11)  # Uncheck add fuel
            else:
                if self.db.config['NFuelSetMethod'] == 0:
                    self.ir.pit_command(2, self.db.config['VUserFuelSet'])
                elif self.db.config['NFuelSetMethod'] == 1:
                    self.ir.pit_command(2, round(self.db.VFuelAdd + 1 + 1e-10))

        self.db.BPitCommandUpdate = False

    def pitStop(self):
        # lf_tire_change = 0x01
        # rf_tire_change = 0x02
        # lr_tire_change = 0x04
        # rr_tire_change = 0x08
        # fuel_fill = 0x10
        # windshield_tearoff = 0x20
        # fast_repair = 0x40

        PitSvFlagsCompleted = self.db.PitSvFlagsEntry - self.db.PitSvFlags

        if PitSvFlagsCompleted & 0x01:
            self.db.BTyreChangeCompleted[0] = True
        if PitSvFlagsCompleted & 0x02:
            self.db.BTyreChangeCompleted[1] = True
        if PitSvFlagsCompleted & 0x04:
            self.db.BTyreChangeCompleted[2] = True
        if PitSvFlagsCompleted & 0x08:
            self.db.BTyreChangeCompleted[3] = True
        if PitSvFlagsCompleted & 0x10:
            self.db.BFuelCompleted = True

    def distance2PitStall(self):
        if self.db.DriverInfo['DriverPitTrkPct'] > 0.5:
            if self.db.LapDistPct < 0.5:
                self.db.sToPitStall = - ((1 - self.db.DriverInfo['DriverPitTrkPct'] + self.db.LapDistPct) * self.db.TrackLength * 1000)
            else:
                self.db.sToPitStall = (self.db.DriverInfo['DriverPitTrkPct'] - self.db.LapDistPct) * self.db.TrackLength * 1000
        else:
            if self.db.LapDistPct > 0.5:
                self.db.sToPitStall = (1 - self.db.LapDistPct + self.db.DriverInfo['DriverPitTrkPct']) * self.db.TrackLength * 1000
            else:
                self.db.sToPitStall = (self.db.DriverInfo['DriverPitTrkPct'] - self.db.LapDistPct) * self.db.TrackLength * 1000

    @staticmethod
    def bit2RBG(bitColor):
        hexColor = format(bitColor, '06x')
        return int('0x' + hexColor[0:2], 0), int('0x' + hexColor[2:4], 0), int('0x' + hexColor[4:6], 0)

    # def LiftTone(self):
    #
    #     if len(self.db.LapDistPctLift) > 0 and (len(self.db.LapDistPctLift) > self.db.NNextLiftPoint):
    #
    #         if self.db.LapDistPctLift[self.db.NNextLiftPoint] > 1 and self.db.LapDistPct < 0.4:
    #             ds = (self.db.LapDistPct - self.db.LapDistPctLift[self.db.NNextLiftPoint] + 1) * self.db.track.sTrack
    #         else:
    #             if self.db.LapDistPct > (self.db.LapDistPctLift[self.db.NNextLiftPoint] + (75 / self.db.track.sTrack)):
    #                 ds = (self.db.LapDistPct - self.db.LapDistPctLift[self.db.NNextLiftPoint] - 1) * self.db.track.sTrack
    #             else:
    #                 ds = (self.db.LapDistPct - self.db.LapDistPctLift[self.db.NNextLiftPoint]) * self.db.track.sTrack
    #
    #         LongAccel = self.db.LongAccel
    #         Speed = self.db.Speed
    #         if LongAccel == 0:
    #             self.db.tNextLiftPoint = - ds / Speed
    #         else:
    #             self.db.tNextLiftPoint = - Speed / LongAccel + np.sqrt(np.square(Speed / LongAccel) - (2 * ds) / LongAccel)
    #
    #         if self.db.BLiftBeepPlayed[self.db.NNextLiftPoint] < 3 and self.db.tNextLiftPoint <= tLiftTones[self.db.BLiftBeepPlayed[self.db.NNextLiftPoint]]:
    #             self.db.BLiftToneRequest = True
    #             self.db.BLiftBeepPlayed[self.db.NNextLiftPoint] = self.db.BLiftBeepPlayed[self.db.NNextLiftPoint] + 1
    #
    #         # check which lift point is next
    #         d = self.db.LapDistPctLift - self.db.LapDistPct
    #         d[d < 0] = np.nan
    #         d[d > 1] = d[d > 1] - 1
    #         NNextLiftPointOld = self.db.NNextLiftPoint
    #         if np.all(np.isnan(d)):
    #             self.db.NNextLiftPoint = 0
    #         else:
    #             self.db.NNextLiftPoint = np.nanargmin(d)
    #
    #         if not self.db.NNextLiftPoint == NNextLiftPointOld:
    #             self.db.BLiftBeepPlayed[NNextLiftPointOld] = 0

    def LiftTone(self):

        if len(self.db.VFuelBudget) > 0 and (len(self.db.VFuelBudget) > self.db.NNextLiftPoint):

            self.db.VFuelBudgetActive = self.db.VFuelBudget[self.db.NNextLiftPoint]
            self.db.VFuelReferenceActive = self.db.VFuelReference[self.db.NNextLiftPoint]
            self.db.dVFuelTgt = self.db.FuelLevel + self.db.VFuelBudgetActive - self.db.VFuelStartStraight

            self.db.tNextLiftPoint = self.db.dVFuelTgt / (self.db.FuelUsePerHour / 3600 / self.db.DriverInfo['DriverCarFuelKgPerLtr'])

            if self.db.BLiftBeepPlayed[self.db.NNextLiftPoint] < 3 and \
                    self.db.tNextLiftPoint <= self.db.tLiftTones[self.db.BLiftBeepPlayed[self.db.NNextLiftPoint]] + self.db.config['tReactionLift'] and \
                    self.db.LapDistPct < self.db.FuelTGTLiftPoints['LapDistPctBrake'][self.db.NNextLiftPoint] / 100:
                self.db.BLiftToneRequest = True
                self.db.BLiftBeepPlayed[self.db.NNextLiftPoint] = self.db.BLiftBeepPlayed[self.db.NNextLiftPoint] + 1

            # check which lift point is next; 0 = approaching first corner
            NNextLiftPointOld = self.db.NNextLiftPoint
            self.getNStraight()

            # change in straight
            if not self.db.NNextLiftPoint == NNextLiftPointOld:
                self.db.BLiftBeepPlayed[NNextLiftPointOld] = 0
                # self.db.VFuelStartStraight = self.db.FuelLevel
                self.db.BUpdateVFuelDelta = True

                if self.db.SessionTime - self.db.newLapTime > self.db.config['tDisplayConsumption']:
                    self.db.RenderLabel[4] = False
                    self.db.RenderLabel[5] = False
                    self.db.RenderLabel[28] = True
                    self.db.RenderLabel[29] = True

    def setFuelTgt(self, tgt, offset):
        if self.db.BFuelSavingConfigLoaded:
            self.db.LapDistPctLift = np.array([])
            self.db.VFuelBudget = np.array([])
            self.db.VFuelReference = np.array([])
            rLift = np.array([])
            self.db.config['VFuelTgt'] = np.min([np.max(self.db.FuelTGTLiftPoints['VFuelTGT']),
                                                 np.max([tgt, np.min(self.db.FuelTGTLiftPoints['VFuelTGT'])]).round(2)])
            self.db.config['VFuelTgtOffset'] = np.min([1, np.max([offset, -1])]).astype(float)
            self.db.VFuelTgtEffective = np.min([np.max(self.db.FuelTGTLiftPoints['VFuelTGT']),
                                                np.max([tgt + offset, np.min(self.db.FuelTGTLiftPoints['VFuelTGT'])])]).round(2)

            for i in range(0, len(self.db.FuelTGTLiftPoints['LapDistPctLift'])):
                x = self.db.FuelTGTLiftPoints['VFuelTGT']
                y = self.db.FuelTGTLiftPoints['LapDistPctLift'][i]
                self.db.LapDistPctLift = np.append(self.db.LapDistPctLift, np.interp(self.db.VFuelTgtEffective, x, y) / 100)
                rLift = np.append(rLift, np.interp(self.db.VFuelTgtEffective, x, self.db.FuelTGTLiftPoints['LiftPoints'][i]))

                y2 = self.db.FuelTGTLiftPoints['VFuelBudget'][i]
                self.db.VFuelBudget = np.append(self.db.VFuelBudget, np.interp(self.db.config['VFuelTgt'], x, y2))

                y3 = self.db.FuelTGTLiftPoints['VFuelReference'][i]
                self.db.VFuelReference = np.append(self.db.VFuelReference, np.interp(self.db.config['VFuelTgt'], x, y3))

            self.db.LapDistPctLift = self.db.LapDistPctLift

            self.db.BLiftBeepPlayed = [0] * len(self.db.FuelTGTLiftPoints['LapDistPctLift'])
        else:
            return

    def getNStraight(self):
        # 0 = approaching first corner
        d = np.array(self.db.FuelTGTLiftPoints['LapDistPctApex']) / 100 - self.db.LapDistPct

        d = np.where(d >= 0)

        if len(d[0]) > 0:
            d = np.min(d)
        else:
            d = 0

        self.db.NNextLiftPoint = np.min(d)

    def mapABSActivity(self, pBrake):
        if pBrake < self.db.car.rABSActivityMap[2]:
            return 3
        elif pBrake < self.db.car.rABSActivityMap[1]:
            return 2
        elif pBrake < self.db.car.rABSActivityMap[0]:
            return 1
        else:
            return 0
