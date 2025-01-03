# import all required packages
import time
import numpy as np
from libs.RTDB import RTDB
from libs import iDDURender, iDDUcalc, UpshiftTone, raceLapsEstimation, Logger, SerialComs, SteeringWheelComs, PedalController
from gui import iDDUgui
import os
from libs.MultiSwitch import MultiSwitch
from libs.auxiliaries import importExport
from shutil import copyfile
from libs import IDDU
import sys
#import ntp_update_time


nan = float('nan')
CarNumber = 64
LapNumber = 500
CarIdxtLap_temp = [[] * LapNumber] * CarNumber
for x in range(0, CarNumber):
    CarIdxtLap_temp[x] = [nan] * LapNumber

# data for initialisation of RTDB TODO: read these in from a file
# helper variables
helpData = {'done': False,
            'timeStr': time.strftime("%H:%M:%S", time.localtime()),
            'BWaiting': False,
            'LabelSessionDisplay': [1, 1, 1, 0, 1, 1]
            }
# data from iRacing
iRData = {'LapBestLapTime': 0,
          'SessionTick': 0,
          'LapLastLapTime': 0,
          'LapDeltaToSessionBestLap': 0,
          'dcFuelMixture': 0,
          'dcThrottleShape': 0,
          'dcTractionControl': 0,
          'dcTractionControl2': 0,
          'dcTractionControlToggle': 0,
          'dcABS': 0,
          'dcABSToggle': 0,
          'dcBrakeBias': 0,
          'FuelLevel': 0,
          'FuelUsePerHour': 0,
          'Lap': 0,
          'IsInGarage': 0,
          'LapDistPct': 0,
          'OnPitRoad': 0,
          'PlayerCarClassPosition': 0,
          'PlayerCarPosition': 0,
          'PlayerTrackSurface': 0,
          'SessionLapsRemain': 0,
          'Throttle': 0,
          'ThrottleRaw': 0,
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
          'CarIdxLapDistPct': np.array([0] * 64),
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
          'P2P_Count': 0,
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
          'DriverCarEstLapTime': 0,
          'LongAccel': 0,
          'dcWeightJackerRight': 0,
          'dcAntiRollFront': 0,
          'dcAntiRollRear': 0,
          'dcPitSpeedLimiterToggle': False,
          'dcStarter': False,
          'Brake': 0,
          'LFbrakeLinePress': 0,
          'LRbrakeLinePress': 0,
          'RFbrakeLinePress': 0,
          'RRbrakeLinePress': 0,
          'CarSetup': None,
          'Clutch': 0,
          'BrakeABSactive': False,
          'CarIdxP2P_Status': [False] * 64,
          'TrackWetness': 1,
          'WeatherDeclaredWet': False,
          'Precipitation': 0
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
            'NStintLap': 0,
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
            'Alarm': np.array([0]*10),
            'VFuelAddOld': 1,
            'GreenTime': 0,
            'RemTimeValue': 0,
            'JokerStr': '2/2',
            'LapDistPct': [],
            'x': [],
            'y': [],
            'map': [],
            'RX': False,
            'BCreateTrack': True,
            'dx': [],
            'dy': [],
            'logLap': 0,
            'tempdist': -1,
            'StartUp': False,
            'oldSessionFlags': 0,
            'backgroundColour': (0, 0, 0),
            'textColourFuelAdd': (255, 255, 255),
            'textColourLapCons': (255, 255, 255),
            'textColourDelta': (255, 255, 255),
            'textColourFuelAddOverride': (255, 255, 255),
            'BTextColourFuelAddOverride': False,
            'textColour': (255, 255, 255),
            'FuelLaps': 1,
            'FuelAdd': 1,
            'time': [],
            'iRShiftRPM': [100000, 100000, 100000, 100000],
            'StartDDU': False,
            'StopDDU': False,
            'DDUrunning': False,
            'SessionLength': 86400,
            'CarIdxPitStops': [0] * 64,
            'CarIdxOnPitRoadOld': [True] * 64,
            'old_DRS_Status': 0,
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
                False,  # 28 VFuelTgt
                False,  # 29 VFuelDelta
                False,  # 30 FARB
                False,  # 31 RARB
                False,  # 32 Weigth Jacker
            ],
            'P2P': False,
            'DRS': False,
            'LapLimit': False,
            'TimeLimit': False,
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
            'dcTearOffVisor': 0,
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
            'weatherStr': 'TAir: -°C     TTrack: -°C     Wetness: -     vWind: - km/h',
            'SOFstr': 'SOF: 0',
            'BdcHeadlightFlash': False,
            'tdcHeadlightFlash': 0,
            'dcHeadlightFlashOld': False,
            'newLapTime': 0,
            'dir': os.getcwd(),
            'track': None,
            'car': None,
            'SubSessionIDOld': -99,
            'NDDUPage': 1,
            'dc': {},
            'dcOld': {},
            'dcChangedItems': {},
            'tExecuteRTDB': 0,
            'tExecuteUpshiftTone': 0,
            'tExecuteRaceLapsEstimation': 0,
            'tExecuteSerialComs': 0,
            'tExecuteSerialComs2': 0,
            'tExecuteLogger': 0,
            'tExecuteRender': 0,
            'tExecuteCalc': 0,
            'tExecuteMulti': 0,
            'tShiftReaction': float('nan'),
            'BPitCommandUpdate': False,
            'PlayerTrackSurfaceOld': 0,
            'BEnteringPits': False,
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
            'NLappingCars': [],
            'PlayerCarClassRelSpeed': 0,
            'Exception': None,
            'CarIdxMap': np.linspace(0, 63, 64).astype(int).tolist(),
            'BLiftToneRequest': False,
            'FuelTGTLiftPoints': {
                'SFuelConfigCarName': None,
                'SFuelConfigTrackName': None,
                'VFuelTGT': None,
                'CarSetup': None,
                'LapDistPct': None,
                'SetupName': None,
                'ibtFileName': None
            },
            'LapDistPctLift': np.array([]),
            'VFuelLiftTarget': np.array([]),
            'VFuelTgtEffective': 3.05,
            'BLiftBeepPlayed': [],
            'NNextLiftPoint': 0,
            'tNextLiftPoint': 0,
            'BMultiInitRequest': False,
            'BFuelSavingConfigLoaded': False,
            'BSnapshotMode': False,
            'pBrakeFMax': 0,
            'pBrakeRMax': 0,
            'rABSActivity': [0, 0, 0, 0],
            'rRearLocking': 0,
            'rWheelSpin': 0,
            'rSlipR': 0,
            'VFuelUsedLap': 0,
            'VFuelBudgetActive': 0,
            'VFuelReferenceActive': 0,
            'VFuelBudget': np.array([]),
            'VFuelReference': np.array([]),
            'dVFuelTgt': 0,
            'VFuelStartStraight': 0,
            'BUpdateVFuelDelta': False,
            'VFuelDelta': 0,
            'tLiftTones': [1, 0.5, 0],
            'BLEDsInit': False,
            'NShiftLEDState': 0,
            'BLoadRaceSetupWarning': False,
            'BTyreChoiceWarning': 0,
            'BLowRaceFuelWarning': False,
            'LastSetup': {
                'DriverSetupName': 'None',
                'UpdateCount': None,
                'FuelLevel': None},
            'SessionTypeOld': None,
            'BFuelTgtSet': False,
            'BStartMode': False,
            'BSteeringWheelStartMode': False,
            'tStart100': 0,
            'tStartReaction': 0,
            'BThumbWheelErrorL': False,
            'BThumbWheelErrorR': False,
            'BThumbWheelActive': True,
            'NRotaryR': 0,
            'NRotaryL': 0,
            'NLapsTotal': 0,
            'rThrottleRead': 0,
            'rClutchRead': 0,
            'BForceLift': False,
            'BForceClutch': False,
            'BEnableAutoLift': True,
            'BInLiftZone': False,
            'BEnableAutoClutch': True,
            'GearID': 'base',
            'FuelLevelDisp': 0,
            'BRequestPitSpeedBeep': False,            
            'TrackWetnessOld': 1,
            'WeatherDeclaredWetOld': False,
            'BYellow': False,
            'tYellow': 0,
            'CarIdxSpeed': np.zeros(shape=(64, 3)),
            'SessionTickOld': 0,
            'SessionTimeOld': 0,
            'CarIdxLapDistPctOld': np.array([0] * 64),
            'BSpeedProfile': False,
            'NSector': None,
            'SectorBasedOffsets': {},
            'BEnableSectorMode': False,
            'BInitSectorMode': False
            }

iDDUControls = {  # DisplayName, show, decimals, initial value, min value, max value, steps, Name Map
    'ShiftToneEnabled': ['Enable Shift Beep', True, 0, True, None, None, None, ['Off', 'On']],
    'NSlipLEDMode': ['Slip LED Mode', True, 0, 1, 0, 6, 1, ['Off', 'On', 'Traction + ABS', 'ABS only', 'Slip only', 'Traction only', 'Braking only']],
    'UserRaceLaps': ['Race Laps', True, 0, 23, 1, 999, 1],
    'NLapsStintPlanned': ['Stint Laps', True, 0, 23, 1, 999, 1],
    'BEnableRaceLapEstimation': ['Enable Race Lap Estimation', True, 0, True, None, None, None, ['Off', 'On']],
    'NRaceLapsSource': ['Race Laps Source', True, 0, 0, 0, 1, 1, ['Calc', 'User']],
    'VFuelTgt': ['VFuelTgt', True, 2, 0, 0, 50, 0.01],
    'NFuelConsumptionMethod': ['Fuel Consumption Method', True, 1, 0, 0, 2, 1, ['Avg', 'Last 3', 'Ref']],
    'NFuelTargetMethod': ['Fuel Management', True, 1, 0, 0, 3, 1, ['Off', 'Static', 'Finish', 'Stint']],
    'BPitCommandControl': ['Enable Pit Control', True, 0, True, None, None, None, ['Off', 'On']],
    'rBitePoint': ['Bite Point', True, 1, 30.0, 10, 80, 0.5]
}

iDDUControls2 = {  # DisplayName, show, decimals, initial value, min value, max value, steps, Name Map
    'BEnableSectorDCMode': ['Enable Sector Offsets', True, 0, False, None, None, None, ['Off', 'On']],
    'BEnableSectorSetMode': ['Enable Sector Set Mode', True, 0, False, None, None, None, ['Off', 'On']],    
    'BEnableShiftLEDs': ['Enable Shift LEDs', True, 0, True, None, None, None, ['Off', 'On']],
    'tReactionLift': ['Lift Reaction Time', True, 2, 0.15, 0, 1, 0.05],
    'fShiftBeep': ['Shift Beep Frequency', True, 0, 1100, 0, 2000, 50],    
    'BClearSectorDCMode': ['Clear Sector Offsets', True, 0, False, None, None, None, ['Off', 'On']]
}

inCarControls = [
    'dcBrakeBias',
    'dcTractionControl',
    'dcTractionControl2',
    'dcABS',
    'dcAntiRollFront',
    'dcAntiRollRear',
    'dcFuelMixture',
    'dcThrottleShape',
    'dcBoostLevel',
    'dcDiffPreload',
    'dcWeightJackerRight',
    'dcPeakBrakeBias'
]

if __name__ == "__main__":

    IDDU.IDDUItem.logger.info('Starting iDDU')

    # ntp_update_time.updateWindowsTime()

    if not os.path.exists(calcData['dir'] + '/data/configs/config.json'):
        copyfile(calcData['dir'] + '/data/configs/config_default.json', calcData['dir'] + '/data/configs/config.json')
        IDDU.IDDUItem.logger.info('No config.json found. Created new default config.json from config_default.json')

    config_default = importExport.loadJson(calcData['dir'] + '/data/configs/config_default.json')
    config_local = importExport.loadJson(calcData['dir'] + '/data/configs/config.json')

    config = {**config_default, **config_local}

    iDDUControlsNameInit = {}

    iDDUControlsName = list(iDDUControls.keys())
    iDDUControlsName2 = list(iDDUControls2.keys())
    # for i in range(0, len(iDDUControlsName)):
    #     if type(iDDUControls[iDDUControlsName[i]][3]) is bool:
    #         iDDUControlsNameInit[iDDUControlsName[i]] = iDDUControls[iDDUControlsName[i]]
    #     else:
    #         iDDUControlsNameInit[iDDUControlsName[i]] = iDDUControls[iDDUControlsName[i]][0]

    # Create RTDB and initialise with
    myRTDB = RTDB.RTDB()
    myRTDB.initialise(helpData, False, False)
    myRTDB.initialise(iRData, True, False)
    myRTDB.initialise(calcData, False, False)
    myRTDB.initialise({'iDDUControls': iDDUControls}, False, False)
    myRTDB.initialise({'iDDUControls2': iDDUControls2}, False, False)
    myRTDB.initialise({'inCarControls': inCarControls}, False, False)
    myRTDB.initialise({'config': config}, False, False)

    dcList = list(myRTDB.car.dcList.keys())

    # initialise and start thread
    rtdbThread = RTDB.RTDBThread(0.01)
    rtdbThread.setDB(myRTDB)
    calcThread = iDDUcalc.IDDUCalcThread(0.017)
    shiftToneThread = UpshiftTone.ShiftToneThread(0.01)
    guiThread = iDDUgui.iDDUGUIThread(0.02)
    serialComsThread = SerialComs.SerialComsThread(0.016)
    steeringWheelComsThread = SteeringWheelComs.SteeringWheelComsThread(0.01)
    pedalControllerlThread = PedalController.PedalControllerThread(0.01)
    raceLapsEstimationThread = raceLapsEstimation.RaceLapsEstimationThread(15)
    loggerThread = Logger.LoggerThread(0.016)
    ms = MultiSwitch.MultiSwitch(0.02)

    for i in range(0, len(iDDUControlsName)):
        if type(iDDUControls[iDDUControlsName[i]][3]) is bool:
            ms.addMapping(iDDUControlsName[i])
        else:
            ms.addMapping(iDDUControlsName[i], minValue=iDDUControls[iDDUControlsName[i]][4], maxValue=iDDUControls[iDDUControlsName[i]][5], step=iDDUControls[iDDUControlsName[i]][6])
    
    for i in range(0, len(iDDUControlsName2)):
        if type(iDDUControls2[iDDUControlsName2[i]][3]) is bool:
            ms.addMapping(iDDUControlsName2[i], level=2)
        else:
            ms.addMapping(iDDUControlsName2[i], minValue=iDDUControls2[iDDUControlsName2[i]][4], maxValue=iDDUControls2[iDDUControlsName2[i]][5], step=iDDUControls2[iDDUControlsName2[i]][6], level=2)

    ms.initCar()

    calcThread.start()
    rtdbThread.start()
    guiThread.start()
    shiftToneThread.start()
    raceLapsEstimationThread.start()
    loggerThread.start()
    serialComsThread.start()
    steeringWheelComsThread.start()
    #pedalControllerlThread.start()
    ms.start()

    iRRender = None

    # loop to run programme
    time.sleep(0.3)
    while not myRTDB.done:
        if myRTDB.DDUrunning:
            myRTDB.done = iRRender.render()
            if myRTDB.StartDDU:
                myRTDB.StartDDU = False

            if myRTDB.StopDDU:
                IDDU.IDDUItem.logger.info('Stopping DDU')
                iRRender.stopRendering()
                myRTDB.StopDDU = False
                myRTDB.DDUrunning = False

        elif myRTDB.StartDDU:
            IDDU.IDDUItem.logger.info('Starting DDU')
            iRRender = iDDURender.RenderScreen()
            myRTDB.DDUrunning = True
            # myRTDB.StartDDU = False

        time.sleep(0.001)

    IDDU.IDDUItem.logger.info('############## Thread Execution Times ##############')
    shiftToneThread.stop()
    raceLapsEstimationThread.stop()
    loggerThread.stop()
    serialComsThread.stop()
    # steeringWheelComsThread.stop()
    pedalControllerlThread.stop()
    ms.stop()    
    calcThread.stop()
    guiThread.stop()
    if iRRender:
        iRRender.stop()
    rtdbThread.stop()
    quit()
