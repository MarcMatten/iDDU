import os, threading
from time import sleep
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
        # self.ir = irsdk.IRSDK()

    def run(self):
        while 1:
            while self.db.BLoggerActive:
                if not self.init:
                    self.init = True
                    print('Logger active')

                if self.logging:
                    if self.db.IsOnTrack:
                        # normal logging
                        now = datetime.now()
                        self.file.write(now.strftime("%H:%M:%S.%f") + "," + str(self.db.SessionTime) + "," + str(self.db.RPM) + "," + str(self.db.Gear) + "," + str(self.db.Alarm[7]) + "\n")
                        self.file.flush()
                    else:
                        # stop logging, close logfile,
                        self.file.flush()
                        sleep(1)
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

                        self.file = open(self.db.dir + '/laplog/' + fileName, "a")
                        # write header
                        if os.stat(self.db.dir + "/data_log.csv").st_size == 0:
                            self.file.write("Time,SessionTime,RPM,Gear,Alarm\n")

                        # log first line
                        now = datetime.now()
                        # if self.ir.startup():
                        self.file.write(now.strftime("%H:%M:%S.%f") + "," + str(self.db.SessionTime) + "," + str(self.db.RPM) + "," + str(self.db.Gear) + "," + str(self.db.Alarm[7]) + "\n")
                        self.file.flush()

                        self.logging = True

                sleep(self.rate)

            if self.init and not self.db.BLoggerActive:
                self.init = False
                print('Logger inactive')

            sleep(self.rate)