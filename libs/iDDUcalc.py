import os
import sys
import time
import traceback
from datetime import datetime

import numpy as np
from scipy import interpolate

from libs import Track, Car
from libs.IDDU import IDDUThread, IDDUItem
from libs.auxiliaries import importExport, convertString, maths
from functools import wraps


nan = float('nan')  # TODO: add to IDDu object?


# TODO: add more comments
# TODO: try to spread into more nested functions, i.e. approachingPits, inPitStall, exitingPits, ...


def a_new_decorator(a_func, *args, **kwargs):
    @wraps(a_func)
    def wrapTheFunction(*args, **kwargs):
        try:
            a_func(*args, **kwargs)
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            s = traceback.format_exception(exc_type, exc_value, exc_traceback, limit=2, chain=True)
            S = '\n'
            for i in s:
                S = S + i
            IDDUItem.logger.error(S)
            
    return wrapTheFunction

class IDDUCalcThread(IDDUThread):
    BError = False
    SError = ''
    Brake = 0
    PitStates = None
    PitStatesOld = None
    dpBrakeOld = np.array([0, 0, 0, 0])
    BClutchRelased = False
    BStartCompleted = True
    tStart100Timer = -1
    tStartCompleted = -1
    tStartModeEnd = -1
    NGearOld = 1
    tUpshift = 0
    tABSLastActivated = None
    ABSActivationMap = interpolate.interp1d([0, 0.13, 0.3, 0.45, 99999999999], [0, 1, 2, 3, 4], kind='next')
    NPitApproachBeepsPlayed = 0
    vPitSpeedDeltaBeep = [50, 25, 3]
    BPitSpeedBeepsEnabled = False
    SessionTick = 0
    SessionTickOld = 0
    x0 = 0
    x1 = 0
    t0 = 0
    t1 = 0
    vYellowFlag = None
 
    @a_new_decorator
    def __init__(self, rate):
        IDDUThread.__init__(self, rate)

        self.FlagCallTime = 0
        self.init = False

        self.Yaw = np.array([])
        self.YawNorth = np.array([])
        self.VelocityX = np.array([])
        self.VelocityY = np.array([])
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
        self.GearID = 'base'

        self.DRSList = ['formularenault35', 'mclarenmp430']  # TODO: still required?
        self.P2PList = ['dallaradw12', 'dallarair18']  # TODO: still required?

        self.dir = os.getcwd()
        self.trackList = importExport.getFiles(self.dir + '/data/track', 'json')
        self.carList = importExport.getFiles(self.dir + '/data/car', 'json')

        self.x = None
        self.y = None
        self.snapshot = False

        self.BRanQuali = False

        self.logger.info('Started iDDUcalc')

    @a_new_decorator
    def run(self):
        
        
        self.loadTrack('default')
        
        while self.running:
            self.tic()
            try:
                t = time.perf_counter()
                # Check if DDU is initialised
                if not self.db.BDDUexecuting:
                    # initialise
                    if not self.db.BWaiting:
                        self.logger.info('Waiting for iRacing')
                        self.db.BWaiting = True
                #
                # self.MarcsJoystick.update()

                # Check if iRacing Service is running
                if self.db.startUp:
                    # iRacing is running
                    if not self.db.BDDUexecuting:
                        self.logger.info('Connecting to iRacing')

                    if not self.db.WeekendInfo['SubSessionID'] == self.db.SubSessionIDOld or not self.db.SessionTypeOld == self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionType']: # self.db.oldSessionNum < self.db.SessionNum or 
                        self.initSession()

                    if self.db.SessionTime < 10 + self.db.GreenTime:
                        self.db.CarIdxPitStops = [0] * 64

                    if self.db.SessionInfo['Sessions'][self.db.SessionNum]['ResultsPositions']:
                        for i in range(0, len(self.db.SessionInfo['Sessions'][self.db.SessionNum]['ResultsPositions'])):
                            if self.db.SessionInfo['Sessions'][self.db.SessionNum]['ResultsPositions'][i]['CarIdx'] == self.db.DriverCarIdx:
                                self.db.NClassPosition = self.db.SessionInfo['Sessions'][self.db.SessionNum]['ResultsPositions'][i]['ClassPosition'] + 1
                                self.db.NPosition = self.db.SessionInfo['Sessions'][self.db.SessionNum]['ResultsPositions'][i]['Position']
                                self.db.BResults = True

                    if self.db.IsInGarage:
                        self.db.FuelLevelDisp = self.db.FuelLevel

                    if self.db.BLoadRaceSetupWarning:
                        # CurrentSetup = {'DriverSetupName': self.db.DriverInfo['DriverSetupName'],
                        #                 'UpdateCount': self.db.CarSetup['UpdateCount'],
                        #                 'FuelLevel': self.db.FuelLevel}
                        #
                        # if not self.db.LastSetup == CurrentSetup:
                        #     if CurrentSetup['FuelLevel'] == 0:
                        #         pass
                        #     if CurrentSetup['FuelLevel'] > self.db.LastSetup['FuelLevel']:
                        #         self.db.BLoadRaceSetupWarning = False

                        if (not self.db.DriverInfo['DriverSetupName'] == self.db.LastSetup['DriverSetupName']) or (self.db.FuelLevelDisp > self.db.LastSetup['FuelLevel'] + 0.5):
                            self.db.BLoadRaceSetupWarning = False

                    if self.db.BResults:
                        self.db.PosStr = str(self.db.NClassPosition) + '/' + str(self.db.NDriversMyClass)
                    else:
                        self.db.PosStr = '-/' + str(self.db.NDriversMyClass)

                    if self.db.PlayerTrackSurface == 3:  # on track
                        self.db.BEnteringPits = False
                        self.NPitApproachBeepsPlayed = 0
                    elif self.db.PlayerTrackSurfaceOld == 3 and not self.db.BEnteringPits and self.db.PlayerTrackSurface == 2:  # entering pit entry event
                        self.db.BEnteringPits = True
                        self.db.track.setPitIn(self.db.LapDistPct * 100)

                    self.db.PlayerTrackSurfaceOld = self.db.PlayerTrackSurface

                    if self.db.OnPitRoad and self.db.BEnteringPits and not self.db.PlayerCarPitSvStatus == 2:  # from pit entry end of pit stop
                        self.db.NDDUPage = 3

                    pitSpeedLimit = self.db.WeekendInfo['TrackPitSpeedLimit']
                    deltaSpeed = [self.db.Speed * 3.6 - float(pitSpeedLimit.split(' ')[0])]

                    if self.db.OnPitRoad or self.db.BEnteringPits:  # do when in pit entry or in pit lane but not on track                        
                        #                            k   k   b   c  g    g    y    o   r   r
                        r = np.interp(deltaSpeed, [-10, -5, -2, -1, 0, 0.7, 1.2, 1.6, 20, 40],
                                      [self.black[0], self.black[0], self.blue[0], self.cyan[0], self.green[0], self.green[0], self.yellow[0], self.orange[0], self.red[0], self.red[0]])
                        g = np.interp(deltaSpeed, [-10, -5, -2, -1, 0, 0.7, 1.2, 1.6, 20, 40],
                                      [self.black[1], self.black[1], self.blue[1], self.cyan[1], self.green[1], self.green[1], self.yellow[1], self.orange[1], self.red[1], self.red[1]])
                        b = np.interp(deltaSpeed, [-10, -5, -2, -1, 0, 0.7, 1.2, 1.6, 20, 40],
                                      [self.black[2], self.black[2], self.blue[2], self.cyan[2], self.green[2], self.green[2], self.yellow[2], self.orange[2], self.red[2], self.red[2]])
                            
                        self.db.backgroundColour = tuple([r, g, b])
                        self.db.textColour = self.white
                        self.distance2PitStall()

                        # play beeps to countdown to speed limit
                        if self.BPitSpeedBeepsEnabled:
                            if self.NPitApproachBeepsPlayed < 3:
                                if deltaSpeed[0] <= self.vPitSpeedDeltaBeep[self.NPitApproachBeepsPlayed]:
                                    self.logger.info('Pit Approach Beep {} at {} kph delta'.format(self.NPitApproachBeepsPlayed, deltaSpeed[0]))
                                    self.db.BRequestPitSpeedBeep = True
                                    self.NPitApproachBeepsPlayed = self.NPitApproachBeepsPlayed + 1

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

                        if (not self.db.SessionFlags == self.db.oldSessionFlags) or (not self.db.TrackWetnessOld == self.db.TrackWetness):
                            self.FlagCallTime = self.db.SessionTime
                            self.db.FlagExceptionVal = 0
                            if self.db.SessionFlags & 0x80000000:  # startGo
                                self.db.backgroundColour = self.green
                                if not self.db.GreenTime:
                                    self.db.GreenTime = self.db.SessionTime
                                    self.db.BLoadRaceSetupWarning = False
                                    self.db.AM.LOADRACESETUP.cancelAlert()
                                self.db.CarIdxPitStops = [0] * 64
                                if self.db.TimeLimit:
                                    self.db.RenderLabel[15] = True  # 15 Remain
                                    self.db.RenderLabel[16] = False  # 16 Elapsed
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
                                self.db.slipFlagExceptionVal = 3
                            if self.db.SessionFlags & 0x10:  # red
                                self.db.backgroundColour = self.red
                            if not self.db.TrackWetnessOld == self.db.TrackWetness:
                                self.FlagCallTime = self.db.SessionTime
                                self.db.FlagException = True
                                if self.db.TrackWetness == 1:
                                    self.db.FlagExceptionVal = 11
                                elif self.db.TrackWetness == 2:
                                    self.db.FlagExceptionVal = 12
                                elif self.db.TrackWetness == 3:
                                    self.db.FlagExceptionVal = 13
                                elif self.db.TrackWetness == 4:
                                    self.db.FlagExceptionVal = 14
                                elif self.db.TrackWetness == 5:
                                    self.db.FlagExceptionVal = 15
                                elif self.db.TrackWetness == 6:
                                    self.db.FlagExceptionVal = 16
                                elif self.db.TrackWetness == 7:
                                    self.db.FlagExceptionVal = 17
                                    

                        elif self.db.SessionTime > (self.FlagCallTime + 4):
                            self.db.backgroundColour = self.black

                            if len(self.db.NLappingCars) > 0 and (self.db.PlayerTrackSurface == 1 or self.db.PlayerTrackSurface == 3) and self.db.IsOnTrack:
                                self.db.backgroundColour = self.blue

                            self.db.textColour = self.white
                            self.db.FlagException = False
                            self.db.FlagExceptionVal = 0

                    self.db.oldSessionFlags = self.db.SessionFlags
                    self.db.TrackWetnessOld = self.db.TrackWetness
                    self.db.WeatherDeclaredWetOld = self.db.WeatherDeclaredWet
                    
                    if self.db.IsOnTrack:
                        # do if car is on track #############################################################################################
                        if not self.db.WasOnTrack:
                            self.db.WasOnTrack = True
                            self.db.StintLap = 0

                        # self.db.Alarm = np.array([0] * 10)
                        self.db.Alarm[0:7] = 0
                        self.db.Alarm[8:] = 0

                        # my flags
                        if self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionType'] in ['Practice', 'Race']:
                            self.blueFlag()
                            self.yellowFlag()

                        self.db.FuelLevelDisp = self.db.FuelLevel

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
                            self.db.init = False
                            self.db.OutLap = True
                            self.db.BMultiInitRequest = True
                            self.db.BTyreChoiceWarning = 0
                            self.db.AM.CHECKTIRES.cancelAlert()
                            self.db.LastFuelLevel = self.db.FuelLevel
                            self.db.FuelConsumptionList = []
                            self.db.RunStartTime = self.db.SessionTime
                            self.db.Run = self.db.Run + 1
                            self.logger.info('Starting Run {}'.format(self.db.Run))
                            self.db.BLEDsInit = True
                            self.BPitSpeedBeepsEnabled = False
                            if self.db.config['BPitCommandControl']:
                                self.ir.pit_command(0)

                            # get GearID
                            self.db.GearID = self.db.car.getGearID(self.db.CarSetup)
                            if self.db.GearID in self.db.car.rGearRatios:
                                pass
                            else:
                                self.GearID = 'base'

                            if self.db.FuelTGTLiftPoints['SFuelConfigCarName'] == self.db.DriverInfo['Drivers'][self.db.DriverCarIdx]['CarScreenNameShort'] \
                                    and self.db.FuelTGTLiftPoints['SFuelConfigTrackName'] == self.db.WeekendInfo['TrackName']:
                                self.db.BFuelSavingConfigLoaded = True
                            else:
                                self.db.BFuelSavingConfigLoaded = False
                                self.logger.warning('Fuel Saving config loaded ({}, {}) does not match current session ({}, {})'.format(self.db.FuelTGTLiftPoints['SFuelConfigCarName'],
                                                                                                                                        self.db.FuelTGTLiftPoints['SFuelConfigTrackName'],
                                                                                                                                        self.db.DriverInfo['Drivers'][self.db.DriverCarIdx][
                                                                                                                                            'CarScreenNameShort'],
                                                                                                                                        self.db.WeekendInfo['TrackDisplayShortName']))
                            if 'dcABS' in self.db.car.dcList or self.db.car.name in self.CarsWithABS:
                                if self.db.dcBrakeBias:
                                    pBrakeLFMax = self.db.LFbrakeLinePress / (self.db.dcBrakeBias / 100) / self.db.Brake
                                    pBrakeRFMax = self.db.RFbrakeLinePress / (self.db.dcBrakeBias / 100) / self.db.Brake
                                    pBrakeLRMax = self.db.LRbrakeLinePress / (1 - self.db.dcBrakeBias / 100) / self.db.Brake
                                    pBrakeRRMax = self.db.RRbrakeLinePress / (1 - self.db.dcBrakeBias / 100) / self.db.Brake
                                else:
                                    pBrakeLFMax = self.db.LFbrakeLinePress / self.db.Brake
                                    pBrakeRFMax = self.db.RFbrakeLinePress / self.db.Brake
                                    pBrakeLRMax = self.db.LRbrakeLinePress / self.db.Brake
                                    pBrakeRRMax = self.db.RRbrakeLinePress / self.db.Brake

                                self.db.car.setpBrakeMax((pBrakeLFMax + pBrakeRFMax) / 2, (pBrakeLRMax + pBrakeRRMax) / 2)
                                self.db.car.save(self.db.dir)
                                self.db.car.MotecXMLexport(rootPath=self.dir, MotecPath=self.db.config['MotecProjectPath'], GearID=self.db.GearID)

                            if not self.db.LastSetup['DriverSetupName'] == self.db.DriverInfo['DriverSetupName'] or not self.db.LastSetup['UpdateCount'] == self.db.CarSetup['UpdateCount']:
                                self.db.BUpshiftToneInitRequest = True

                            self.db.LastSetup = {'DriverSetupName': self.db.DriverInfo['DriverSetupName'],
                                                 'UpdateCount': self.db.CarSetup['UpdateCount'],
                                                 'FuelLevel': self.db.FuelLevel}

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
                                    self.BPitSpeedBeepsEnabled = False

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
                            self.NPitApproachBeepsPlayed = 0
                            self.BPitSpeedBeepsEnabled = True
                            self.db.track.setPitOut(self.db.LapDistPct * 100)

                        # check if new lap
                        if self.db.Lap > self.db.oldLap and self.db.SessionState == 4 and self.db.SessionTime > self.db.newLapTime + 10:
                            self.db.BNewLap = True
                            self.newLap()
                        else:
                            self.db.BNewLap = False

                        # Create Track Map
                        if (self.BCreateTrack or self.BRecordtLap) and not self.db.OutLap and self.db.StintLap > 0:
                            self.Yaw = np.append(self.Yaw, self.db.Yaw)
                            self.YawNorth = np.append(self.YawNorth, self.db.YawNorth)
                            self.VelocityX = np.append(self.VelocityX, self.db.VelocityX)
                            self.VelocityY = np.append(self.VelocityY, self.db.VelocityY)
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
                                                       self.db.DriverCarFuelMaxLtr)
                                if self.db.VFuelAdd == 0:
                                    # self.ir.pit_command(2, 1) # Add fuel, optionally specify the amount to add in liters or pass '0' to use existing amount
                                    # self.ir.pit_command(11) # Uncheck add fuel
                                    self.db.BTextColourFuelAddOverride = False
                                else:
                                    if not round(self.db.VFuelAdd) == round(self.db.VFuelAddOld):
                                        if self.db.config['NFuelSetMethod'] == 1 and self.db.config['BBeginFueling'] and self.db.config['BPitCommandControl']:
                                            self.ir.pit_command(2, round(self.db.VFuelAdd + 1 + 1e-10))  # Add fuel
                                    if self.db.VFuelAdd < self.db.DriverCarFuelMaxLtr - self.db.FuelLevel + self.db.FuelAvgConsumption:
                                        self.db.textColourFuelAddOverride = self.green
                                        self.db.BTextColourFuelAddOverride = True
                                    elif self.db.VFuelAdd < self.db.DriverCarFuelMaxLtr - self.db.FuelLevel + 2 * self.db.FuelAvgConsumption:
                                        self.db.textColourFuelAddOverride = self.yellow
                                        self.db.BTextColourFuelAddOverride = True
                                    elif self.db.VFuelAdd < self.db.DriverCarFuelMaxLtr - self.db.FuelLevel + 3 * self.db.FuelAvgConsumption:
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

                            if self.db.CarIdxP2P_Status[self.db.DriverCarIdx]:
                                self.db.Alarm[4] = 1
                                if not self.db.old_PushToPass:
                                    self.db.P2PTime = self.db.SessionTime
                                    self.db.P2PCounter = self.db.P2PCounter + 1
                                    self.db.AM.P2PON.raiseAlert()

                            if not self.db.CarIdxP2P_Status[self.db.DriverCarIdx] and self.db.old_PushToPass:
                                self.db.AM.P2POFF.raiseAlert()

                            # if self.db.SessionTime < self.db.P2PTime + 20:
                            #   self.db.Alarm[4] = 1

                            self.db.old_PushToPass = self.db.CarIdxP2P_Status[self.db.DriverCarIdx]  # self.db.PushToPass

                        # alarm
                        if self.db.car.name in ['Dallara P217 LMP2', 'Porsche 911 GT3.R', 'Ferrari 488 GT3 Evo 2020', 'Mercedes GT3 2020', 'Toyota GR86',
                                                'Lamborghini GT3', 'C6R', 'AM DBR9 GT1']:
                            BTcToggle = True
                            BABSToggle = True
                        elif self.db.car.name in ['Ford Mustang GT3', 'Mercedes AMG GT4', 'Ferrari 296 GT3', 'Porsche 718 Cayman GT4']:
                            BTcToggle = False
                            BABSToggle = True
                        else:
                            BTcToggle = self.db.dcTractionControlToggle
                            BABSToggle = self.db.dcABSToggle

                        if not self.db.dcTractionControl == None:
                            if BTcToggle or self.db.dcTractionControl == self.db.car.NTC1Disabled or self.db.AM.TCOFF.BActive:
                                self.db.Alarm[1] = 3
                                self.db.Alarm[9] = 3
                            if BTcToggle or self.db.dcTractionControl2 == self.db.car.NTC2Disabled:
                                self.db.Alarm[9] = 3

                        if (not BABSToggle and self.db.dcABS) or self.db.dcABS == self.db.car.NABSDisabled :
                            self.db.Alarm[8] = 3
                        elif self.db.Brake > 0.75 and self.db.Speed > 10:
                            self.db.Alarm[8] = 2
                        # elif self.db.BrakeABSactive and self.db.Brake > 0:
                            # self.db.Alarm[8] = 1

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
                                    if np.max(self.db.FuelTGTLiftPoints['VFuelTGT']) == self.db.config['VFuelTgt'] and 'VFuelTgt' in self.db.dcChangedItems:
                                        self.db.dcChangedItems[self.db.dcChangedItems.index('VFuelTgt')] = 'Push'
                                    self.db.BFuelTgtSet = self.setFuelTgt(self.db.config['VFuelTgt'], np.float(self.db.VFuelTgtOffset))

                        self.db.dcOld = self.db.dc.copy()

                        # rear slip ratio
                        if self.db.VelocityX > 10 and not self.db.WeekendInfo['Category'] == 'Oval':
                            if self.db.Gear > 0 and self.db.car.rGearRatios[self.GearID][self.db.Gear] > 0:
                                self.db.rSlipR = (self.db.RPM / 60 * np.pi / self.db.car.rGearRatios[self.GearID][self.db.Gear] * 0.3 / self.db.VelocityX - 1) * 100
                        else:
                            self.db.rSlipR = 0

                        # wheel spin
                        if self.NGearOld < self.db.Gear and self.db.Gear > 0:
                            self.tUpshift = self.db.SessionTime
                        self.NGearOld = self.db.Gear

                        temp = 0
                        if self.db.Throttle > 0.1 and self.db.SessionTime > self.tUpshift + self.db.config['tSurpressSlipOnUpshift']:
                            for i in range(len(self.db.car.rSlipMapAcc)):
                                if self.db.rSlipR >= self.db.car.rSlipMapAcc[i]:
                                    temp = i + 1
                                else:
                                    pass

                        self.db.rWheelSpin = temp

                        # ABS Activity
                        if 'dcABS' in self.db.car.dcList or self.db.car.name in self.CarsWithABS:
                            '''if self.db.dcBrakeBias:
                                pBrakeFRef = self.db.car.pBrakeFMax * self.db.dcBrakeBias / 100 * self.Brake
                                pBrakeRRef = self.db.car.pBrakeFMax * (1 - self.db.dcBrakeBias / 100) * self.Brake
                            else:
                                pBrakeFRef = self.db.car.pBrakeFMax * self.Brake
                                pBrakeRRef = self.db.car.pBrakeRMax * self.Brake

                            dpBrake = [self.db.LFbrakeLinePress - pBrakeFRef, self.db.RFbrakeLinePress - pBrakeFRef, self.db.LRbrakeLinePress - pBrakeRRef, self.db.RRbrakeLinePress - pBrakeRRef]

                            self.db.rABSActivity = list(map(self.mapABSActivity, np.array([dpBrake, self.dpBrakeOld]).max(axis=0)))

                            self.dpBrakeOld = dpBrake'''

                            tABSActive = 0
                            if self.db.BrakeABSactive:
                                if self.tABSLastActivated:
                                    tABSActive = self.db.SessionTime - self.tABSLastActivated
                                    self.db.rABSActivity = self.ABSActivationMap(tABSActive) * [1, 1, 1, 1]
                                else:
                                    self.tABSLastActivated = self.db.SessionTime
                                    self.db.rABSActivity = [0, 0, 0, 0]
                            else:
                                self.tABSLastActivated = None
                                self.db.rABSActivity = [0, 0, 0, 0]

                            
                        else:  # rear locking
                            temp = 0
                            if self.db.Brake > 0.1:
                                for i in range(len(self.db.car.rSlipMapBrk)):
                                    if self.db.rSlipR <= self.db.car.rSlipMapBrk[i]:
                                        temp = i + 1
                                    else:
                                        pass

                            self.db.rRearLocking = temp

                        # Start mode detection
                        if self.db.BSteeringWheelStartMode and not self.db.BStartMode:
                            self.db.BStartMode = True
                            self.db.NDDUPage = 4
                        elif self.db.BStartMode and not self.db.BSteeringWheelStartMode:
                            if self.tStartModeEnd == -1:
                                self.tStartModeEnd = self.db.SessionTime
                            elif (self.tStartModeEnd > 0 or self.tStartCompleted > 0) \
                                    and (self.db.SessionTime - self.tStartModeEnd > 5 or self.tStartCompleted - self.tStartCompleted > 5):
                                self.db.BStartMode = False
                                self.db.NDDUPage = 1
                                self.tStartModeEnd = -1
                                self.tStartCompleted = -1

                        # start mode timing logics
                        if self.db.BStartMode:
                            if not self.BClutchRelased and not self.BStartCompleted:
                                self.db.tStart100 = 0
                                self.db.tStartReaction = 0
                                self.BStartCompleted = False
                                if self.db.Clutch > 0.1:
                                    self.BClutchRelased = True
                                    self.tStart100Timer = self.db.SessionTime
                                    if self.db.SessionFlags & 0x80000000:
                                        self.db.tStartReaction = self.db.SessionTime - self.db.GreenTime
                                        self.logger.info('Start Reaction Time: {}'.format(np.round(self.db.tStartReaction, 2)))
                            else:
                                if self.db.Clutch > 0.05 and self.db.Speed > (100 / 3.6) and not self.BStartCompleted:
                                    self.db.tStart100 = self.db.SessionTime - self.tStart100Timer
                                    self.BStartCompleted = True
                                    self.tStartCompleted = self.db.SessionTime
                                    self.logger.info('Start Launch Time (0-100): {} | Bite Point: {}'.format(np.round(self.db.tStart100, 2), np.round(self.db.config['rBitePoint'], 1)))

                        elif self.BStartCompleted:
                            self.BClutchRelased = False
                            self.BStartCompleted = False
                        
                        # Oval Downshift Logic
                        if True : # self.db.WeekendInfo['Category'] == 'Oval':
                            if self.db.Gear > 1 and self.db.Gear <= self.db.car.NGearMax:
                                if (self.db.RPM / self.db.car.rGearRatios[self.GearID][self.db.Gear] * self.db.car.rGearRatios[self.GearID][self.db.Gear-1]) < self.db.car.UpshiftSettings[self.GearID]['nMotorShiftLEDs'][self.db.Gear-2][0]:
                                    self.db.Alarm[10] = 1
                                else:
                                    self.db.Alarm[10] = 0
                            else:
                                self.db.Alarm[10] = 0
                        
                    else:
                        if self.db.WasOnTrack:
                            self.db.NDDUPage = 1
                            self.db.WasOnTrack = False
                            self.db.init = True
                            self.logger.info('Ending Run - {} laps completed, {} in total'.format(self.db.StintLap, self.db.Lap))
                            if len(self.db.FuelConsumptionList) > 0:
                                self.logger.info('Fuel Consumption - Avg: {} - Min: {} - Max: {}'.format(convertString.roundedStr2(self.db.FuelAvgConsumption),
                                                                                                         convertString.roundedStr2(np.min(self.db.FuelConsumptionList)),
                                                                                                         convertString.roundedStr2(np.max(self.db.FuelConsumptionList))))
                            self.db.track.setLapTime(self.db.car.name, self.db.LapBestLapTime)
                            self.db.track.save(self.db.dir)
                            self.db.AM.resetAll()

                        # do if car is not on track but don't do if car is on track ------------------------------------------------
                        self.init = True
                        TireType = None
                        
                        if self.db.car.BWetTiresAvailable and self.db.CarSetup:
                            if 'TiresAero' in self.db.CarSetup:
                                if  'TireType' in self.db.CarSetup['TiresAero']:
                                    TireType = self.db.CarSetup['TiresAero']['TireType']['TireType']
                            if 'Tires' in self.db.CarSetup:
                                if  'TireType' in self.db.CarSetup['Tires']:
                                    TireType = self.db.CarSetup['Tires']['TireType']['TireType']
                            if TireType:
                                if (self.db.TrackWetness > 1 or self.db.WeatherDeclaredWet) and TireType == 'Dry':
                                    self.db.BTyreChoiceWarning = 1
                                    self.db.AM.CHECKTIRES.raiseAlert()
                                elif (self.db.TrackWetness == 0 or not self.db.WeatherDeclaredWet) and TireType == 'Wet':
                                    self.db.BTyreChoiceWarning = 2
                                    self.db.AM.CHECKTIRES.raiseAlert()
                                else:
                                    self.db.BTyreChoiceWarning = 0
                                    self.db.AM.CHECKTIRES.cancelAlert()

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
                        self.loadTrack('default')
                        self.loadCar('default', 'default')  # TODO: required?
                        # self.db.car = Car.Car(Driver=self.db.DriverInfo['Drivers'][self.db.DriverCarIdx])
                        # self.db.car.createCar(self.db)
                        # self.db.car.save(self.db.dir)
                        self.logger.info('Lost connection to iRacing')

                self.db.tExecuteCalc = (time.perf_counter() - t) * 1000
                self.toc()
                time.sleep(self.rate)

            except Exception:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                s = traceback.format_exception(exc_type, exc_value, exc_traceback, limit=2, chain=True)
                S = '\n'
                for i in s:
                    S = S + i
                self.logger.error(S)

    @a_new_decorator
    def initSession(self):
        self.logger.info('===== Initialising Session: {} =========================='.format(self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionType']))
        time.sleep(0.3)
        self.trackList = importExport.getFiles(self.dir + '/data/track', 'json')
        self.carList = importExport.getFiles(self.dir + '/data/car', 'json')
        self.db.init = True
        self.db.BResults = False
        if self.db.WeatherDeclaredWet:
            tempWetnessStr = 'Wetness: {}     Precipitation: {}'.format(self.db.TrackWetness, convertString.roundedStr0(self.db.Precipitation*100))
        else:
            tempWetnessStr = 'Wetness: Dry'
        self.db.weatherStr = 'TAir: {}°C     TTrack: {}°C     {}     vWind: {} km/h'.format(convertString.roundedStr0(self.db.AirTemp),
                                                                                            convertString.roundedStr0(self.db.TrackTemp), 
                                                                                            tempWetnessStr, 
                                                                                            convertString.roundedStr0(self.db.WindVel * 3.6))
        self.db.FuelConsumptionList = []
        self.db.FuelLastCons = 0
        self.db.newLapTime = 0
        self.db.oldLap = self.db.Lap
        self.db.NLapsTotal = 0
        self.db.TrackLength = float(self.db.WeekendInfo['TrackLength'].split(' ')[0])
        self.db.config['MapHighlight'] = False
        self.db.Alarm = np.array([0] * 11)
        self.db.BMultiInitRequest = True

        if self.db.startUp:
            self.db.StartDDU = False
            self.db.oldSessionNum = self.db.SessionNum
            self.db.DriverCarFuelMaxLtr = self.db.DriverInfo['DriverCarFuelMaxLtr'] * self.db.DriverInfo['DriverCarMaxFuelPct']
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
                self.logger.info('Creating Track')

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

                self.logger.info('Created Car ' + carName)

            self.logger.info('TrackName: ' + self.db.WeekendInfo['TrackDisplayName'])
            self.logger.info('SessionType: ' + self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionType'])

            if self.db.WeekendInfo['Category'] == 'DirtRoad':
                self.db.__setattr__('RX', True)
                self.db.__setattr__('JokerLapsRequired', self.db.WeekendInfo['WeekendOptions']['NumJokerLaps'])
                self.db.config['MapHighlight'] = True
                self.db.RenderLabel[17] = True
            else:
                self.db.__setattr__('RX', False)
                self.db.RenderLabel[17] = False

            self.db.config['PitStopsRequired'] = 0
            self.db.config['MapHighlight'] = False

            tempSessionLength = self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionTime']
            if not tempSessionLength == 'unlimited':
                self.db.SessionLength = float(tempSessionLength.split(' ')[0])
            if self.db.WeekendInfo['TrackName'] in self.db.car.tLap:
                tLapEst = self.db.car.tLap[self.db.WeekendInfo['TrackName']][-1]
            else:
                tLapEst = None

            # unlimited laps
            if self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionLaps'] == 'unlimited':
                self.db.config['RaceLaps'] = self.db.config['UserRaceLaps']
                self.db.LapLimit = False
                self.db.RenderLabel[20] = False
                self.db.RenderLabel[21] = False

                # unlimited time
                if self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionTime'] == 'unlimited':
                    self.db.SessionLength = 86400
                    self.db.RenderLabel[15] = False
                    self.db.RenderLabel[16] = True
                    self.db.TimeLimit = False
                # limited time
                else:
                    self.db.RenderLabel[15] = True  # 15 Remain
                    self.db.RenderLabel[16] = False  # 16 Elapsed
                    self.db.TimeLimit = True
                    if self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionType'] == 'Race':
                        if self.db.SessionLength > 2100:
                            self.db.config['PitStopsRequired'] = 1
                            self.db.config['MapHighlight'] = True
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
                    if (self.db.TrackLength * self.db.config['RaceLaps']) > 145:
                        self.db.config['PitStopsRequired'] = 1
                        self.db.config['MapHighlight'] = True
                # unlimited time
                if self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionTime'] == 'unlimited':
                    self.db.SessionLength = 86400
                    self.db.TimeLimit = False
                    self.db.RenderLabel[15] = True
                    self.db.RenderLabel[16] = False
                    if tLapEst:
                        if self.db.SessionLength > self.db.config['RaceLaps'] * 1.05 * tLapEst:
                            self.db.RenderLabel[15] = False  # remain
                            self.db.RenderLabel[16] = True  # elapsed
                            self.db.TimeLimit = True

                # limited time
                else:
                    self.db.RenderLabel[15] = True
                    self.db.RenderLabel[16] = False
                    self.db.TimeLimit = True
                    if tLapEst:
                        if self.db.SessionLength > self.db.config['RaceLaps'] * 1.05 * tLapEst:
                            self.db.RenderLabel[15] = False
                            self.db.RenderLabel[16] = True

            if self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionType'] == 'Race' and (not self.db.LapLimit) and self.db.TimeLimit:
                self.db.config['BEnableRaceLapEstimation'] = True
                if self.db.WeekendInfo['TrackName'] in self.db.car.tLap:
                    NLapRaceTime = (self.db.SessionLength - (np.int(self.db.config['PitStopsRequired']) * self.db.config['PitStopDelta'])) / self.db.car.tLap[self.db.WeekendInfo['TrackName']][-1]
                    self.db.NLapDriver = float(NLapRaceTime)
                    self.db.config['RaceLaps'] = int(self.db.NLapDriver + 1)
            else:
                self.db.config['BEnableRaceLapEstimation'] = False

            # # Fuel to finish
            # if (self.db.WeekendInfo['TrackName'] in self.db.car.tLap or self.db.LapLimit) and self.db.WeekendInfo['TrackName'] in self.db.car.VFuelLap:
            #     self.db.config['RaceLaps']



            CarNumber = len(self.db.DriverInfo['Drivers']) + 2
            if not self.db.LapLimit:
                LapNumber = int(self.db.SessionLength / (self.db.TrackLength * 13)) + 2
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
        self.db.SessionTypeOld = self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionType']

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

        # check if setup has changed since quali
        if 'Qual' in self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionType']:
            self.BRanQuali = True

        if self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionType'] == 'Race' and not self.db.WeekendInfo['WeekendOptions']['IsFixedSetup'] and self.db.LastSetup:
            CurrentSetup = {'DriverSetupName': self.db.DriverInfo['DriverSetupName'],
                            'UpdateCount': self.db.CarSetup['UpdateCount'],
                            'FuelLevel': self.db.FuelLevel}

            if (self.db.DriverInfo['DriverSetupName'] == self.db.LastSetup['DriverSetupName'] or self.db.FuelLevelDisp < 0.1 * self.db.DriverCarFuelMaxLtr) and self.BRanQuali:
                self.db.BLoadRaceSetupWarning = True

            # if self.db.FuelLevelDisp < 0.99 * self.db.DriverCarFuelMaxLtr and self.db.FuelLevelDisp:
            #     self.db.BLowRaceFuelWarning = True
        
        self.initSpeedProfile()

    @a_new_decorator
    def loadTrack(self, name):
        self.logger.info('Loading track: ' + r"track/" + name + '.json')
        
        self.db.track = Track.Track(name)
        self.db.track.load("data/track/" + name + '.json')

        self.logger.info('successfull')

    @a_new_decorator
    def loadCar(self, name, carPath):  # TODO: required?
        self.logger.info('Loading car: ' + r"car/" + name + '.json')

        self.db.car = Car.Car(name=name, carPath=carPath)
        self.db.car.load("data/car/" + name + '.json')

        self.db.queryData.extend(list(self.db.car.dcList.keys()))

        if self.db.car.UpshiftSettings['base']['BValid']:
            self.db.config['UpshiftStrategy'] = 5
        else:
            self.db.config['UpshiftStrategy'] = self.db.car.UpshiftStrategy

        self.logger.info('Successful')

        time.sleep(0.2)

    @a_new_decorator
    def newLap(self):
        # Lap Counting
        self.db.newLapTime = self.db.SessionTime

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

        if self.db.LapsToGo == 0:
            VFuelConsumptionTargetFinish = (self.db.FuelLevel - 0.3)
        else:
            VFuelConsumptionTargetFinish = (self.db.FuelLevel - 0.3) / self.db.LapsToGo
        NLapStintRemaining = self.db.config['NLapsStintPlanned'] - self.db.StintLap
        if NLapStintRemaining > 0:
            VFuelConsumptionTargetStint = (self.db.FuelLevel - 0.3) / NLapStintRemaining

        if self.db.config['NFuelTargetMethod'] == 2:  # Finish
            self.db.BFuelTgtSet = self.setFuelTgt(VFuelConsumptionTargetFinish, 0)
        elif self.db.config['NFuelTargetMethod'] == 3:  # Stint
            if self.db.config['PitStopsRequired'] > 0 and self.db.config['PitStopsRequired'] <= self.db.CarIdxPitStops[self.db.DriverCarIdx]:
                self.db.BFuelTgtSet = self.setFuelTgt(VFuelConsumptionTargetFinish, 0)
            else:
                self.db.BFuelTgtSet = self.setFuelTgt(VFuelConsumptionTargetStint, 0)

        if self.db.WeatherDeclaredWet:
            tempWetnessStr = 'Wetness: {}     Precipitation: {}'.format(self.db.TrackWetness, convertString.roundedStr0(self.db.Precipitation*100))
        else:
            tempWetnessStr = 'Wetness: Dry'
            
        self.db.weatherStr = 'TAir: {}°C     TTrack: {}°C     {}     vWind: {} km/h'.format(convertString.roundedStr0(self.db.AirTemp),
                                                                                            convertString.roundedStr0(self.db.TrackTemp), 
                                                                                            tempWetnessStr, 
                                                                                            convertString.roundedStr0(self.db.WindVel * 3.6))

        # display fuel consumption information
        self.db.RenderLabel[4] = True
        self.db.RenderLabel[5] = True
        self.db.RenderLabel[28] = False
        self.db.RenderLabel[29] = False

        self.db.StintLap = self.db.StintLap + 1
        self.db.NLapsTotal += 1

        if (self.BCreateTrack or self.BRecordtLap) and self.Logging:
            self.createTrackFile(self.BCreateTrack, self.BRecordtLap)

        if (self.BCreateTrack or self.BRecordtLap) and not self.db.OutLap and self.db.StintLap > 0:
            # Logging track data
            if not self.Logging:
                self.logLap = self.db.Lap
                self.Logging = True
                self.timeLogingStart = self.db.SessionTime

        # self.logger.info('Fuel Budget used up to Timing Line: {}'.format(np.round(self.db.VFuelStartStraight - self.db.FuelLevel , 3)))
        # self.logger.info('Fuel Budget up to Timing Line: {}'.format(np.round(self.db.VFuelBudgetActive , 3)))

    @a_new_decorator
    def createTrackFile(self, BCreateTrack, BRecordtLap):

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

            tempdx = np.append(tempdx, self.dx[1:len(self.dx)] - xError / (len(self.dx) - 1))
            tempdy = np.append(tempdy, self.dy[1:len(self.dy)] - yError / (len(self.dy) - 1))

            self.x = np.cumsum(tempdx, dtype=float)
            self.y = np.cumsum(tempdy, dtype=float)

            # self.x = np.cumsum([np.array(self.dx) - xError / len(tempx)], dtype=float)
            # self.y = np.cumsum([np.array(self.dy) - yError / len(tempy)], dtype=float)

            self.x[-1] = 0
            self.y[-1] = 0

            self.db.track = Track.Track(self.db.WeekendInfo['TrackName'])

            aNorth = self.YawNorth[0]

            self.db.track.createTrack(self.x, self.y, self.LapDistPct, aNorth, self.db.TrackLength * 1000)
            self.db.track.setLapTime(self.db.car.name, self.time[-1])
            self.db.track.save(self.db.dir)

            self.db.LapDistPct = self.db.track.LapDistPct

            self.logger.info(':Track has been successfully created')
            self.logger.info(':Saved track as: ' + r"data/track/" + self.db.track.name + ".json")

        if BRecordtLap:
            while not maths.strictly_increasing(self.time):
                self.time, self.LapDistPct = maths.makeMonotonic2D(self.time, self.LapDistPct)
            while not maths.strictly_increasing(self.LapDistPct):
                self.LapDistPct, self.time = maths.makeMonotonic2D(self.LapDistPct, self.time)

            self.db.car.addLapTime(self.db.WeekendInfo['TrackName'], self.time, self.LapDistPct, self.db.track.LapDistPct, self.db.FuelConsumptionList[-1])
            self.db.car.save(self.db.dir)
            self.db.time = self.db.car.tLap[self.db.WeekendInfo['TrackName']]

            self.db.track.setLapTime(self.db.car.name, self.time[-1])
            self.db.track.save(self.db.dir)

            self.logger.info('Lap time has been recorded successfully: {} s'.format(convertString.convertTimeMMSSsss(self.time[-1])))
            self.logger.info('Saved car as: ' + r"data/car/" + self.db.car.name + ".json")
            self.logger.info('Saved track as: ' + r"data/track/" + self.db.track.name + ".json")

        self.BCreateTrack = False
        self.BRecordtLap = False
        self.Logging = False

    @a_new_decorator
    def SOFstring(self):
        if self.db.NClasses > 1:
            temp = 'SOF: ' + convertString.roundedStr0(self.db.SOFMyClass) + '('
            keys = self.db.classStruct.keys()
            for i in range(0, self.db.NClasses):
                temp = temp + self.db.classStruct[keys[i]] + ': ' + convertString.roundedStr0(self.db.classStruct[keys[i]]['SOF'])
            self.db.SOFstr = temp + ')'
        else:
            self.db.SOFstr = 'SOF: ' + convertString.roundedStr0(self.db.SOF)

    @a_new_decorator
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

    @a_new_decorator
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

    @a_new_decorator
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
    @a_new_decorator
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

    @a_new_decorator
    def LiftTone(self):
        # self.db.Alarm[7] = 4

        if not self.db.BFuelTgtSet:
            self.db.BFuelTgtSet = self.setFuelTgt(self.db.config['VFuelTgt'], np.float(self.db.VFuelTgtOffset))

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
                self.db.BForceLift = False
                self.db.BCancelAutoLift = False

                if self.db.SessionTime - self.db.newLapTime > self.db.config['tDisplayConsumption']:
                    self.db.RenderLabel[4] = False
                    self.db.RenderLabel[5] = False
                    self.db.RenderLabel[28] = True
                    self.db.RenderLabel[29] = True

            # check if in Lift Zone
            LapDistPct = self.db.LapDistPct * 100
            if self.db.NNextLiftPoint == 0:
                LapDistPctEnd = 100 + self.db.FuelTGTLiftPoints['LapDistPctReference'][self.db.NNextLiftPoint]
                ds = 100 - self.db.FuelTGTLiftPoints['LapDistPctWOT'][-1] + self.db.FuelTGTLiftPoints['LapDistPctReference'][self.db.NNextLiftPoint]
                LapDistPctStart = self.db.FuelTGTLiftPoints['LapDistPctWOT'][-1] + ds / 2
                if LapDistPct < self.db.FuelTGTLiftPoints['LapDistPctWOT'][-1]:
                    LapDistPct = LapDistPct + 100
                BInLiftZone = LapDistPctStart < LapDistPct < LapDistPctEnd
            else:
                LapDistPctEnd = self.db.FuelTGTLiftPoints['LapDistPctReference'][self.db.NNextLiftPoint]
                LapDistPctWOT = self.db.FuelTGTLiftPoints['LapDistPctWOT'][self.db.NNextLiftPoint - 1]
                LapDistPctStart = LapDistPctWOT + (LapDistPctEnd - LapDistPctWOT) / 2
                BInLiftZone = LapDistPctStart < LapDistPct < LapDistPctEnd

            self.db.BInLiftZone = BInLiftZone

            # Auto Lift and Clutch
            if BInLiftZone and self.db.Speed > 15:
                # auto lift
                if self.db.BEnableAutoLift and self.db.BLiftBeepPlayed[self.db.NNextLiftPoint] == 3 and not self.db.AM.CANCELLIFT.BActive:
                    self.db.BForceLift = True
                else:
                    if self.db.Brake > 0:
                        self.db.BForceLift = False

                # auto clutch
                if self.db.BEnableAutoClutch and self.db.Throttle == 0 and self.db.Brake == 0:
                    self.db.BForceClutch = True
                else:
                    self.db.BForceClutch = False

                if self.db.AM.CANCELLIFT.BActive and (self.db.Throttle == 0 or self.db.Brake > 0):
                    self.db.AM.CANCELLIFT.reset()
            else:
                self.db.AM.CANCELLIFT.reset()
                if self.db.BForceClutch:
                    self.db.BForceClutch = False
                if self.db.BForceLift:
                    self.db.BForceLift = False

    @a_new_decorator
    def setFuelTgt(self, tgt, offset):
        if self.db.BFuelSavingConfigLoaded:
            BTGTSet = False
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

                BTGTSet = True

            self.db.LapDistPctLift = self.db.LapDistPctLift

            self.db.BLiftBeepPlayed = [0] * len(self.db.FuelTGTLiftPoints['LapDistPctLift'])

            return BTGTSet
        else:
            return False

    @a_new_decorator
    def getNStraight(self):
        # 0 = approaching first corner
        d = np.array(self.db.FuelTGTLiftPoints['LapDistPctApex']) / 100 - self.db.LapDistPct

        d = np.where(d >= 0)

        if len(d[0]) > 0:
            d = np.min(d)
        else:
            d = 0

        self.db.NNextLiftPoint = np.min(d)

    @a_new_decorator
    def mapABSActivity(self, pBrake):
        if pBrake < self.db.car.rABSActivityMap[3]:
            return 4
        if pBrake < self.db.car.rABSActivityMap[2]:
            return 3
        elif pBrake < self.db.car.rABSActivityMap[1]:
            return 2
        elif pBrake < self.db.car.rABSActivityMap[0]:
            return 1
        else:
            return 0
    
    @a_new_decorator
    def yellowFlag(self):
        
        # vCar calculation
        if not self.db.SessionTick == self.db.SessionTickOld:
            # self.SessionTickOld = self.SessionTick
            # self.SessionTick = self.db.SessionTick
            
            # self.x0 = self.x1
            # self.x1 = np.array(self.db.CarIdxLapDistPct)
            
            # self.t0 = self.t1
            # self.t1 = self.db.SessionTime
            
            # dt = self.t1 - self.t0
            dt = self.db.SessionTime - self.db.SessionTimeOld
            
            if dt <= 0 or dt > 0.1:
                return
            
            dx = np.array(self.db.CarIdxLapDistPct) - np.array(self.db.CarIdxLapDistPctOld)
            
            # CarIdxSpeed = np.mod(self.x1-self.db.x0, 1)*self.db.TrackLength*1000/dt*3.6
            CarIdxSpeed = np.sign(dx)*np.mod(np.abs(dx), 1)*self.db.TrackLength*1000/dt*3.6      
            CarIdxSpeed = np.where(np.isnan(CarIdxSpeed), 0, CarIdxSpeed)
            CarIdxSpeed = np.where(CarIdxSpeed<0, self.db.CarIdxSpeed[:, 1], np.where(CarIdxSpeed>400, self.db.CarIdxSpeed[:, 1], CarIdxSpeed))
            
            self.db.CarIdxSpeed[:, 0] = self.db.CarIdxSpeed[:, 1]
            self.db.CarIdxSpeed[:, 1] = self.db.CarIdxSpeed[:, 2]
            self.db.CarIdxSpeed[:, 2] = CarIdxSpeed
                        
            # if abs(self.x1-self.x0) > 0.9: 
            #     # crossing finish line
            #     self.db.CarIdxSpeed = np.mod(self.x1-self.x0, 1)*self.db.TrackLength*1000/dt*3.6
            # else:
            #     if self.x1 >= self.x0:
            #         # forwards
            #         self.db.CarIdxSpeed = np.mod(self.x1-self.x0, 1)*self.db.TrackLength*1000/dt*3.6
            #     else:
            #         # reverse
            #         self.db.CarIdxSpeed = np.mod(self.x1-self.x0, 1)*self.db.TrackLength*1000/dt*3.6
                    
            
        # filter cars: only on track, not in pitlane, within x meter in front 
        # CarIdxInRange = np.logical_and.reduce(np.logical_xor(np.array(self.db.CarIdxTrackSurface) == 0, np.array(self.db.CarIdxTrackSurface) == 3), 
        #                                       np.logical_not(self.db.CarIdxOnPitRoad), 
        #                                       np.mod(np.array(self.db.CarIdxLapDistPct) - np.array(self.db.LapDistPct), 1) * self.db.TrackLength * 1000 <= 250)
        
        CarIdxInRange = np.logical_and(
                            np.logical_and(
                                np.logical_xor(
                                    np.array(self.db.CarIdxTrackSurface) == 0, 
                                    np.array(self.db.CarIdxTrackSurface) == 3), 
                                np.logical_not(self.db.CarIdxOnPitRoad)), 
                            np.mod(np.array(self.db.CarIdxLapDistPct) - np.array(self.db.LapDistPct), 1) * self.db.TrackLength * 1000 <= 250)
        
        
        CarIdxInRange[self.db.DriverCarIdx] = False
        CarIdxInRange[self.db.DriverInfo['PaceCarIdx']] = False
                
        if self.db.SessionState == 4 and self.db.IsOnTrack and not self.db.OnPitRoad and self.db.SessionTime > 5 + self.db.GreenTime:
            # if not self.db.track.name == 'default' and self.db.car.name in self.db.track.tLap:
            #     # it speed profile take this as reference
            #     pass
            # else:
            #    # if not speed profile take minimum speed as reference
            #    # check for too slow cars
            
            if self.db.WeatherDeclaredWet:
                rWeatherGain = 0.55
            else:
                rWeatherGain = 1
            
            if self.db.BSpeedProfile:
                if np.any(np.logical_and(CarIdxInRange, np.logical_or(np.max(self.db.CarIdxSpeed, axis=1) < rWeatherGain * self.vYellowFlag(np.array(self.db.CarIdxLapDistPct, dtype=float)*100), np.max(self.db.CarIdxSpeed, axis=1) < 30))):
                    self.db.BYellow = True
                else:
                    self.db.BYellow = False
            else:
                if np.any(np.logical_and(CarIdxInRange, np.max(self.db.CarIdxSpeed, axis=1) < 30)):
                    self.db.BYellow = True
                else:
                    self.db.BYellow = False                
        else:
            self.db.BYellow = False
        
    @a_new_decorator
    def blueFlag(self):
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
    
    @a_new_decorator
    def initSpeedProfile(self):
        if self.db.track.LapDistPctPitIn and \
            self.db.track.LapDistPctPitOut and \
            self.db.track.LapDistPctPitDepart and \
            self.db.track.LapDistPctPitRemerged and \
            self.db.track.name in self.db.car.tLap and \
            self.db.WeekendInfo['TrackName']     == self.db.track.name and \
            self.db.car.name == self.db.DriverInfo['Drivers'][self.db.DriverCarIdx]['CarScreenNameShort']:
            
            vPSL = float(self.db.WeekendInfo['TrackPitSpeedLimit'].split(' ')[0])
            
            dt = np.diff(self.db.car.tLap[self.db.track.name])
            ds = np.diff(np.array(self.db.track.LapDistPct)/100) * self.db.track.sTrack
            vRaw = ds / dt * 3.6
            vRaw[[0,1,-2,-1]] = np.mean(vRaw[[2, 3, -4, -3]])
            
            v = 0.95 * vRaw - 10
            
            NIdxPitIn = next(i for i, x in enumerate(self.db.track.LapDistPct) if x > self.db.track.LapDistPctPitIn)
            NIdxPitOut = next(i for i, x in enumerate(self.db.track.LapDistPct) if x > self.db.track.LapDistPctPitOut)-1
            NIdxPitDepart = next(i for i, x in enumerate(self.db.track.LapDistPct) if x > self.db.track.LapDistPctPitDepart)-1
            NIdxPitRemerged = next(i for i, x in enumerate(self.db.track.LapDistPct) if x > self.db.track.LapDistPctPitRemerged)

            v[NIdxPitDepart:NIdxPitIn] = vPSL + np.linspace(1,0,NIdxPitIn - NIdxPitDepart)* (v[NIdxPitDepart] - vPSL)
            v[NIdxPitOut:NIdxPitRemerged] = vPSL + np.linspace(0,1,NIdxPitRemerged - NIdxPitOut)* (v[NIdxPitRemerged] - vPSL)
            
            
            self.vYellowFlag = interpolate.interp1d(self.db.track.LapDistPct[:-1], v, fill_value="extrapolate")
            self.db.BSpeedProfile = True

