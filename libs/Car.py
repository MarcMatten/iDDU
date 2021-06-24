import numpy as np
import time
import irsdk
from functionalities.libs import importExport
import xmltodict
from collections import OrderedDict


class Car:
    def __init__(self, **kwargs):
        if 'Driver' in kwargs:
            self.name = kwargs['Driver']['CarScreenNameShort']
            self.carPath = kwargs['Driver']['CarPath']
        else:
            if 'name' in kwargs:
                self.name = kwargs['name']
            else:
                print('Error while creating car! No NAME provided.')
            if 'carPath' in kwargs:
                self.carPath = kwargs['carPath']
            else:
                print('Error while creating car! No CARPATH provided.')

        self.iRShiftRPM = []
        self.BDRS = False
        self.BP2P = False
        self.dcList = {}
        self.NABSDisabled = None
        self.NTC1Disabled = None
        self.NTC2Disabled = None
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
            'gLongCoastPolyFit': np.repeat([[1.25, -0.099, 0]], 8, axis=0),
            'QFuelCoastPolyFit':  np.repeat([[0.001, 0, 0]], 8, axis=0),
            'NGear': [0, 1, 2, 3, 4, 5, 6, 7],
            'SetupName': 'SetupName',
            'CarSetup': {},
            'BValid': False
        }
        self.pBrakeFMax = 0
        self.pBrakeRMax = 0
        self.rGearRatios = [0]*8
        self.rSlipMapAcc = [4.5, 7, 8.5]
        self.rSlipMapBrk = [-4.5, -7, -8.5]
        self.rABSActivityMap = [-2, -10, -15]
        self.NGearMax = 0

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

    def setShiftRPM(self, nMotorShiftOptimal, vCarShiftOptimal, nMotorShiftTarget, vCarShiftTarget, NGear, SetupName, CarSetup, NGearMax):
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
        self.NGearMax = NGearMax

    def setCoastingData(self, gLongPolyFit, QFuelPolyFit, NGear, SetupName, CarSetup):
        self.Coasting['gLongCoastPolyFit'] = gLongPolyFit
        self.Coasting['QFuelCoastPolyFit'] = QFuelPolyFit
        self.Coasting['NGear'] = NGear
        self.Coasting['SetupName'] = SetupName
        self.Coasting['CarSetup'] = CarSetup
        self.Coasting['BValid'] = True

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

    def MotecXMLexport(self, rootPath=str, MotecPath=str) -> None:
        """
        Exports all calculated vehilce parameters to a Motec readable XML file

        :param rootPath: Path to project  directory
        :param MotecPath: Path to Motec project directory
        :return:
        """

        def write2XML(name, value, unit):
            BDone = False
            for exp in doc['Maths']['MathConstants']['MathConstant']:
                if exp['@Name'] == name:
                    exp['@Value'] = str(value)
                    exp['@Unit'] = unit
                    BDone = True

            if not BDone:
                OD = OrderedDict()
                OD['@Name'] = name
                OD['@Value'] = str(value)
                OD['@Unit'] = unit
                doc['Maths']['MathConstants']['MathConstant'].append(OD)



        # read default xml
        with open(rootPath + '/files/default.xml') as fd:
            doc = xmltodict.parse(fd.read())

        # populate struct with new values
        doc['Maths']['@Id'] = self.carPath
        doc['Maths']['@Condition'] = '\'Vehicle Id\' == "{}"'.format(self.carPath)

        # shift RPM
        if self.UpshiftSettings['BValid']:
            for i in range(0, self.NGearMax):
                write2XML('nMotorShiftGear{}'.format(i+1), self.UpshiftSettings['nMotorShiftOptimal'][i], 'rpm')
        self.Coasting['gLongCoastPolyFit'][0][0]
        # gear ratios
        if self.UpshiftSettings['BValid'] or self.Coasting['BValid']:
            for i in range(1, self.NGearMax + 1):
                write2XML('rGear{}'.format(i), self.rGearRatios[i], 'ratio')

        # coasting
        if self.Coasting['BValid']:
            for i in range(0, self.NGearMax + 1):
                for k in range(0, len(self.Coasting['gLongCoastPolyFit'][i])):
                    write2XML('gLongCoastGear{}Poly{}'.format(i, k), self.Coasting['gLongCoastPolyFit'][i][k], '')

        # brake line pressure
        write2XML('pBrakeFMax', self.pBrakeFMax, 'bar')
        write2XML('pBrakeRMax', self.pBrakeRMax, 'bar')

        # export xml
        xmlString = xmltodict.unparse(doc, pretty=True)
        f = open(MotecPath + '/Maths/{}.xml'.format(self.name), "a")
        f.write(xmlString)
        f.close()
        print(time.strftime("%H:%M:%S", time.localtime()) + ':\tExported Motec XML file: {}.xml'.format(self.name))


