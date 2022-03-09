import time
from libs import Car, Track
import os
from libs.auxiliaries import importExport
from libs.IDDU import IDDUThread
import numpy as np


class RTDB:
    dir = os.getcwd()
    WeekendInfo = None
    FuelTGTLiftPoints = None
    VFuelTgtOffset = 0
    VFuelTgt = 100
    car = None
    track = None
    map = None
    init = True
    WasOnTrack = False

    def __init__(self):
        timeStr = time.strftime("%H:%M:%S", time.localtime())
        self.initData = list()
        self.queryData = list()
        self.StopDDU = True
        self.StartDDU = False
        self.timeStr = time.strftime("%H:%M:%S", time.localtime())
        print(timeStr + ': RTDB initialised!')

    def initialise(self, data, BQueryData, BSnapshot):
        temp = list(data.items())
        for i in range(0, len(data)):
            self.__setattr__(temp[i][0], temp[i][1])
        self.initData.extend(temp)
        if BQueryData:
            self.queryData.extend(list(data.keys()))

        if not BSnapshot:
            self.BSnapshotMode = False
            self.car = Car.Car(name='default', carPath='default')
            self.car.load(self.dir + '/data/car/default.json')
            self.track = Track.Track('default')
            self.track.load(self.dir + '/data/track/default.json')
        else:
            self.BSnapshotMode = True

    def get(self, string):
        return self.__getattribute__(string)

    def reinitialise(self):
        print(time.strftime("%H:%M:%S", time.localtime()) + ': reinitialise RTDB!')
        self.StopDDU = True
        for i in range(0, len(self.initData)):
            self.__setattr__(self.initData[i][0], self.initData[i][1])
        self.timeStr = time.strftime("%H:%M:%S", time.localtime())
        print(time.strftime("%H:%M:%S", time.localtime()) + ': RTDB successfully reinitialised!')
        self.StartDDU = True

    def snapshot(self):
        snapshotDir = "data/snapshots/"

        if not os.path.exists(snapshotDir):
            os.mkdir(snapshotDir)

        nameStr = time.strftime(snapshotDir + "%Y_%m_%d-%H-%M-%S", time.localtime())+'_RTDBsnapshot'

        variables = list(self.__dict__.keys())
        variables.remove('car')
        variables.remove('track')

        self.car.save(self.dir, nameStr+'_car')
        self.track.save(self.dir, nameStr+'_track')

        self.WeekendInfo['WeekendOptions']['Date'] = str(self.WeekendInfo['WeekendOptions']['Date'])

        data = {}

        for i in range(0, len(variables)):
            data[variables[i]] = self.__getattribute__(variables[i])

        importExport.saveJson(data, nameStr + '.json')

        print(time.strftime("%H:%M:%S", time.localtime()) + ': Saved snapshot: ' + nameStr+'.json')

    def loadSnapshot(self, name):
        self.StopDDU = True

        path = self.dir + '/data/snapshots/' + name

        self.StartDDU = True

        data = importExport.loadJson(path + '.json')

        carPath = path + '_car.json'
        self.car = Car.Car('default', 'default')
        self.car.load(carPath)

        trackPath = path + '_track.json'
        self.track = Track.Track('default')
        self.track.load(trackPath)
        self.map = self.track.map



        data['DDUrunning'] = False
        data['StopDDU'] = True
        data['StartDDU'] = False

        self.initialise(data, False, True)

        print(time.strftime("%H:%M:%S", time.localtime()) + ': Loaded RTDB snapshot: ' + name +'.json')

    def loadFuelTgt(self, path):  # TODO: does this need to live in here?
        data = importExport.loadJson(path)

        temp = list(data.items())
        for i in range(0, len(data)):
            self.FuelTGTLiftPoints.__setitem__(temp[i][0], temp[i][1])

        self.VFuelTgtOffset = 0
        self.VFuelTgt = np.max(self.FuelTGTLiftPoints['VFuelTGT'])
        self.config['VFuelTgt'] = np.max(self.FuelTGTLiftPoints['VFuelTGT'])

        self.car.VFuelLap[self.FuelTGTLiftPoints['SFuelConfigTrackName']] = self.VFuelTgt
        self.car.save(self.dir)

        self.init = True
        self.WasOnTrack = False

        print(time.strftime("%H:%M:%S", time.localtime()) + ':\tImported ' + path)


# create thread to update RTDB
class RTDBThread(IDDUThread):

    def __init__(self, rate):
        IDDUThread.__init__(self, rate)

    def run(self):
        while 1:
            t = time.perf_counter()
            self.db.startUp = self.ir.startup()
            if self.db.startUp:
                # self.ir.freeze_var_buffer_latest()
                for i in range(0, len(self.db.queryData)):
                    self.db.__setattr__(self.db.queryData[i], self.ir[self.db.queryData[i]])
                # self.ir.unfreeze_var_buffer_latest()

                # Mapping CarIdx for DriverInfo['Drivers']
                self.db.CarIdxMap = [None]*64
                for i in range(0, len(self.db.DriverInfo['Drivers'])):
                    self.db.CarIdxMap[self.db.DriverInfo['Drivers'][i]['CarIdx']] = i

            else:
                self.ir.shutdown()
            self.db.timeStr = time.strftime("%H:%M:%S", time.localtime())
            self.db.tExecuteRTDB = (time.perf_counter() - t) * 1000
            time.sleep(self.rate)
