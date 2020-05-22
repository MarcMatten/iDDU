# import all required packages
import time
import numpy as np
from functionalities.RTDB import RTDB
from functionalities.UpshiftTone import UpshiftTone
from gui.iDDUgui import iDDUgui
from libs import iDDURender, iDDUcalc, raceLapsEstimation, Logger
import os

nan = float('nan')
CarNumber = 64
LapNumber = 500
CarIdxtLap_temp = [[] * LapNumber] * CarNumber
for x in range(0, CarNumber):
    CarIdxtLap_temp[x] = [nan] * LapNumber

# data for initialisation of RTDB
# helper variables
helpData = {'done': False,
            'timeStr': time.strftime("%H:%M:%S", time.localtime()),
            'BWaiting': False,
            'LabelSessionDisplay': [1, 1, 1, 0, 1, 1]
            }
# data from iRacing
iRData = {'LapBestLapTime': 0,
          'LapLastLapTime': 0,
          'LapDeltaToSessionBestLap': 0,
          'dcFuelMixture': 0,
          'dcThrottleShape': 0,
          'dcTractionControl': 0,
          'dcTractionControl2': 0,
          'dcTractionControlToggle': 0,
          'dcABS': 0,
          'dcBrakeBias': 0,
          'FuelLevel': 96.2345,
          'Lap': 0,
          'IsInGarage': 0,
          'LapDistPct': 0,
          'OnPitRoad': 0,
          'PlayerCarClassPosition': 0,
          'PlayerCarPosition': 0,
          'PlayerTrackSurface': 0,
          'SessionLapsRemain': 0,
          'Throttle': 0,
          'SessionTimeRemain': 86400,
          'SessionTime': 0,
          'SessionFlags': 0,
          'SessionNum': 0,
          'IsOnTrack': False,
          'Gear': 0,
          'Speed': 0,
          'DriverInfo':
              {'DriverCarIdx': 0, 'DriverUserID': 88407, 'PaceCarIdx': -1, 'DriverHeadPosX': -0.559, 'DriverHeadPosY': 0.376, 'DriverHeadPosZ': 0.62, 'DriverCarIdleRPM': 800.0,
               'DriverCarRedLine': 7200.0, 'DriverCarEngCylinderCount': 8, 'DriverCarFuelKgPerLtr': 0.75, 'DriverCarFuelMaxLtr': 83.239, 'DriverCarMaxFuelPct': 1.0, 'DriverCarSLFirstRPM': 5500.0,
               'DriverCarSLShiftRPM': 6500.0, 'DriverCarSLLastRPM': 6500.0, 'DriverCarSLBlinkRPM': 7200.0, 'DriverPitTrkPct': 0.136028, 'DriverCarEstLapTime': 17.001,
               'DriverSetupName': 'southboston.sto', 'DriverSetupIsModified': 0, 'DriverSetupLoadTypeName': 'user', 'DriverSetupPassedTech': 1, 'DriverIncidentCount': 0, 'Drivers': [
                  {'CarIdx': 0, 'UserName': 'Marc Matten', 'AbbrevName': None, 'Initials': None, 'UserID': 88407, 'TeamID': 0, 'TeamName': 'Marc Matten', 'CarNumber': '23', 'CarNumberRaw': 23,
                   'CarPath': 'streetstock', 'CarClassID': 34, 'CarID': 36, 'CarIsPaceCar': 0, 'CarIsAI': 0, 'CarScreenName': 'Street Stock', 'CarScreenNameShort': 'Street Stock',
                   'CarClassShortName': None, 'CarClassRelSpeed': 0, 'CarClassLicenseLevel': 0, 'CarClassMaxFuelPct': '1.000 %', 'CarClassWeightPenalty': '0.000 kg', 'CarClassColor': 16777215,
                   'IRating': 1, 'LicLevel': 1, 'LicSubLevel': 1, 'LicString': 'R 0.01', 'LicColor': 87003, 'IsSpectator': 0, 'CarDesignStr': '1,fd7704,000000,ffffff',
                   'HelmetDesignStr': '14,000000,000000,FFFFFF', 'SuitDesignStr': '0,000000,6D6E71,6D6E71', 'CarNumberDesignStr': '1,fd7704,000000,ffffff', 'CarSponsor_1': 107, 'CarSponsor_2': 2,
                   'CurDriverIncidentCount': 0, 'TeamIncidentCount': 0}]},
          'CarIdxLapDistPct': [0],
          'CarIdxOnPitRoad': [True] * 64,
          'SessionInfo':
              {
                  'Sessions':
                      [
                          {
                              'SessionType': 'Session',
                              'SessionTime': 'unlimited',
                              'SessionLaps': 0,
                              'ResultsPositions':
                                  [
                                      {
                                          'CarIdx': 0,
                                          'JokerLapsComplete': 0
                                      }
                                  ]
                          }
                      ]
              },
          'Yaw': 0,
          'VelocityX': 0,
          'VelocityY': 0,
          'YawNorth': 0,
          'WeekendInfo':
              {'TrackName': 'mosport', 'TrackID': 144, 'TrackLength': '3.91 km', 'TrackDisplayName': 'Canadian Tire Motorsport Park', 'TrackDisplayShortName': 'Mosport', 'TrackConfigName': None,
               'TrackCity': 'Bowmanville', 'TrackCountry': 'Canada', 'TrackAltitude': '339.74 m', 'TrackLatitude': '44.054339 m', 'TrackLongitude': '-78.674384 m', 'TrackNorthOffset': '1.6678 rad',
               'TrackNumTurns': 10, 'TrackPitSpeedLimit': '55.98 kph', 'TrackType': 'road course', 'TrackDirection': 'neutral', 'TrackWeatherType': 'Specified / Dynamic Sky',
               'TrackSkies': 'Partly Cloudy', 'TrackSurfaceTemp': '32.58 C', 'TrackAirTemp': '18.33 C', 'TrackAirPressure': '28.73 Hg', 'TrackWindVel': '0.45 m/s', 'TrackWindDir': '0.00 rad',
               'TrackRelativeHumidity': '55 %', 'TrackFogLevel': '0 %', 'TrackCleanup': 0, 'TrackDynamicTrack': 1, 'SeriesID': 0, 'SeasonID': 0, 'SessionID': 0, 'SubSessionID': 0, 'LeagueID': 0,
               'Official': 0, 'RaceWeek': 0, 'EventType': 'Test', 'Category': 'Road', 'SimMode': 'full', 'TeamRacing': 0, 'MinDrivers': 0, 'MaxDrivers': 0, 'DCRuleSet': 'None',
               'QualifierMustStartRace': 0, 'NumCarClasses': 1, 'NumCarTypes': 1, 'HeatRacing': 0,
               'WeekendOptions': {'NumStarters': 0, 'StartingGrid': 'single file', 'QualifyScoring': 'best lap', 'CourseCautions': False, 'StandingStart': 0, 'Restarts': 'single file',
                                  'WeatherType': 'Specified / Dynamic Sky', 'Skies': 'Partly Cloudy', 'WindDirection': 'N', 'WindSpeed': '1.61 km/h', 'WeatherTemp': '18.33 C',
                                  'RelativeHumidity': '55 %', 'FogLevel': '0 %', 'TimeOfDay': '12:00 pm', 'Date': '2019-05-15', 'EarthRotationSpeedupFactor': 1, 'Unofficial': 0,
                                  'CommercialMode': 'consumer', 'NightMode': 'variable', 'IsFixedSetup': 0, 'StrictLapsChecking': 'default', 'HasOpenRegistration': 0, 'HardcoreLevel': 1,
                                  'NumJokerLaps': 0, 'IncidentLimit': 'unlimited'}, 'TelemetryOptions': {'TelemetryDiskFile': ''}},
          'RPM': 0,
          'LapCurrentLapTime': 0,
          'EngineWarnings': 0,
          'CarIdxTrackSurface': 0,
          'CarLeftRight': 0,
          'DRS_Status': 0,
          'PushToPass': False,
          'CarIdxF2Time': [],
          'CarIdxClassPosition': [],
          'CarIdxPosition': [],
          'AirDensity': 1.246246,
          'AirPressure': 29.85,
          'AirTemp': 25.134513,
          'TrackTemp': 40.2436,
          'WindDir': 0,
          'WindVel': 13.246,
          'RelativeHumidity': 50.2346,
          'dcHeadlightFlash': False,
          'SessionState': 0,
          'PitSvFlags': None,
          'PitSvLFP': None,
          'PitSvRFP': None,
          'PitSvLRP': None,
          'PitSvRRP': None,
          'PitSvFuel': None,
          'PlayerCarInPitStall': None,
          'PlayerCarPitSvStatus': None,
          'PitRepairLeft': None,
          'PitOptRepairLeft': None,
          'PitstopActive': None,
          'CarIdxEstTime': [],
          'DriverCarEstLapTime': 0
          }

# calculated data
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
            'ShiftToneEnabled': True,
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
            'dcThrottleShapeOld': 0,
            'dcTractionControlOld': 0,
            'dcTractionControl2Old': 0,
            'dcTractionControlToggleOld': 0,
            'dcABSOld': 0,
            'dcBrakeBiasOld': 0,
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
            'CarIdxtLap_temp': CarIdxtLap_temp,
            'CarIdxtLap': CarIdxtLap_temp,
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
            'BEnableRaceLapEstimation': False,
            'dir': os.getcwd(),
            'track': None,
            'car': None,
            'SubSessionIDOld': 0,
            'NDDUPage': 1,
            'dc': {},
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
            'BPitCommandControl': False,
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
            'CarIdxMap': np.linspace(0,63,64).astype(int).tolist(),
            'BLiftToneRequest': False,
            'FuelTGTLiftPoints': {},
            'LapDistPctLift': np.array([]),
            'VFuelTgt': 3.05,
            'VFuelTgtEffective': 3.05,
            'VFuelTgtOffset': 0,
            'BLiftBeepPlayed': [],
            'NNextLiftPoint': 0,
            'BEnableLiftTones': True,
            'tNextLiftPoint': 0,
            'DDUControlList':
                {
                'VFuelTgt': ['VFuelTgt', True, 2],
                'VFuelTgtOffset': ['VFuelTgtOffset', True, 2]
                }
            }

# Create RTDB and initialise with
myRTDB = RTDB.RTDB()
myRTDB.initialise(helpData, False)
myRTDB.initialise(iRData, True)
myRTDB.initialise(calcData, False)

# initialise and start thread
thread0 = iDDUcalc.IDDUCalc(myRTDB, 0.005)
thread1 = RTDB.iRThread(myRTDB, 0.01)
thread2 = UpshiftTone.UpShiftTone(myRTDB, 0.01)
thread3 = iDDUgui(myRTDB)
thread4 = raceLapsEstimation.raceLapsEstimation(myRTDB, 15)
thread5 = Logger.Logger(myRTDB, 0.01)
thread0.start()
time.sleep(0.1)
thread1.start()
time.sleep(0.1)
thread3.start()
time.sleep(0.1)
thread2.start()
time.sleep(0.1)
thread4.start()
time.sleep(0.1)
thread5.start()
time.sleep(0.1)

# loop to run programme
iRRender = None
while not myRTDB.done:
    if myRTDB.StartDDU:
        print(myRTDB.timeStr + ': Starting DDU')
        iRRender = iDDURender.RenderScreen(myRTDB)
        myRTDB.DDUrunning = True
    elif myRTDB.DDUrunning:
        myRTDB.done = iRRender.render()
        if myRTDB.StartDDU:
            myRTDB.StartDDU = False

    if myRTDB.StopDDU:
        print(myRTDB.timeStr + ': Stopping DDU')
        iRRender.stopRendering()
        myRTDB.StopDDU = False
        myRTDB.DDUrunning = False

    time.sleep(0.001)
