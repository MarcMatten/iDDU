from functionalities.MultiSwitch import MultiSwitch
from functionalities.RTDB import RTDB
from libs import Car
import os

calcData = {'startUp': False,
            'LastFuelLevel': 0,
            'SessionInfoAvailable': False,
            'SessionNum': 0,
            'init': False,
            'BWasOnPitRoad': False,
            'BDDUexecuting': False,
            'WasOnTrack': False,
            'StintLap': 0,
            'oldSessionNum': -1,
            'oldLap': 0.1,
            'FuelConsumptionList': [],
            'FuelAvgConsumption': 0,
            'NLapRemaining': 0,
            'VFuelAdd': 0,
            'FuelLastCons': 0,
            'OutLap': True,
            'oldSessionlags': 0,
            'LapsToGo': 27,
            'Run': 0,
            'SessionLapRemain': 0,
            'FuelConsumptionStr': '6.35',
            'RemLapValueStr': '9.3',
            'FuelLapStr': '6.3',
            'FuelAddStr': '23.6',
            'ToGoStr': '102/256',
            'FlagCallTime': 0,
            'FlagException': False,
            'FlagExceptionVal': 0,
            'Alarm': [0]*10,
            'dir': os.getcwd(),
            'VFuelAddOld': 1,
            'GreenTime': 0,
            'RemTimeValue': 0,
            'RaceLaps': 37,
            'JokerStr': '2/2',
            'dist': [],
            'x': [],
            'y': [],
            'map': [],
            'RX': False,
            'BCreateTrack': True,
            'dx': [],
            'dy': [],
            'logLap': 0,
            'Logging': False,
            'tempdist': -1,
            'StartUp': False,
            'oldSessionFlags': 0,
            'backgroundColour': (0, 0, 0),
            'textColourFuelAdd': (255, 255, 255),
            'textColourFuelAddOverride': (255, 255, 255),
            'BTextColourFuelAddOverride': False,
            'textColour': (255, 255, 255),
            'FuelLaps': 1,
            'FuelAdd': 1,
            'PitStopDelta': 61,
            'time': [],
            'UpshiftStrategy': 0,
            'UserShiftRPM': [100000, 100000, 100000, 100000, 100000, 100000, 100000],
            'UserShiftFlag': [1, 1, 1, 1, 1, 1, 1],
            'iRShiftRPM': [100000, 100000, 100000, 100000],
            # 'ShiftToneEnabled': True,
            'StartDDU': False,
            'StopDDU': False,
            'DDUrunning': False,
            'UserRaceLaps': 0,
            'SessionLength': 86400,
            'CarIdxPitStops': [0] * 64,
            'CarIdxOnPitRoadOld': [True] * 64,
            'PitStopsRequired': 0,
            'old_DRS_Status': 0,
            'DRSActivations': 8,
            'P2PActivations': 12,
            'DRSActivationsGUI': 8,
            'P2PActivationsGUI': 12,
            'JokerLapDelta': 2,
            'JokerLaps': 1,
            'MapHighlight': False,
            'old_PushToPass': False,
            'textColourDRS': (255, 255, 255),
            'textColourP2P': (255, 255, 255),
            'textColourJoker': (255, 255, 255),
            'DRSCounter': 0,
            'P2PCounter': 0,
            'P2PStr': '12',
            'DRSStr': '12',
            'RenderLabel': [
                True,  # 0 Best
                True,  # 1 Last
                True,  # 2 Delta
                True,  # 3 FuelLevel
                True,  # 4 FuelCons
                True,  # 5 FuelLastCons
                True,  # 6 FuelLaps
                True,  # 7 FuelAdd
                True,  # 8 ABS
                True,  # 9 BBias
                True,  # 10 Mix
                True,  # 11 TC1
                True,  # 12 TC2
                True,  # 13Lap
                True,  # 14 Clock
                True,  # 15 Remain
                False,  # 16 Elapsed
                True,  # 17 Joker
                False,  # 18 DRS
                False,  # 19 P2P
                True,  # 20 ToGo
                True,  # 21 Est
                True,  # 22 Gear
                True,  # 23 Speed
                True,  # 24 Position
                True,  # 25 Distance to pit stall
                True,  # 26 speed in pit lane
                True,  # 27 Gear in pit lane
            ],
            'P2P': False,
            'DRS': False,
            'LapLimit': False,
            'TimeLimit': False,
            'P2PTime': 0,
            'DRSRemaining': 0,
            'dcFuelMixtureOld': 0,
            'dcFuelMixture': 0,
            'dcThrottleShapeOld': 0,
            'dcThrottleShape': 0,
            'dcTractionControlOld': 0,
            'dcTractionControl2Old': 0,
            'dcTractionControl': 0,
            'dcTractionControl2': 0,
            'dcTractionControlToggleOld': 0,
            'dcABSOld': 0,
            'dcBrakeBiasOld': 0,
            'dcBrakeBias': 0,
            'RunStartTime': 0,
            'changeLabelsOn': True,
            'dcChangeTime': 0,
            'dcFuelMixtureChange': False,
            'dcThrottleShapeChange': False,
            'dcTractionControlChange': False,
            'dcTractionControl2Change': False,
            'dcTractionControlToggleChange': False,
            'dcABSChange': False,
            'dcBrakeBiasChange': False,
            'BUpshiftToneInitRequest': False,
            'BNewLap': False,
            'NLapDriver': 0,
            'NLapRaceTime': [0] * 64,
            'TFinishPredicted': [0] * 64,
            'WinnerCarIdx': 0,
            'DriverCarIdx': 0,
            'NLapWinnerRaceTime': 0,
            'PosStr': '64/64',
            'SpeedStr': '234',
            'GearStr': 'N',
            'classStruct': {},
            'NClasses': 1,
            'NDrivers': 1,
            'NDriversMyClass': 1,
            'SOF': 0,
            'SOFMyClass': 0,
            'NClassPosition': 1,
            'NPosition': 1,
            'BResults': False,
            'aOffsetTrack': 0,
            'weatherStr': 'TAir: 25°C     TTrack: 40°C     pAir: 1.01 bar    rHum: 50 %     rhoAir: 1.25 kg/m³     vWind: ',
            'SOFstr': 'SOF: 0',
            'BdcHeadlightFlash': False,
            'tdcHeadlightFlash': 0,
            'dcHeadlightFlashOld': False,
            'newLapTime': 0,
            # 'BEnableRaceLapEstimation': False,
            'track': None,
            'car': None,
            'SubSessionIDOld': 0,
            'NDDUPage': 1,
            'dc': {'dcABS',
                   'dcTractionControl',
                   'dcTractionControl2',
                   'dcBrakeBias'
                   },
            'dcOld': {},
            'dcChangedItems': {},
            'BLoggerActive': False,
            'tExecuteRTDB': 0,
            'tExecuteUpshiftTone': 0,
            'tExecuteRaceLapsEstimation': 0,
            'tExecuteLogger': 0,
            'tExecuteRender': 0,
            'tExecuteCalc': 0,
            'tShiftReaction': float('nan'),
            'BEnableLapLogging': False,
            'BChangeTyres': False,
            'BBeginFueling': False,
            'VUserFuelSet': 0,
            'NFuelSetMethod': 0, # 0 = User pre set; 1 = calculated
            'BPitCommandUpdate': False,
            'PlayerTrackSurfaceOld': 0,
            'BEnteringPits': False,
            # 'BPitCommandControl': False,
            'sToPitStall': 0,
            'sToPitStallStr': '463',
            'PitSvFlagsEntry': 0,
            'BFuelRequest': False,
            'BFuelCompleted': False,
            'BTyreChangeRequest': [False, False, False, False],
            'BTyreChangeCompleted':  [False, False, False, False],
            'VFuelPitStopStart': 0,
            'BPitstop': False,
            'BPitstopCompleted': False,
            'NLappingCars': [
                {
                'Class': 'LMP1',
                'NCars': 2,
                'Color': (255, 218, 89),
                'sDiff': -10
                },
                {
                'Class': 'HPD',
                'NCars': 1,
                'Color': (255, 218, 89),
                'sDiff': -50
                }
            ],
            'PlayerCarClassRelSpeed': 0,
            'Exception': None,
            'BLiftToneRequest': False,
            'FuelTGTLiftPoints': {},
            # 'VFuelTgt': 3.05,
            'VFuelTgtEffective': 3.05,
            # 'VFuelTgtOffset': 0,
            'BLiftBeepPlayed': [],
            'NNextLiftPoint': 0,
            # 'BEnableLiftTones': False,
            'tNextLiftPoint': 0,
            'DDUControlList':
                {
                'VFuelTgt': ['VFuelTgt', True, 2],
                'VFuelTgtOffset': ['VFuelTgtOffset', True, 2]
                },
            'fFuelBeep': 300,
            'tFuelBeep': 150,
            'fShiftBeep': 500,
            'tShiftBeep': 150,
            'dcABS': 6,
            'NButtonPressed': None,
            'NCurrentMap': 0,
            'dcHeadlightFlash': False,
            'dcPitSpeedLimiterToggle': False,
            'dcStarter': False,
            'dcTractionControlToggle': False
            }

iDDUControls = {
    'ShiftToneEnabled': True,
    'BEnableRaceLapEstimation': True,
    'BPitCommandControl': True,
    'VFuelTgt': (0, 0, 50, 0.01),
    'VFuelTgtOffset': (0, -5, 5, 0.01),
    'BEnableLiftTones': True
}

iDDUControlsNameInit = {}

iDDUControlsName = list(iDDUControls.keys())
for i in range(0, len(iDDUControlsName)):
    if type(iDDUControls[iDDUControlsName[i]]) is bool:
        iDDUControlsNameInit[iDDUControlsName[i]] = iDDUControls[iDDUControlsName[i]]
    else:
        iDDUControlsNameInit[iDDUControlsName[i]] = iDDUControls[iDDUControlsName[i]][0]

myRTDB = RTDB.RTDB()
myRTDB.initialise(calcData, False, False)
myRTDB.initialise(iDDUControlsNameInit, False, False)

myRTDB.car = Car.Car('name', 'path')
# myRTDB.car.load('C:/Users/Marc/Documents/Projekte/iDDU/data/car/Porsche 718 Cayman GT4.json')
myRTDB.car.load('C:/Users/Marc/Documents/Projekte/iDDU/data/car/Ferrari 488 GTE.json')

dcList = list(myRTDB.car.dcList.keys())
myRTDB.queryData.extend(dcList)


ms = MultiSwitch.MultiSwitch(myRTDB, 0.01)

for i in range(0, len(iDDUControlsName)):
    if type(iDDUControls[iDDUControlsName[i]]) is bool:
        ms.addMapping(iDDUControlsName[i])
    else:
        ms.addMapping(iDDUControlsName[i], minValue=iDDUControls[iDDUControlsName[i]][1], maxValue=iDDUControls[iDDUControlsName[i]][2], step=iDDUControls[iDDUControlsName[i]][3])

ms.initCar()

ms.run()