# import all required packages
import threading
import time

import irsdk

import iDDURender2
import iDDUcalc2
from functionalities.RTDB import RTDB

# data for initialisation of RTDB
# helper variables
helpData = {'done': False, 'timeStr': 0, 'waiting': True, 'LabelSessionDisplay': [1, 1, 1, 0, 1, 1]}
# data from iRacing
iRData = {'LapBestLapTime': 0, 'LapLastLapTime': 0, 'LapDeltaToSessionBestLap': 0, 'dcFuelMixture': 0,
          'dcThrottleShape': 0, 'dcTractionControl': 0, 'dcTractionControl2': 0, 'dcTractionControlToggle': 0,
          'dcABS': 0, 'dcBrakeBias': 0, 'FuelLevel': 0, 'Lap': 123, 'IsInGarage': 0, 'LapDistPct': 0, 'OnPitRoad': 0,
          'PlayerCarClassPosition': 0, 'PlayerCarPosition': 0, 'RaceLaps': 0, 'SessionLapsRemain': 0,
          'SessionTimeRemain': 0, 'SessionTime': 0, 'SessionFlags': 0, 'SessionNum': 0, 'IsOnTrack': False, 'Gear': 0,
          'Speed': 0, 'DriverInfo': {'DriverCarIdx': 0, 'DriverCarFuelMaxLtr': 0, 'DriverCarMaxFuelPct': 1,
                                     'Drivers': []}, 'CarIdxLapDistPct': [], 'CarIdxOnPitRoad': [],
          'SessionInfo': {'Sessions':
                              [{'SessionType': 'Session', 'SessionTime': 'unlimited', 'SessionLaps': 0,
                                'ResultsPositions':
                                    [{'CarIdx': 0, 'JokerLapsComplete': 0}]}]}, 'Yaw': 0, 'VelocityX': 0,
          'VelocityY': 0, 'YawNorth': 0, '': 0, 'WeekendInfo': []}
# calculated data
calcData = {'LastFuelLevel': 0, 'GearStr': '-', 'SessionInfoAvailable': False, 'SessionNum': 0, 'init': True,
            'onPitRoad': True, 'isRunning': False, 'WasOnTrack': False, 'StintLap': 0, 'SessionTime': 0,
            'oldSessionNum': -1, 'oldLap': 0.1, 'FuelConsumption': [], 'FuelLastCons': 0, 'OutLap': True,
            'SessionFlags': 0, 'oldSessionlags': 0, 'LapsToGo': 0, 'SessionLapRemain': 0, 'FuelConsumptionStr': '5.34',
            'RemLapValueStr': '10', 'FuelLapStr': '0', 'FuelAddStr': '0.0', 'FlagCallTime': 0, 'FlagException': False,
            'FlagExceptionVal': 0, 'Alarm': [], 'RaceLaps': 0, 'oldFuelAdd': 1, 'GreenTime': 0, 'RemTimeValue': 0,
            'JokerStr': '-/-', 'dist': [], 'x': [], 'y': [], 'map': [], 'RX': False, 'createTrack': True, 'dx': [],
            'dy': [], 'logLap': 0, 'Logging': False, 'tempdist': -1, 'StartUp': False}

# Create RTDB and initialise with
myRTDB = RTDB.RTDB()
myRTDB.initialise(helpData)
myRTDB.initialise(iRData)
myRTDB.initialise(calcData)

# create thread to update RTDB
class iRThread(threading.Thread):
    def __init__(self, RTDB, keys, rate):
        threading.Thread.__init__(self)
        self.rate = rate
        self.db = RTDB
        self.keys = keys
        self.ir = irsdk.IRSDK()

    def run(self):
        while 1:
            self.db.startUp = self.ir.startup()
            if self.db.startUp:
                for i in range(0, len(self.keys)):
                    self.db.__setattr__(self.keys[i], self.ir[self.keys[i]])
            self.db.timeStr = time.strftime("%H:%M:%S", time.localtime())
            time.sleep(self.rate)

# initialise and start thread
thread1 = iRThread(myRTDB, list(iRData.keys()), 0.01)
thread1.start()

# create objects for rendering and calculation
iRRender = iDDURender2.RenderScreen(myRTDB)
iDDUcalc = iDDUcalc2.IDDUCalc2(myRTDB)

# loop to run programme
while not myRTDB.done:
    iDDUcalc.calc()
    myRTDB.done = iRRender.render()

iRRender.pygame.quit()
del iRRender
del iDDUcalc
del thread1
exit()
