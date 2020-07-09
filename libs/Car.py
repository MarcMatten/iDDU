import json
import numpy as np
import time
import irsdk


class NumpyArrayEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NumpyArrayEncoder, self).default(obj)


class Car:
    def __init__(self, name):
        self.name = name
        self.iRShiftRPM = []
        self.BDRS = False
        self.BP2P = False
        self.dcList = {}
        self.NABSDisabled = 0
        self.NTC1Disabled = 0
        self.NTC2Disabled = 0
        self.tLap = {}
        self.UserShiftRPM = 0
        self.UpshiftStrategy = 0
        self.UserShiftFlag = 0
        self.UpshiftSettings = {
            'nMotorShiftOptimal': [99999]*7,
            'nMotorShiftTarget': [99999]*7,
            'vCarShiftOptimal': [99999]*7,
            'vCarShiftTarget': [99999]*7,
            'BShiftTone': [False]*7,
            'NGear': [1, 2, 3, 4, 5, 6, 7]
        }
        self.Coasting = {
            'gLongCoastPolyFit': [],
            'QFuelCoastPolyFit':  [],
            'NGear': []
        }

    def createCar(self, db):
        self.name = db.DriverInfo['Drivers'][db.DriverCarIdx]['CarScreenNameShort']
        self.iRShiftRPM = [db.DriverInfo['DriverCarSLFirstRPM'], db.DriverInfo['DriverCarSLShiftRPM'], db.DriverInfo['DriverCarSLLastRPM'], db.DriverInfo['DriverCarSLBlinkRPM']]

        DRSList = ['formularenault35',
                   'mclarenmp430']

        if any(self.name in s for s in DRSList):
            self.BDRS = True
        else:
            self.BDRS = False

        P2PList = ['dallaradw12',
                   'dallarair18']

        if any(self.name in s for s in P2PList):
            self.BP2P = True
        else:
            self.BP2P = False

        ir = irsdk.IRSDK()

        dcIgnoreList =['dcHeadlightFlash',
                       'dcPitSpeedLimiterToggle',
                       'dcStarter']


        dcNotInt =['dcBrakeBias']

        if ir.startup():
            keys = ir.var_headers_names

            for i in range(0, len(keys)):
                temp = keys[i]
                if temp.startswith('dc'):
                    if not (temp.endswith('Change') or temp.endswith('Old') or temp.endswith('Str') or temp.endswith('Time')):
                        if not keys[i] is None:
                            if any(keys[i] in s for s in dcIgnoreList):
                                self.dcList[keys[i]] = (keys[i].split('dc')[1], False, 0)
                            else:
                                if any(keys[i] in s for s in dcNotInt):
                                    self.dcList[keys[i]] = (keys[i].split('dc')[1], True, 1)
                                else:
                                    self.dcList[keys[i]] = (keys[i].split('dc')[1], True, 0)

        ir.shutdown()

        self.setUserShiftRPM(db)

        self.tLap = {}

    def setUserShiftRPM(self, db):
        self.UserShiftRPM = db.UserShiftRPM
        self.UpshiftStrategy = db.UpshiftStrategy
        self.UserShiftFlag = db.UserShiftFlag

    def setShiftRPM(self, nMotorShiftOptimal, vCarShiftOptimal, nMotorShiftTarget, vCarShiftTarget, NGear):
        for i in range(0, len(NGear)):
            self.UpshiftSettings['nMotorShiftOptimal'][i] = nMotorShiftOptimal[i]
            self.UpshiftSettings['vCarShiftOptimal'][i] = vCarShiftOptimal[i]
            self.UpshiftSettings['nMotorShiftTarget'][i] = nMotorShiftTarget[i]
            self.UpshiftSettings['vCarShiftTarget'][i] = vCarShiftTarget[i]
            self.UpshiftSettings['BShiftTone'][i] = True

    def setCoastingData(self, gLongPolyFit, QFuelPolyFit, NGear):
        self.Coasting['gLongCoastPolyFit'] = gLongPolyFit
        self.Coasting['QFuelCoastPolyFit'] = QFuelPolyFit
        self.Coasting['NGear'] = NGear

    def addLapTime(self, trackName, tLap, dist, distTrack):
        self.tLap[trackName] = np.interp(distTrack, dist, tLap).tolist()

    def saveJson(self, *args):
        if len(args) == 1:
            if args[0].endswith('.json'):
                filepath = args[0]
            elif '/' in args[0]:
                filepath = args[0] + '/car/' + self.name + '.json'
            else:
                print('I dont know how to save the car as: ', args[0])
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
            json.dump(data, outfile, indent=4, sort_keys=True, cls=NumpyArrayEncoder)

        print(time.strftime("%H:%M:%S", time.localtime()) + ':\tSaved car ' + filepath)

    def loadJson(self, path):
        with open(path) as jsonFile:
            data = json.loads(jsonFile.read())

        temp = list(data.items())
        for i in range(0, len(data)):
            self.__setattr__(temp[i][0], temp[i][1])

        print(time.strftime("%H:%M:%S", time.localtime()) + ':\tLoaded car ' + path)