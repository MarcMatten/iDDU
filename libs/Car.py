import json
import numpy as np
import time

class Car:
    def __init__(self, name):
        self.name = name
        self.iRShiftRPM = []
        self.BDRS = False
        self.BP2P = False
        self.dcList = []
        self.NABSDisabled = 0
        self.NTC1Disabled = 0
        self.NTC2Disabled = 0
        self.tLap = {}
        self.UserShiftRPM = 0
        self.UpshiftStrategy = 0
        self.UserShiftFlag = 0

    def createCar(self, db):
        self.name = db.DriverInfo['Drivers'][db.DriverInfo['DriverCarIdx']]['CarScreenNameShort']
        self.iRShiftRPM = [db.DriverInfo['DriverCarSLFirstRPM'], db.DriverInfo['DriverCarSLShiftRPM'], db.DriverInfo['DriverCarSLLastRPM'], db.DriverInfo['DriverCarSLBlinkRPM']]

        DRSList = ['formularenault35', 'mclarenmp430']
        if any(self.name in s for s in DRSList):
            self.BDRS = True
        else:
            self.BDRS = False

        P2PList = ['dallaradw12', 'dallarair18']
        if any(self.name in s for s in P2PList):
            self.BP2P = True
        else:
            self.BP2P = False

        keys = db.__dir__()

        for i in range(0, len(keys)):
            temp = keys[i]
            if temp.startswith('dc'):
                if not (temp.endswith('Change') or temp.endswith('Old') or temp.endswith('Str') or temp.endswith('Time')):
                    if not db.get(keys[i]) is None:
                        self.dcList.append(keys[i])

        self.setUserShiftRPM(db)

        self.tLap = {}

    def setUserShiftRPM(self, db):
        self.UserShiftRPM = db.UserShiftRPM
        self.UpshiftStrategy = db.UpshiftStrategy
        self.UserShiftFlag = db.UserShiftFlag

    def addLapTime(self, trackName, tLap, dist, distTrack):
        self.tLap[trackName] = np.interp(distTrack, dist, tLap).tolist()

    def saveJson(self, *args):
        if len(args) == 1:
            filepath = args[0] + '/car/' + self.name + '.json'
        elif len(args) == 2:
            filepath = args[0] + '/' + args[1] + '.json'
        else:
            print('Invalid number if arguments. Max 2 arguments accepted!')
            return

        variables = list(self.__dict__.keys())
        data = {}

        for i in range(0, len(variables)):
            data[variables[i]] = self.__dict__[variables[i]]

        with open(filepath, 'w') as outfile:
            json.dump(data, outfile, indent=4, sort_keys=True)

        print(time.strftime("%H:%M:%S", time.localtime()) + ':\tSaved car ' + filepath)

    def loadJson(self, path):
        with open(path) as jsonFile:
            data = json.loads(jsonFile.read())

        temp = list(data.items())
        for i in range(0, len(data)):
            self.__setattr__(temp[i][0], temp[i][1])

        print(time.strftime("%H:%M:%S", time.localtime()) + ':\tLoaded car ' + path)