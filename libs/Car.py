import numpy as np
import time
import irsdk
from libs.auxiliaries import importExport
import xmltodict
from collections import OrderedDict
from libs import IDDU


class Car:
    def __init__(self, **kwargs):
        if 'Driver' in kwargs:
            self.name = kwargs['Driver']['CarScreenNameShort']
            self.carPath = kwargs['Driver']['CarPath']
        else:
            if 'name' in kwargs:
                self.name = kwargs['name']
            else:
                IDDU.IDDUItem.logger.error('Error while creating car! No NAME provided.')
            if 'carPath' in kwargs:
                self.carPath = kwargs['carPath']
            else:
                IDDU.IDDUItem.logger.error('Error while creating car! No CARPATH provided.')

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
            'base': {
                'nMotorShiftOptimal': [0]*8,
                'nMotorShiftTarget': [0]*8,
                'vCarShiftOptimal': [0]*8,
                'vCarShiftTarget': [0]*8,
                'nMotorShiftLEDs': [[0, 0, 0]] * 8,
                'BShiftTone': [False]*7,
                'NGear': [1, 2, 3, 4, 5, 6, 7, 8],
                'SetupName': 'SetupName',
                'BValid': False
            }
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
        self.rGearRatios = {'base': [0]*8}
        self.rSlipMapAcc = [2.5, 4, 6.5, 9]
        self.rSlipMapBrk = [-2.5, -4, -6.5, -9]
        self.rABSActivityMap = [-1, -5, -10, -15]
        self.NGearMax = 0

        self.tempKey = []
        self.tempVals = []

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

        dcIgnoreList = ['dcHeadlightFlash', 'dcPitSpeedLimiterToggle', 'dcStarter', 'dcTractionControlToggle', 'dcTearOffVisor', 'dcPushToPass', 'dcDashPage', 'dcToggleWindshieldWipers', 'dcTriggerWindshieldWipers']  # TODO: shouldn't be here

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
                            self.dcList[keys[i]] = (keys[i].split('dc')[1], False, 0, [None]*12)
                        else:
                            if any(keys[i] in s for s in dcNotInt):
                                self.dcList[keys[i]] = (keys[i].split('dc')[1], True, 1, [None]*12)
                            else:
                                self.dcList[keys[i]] = (keys[i].split('dc')[1], True, 0, [None]*12)

        self.setUserShiftRPM(db)

        self.tLap = {}

        db.BMultiInitRequest = True

    def setUserShiftRPM(self, db):
        if 'config' in dir(db):
            self.UserShiftRPM = db.config['UserShiftRPM']
            self.UpshiftStrategy = db.config['UpshiftStrategy']
            self.UserShiftFlag = db.config['UserShiftFlag']

    def setShiftRPM(self, nMotorShiftOptimal, vCarShiftOptimal, nMotorShiftTarget, vCarShiftTarget, NGear, SetupName, CarSetup, NGearMax, nMotorShiftLEDs, GearID):
        UpshiftSettings = {
            'nMotorShiftOptimal': [0]*8,
            'nMotorShiftTarget': [0]*8,
            'vCarShiftOptimal': [0]*8,
            'vCarShiftTarget': [0]*8,
            'nMotorShiftLEDs': [[0, 0, 0]] * 8,
            'BShiftTone': [False]*7,
            'NGear': [1, 2, 3, 4, 5, 6, 7, 8],
            'SetupName': 'SetupName',
            'BValid': False
            }

        for i in range(0, len(NGear)):
            UpshiftSettings['nMotorShiftOptimal'][i] = nMotorShiftOptimal[i]
            UpshiftSettings['vCarShiftOptimal'][i] = vCarShiftOptimal[i]
            UpshiftSettings['nMotorShiftTarget'][i] = nMotorShiftTarget[i]
            UpshiftSettings['vCarShiftTarget'][i] = vCarShiftTarget[i]
            UpshiftSettings['nMotorShiftLEDs'][i] = nMotorShiftLEDs[i]
            UpshiftSettings['BShiftTone'][i] = True
            UpshiftSettings['SetupName'] = SetupName
            UpshiftSettings['BValid'] = True
        
        self.UpshiftSettings[GearID] = UpshiftSettings

        if not self.UpshiftSettings['base']['BValid']:
            self.UpshiftSettings['base'] = UpshiftSettings

        #self.UpshiftSettings['SetupName'] = SetupName
        #self.UpshiftSettings['CarSetup'] = CarSetup
        self.UpshiftStrategy = 5
        self.NGearMax = NGearMax

    def setCoastingData(self, gLongPolyFit, QFuelPolyFit, NGear, SetupName, CarSetup):
        self.Coasting['gLongCoastPolyFit'] = gLongPolyFit
        self.Coasting['QFuelCoastPolyFit'] = QFuelPolyFit
        self.Coasting['NGear'] = NGear
        self.Coasting['SetupName'] = SetupName
        self.Coasting['CarSetup'] = CarSetup
        self.Coasting['BValid'] = True

    def setGearRatios(self, rGearRatios, GearID):
        self.rGearRatios[GearID] = rGearRatios

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
                IDDU.IDDUItem.logger.error('I dont know how to save the car as: ', args[0])
        elif len(args) == 2:
            filepath = args[0] + '/' + args[1] + '.json'
        else:
            IDDU.IDDUItem.logger.error('Invalid number if arguments. Max 2 arguments accepted!')
            return

        # get list of track object properties
        variables = list(self.__dict__.keys())

        # create dict of track object properties
        data = {}

        for i in range(0, len(variables)):
            data[variables[i]] = self.__dict__[variables[i]]

        importExport.saveJson(data, filepath)

        IDDU.IDDUItem.logger.info('Saved car ' + filepath)

    def load(self, path):
        data = importExport.loadJson(path)
        BSafeAfterLoading = False

        for i in data:
            if isinstance(data[i], dict):
                if hasattr(self, i):
                    try:
                        self.__getattribute__(i).update(data[i])
                    except:
                        pass
                else:
                    self.__setattr__(i, data[i])
            else:
                self.__setattr__(i, data[i])

        if 'BValid' in self.UpshiftSettings:
            if self.UpshiftSettings['BValid']:
                temp = {}
                for i in self.UpshiftSettings:
                    if not isinstance(self.UpshiftSettings[i], dict):
                        temp[i] = self.UpshiftSettings[i]            
                for i in temp:
                    del self.UpshiftSettings[i]
                if 'CarSetup' in self.UpshiftSettings:
                    del self.UpshiftSettings['CarSetup']
                self.UpshiftSettings['base'] = temp

        if not isinstance(self.rGearRatios, dict):
            temp = self.rGearRatios
            self.rGearRatios = {'base': temp}

        if self.dcList:
            for i in self.dcList:
                if len(self.dcList[i]) < 4:
                    BSafeAfterLoading = True
                    self.dcList[i].append([None]*16)
                

        if BSafeAfterLoading:
            self.save(path)
        IDDU.IDDUItem.logger.info('Loaded car ' + path)


    def setpBrakeMax(self, pBrakeFMax, pBrakeRMax):
        if not pBrakeFMax == 0:
            self.pBrakeFMax = pBrakeFMax
        if not pBrakeRMax == 0:
            self.pBrakeRMax = pBrakeRMax

    def MotecXMLexport(self, rootPath=str, MotecPath=str, GearID=str) -> None:
        """
        Exports all calculated vehilce parameters to a Motec readable XML file

        :param rootPath: Path to project  directory
        :param MotecPath: Path to Motec project directory
        :param GearID: String describing current gearbox configuration
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
        if self.UpshiftSettings[GearID]['BValid']:
            for i in range(0, self.NGearMax):
                write2XML('nMotorShiftGear{}'.format(i+1), self.UpshiftSettings[GearID]['nMotorShiftOptimal'][i], 'rpm')
        # gear ratios
        if self.UpshiftSettings[GearID]['BValid'] or self.Coasting['BValid']:
            for i in range(1, self.NGearMax + 1):
                write2XML('rGear{}'.format(i), self.rGearRatios[GearID][i], 'ratio')

        # coasting
        if self.Coasting['BValid']:
            for i in range(0, self.NGearMax + 1):
                for k in range(0, len(self.Coasting['gLongCoastPolyFit'][i])):
                    write2XML('gLongCoastGear{}Poly{}'.format(i, k), self.Coasting['gLongCoastPolyFit'][i][k], '')

        # brake line pressure
        write2XML('pBrakeFMax', self.pBrakeFMax, 'bar')
        write2XML('pBrakeRMax', self.pBrakeRMax, 'bar')

        # slip rations thresholds
        write2XML('rSlipMapAcc', self.rSlipMapAcc, '%')
        write2XML('rSlipMapBrk', self.rSlipMapBrk, '%')
        write2XML('rABSActivityMap', self.rABSActivityMap, 'bar')

        # export xml
        xmlString = xmltodict.unparse(doc, pretty=True)
        f = open(MotecPath + '/Maths/{}.xml'.format(self.name), "w")
        f.write(xmlString)
        f.close()
        IDDU.IDDUItem.logger.info('Exported Motec XML file: {}.xml'.format(self.name))

    def getGearID(self, CarSetup):
        self.tempKey = []
        self.tempVals = []
        try:
            a, _ = self.myprint(CarSetup)
            del self.tempKey, self.tempVals
        except:
            a = 'base'

        if a == '':
            a = 'base'

        return a

    def myprint(self, setup, N=0):
        if len(self.tempKey) <= N:
            self.tempKey.append('')  

        for k, v in setup.items():
            if isinstance(v, dict):
                self.tempKey[N] = k
                _, _ = self.myprint(v, N+1)
            else:
                if 'Gear' in k or 'FinalDrive' in k or 'SpeedIn' in k:
                    self.tempKey[N] = k
                    self.tempVals.append(v)
                    #print(v)
                    #print(tempKey)
        
        val = ''
        for i in self.tempVals:
            val += ('|' + i.__str__())
        
        
        key = ''
        for i in self.tempKey:
            key += ('.'+i)

        return val[1:], key[1:]


