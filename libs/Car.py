import numpy as np
import time
import irsdk
from functionalities.libs import importExport
import xmltodict



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
        self.VFuelLap = {}
        self.UserShiftRPM = 0
        self.UpshiftStrategy = 0
        self.UserShiftFlag = 0
        self.UpshiftSettings = {
            'nMotorShiftOptimal': [0]*8,
            'nMotorShiftTarget': [0]*8,
            'vCarShiftOptimal': [0]*8,
            'vCarShiftTarget': [0]*8,
            'BShiftTone': [False]*7,
            'NGear': [1, 2, 3, 4, 5, 6, 7, 8],
            'SetupName': 'SetupName',
            'CarSetup': {},
            'BValid': False
        }
        self.Coasting = {
            'gLongCoastPolyFit': [],
            'QFuelCoastPolyFit':  [],
            'NGear': [],
            'SetupName': 'SetupName',
            'CarSetup': {}
        }
        self.pBrakeFMax = 0
        self.pBrakeRMax = 0
        self.rGearRatios = [0]*8
        self.rSlipMapAcc = [4.5, 7, 8.5]
        self.rSlipMapBrk = [-4.5, -7, -8.5]
        self.rABSActivityMap = [-2, -10, -15]

    def createCar(self, db, var_headers_names=None):
        DriverCarIdx = db.DriverInfo['DriverCarIdx']
        self.name = db.DriverInfo['Drivers'][DriverCarIdx]['CarScreenNameShort']
        self.iRShiftRPM = [db.DriverInfo['DriverCarSLFirstRPM'], db.DriverInfo['DriverCarSLShiftRPM'], db.DriverInfo['DriverCarSLLastRPM'], db.DriverInfo['DriverCarSLBlinkRPM']]

        DRSList = ['formularenault35',  # TODO: shouldn't be here
                   'mclarenmp430']

        if any(self.name in s for s in DRSList):
            self.BDRS = True
        else:
            self.BDRS = False

        P2PList = ['dallaradw12',  # TODO: shouldn't be here
                   'dallarair18']

        if any(self.name in s for s in P2PList):
            self.BP2P = True
        else:
            self.BP2P = False

        dcIgnoreList = ['dcHeadlightFlash', 'dcPitSpeedLimiterToggle', 'dcStarter', 'dcTractionControlToggle', 'dcTearOffVisor', 'dcPushToPass', 'dcDashPage']  # TODO: shouldn't be here

        dcNotInt = ['dcBrakeBias']  # TODO: shouldn't be here

        keys = []
        if var_headers_names is None:

            ir = irsdk.IRSDK()

            if ir.startup():
                keys = ir.var_headers_names

            ir.shutdown()

        else:
            keys = var_headers_names

        for i in range(0, len(keys)):
            temp = keys[i]
            if temp.startswith('dc'):
                if not (temp.endswith('Change') or temp.endswith('Old') or temp.endswith('Str') or temp.endswith('Time')):
                    if not keys[i] is None:
                        if keys[i] in dcIgnoreList:
                            self.dcList[keys[i]] = (keys[i].split('dc')[1], False, 0)
                        else:
                            if any(keys[i] in s for s in dcNotInt):
                                self.dcList[keys[i]] = (keys[i].split('dc')[1], True, 1)
                            else:
                                self.dcList[keys[i]] = (keys[i].split('dc')[1], True, 0)

        self.setUserShiftRPM(db)

        self.tLap = {}

        db.BMultiInitRequest = True

    def setUserShiftRPM(self, db):
        if 'config' in dir(db):
            self.UserShiftRPM = db.config['UserShiftRPM']
            self.UpshiftStrategy = db.config['UpshiftStrategy']
            self.UserShiftFlag = db.config['UserShiftFlag']

    def setShiftRPM(self, nMotorShiftOptimal, vCarShiftOptimal, nMotorShiftTarget, vCarShiftTarget, NGear, SetupName, CarSetup):
        for i in range(0, len(NGear)):
            self.UpshiftSettings['nMotorShiftOptimal'][i] = nMotorShiftOptimal[i]
            self.UpshiftSettings['vCarShiftOptimal'][i] = vCarShiftOptimal[i]
            self.UpshiftSettings['nMotorShiftTarget'][i] = nMotorShiftTarget[i]
            self.UpshiftSettings['vCarShiftTarget'][i] = vCarShiftTarget[i]
            self.UpshiftSettings['BShiftTone'][i] = True

        self.UpshiftSettings['SetupName'] = SetupName
        self.UpshiftSettings['CarSetup'] = CarSetup
        self.UpshiftStrategy = 5
        self.UpshiftSettings['BValid'] = True

    def setCoastingData(self, gLongPolyFit, QFuelPolyFit, NGear, SetupName, CarSetup):
        self.Coasting['gLongCoastPolyFit'] = gLongPolyFit
        self.Coasting['QFuelCoastPolyFit'] = QFuelPolyFit
        self.Coasting['NGear'] = NGear
        self.Coasting['SetupName'] = SetupName
        self.Coasting['CarSetup'] = CarSetup

    def setGearRatios(self, rGearRatios):
        self.rGearRatios = rGearRatios

    def addLapTime(self, trackName, tLap, LapDistPct, LapDistPctTrack, VFuelLap):
        self.tLap[trackName] = np.interp(LapDistPctTrack, LapDistPct, tLap).tolist()
        self.VFuelLap[trackName] = VFuelLap

    def save(self, *args):

        filepath = ''

        if len(args) == 1:
            if args[0].endswith('.json'):
                filepath = args[0]
            elif '/' in args[0] or "\\" in args[0]:
                filepath = args[0] + '/data/car/' + self.name + '.json'
            else:
                print('I dont know how to save the car as: ', args[0])
        elif len(args) == 2:
            filepath = args[0] + '/' + args[1] + '.json'
        else:
            print('Invalid number if arguments. Max 2 arguments accepted!')
            return

        # get list of track object properties
        variables = list(self.__dict__.keys())

        # create dict of track object properties
        data = {}

        for i in range(0, len(variables)):
            data[variables[i]] = self.__dict__[variables[i]]

        importExport.saveJson(data, filepath)

        print(time.strftime("%H:%M:%S", time.localtime()) + ':\tSaved car ' + filepath)

    def load(self, path):
        data = importExport.loadJson(path)

        temp = list(data.items())
        for i in range(0, len(data)):
            self.__setattr__(temp[i][0], temp[i][1])

        print(time.strftime("%H:%M:%S", time.localtime()) + ':\tLoaded car ' + path)

    def setpBrakeMax(self, pBrakeFMax, pBrakeRMax):
        self.pBrakeFMax = pBrakeFMax
        self.pBrakeRMax = pBrakeRMax

    def MotecXMLexport(self):
        path = 'C:/Users/marc/Documents/MoTeC/i2/Workspaces/Circuit 1/Maths'

        # real defaul xml

        with open(path +'/default.xml') as fd:
            doc = xmltodict.parse(fd.read())

        # populate struct with new values
        doc['Maths']['@Id'] = self.name
        doc['Maths']['@Condition'] = '\'Vehicle Id\' == "{}"'.format(self.name)

        for i in range(0, max(self.UpshiftSettings['NGear'])):
            for exp in doc['Maths']['MathConstants']['MathConstant']:
                if exp['@Name'] == 'nMotorShiftGear{}'.format(i+1):
                    exp['@Value'] = str(self.UpshiftSettings['nMotorShiftOptimal'][i])

        for i in range(0, len(self.UpshiftSettings['NGear'])):
            for exp in doc['Maths']['MathConstants']['MathConstant']:
                if exp['@Name'] == 'rGear{}'.format(i+1):
                    exp['@Value'] = str(self.rGearRatios[i+1])


        # export xml
        xmlString = xmltodict.unparse(doc, pretty=True)
        f = open(path + '/{}.xml'.format(self.name), "a")
        f.write(xmlString)
        f.close()


