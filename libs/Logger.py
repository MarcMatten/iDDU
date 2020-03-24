import os, threading
import time
from datetime import datetime
# import irsdk


class Logger(threading.Thread):
    logging = False
    init = False

    def __init__(self, db, rate):
        threading.Thread.__init__(self)
        self.db = db
        self.file = []
        self.rate = rate
        self.keys=['SessionTime',
                   'Speed'
                   'RPM',
                   'Gear',
                   'Alarm',
                   'OnPitRoad',
                   'OutLap',
                   'StintLap',
                   'Lap',
                   'WasOnTrack',
                   'Run',
                   'tExecuteRTDB',
                   'tExecuteUpshiftTone',
                   'tExecuteRaceLapsEstimation',
                   'tExecuteLogger',
                   'tExecuteRender',
                   'tExecuteCalc',
                   'tShiftReaction',
                   'BNewLap',
                   'OnPitRoad',
                   'PlayerTrackSurface'
                   ]

        self.header = 'Time'

        for i in range(0,len(self.keys)):
            self.header = self.header + ',' + self.keys[i]

        self.header = self.header + '\n'

        # self.ir = irsdk.IRSDK()

    def run(self):
        while 1:
            while self.db.BLoggerActive:
                t = time.perf_counter()
                if not self.init:
                    self.init = True
                    print('Logger active')

                if self.logging:
                    if self.db.IsOnTrack:
                        # normal logging
                        #now = datetime.now()
                        #self.file.write(now.strftime("%H:%M:%S.%f") + "," + str(self.db.SessionTime) + "," + str(self.db.RPM) + "," + str(self.db.Gear) + "," + str(self.db.Alarm[7]) + "," + str(self.db.OnPitRoad) + "," + str(self.db.OutLap) + "," + str(self.db.StintLap) + "," + str(self.db.Lap) + "," + str(self.db.WasOnTrack) + "," + str(self.db.Run) + "\n")
                        self.file.write(self.getDataStr())
                        self.file.flush()
                    else:
                        # stop logging, close logfile,
                        self.file.flush()
                        time.sleep(1)
                        self.file.close()
                        self.logging = False
                        print('Stopped Logging')
                else:
                    if self.db.IsOnTrack:
                        # create new log file
                        print('Start Logging...')

                        now = datetime.now()
                        date_time = now.strftime("%Y-%m-%d_%H-%M-%S")

                        fileName = date_time + '_Run_'"{:02d}".format(self.db.Run) + '.csv'
                        path = self.db.dir + '/laplog/' + fileName

                        self.file = open(path, "a")
                        # write header
                        if os.stat(path).st_size == 0:
                            self.file.write(self.header)

                        # log first line

                        # if self.ir.startup():
                        # self.file.write(now.strftime("%H:%M:%S.%f") + "," + str(self.db.SessionTime) + "," + str(self.db.RPM) + "," + str(self.db.Gear) + "," + str(self.db.Alarm[7]) + "," + str(self.db.OnPitRoad) + "," + str(self.db.OutLap) + "," + str(self.db.StintLap) + "," + str(self.db.Lap) + "," + str(self.db.WasOnTrack) + "," + str(self.db.Run) + "\n")
                        self.file.write(self.getDataStr())
                        self.logging = True

                self.db.tExecuteLogger = (time.perf_counter() - t) * 1000

                time.sleep(self.rate)

            if self.init and not self.db.BLoggerActive:
                self.init = False
                print('Logger inactive')

                time.sleep(self.rate)


    def getDataStr(self):
        now = datetime.now()
        dataStr = now.strftime("%H:%M:%S.%f")
        for i in range(0,len(self.keys)):
            dataStr = dataStr + "," + str(self.db.get(self.keys[i]))

        return dataStr + "\n"

