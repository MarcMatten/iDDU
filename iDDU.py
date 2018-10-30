# import all required packages
import threading
import time

import irsdk
import winsound
import sys

from gui.iDDUgui import iDDUgui

import iDDURender
import iDDUcalc
from functionalities.RTDB import RTDB

# data for initialisation of RTDB
# helper variables
helpData = {'done': False, 'timeStr': 0, 'waiting': True, 'LabelSessionDisplay': [1, 1, 1, 0, 1, 1]}
# data from iRacing
iRData = {'LapBestLapTime': 0, 'LapLastLapTime': 0, 'LapDeltaToSessionBestLap': 0, 'dcFuelMixture': 0,
          'dcThrottleShape': 0, 'dcTractionControl': 0, 'dcTractionControl2': 0, 'dcTractionControlToggle': 0,
          'dcABS': 0, 'dcBrakeBias': 0, 'FuelLevel': 0, 'Lap': 0, 'IsInGarage': 0, 'LapDistPct': 0, 'OnPitRoad': 0,
          'PlayerCarClassPosition': 0, 'PlayerCarPosition': 0, 'SessionLapsRemain': 0,
          'SessionTimeRemain': 0, 'SessionTime': 0, 'SessionFlags': 0, 'SessionNum': 0, 'IsOnTrack': False, 'Gear': 0,
          'Speed': 0, 'DriverInfo': {'DriverCarIdx': 0, 'DriverCarFuelMaxLtr': 0, 'DriverCarMaxFuelPct': 1,
                                     'Drivers': []}, 'CarIdxLapDistPct': [0], 'CarIdxOnPitRoad': [],
          'SessionInfo': {'Sessions':
                              [{'SessionType': 'Session', 'SessionTime': 'unlimited', 'SessionLaps': 0,
                                'ResultsPositions':
                                    [{'CarIdx': 0, 'JokerLapsComplete': 0}]}]}, 'Yaw': 0, 'VelocityX': 0,
          'VelocityY': 0, 'YawNorth': 0, '': 0, 'WeekendInfo': [], 'RPM': 0, 'LapCurrentLapTime': 0 } #'RaceLaps': 0,
# calculated data
calcData = {'LastFuelLevel': 0, 'GearStr': '-', 'SessionInfoAvailable': False, 'SessionNum': 0, 'init': True,
            'onPitRoad': True, 'isRunning': False, 'WasOnTrack': False, 'StintLap': 0,
            'oldSessionNum': -1, 'oldLap': 0.1, 'FuelConsumption': [], 'FuelLastCons': 0, 'OutLap': True,
            'SessionFlags': 0, 'oldSessionlags': 0, 'LapsToGo': 27, 'SessionLapRemain': 0, 'FuelConsumptionStr': '0.00',
            'RemLapValueStr': '10', 'FuelLapStr': '0', 'FuelAddStr': '0.0', 'FlagCallTime': 0, 'FlagException': False,
            'FlagExceptionVal': 0, 'Alarm': [], 'oldFuelAdd': 1, 'GreenTime': 0, 'RemTimeValue': 0, 'RaceLaps': 28,
            'JokerStr': '-/-', 'dist': [], 'x': [], 'y': [], 'map': [], 'RX': False, 'createTrack': True, 'dx': [],
            'dy': [], 'logLap': 0, 'Logging': False, 'tempdist': -1, 'StartUp': False, 'oldSessionFlags': 0,
            'backgroundColour': (0, 0, 0), 'textColourFuelAdd': (141, 141, 141), 'textColour': (141, 141, 141),
            'FuelLaps': 1, 'FuelAdd': 1, 'PitStopDelta': 61, 'time': [], 'UpshiftStrategy': 0,
            'UserShiftRPM': [100000, 100000, 100000, 100000, 100000, 100000, 100000],
            'UserShiftFlag': [1, 1, 1, 1, 1, 1, 1], 'iRShiftRPM': [100000, 100000, 100000, 100000],
            'ShiftToneEnabled': True}

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


# UpShiftTome Thread
class UpShiftTone(threading.Thread):
    def __init__(self, RTDB, rate):
        threading.Thread.__init__(self)
        self.rate = rate
        self.db = RTDB
        self.ShiftRPM = 20000
        self.initialised = False
        self.fname = "files\Beep.wav"  # path to beep soundfile
        self.IsOnTrack = False

    def run(self):
        while 1:
            # execute this loop while iRacing is running
            while self.db.startUp:
                if not self.initialised:
                    self.initialise()
                # two beeps sounds as notification when entering iRacing
                if self.db.IsOnTrack and not self.IsOnTrack:
                    self.IsOnTrack = True
                    winsound.PlaySound(self.fname, winsound.SND_FILENAME)
                    time.sleep(0.3)
                    winsound.PlaySound(self.fname, winsound.SND_FILENAME)

                # execute this loop while player is on track
                while self.db.IsOnTrack and self.db.ShiftToneEnabled:
                    if self.db.Gear > 0 and self.db.UpshiftStrategy < 4:
                        self.beep(self.db.iRShiftRPM[self.db.UpshiftStrategy])
                    elif self.db.Gear > 0 and self.db.UpshiftStrategy == 4:
                        self.beep2()

                    # #	check if upshift RPM is reached
                    # if self.db.Gear > 0 and self.db.Gear < 6 and self.db.RPM >= self.ShiftRPM:  # disable sound for neutral and reverse gear
                    #     winsound.PlaySound(self.fname, winsound.SND_FILENAME)
                    #     time.sleep(0.75)  # pause for 750 ms to avoid multiple beeps when missing shiftpoint

                # update flag when leaving track
                if not self.db.IsOnTrack and self.IsOnTrack:
                    self.IsOnTrack = False

            self.initialised = False

    def beep(self, shiftRPM):
        if self.db.RPM >= shiftRPM and self.db.UserShiftFlag[self.db.Gear-1]:
            winsound.PlaySound(self.fname, winsound.SND_FILENAME)
            time.sleep(0.75)  # pause for 750 ms to avoid multiple beeps when missing shiftpoint

    def beep2(self):
        if self.db.RPM >= self.db.UserShiftRPM[self.db.Gear-1] and self.db.UserShiftFlag[self.db.Gear-1]:
            winsound.PlaySound(self.fname, winsound.SND_FILENAME)
            time.sleep(0.75)  # pause for 750 ms to avoid multiple beeps when missing shiftpoint
            
    def initialise(self):
        time.sleep(0.1)
        # get optimal shift RPM from iRacing and display message
        self.FirstRPM = self.db.DriverInfo['DriverCarSLFirstRPM']
        self.ShiftRPM = self.db.DriverInfo['DriverCarSLShiftRPM']
        self.LastRPM = self.db.DriverInfo['DriverCarSLLastRPM']
        self.BlinkRPM = self.db.DriverInfo['DriverCarSLBlinkRPM']
        self.DriverCarName = self.db.DriverInfo['Drivers'][self.db.DriverInfo['DriverCarIdx']]['CarScreenNameShort']

        # self.db.DriverInfo['Drivers'][self.db.DriverInfo['DriverCarIdx']]['CarScreenNameShort']
        print('First Shift RPM for', self.DriverCarName, ':', self.FirstRPM)
        print('Shift RPM for', self.DriverCarName, ':', self.ShiftRPM)
        print('Last Shift RPM for', self.DriverCarName, ':', self.LastRPM)
        print('Blink Shift RPM for', self.DriverCarName, ':', self.BlinkRPM)

        self.db.iRShiftRPM = [self.FirstRPM, self.ShiftRPM, self.LastRPM, self.BlinkRPM]

        # play three beep sounds as notification
        winsound.PlaySound(self.fname, winsound.SND_FILENAME)
        time.sleep(0.3)
        winsound.PlaySound(self.fname, winsound.SND_FILENAME)
        time.sleep(0.3)
        winsound.PlaySound(self.fname, winsound.SND_FILENAME)

        self.initialised = True

# GUI Thread
class iGUI(threading.Thread):
    def __init__(self, RTDB, rate):
        threading.Thread.__init__(self)
        self.rate = rate
        self.db = RTDB
        self.ir = irsdk.IRSDK()

    def run(self):
        while 1:
            GUI = iDDUgui(myRTDB)
            GUI.start(myRTDB)
            time.sleep(self.rate)
        

# initialise and start thread
thread1 = iRThread(myRTDB, list(iRData.keys()), 0.01)
thread2 = UpShiftTone(myRTDB, 0.01)
thread3 = iGUI(myRTDB, 0.01)
thread1.start()
time.sleep(1)
thread3.start()
time.sleep(1)
thread2.start()
time.sleep(1)

# create objects for rendering and calculation
iRRender = iDDURender.RenderScreen(myRTDB)
iDDUcalc = iDDUcalc.IDDUCalc2(myRTDB)


# loop to run programme
while not myRTDB.done:
    iDDUcalc.calc()
    myRTDB.done = iRRender.render()

iRRender.pygame.quit()
del iRRender
del iDDUcalc
del thread1
del thread2
del thread3
exit()
