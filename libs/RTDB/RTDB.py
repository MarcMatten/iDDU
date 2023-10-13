import os
import time

import numpy as np

from libs import Car, Track
from libs import IDDU
from libs.IDDU import IDDUThread
from libs.auxiliaries import importExport


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
        self.AM = AlertManager()
        self.AM.initAlarms()
        IDDU.IDDUItem.logger.info('RTDB initialised!')

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
        IDDU.IDDUItem.logger.info('Reinitialise RTDB!')
        self.StopDDU = True
        for i in range(0, len(self.initData)):
            self.__setattr__(self.initData[i][0], self.initData[i][1])
        self.timeStr = time.strftime("%H:%M:%S", time.localtime())
        IDDU.IDDUItem.logger.info('RTDB successfully reinitialised!')
        self.StartDDU = True

    def snapshot(self):
        snapshotDir = "data/snapshots/"

        if not os.path.exists(snapshotDir):
            os.mkdir(snapshotDir)

        nameStr = time.strftime(snapshotDir + "%Y_%m_%d-%H-%M-%S", time.localtime()) + '_RTDBsnapshot'

        variables = list(self.__dict__.keys())
        variables.remove('car')
        variables.remove('track')

        self.car.save(self.dir, nameStr + '_car')
        self.track.save(self.dir, nameStr + '_track')

        self.WeekendInfo['WeekendOptions']['Date'] = str(self.WeekendInfo['WeekendOptions']['Date'])

        data = {}

        for i in range(0, len(variables)):
            data[variables[i]] = self.__getattribute__(variables[i])

        importExport.saveJson(data, nameStr + '.json')

        IDDU.IDDUItem.logger.info('Saved snapshot: ' + nameStr + '.json')

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

        IDDU.IDDUItem.logger.info('Loaded RTDB snapshot: ' + name + '.json')

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

        IDDU.IDDUItem.logger.info('Imported ' + path)


# create thread to update RTDB
class RTDBThread(IDDUThread):

    def __init__(self, rate):
        IDDUThread.__init__(self, rate)

    def run(self):
        while self.running:
            t = time.perf_counter()
            self.tic()
            self.db.startUp = self.ir.startup()
            if self.db.startUp:
                # self.ir.freeze_var_buffer_latest()
                for i in range(0, len(self.db.queryData)):
                    self.db.__setattr__(self.db.queryData[i], self.ir[self.db.queryData[i]])
                # self.ir.unfreeze_var_buffer_latest()

                # Mapping CarIdx for DriverInfo['Drivers']
                self.db.CarIdxMap = [None] * 64
                for i in range(0, len(self.db.DriverInfo['Drivers'])):
                    self.db.CarIdxMap[self.db.DriverInfo['Drivers'][i]['CarIdx']] = i

            else:
                self.ir.shutdown()
            self.db.timeStr = time.strftime("%H:%M:%S", time.localtime())
            self.db.tExecuteRTDB = (time.perf_counter() - t) * 1000
            self.toc()
            time.sleep(self.rate)

    def stop(self):
        self.running = False
        self.logger.info('{} - Avg: {} ms | Min: {} ms | Max: {} ms '.format(type(self).__name__, np.round(self.tAvg, 3), np.round(self.tMin, 3), np.round(self.tMax, 3)))
        self.stopJU()


class AlertManager:
    white = (255, 255, 255)
    red = (255, 0, 0)
    green = (0, 255, 0)
    blue = (0, 0, 255)
    yellow = (255, 255, 0)
    orange = (255, 133, 13)
    grey = (141, 141, 141)
    black = (0, 0, 0)
    cyan = (0, 255, 255)
    purple = (255, 0, 255)
    alarms = []

    def __init__(self):
        pass

    def initAlarms(self):
        self.PITLIMITERACTIVE = Alarm('PIT LIMITER', self.blue, self.white, 4, 59, -1)
        self.ENGINESTALLED = Alarm('ENGINE STALLED', self.yellow, self.black, 4, 89, -1)
        self.FLASH = Alarm('FLASH', self.green, self.white, 5, 99, 2)
        self.PITLIMITEROFF = Alarm('PIT LIMITER OFF', self.red, self.white, 4, 83, -1)
        self.OILPRESSURE = Alarm('LOW OIL PRESSURE', self.red, self.white, 4, 87, -1)
        self.FUELPRESSURE = Alarm('LOW FUEL PRESSURE', self.red, self.white, 4, 88, -1)
        self.WATERTEMP = Alarm('WATER TEMP HIGH', self.red, self.white, 4, 99, -1)
        self.THUMBWHEELERRORL = Alarm('THMBWHL ERROR Left', self.red, self.white, 4, 90, 10)
        self.THUMBWHEELERRORR = Alarm('THMBWHL ERROR Right', self.red, self.white, 4, 90, 10)
        self.THUMBWHEELOFF = Alarm('THUMMBWHEELS OFF', self.red, self.white, 4, 90, 10)
        self.LOADRACESETUP = Alarm('LOAD RACE SETUP!', self.yellow, self.black, 3, 99, -1)
        self.LOWFUEL = Alarm('LOW FUEL!', self.yellow, self.black, 3, 99, -1)
        self.CROSSED = Alarm('CROSSED', self.white, self.black, 4, 9)
        self.RANDOMWAVING = Alarm('RANDOM WAVING', self.white, self.black, 0, 8)
        self.DISQUALIFIED = Alarm('DISQUALIFIED', self.white, self.black, 0, 94)
        self.P2PON = Alarm('P2P ON', self.green, self.white, 1, 99, 1)
        self.P2POFF = Alarm('P2P OFF', self.white, self.black, 1, 99, 1)
        self.TCOFF = Alarm('TC OFF', self.red, self.white, 5, 99, 5)
        self.CANCELLIFT = Alarm('CANCEL LIFT', self.green, self.white, 0, 99, 10)

    def raiseAlert(self):

        tRaised = time.time()

        if (tRaised - self.tRaised) < 5:
            return
        else:
            self.tRaised = tRaised

        if not self.BActive and not self.BIgnore and not self.BSurpress:
            self.BActive = True

        if self in AlertManager.alarms:
            pass
        else:
            AlertManager.alarms.append(self)
            IDDU.IDDUItem.logger.warning('Alarm {} raised!'.format(self.name))

    def ignore(self):
        self.BIgnore = True
        IDDU.IDDUItem.logger.info('Alarm {} ignored!'.format(self.name))

    def surpress(self):
        self.BSurpress = True
        self.tSurpress = time.time()
        IDDU.IDDUItem.logger.info('Alarm {} surpressed for {} seconds!'.format(self.name, self.tSurpressDuration))

    def reset(self):
        self.BSurpress = False
        self.BIgnore = False
        self.tRaised = 0
        self.tSurpress = 0
        self.cancelAlert()

    def resetAll(self):
        for i in self.__dir__():
            if type(self.__getattribute__(i)) == Alarm:
                self.__getattribute__(i).reset()
        IDDU.IDDUItem.logger.info('All alarms reset')

    def cancelAlert(self):
        idx = []

        for i in range(len(self.alarms)):
            if self.alarms[i].name == self.name:
                idx.append(i)

        for i in idx:
            AlertManager.alarms.pop(i)
            self.BActive = False

    def update(self):

        AlertManager.alarms = sorted(self.alarms, key=lambda d: d.priority, reverse=True)

        i = 0
        while i < len(AlertManager.alarms):
            if AlertManager.alarms[i].BSurpress:
                if time.time() - AlertManager.alarms[i].tSurpress > AlertManager.alarms[i].tSurpressDuration:
                    AlertManager.alarms[i].BSurpress = False
                    AlertManager.alarms[i].tSurpress = 0

            if AlertManager.alarms[i].tDuration:
                if AlertManager.alarms[i].tDuration == -1:
                    if AlertManager.alarms[i].tRaised:
                        AlertManager.alarms[i].tRaised = 0
                    else:
                        AlertManager.alarms[i].BActive = False
                        AlertManager.alarms[i].cancelAlert()
                        i = max(0, i - 1)
                    # return
                else:
                    if time.time() - AlertManager.alarms[i].tRaised >= AlertManager.alarms[i].tDuration:
                        AlertManager.alarms[i].BActive = False
                        AlertManager.alarms[i].tRaised = 0
                        AlertManager.alarms[i].cancelAlert()
                        i = max(0, i - 1)
            i += 1

    def display(self, n: int = 1):
        i = 0
        k = 0
        result = [None] * n
        while i < len(self.alarms) and k < n:
            if not (self.alarms[i].BIgnore or self.alarms[i].BSurpress) and self.alarms[i].BActive:
                result[k] = (self.alarms[i].name, self.alarms[i].labelcolour, self.alarms[i].textcolour, self.alarms[i].f)
                k += 1

            i += 1
        return result

    def currentAlarm(self):
        result = None
        k = 0
        for i in self.alarms:
            if i.BActive and not i.BIgnore and not i.BSurpress:
                result = i
                break
            k += 1

        return k


class Alarm(AlertManager):
    BActive = False

    def __init__(self,
                 name: str,
                 labelcolour: tuple,
                 textcolour: tuple,
                 f: float = 0,
                 priority: int = 0,
                 tDuration: float = -1,  # how long to be active
                 tRaised: float = 0,  # when it became active
                 tSurpress: float = 0,  # when it was surpressed
                 tSurpressDuration: float = 90,  # for how long to surpress
                 BIgnore: bool = False,  # ignore completely
                 BSurpress: bool = False):  # surpress

        AlertManager.__init__(self)
        self.name = name
        self.labelcolour = labelcolour
        self.textcolour = textcolour
        self.f = f
        self.priority = priority
        self.tDuration = tDuration
        self.tSurpressDuration = tSurpressDuration
        self.tRaised = tRaised
        self.tSurpress = tSurpress
        self.BIgnore = BIgnore
        self.BSurpress = BSurpress
