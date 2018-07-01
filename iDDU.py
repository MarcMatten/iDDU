# import all required packages
import threading
import time

import irsdk
import winsound

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
          'VelocityY': 0, 'YawNorth': 0, '': 0, 'WeekendInfo': [], 'RPM': 0}
# calculated data
calcData = {'LastFuelLevel': 0, 'GearStr': '-', 'SessionInfoAvailable': False, 'SessionNum': 0, 'init': True,
            'onPitRoad': True, 'isRunning': False, 'WasOnTrack': False, 'StintLap': 0,
            'oldSessionNum': -1, 'oldLap': 0.1, 'FuelConsumption': [], 'FuelLastCons': 0, 'OutLap': True,
            'SessionFlags': 0, 'oldSessionlags': 0, 'LapsToGo': 0, 'SessionLapRemain': 0, 'FuelConsumptionStr': '5.34',
            'RemLapValueStr': '10', 'FuelLapStr': '0', 'FuelAddStr': '0.0', 'FlagCallTime': 0, 'FlagException': False,
            'FlagExceptionVal': 0, 'Alarm': [], 'RaceLaps': 0, 'oldFuelAdd': 1, 'GreenTime': 0, 'RemTimeValue': 0,
            'JokerStr': '-/-', 'dist': [], 'x': [], 'y': [], 'map': [], 'RX': False, 'createTrack': True, 'dx': [],
            'dy': [], 'logLap': 0, 'Logging': False, 'tempdist': -1, 'StartUp': False, 'oldSessionFlags': 0,
            'backgroundColour': (0, 0, 0), 'textColourFuelAdd': (0, 0, 0), 'textColour': (141, 141, 141)}

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
            
class UpShiftTone(threading.Thread):
    def __init__(self, RTDB, rate):
        threading.Thread.__init__(self)
        self.rate = rate
        self.db = RTDB
        self.ShiftRPM = 1234
        self.init = False
        self.fname = "files\Beep.wav"  # path to beep soundfile
        self.IsOnTrack = False

    def run(self):
        while 1:
            if self.db.startUp:
                if not self.init:
                    self.initialise()
                    self.init = True
            else:
                self.init = False

            # execute this loop while iRacing is running
            while self.db.startUp:
                # two beeps sounds as notification when entering track
                if self.db.IsOnTrack and not self.IsOnTrack:
                    self.IsOnTrack = True
                    winsound.PlaySound(self.fname, winsound.SND_FILENAME)
                    time.sleep(0.3)
                    winsound.PlaySound(self.fname, winsound.SND_FILENAME)

                # execute this loop while player is on track
                while self.db.IsOnTrack:
                    #	check if upshift RPM is reached
                    if self.db.Gear > 0 and self.db.RPM >= self.ShiftRPM:  # disable sound for neutral and reverse gear
                        winsound.PlaySound(self.fname, winsound.SND_FILENAME)
                        time.sleep(0.75)  # pause for 750 ms to avoid multiple beeps when missing shiftpoint

                # update flag when leaving track
                if not self.db.IsOnTrack and self.IsOnTrack:
                    self.IsOnTrack = False

            
    def initialise(self):
        time.sleep(0.1)
        # get optimal shift RPM from iRacing and display message
        self.ShiftRPM = self.db.DriverInfo['DriverCarSLShiftRPM']
        self.DriverCarName = self.db.DriverInfo['Drivers'][self.db.DriverInfo['DriverCarIdx']]['CarScreenNameShort']

        # self.db.DriverInfo['Drivers'][self.db.DriverInfo['DriverCarIdx']]['CarScreenNameShort']
        print('Optimal Shift RPM for', self.DriverCarName, ':', self.ShiftRPM)

        # play three beep sounds as notification
        winsound.PlaySound(self.fname, winsound.SND_FILENAME)
        time.sleep(0.3)
        winsound.PlaySound(self.fname, winsound.SND_FILENAME)
        time.sleep(0.3)
        winsound.PlaySound(self.fname, winsound.SND_FILENAME)
        

# initialise and start thread
thread1 = iRThread(myRTDB, list(iRData.keys()), 0.01)
thread2 = UpShiftTone(myRTDB, 0.01)
thread1.start()
time.sleep(0.1)
thread2.start()

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
del thread2
exit()
