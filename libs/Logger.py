import os
import time
from datetime import datetime
from libs.IDDU import IDDUThread


class LoggerThread(IDDUThread):
    logging = False
    init = False

    def __init__(self, rate):
        IDDUThread.__init__(self, rate)
        self.file = []
        self.rate = rate
        self.keys = ['SessionTime',
                     'Speed',
                     'ThrottleRaw',
                     'LongAccel',
                     'RPM',
                     'Gear',
                     'StintLap',
                     'Lap',
                     'tExecuteRTDB',
                     'tExecuteUpshiftTone',
                     'tExecuteRaceLapsEstimation',
                     'tExecuteLogger',
                     'tExecuteRender',
                     'tExecuteCalc',
                     'tShiftReaction',
                     'FuelLevel',
                     'tNextLiftPoint',
                     'LapDistPct',
                     'BLiftToneRequest',
                     'NNextLiftPoint',
                     'VFuelTgtEffective',
                     'VFuelStartStraight',
                     'VFuelBudgetActive',
                     'dVFuelTgt',
                     'BUpdateVFuelDelta',
                     'VFuelReferenceActive',
                     'VFuelUsedLap']

        self.header = 'Time'

        for i in range(0, len(self.keys)):
            self.header = self.header + ',' + self.keys[i]

        self.header = self.header + '\n'

        if not os.path.exists("data/laplog/"):
            os.mkdir("data/laplog/")

    def run(self):
        while 1:
            while self.db.config['BLoggerActive']:
                t = time.perf_counter()
                if not self.init:
                    self.init = True
                    print('Logger active')

                if self.logging:
                    if self.db.IsOnTrack:
                        # normal logging
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
                        path = self.db.dir + '/data/laplog/' + fileName

                        self.file = open(path, "a")
                        # write header
                        if os.stat(path).st_size == 0:
                            self.file.write(self.header)

                        # log first line
                        self.file.write(self.getDataStr())
                        self.logging = True

                self.db.tExecuteLogger = (time.perf_counter() - t) * 1000

                time.sleep(self.rate)

            if self.init and not self.db.config['BLoggerActive']:
                self.init = False
                print('Logger inactive')

            time.sleep(1)


    def getDataStr(self):
        now = datetime.now()
        dataStr = now.strftime("%H:%M:%S.%f")
        for i in range(0,len(self.keys)):
            dataStr = dataStr + "," + str(self.db.get(self.keys[i]))

        return dataStr + "\n"

