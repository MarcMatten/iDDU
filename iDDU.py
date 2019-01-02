# import all required packages
import time

from gui.iDDUgui import iDDUgui
import iDDURender
import iDDUcalc
from functionalities.RTDB import RTDB
from functionalities.UpshiftTone import UpshiftTone

# data for initialisation of RTDB
# helper variables
helpData = {'done': False, 'timeStr': 0, 'waiting': False, 'LabelSessionDisplay': [1, 1, 1, 0, 1, 1]}
# data from iRacing
iRData = {'LapBestLapTime': 0, 'LapLastLapTime': 0, 'LapDeltaToSessionBestLap': 0, 'dcFuelMixture': 0,
          'dcThrottleShape': 0, 'dcTractionControl': 0, 'dcTractionControl2': 0, 'dcTractionControlToggle': 0,
          'dcABS': 0, 'dcBrakeBias': 0, 'FuelLevel': 0, 'Lap': 0, 'IsInGarage': 0, 'LapDistPct': 0, 'OnPitRoad': 0,
          'PlayerCarClassPosition': 0, 'PlayerCarPosition': 0, 'SessionLapsRemain': 0, 'Throttle': 0,
          'SessionTimeRemain': 0, 'SessionTime': 0, 'SessionFlags': 0, 'SessionNum': 0, 'IsOnTrack': False, 'Gear': 0,
          'Speed': 0, 'DriverInfo': {'DriverCarIdx': 0, 'DriverCarFuelMaxLtr': 0, 'DriverCarMaxFuelPct': 1,
                                     'Drivers': [], 'DriverPitTrkPct' : 0}, 'CarIdxLapDistPct': [0],
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

# Create RTDB and initialise with
myRTDB = RTDB.RTDB()
myRTDB.initialise(helpData)
myRTDB.initialise(iRData)
myRTDB.initialise(calcData)

# initialise and start thread
thread1 = RTDB.iRThread(myRTDB, list(iRData.keys()), 0.01)
thread2 = UpshiftTone.UpShiftTone(myRTDB, 0.01)
thread3 = iDDUgui(myRTDB, 0.1)
thread1.start()
time.sleep(1)
thread3.start()
time.sleep(1)
thread2.start()
time.sleep(1)

# create objects for rendering and calculation
iDDUcalc = iDDUcalc.IDDUCalc(myRTDB)

# loop to run programme
while not myRTDB.done:
    iDDUcalc.calc()
    if myRTDB.DDUrunning:
        if myRTDB.StartDDU:
            myRTDB.StartDDU = False
        myRTDB.done = iRRender.render()
    elif myRTDB.StartDDU:
        print(myRTDB.timeStr+': Starting DDU')
        iRRender = iDDURender.RenderScreen(myRTDB)
        myRTDB.StartDDU = False
        myRTDB.DDUrunning = True
    if myRTDB.StopDDU:
        print(myRTDB.timeStr+': Stopping DDU')
        iRRender.stop()
        myRTDB.StopDDU = False
        myRTDB.DDUrunning = False

iRRender.pygame.quit()
del iRRender
del iDDUcalc
del thread1
del thread2
del thread3
exit()
