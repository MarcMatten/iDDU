import numpy as np
import time
from libs.auxiliaries import importExport
from libs.IDDU import IDDUItem, IDDUThread

# Button Documentation
# 00:  PAGE  - change dash page
# 01:  P2P   - Cancel lift when Fuel saving active TODO: boost otherwise
# 02:  ACK   - surpress Alarm
# 03:  TC    - switch off Traction Control
# 04:  PIT   - Pit speed Limiter
# 05:  RADIO - not used
# 06:  MARK  - Ignore Alarm when Alarm active, Telemetry Marker otherwise
# 07:  WIPER - turn on / toggle wipers
# 08:  
# 09:  
# 10:  
# 11:  
# 12:  Rotary left plus
# 13:  Rotary left minus
# 14:  Rotary right plus
# 15:  Rotary right minus
# 16 - 28:  Left rotary positions (1-12)
# 29 - 40:  Right rotary positions (1-12)


class MultiSwitchItem(IDDUItem):
    NButtonIncMap = 23
    NButtonDecMap = 22
    NButtonIncValue = 9
    NButtonDecValue = 8

    dcIgnoreList = ['dcHeadlightFlash', 'dcPitSpeedLimiterToggle', 'dcStarter', 'dcTractionControlToggle', 'dcTearOffVisor', 'dcPushToPass', 'dcDashPage', 'dcToggleWindshieldWipers', 'dcTriggerWindshieldWipers']

    def __init__(self):
        IDDUItem.__init__(self)
        MultiSwitchItem.dcConfig = importExport.loadJson(self.db.dir + '/data/configs/multi.json')
        pass


class MultiSwitchThread(MultiSwitchItem, IDDUThread):
    def __init__(self, rate):
        MultiSwitchItem.__init__(self)
        IDDUThread.__init__(self, rate)


class MultiSwitch(MultiSwitchThread):
    mapDDU = {}
    mapDDU2 = {}
    mapIR = {}
    NCurrentMapDDU = 0
    NCurrentMapDDU2 = 0
    NCurrentMapIR = 0
    NMultiState = 0
    tMultiChange = 0
    mapDDUList = []
    mapDDU2List = []
    mapIRList = []
    NRotaryOldL = 0
    NRotaryOldR = 0
    NPositionMapDDU2 = 0

    def __init__(self, rate):
        MultiSwitchThread.__init__(self, rate)
        self.timeStr = ''

    def run(self):
        self.mapDDUList = list(self.mapDDU.keys())
        self.mapDDU2List = list(self.mapDDU2.keys())
        # self.mapIRList = list(self.mapIR.keys())
        
        while self.running:
            t = time.perf_counter()
            self.tic()
            if self.db.BMultiInitRequest:
                self.initCar()
                self.db.BMultiInitRequest = False

            self.MarcsJoystick.update()

            if self.MarcsJoystick.Event():
                # P2P
                if self.MarcsJoystick.isPressed(1):
                    if self.db.config['NFuelTargetMethod'] and self.db.BInLiftZone:
                        # Cancel Lift
                        self.db.AM.CANCELLIFT.raiseAlert()
                    else:
                        # P2P
                        pass

                # ACK + MARK
                if self.MarcsJoystick.isPressed(2) and self.MarcsJoystick.isPressed(6):
                    self.db.AM.resetAll()

                # forward Driver Marker
                if self.MarcsJoystick.ButtonPressedEvent(6):
                    self.vjoy.set_button(64, 1)
                    if self.db.OutLap and self.db.LapDistPct < 0.5:
                        self.db.track.setPitRemerged(self.db.LapDistPct * 100)
                    elif self.db.AM.PSLARMED.BActive:
                        self.db.track.setPitDepart(self.db.LapDistPct * 100)
                        
                if self.MarcsJoystick.ButtonReleasedEvent(6):
                    self.vjoy.set_button(64, 0)

                currentAlarm = self.db.AM.currentAlarm()
                if currentAlarm in range(0, len(self.db.AM.alarms)):
                    # ACK
                    if self.MarcsJoystick.ButtonPressedEvent(2):
                        self.db.AM.alarms[currentAlarm].surpress()
                    # MARK
                    if self.MarcsJoystick.ButtonPressedEvent(6):
                        self.db.AM.alarms[currentAlarm].ignore()

                # PAGE
                if self.MarcsJoystick.ButtonPressedEvent(0):
                    if self.db.NDDUPage == 1:
                        self.db.NDDUPage = 2
                    else:
                        self.db.NDDUPage = 1

                # TC
                if 'dcTractionControl' in self.db.car.dcList:
                    if self.MarcsJoystick.ButtonPressedEvent(3):
                        self.db.AM.TCOFF.raiseAlert()

                # Thumbwheels
                if self.NMultiState == 1:
                    if self.MarcsJoystick.ButtonPressedEvent(13):
                        self.mapDDU[self.mapDDUList[self.db.NRotaryL]].decrease() 
                        self.tMultiChange = time.time()
                        self.db.dcChangeTime = time.time()
                        self.db.dcChangedItems = [self.mapDDUList[self.db.NRotaryL]]
                    if self.MarcsJoystick.ButtonPressedEvent(12):
                        self.mapDDU[self.mapDDUList[self.db.NRotaryL]].increase()  
                        self.tMultiChange = time.time()
                        self.db.dcChangeTime = time.time()
                        self.db.dcChangedItems = [self.mapDDUList[self.db.NRotaryL]]
                elif self.NMultiState == 3:
                    if self.MarcsJoystick.ButtonPressedEvent(13):  # L-
                        self.NPositionMapDDU2 = np.mod(self.NPositionMapDDU2 - 1, len(self.mapDDU2List))
                        self.tMultiChange = time.time()
                        self.db.dcChangeTime = time.time()
                        self.db.dcChangedItems = [self.mapDDU2List[self.NPositionMapDDU2]]
                    if self.MarcsJoystick.ButtonPressedEvent(12):  # L+
                        self.NPositionMapDDU2 = np.mod(self.NPositionMapDDU2 + 1, len(self.mapDDU2List))
                        self.tMultiChange = time.time()
                        self.db.dcChangeTime = time.time()
                        self.db.dcChangedItems = [self.mapDDU2List[self.NPositionMapDDU2]]
                    if self.MarcsJoystick.ButtonPressedEvent(15):  # R-
                        self.mapDDU2[self.mapDDU2List[self.NPositionMapDDU2]].decrease() 
                        self.tMultiChange = time.time()
                        self.db.dcChangeTime = time.time()
                        self.db.dcChangedItems = [self.mapDDU2List[self.NPositionMapDDU2]]
                    if self.MarcsJoystick.ButtonPressedEvent(14):  # R+
                        self.mapDDU2[self.mapDDU2List[self.NPositionMapDDU2]].increase()  
                        self.tMultiChange = time.time()
                        self.db.dcChangeTime = time.time()
                        self.db.dcChangedItems = [self.mapDDU2List[self.NPositionMapDDU2]]
                elif self.NMultiState == 2:
                    if self.MarcsJoystick.ButtonPressedEvent(15) and self.mapIRList[self.db.NRotaryR] in self.db.car.dcList:
                        self.mapIR[self.mapIRList[self.db.NRotaryR]].decrease() 
                        self.tMultiChange = time.time()
                        self.db.dcChangeTime = time.time()
                        self.db.dcChangedItems = [self.mapIRList[self.db.NRotaryR]]
                    if self.MarcsJoystick.ButtonPressedEvent(14) and self.mapIRList[self.db.NRotaryR] in self.db.car.dcList:
                        self.mapIR[self.mapIRList[self.db.NRotaryR]].increase()  
                        self.tMultiChange = time.time()
                        self.db.dcChangeTime = time.time()
                        self.db.dcChangedItems = [self.mapIRList[self.db.NRotaryR]]
                elif self.NMultiState == 0:
                    if any([self.MarcsJoystick.ButtonPressedEvent(12), self.MarcsJoystick.ButtonPressedEvent(13)]):
                        self.NMultiState = 1
                        self.tMultiChange = time.time()
                        self.db.dcChangeTime = time.time()
                        self.db.dcChangedItems = [self.mapDDUList[self.db.NRotaryL]]
                    elif any([self.MarcsJoystick.ButtonPressedEvent(14), self.MarcsJoystick.ButtonPressedEvent(15)]):
                        self.NMultiState = 2
                        self.tMultiChange = time.time()
                        self.db.dcChangeTime = time.time()
                        self.db.dcChangedItems = [self.mapIRList[self.db.NRotaryR]]

            # Rotatries
            BRotaryStates = self.MarcsJoystick.isPressed(range(16, 40))
            BRotaryStatesL = list(BRotaryStates[0:12])
            BRotaryStatesR = list(BRotaryStates[12:24])

            if sum(BRotaryStatesL) == 1:
                self.db.NRotaryL = BRotaryStatesL.index(1)
                if not self.db.NRotaryL == self.NRotaryOldL:
                    self.NRotaryOldL = self.db.NRotaryL
                    if self.db.NRotaryL == 0:
                        self.NMultiState = 3
                        self.db.dcChangedItems = [self.mapDDU2List[self.NPositionMapDDU2]]
                    else:
                        self.NMultiState = 1
                        self.db.dcChangedItems = [self.mapDDUList[self.db.NRotaryL]]
                    self.tMultiChange = time.time()
                    self.db.dcChangeTime = time.time()
                    

            if sum(BRotaryStatesR) == 1:
                self.db.NRotaryR = BRotaryStatesR.index(1)
                if not self.db.NRotaryR == self.NRotaryOldR:
                    if self.mapIRList[self.db.NRotaryR] in self.db.inCarControls:
                        self.NRotaryOldR = self.db.NRotaryR
                        self.NMultiState = 2
                        self.db.dcChangedItems = [self.mapIRList[self.db.NRotaryR]]
                        self.tMultiChange = time.time()
                        self.db.dcChangeTime = time.time()

            if time.time() > (self.tMultiChange + 2):
                if not self.NMultiState == 0 or not self.NMultiState == 3:
                    self.NMultiState = 0

            self.db.tExecuteMulti = (time.perf_counter() - t) * 1000
            self.toc()
            time.sleep(self.rate)

    def addMapping(self, name='name', minValue=0, maxValue=1, step=1, level=1):
        if level == 1:
            if name in self.db.car.dcList:
                self.mapIR[name] = MultiSwitchMapiRControl(name, minValue , maxValue, step)
            else:
                self.mapDDU[name] = MultiSwitchMapDDUControl(name, minValue , maxValue, step)
        elif level == 2:            
            if name in self.db.car.dcList:
                self.mapIR[name] = MultiSwitchMapiRControl(name, minValue , maxValue, step)
            else:
                self.mapDDU2[name] = MultiSwitchMapDDU2Control(name, minValue , maxValue, step)

    def initCar(self):

        IDDUItem.dcConfig = importExport.loadJson(self.db.dir + '/data/configs/multi.json')

        dcList = list(self.db.car.dcList.keys())

        self.mapIR = {}
        self.mapIRList = []

        for i in range(0, len(dcList)):

            if not dcList[i] in self.dcIgnoreList:

                if not dcList[i] in IDDUItem.dcConfig:
                    n = len(IDDUItem.dcConfig)
                    IDDUItem.dcConfig[dcList[i]] = [2*n, 2*n+1]

                try:
                    if self.db.car.dcList[dcList[i]][1]:
                        self.addMapping(dcList[i])
                except:
                    pass

        importExport.saveJson(IDDUItem.dcConfig, self.db.dir + '/data/configs/multi.json')

        self.mapDDU2List = list(self.mapDDU2.keys())
        self.mapDDUList = list(self.mapDDU.keys())
        # self.mapIRList = list(self.mapIR.keys())
        self.mapIRList = self.db.inCarControls


class MultiSwitchMapDDUControl(MultiSwitchItem):
    def __init__(self, name, minValue , maxValue, step):
        MultiSwitchItem.__init__(self)
        self.name = name
        self.type = type(self.db.config[self.name])
        if self.type is not bool:
            self.minValue = minValue
            self.maxValue = maxValue
            self.step = step

    def increase(self):
        if self.type is not bool:
            newVal = np.min([self.db.config[self.name] + self.step, self.maxValue])
            self.db.config[self.name] = newVal
        else:
            self.db.config[self.name] = not self.db.config[self.name]

    def decrease(self):
        if self.type is not bool:
            newVal = np.max([self.db.config[self.name] - self.step, self.minValue])
            self.db.config[self.name] = newVal
        else:
            self.db.config[self.name] = not self.db.config[self.name]
            
class MultiSwitchMapDDU2Control(MultiSwitchItem):
    def __init__(self, name, minValue , maxValue, step):
        MultiSwitchItem.__init__(self)
        self.name = name
        self.type = type(self.db.config[self.name])
        if self.type is not bool:
            self.minValue = minValue
            self.maxValue = maxValue
            self.step = step

    def increase(self):
        if self.type is not bool:
            newVal = np.min([self.db.config[self.name] + self.step, self.maxValue])
            self.db.config[self.name] = newVal
        else:
            self.db.config[self.name] = not self.db.config[self.name]

    def decrease(self):
        if self.type is not bool:
            newVal = np.max([self.db.config[self.name] - self.step, self.minValue])
            self.db.config[self.name] = newVal
        else:
            self.db.config[self.name] = not self.db.config[self.name]


class MultiSwitchMapiRControl(MultiSwitchItem):
    def __init__(self, name, minValue , maxValue, step):
        MultiSwitchItem.__init__(self)
        self.name = name
        self.type = type(self.db.__getattribute__(name))
        if self.type is not bool:
            self.minValue = minValue
            self.maxValue = maxValue
            self.step = step

    def increase(self):
        self.pressButton(IDDUItem.dcConfig[self.name][1]+1, 0.05)

    def decrease(self):
        self.pressButton(IDDUItem.dcConfig[self.name][0]+1, 0.05)
