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
# 12:  Rotary left minus
# 13:  Rotary left plus
# 14:  Rotary right minus
# 15:  Rotary right plus
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
    mapIR = {}
    NCurrentMapDDU = 0
    NCurrentMapIR = 0
    NMultiState = 0
    tMultiChange = 0
    mapDDUList = []
    mapIRList = []
    NRotaryOldL = 0
    NRotaryOldR = 0

    def __init__(self, rate):
        MultiSwitchThread.__init__(self, rate)
        self.timeStr = ''

    def run(self):
        self.mapDDUList = list(self.mapDDU.keys())
        # self.mapIRList = list(self.mapIR.keys())
        
        while self.running:
            t = time.perf_counter()
            self.tic()
            if self.db.BMultiInitRequest:
                self.initCar()
                self.db.BMultiInitRequest = False

                # if self.pygame.display.get_init() == 1:

                    # observe input controller

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

                # if self.MarcsJoystick.ButtonPressedEvent(14):
                #     if self.NMultiState == 0:
                #         self.NMultiState = 1
                #         if len(self.mapIRList) > 0:
                #             self.db.dcChangedItems = [self.mapIRList[self.NCurrentMapIR]]
                #         else:
                #             self.NMultiState = 2
                #     else:
                #         if self.NMultiState == 1 and len(self.mapIRList) > 0:
                #             NCurrentMapIR = self.NCurrentMapIR + 1
                #             if NCurrentMapIR > len(self.mapIRList) - 1:
                #                 NCurrentMapIR = NCurrentMapIR - len(self.mapIRList)

                #             self.NCurrentMapIR = NCurrentMapIR
                #             self.db.dcChangedItems = [self.mapIRList[self.NCurrentMapIR]]
                #         elif self.NMultiState == 2:
                #             NCurrentMapDDU = self.NCurrentMapDDU + 1
                #             if NCurrentMapDDU > len(self.mapDDUList) - 1:
                #                 NCurrentMapDDU = NCurrentMapDDU - len(self.mapDDUList)

                #             self.NCurrentMapDDU = NCurrentMapDDU

                #             self.db.dcChangedItems = [self.mapDDUList[self.NCurrentMapDDU]]

                #     self.tMultiChange = time.time()
                #     self.db.dcChangeTime = time.time()

                # elif self.MarcsJoystick.ButtonPressedEvent(15):
                #     if self.NMultiState == 0:
                #         self.NMultiState = 2
                #         self.db.dcChangedItems = [self.mapDDUList[self.NCurrentMapDDU]]
                #     else:
                #         if self.NMultiState == 1 and len(self.mapIRList) > 0:
                #             NCurrentMapIR = self.NCurrentMapIR - 1
                #             if NCurrentMapIR < 0:
                #                 NCurrentMapIR = len(self.mapIRList) + NCurrentMapIR

                #             self.NCurrentMapIR = NCurrentMapIR

                #             self.db.dcChangedItems = [self.mapIRList[self.NCurrentMapIR]]

                #         elif self.NMultiState == 2:
                #             NCurrentMapDDU = self.NCurrentMapDDU - 1
                #             if NCurrentMapDDU < 0:
                #                 NCurrentMapDDU = len(self.mapDDUList) + NCurrentMapDDU

                #             self.NCurrentMapDDU = NCurrentMapDDU

                #             self.db.dcChangedItems = [self.mapDDUList[self.NCurrentMapDDU]]

                #     self.tMultiChange = time.time()
                #     self.db.dcChangeTime = time.time()

                # elif self.MarcsJoystick.ButtonPressedEvent(12):
                #     if self.NMultiState == 0 and 'dcBrakeBias' in self.db.car.dcList:
                #         self.mapIR['dcBrakeBias'].increase()
                #     elif self.NMultiState == 1:
                #         self.mapIR[self.mapIRList[self.NCurrentMapIR]].increase()
                #         self.db.dcChangedItems = [self.mapIRList[self.NCurrentMapIR]]
                #     elif self.NMultiState == 2:
                #         self.mapDDU[self.mapDDUList[self.NCurrentMapDDU]].increase()
                #         self.db.dcChangedItems = [self.mapDDUList[self.NCurrentMapDDU]]
                #     else:
                #         break

                #     self.tMultiChange = time.time()
                #     self.db.dcChangeTime = time.time()

                # elif self.MarcsJoystick.ButtonPressedEvent(13):
                #     if self.NMultiState == 0 and 'dcBrakeBias' in self.db.car.dcList:
                #         self.mapIR['dcBrakeBias'].decrease()
                #     elif self.NMultiState == 1:
                #         self.mapIR[self.mapIRList[self.NCurrentMapIR]].decrease()
                #         self.db.dcChangedItems = [self.mapIRList[self.NCurrentMapIR]]
                #     elif self.NMultiState == 2:
                #         self.mapDDU[self.mapDDUList[self.NCurrentMapDDU]].decrease()
                #         self.db.dcChangedItems = [self.mapDDUList[self.NCurrentMapDDU]]
                #     else:
                #         break

                #     self.tMultiChange = time.time()
                #     self.db.dcChangeTime = time.time()

            # Rotatries
            BRotaryStates = self.MarcsJoystick.isPressed(range(16, 40))
            BRotaryStatesL = list(BRotaryStates[0:12])
            BRotaryStatesR = list(BRotaryStates[12:24])

            if sum(BRotaryStatesL) == 1:
                self.db.NRotaryL = BRotaryStatesL.index(1)
                if not self.db.NRotaryL == self.NRotaryOldL:
                    self.NRotaryOldL = self.db.NRotaryL
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

       
                
            # if self.pygame.display.get_init() == 1:
            #
            #     # observe input controller
            #     events = self.pygame.event.get()
            #     for event in events:
            #         #print('vvvvvvvvvvvvvv')
            #         #print(event)
            #         #print('##############')
            #
            #         if event.type == self.pygame.JOYBUTTONDOWN:
            #
            #             #print(event.button)
            #             #print(self.pygame.joystick.Joystick(event.joy).get_name())
            #             if event.button == self.db.config['ButtonAssignments']['DDUPage']['Button'] and self.pygame.joystick.Joystick(event.joy).get_name() == self.db.config['ButtonAssignments']['DDUPage']['Joystick']:
            #                 if self.db.NDDUPage == 1:
            #                     self.db.NDDUPage = 2
            #                 else:
            #                     self.db.NDDUPage = 1
            #
            #
            #             if event.button == self.db.config['ButtonAssignments']['NextMulti']['Button'] and self.pygame.joystick.Joystick(event.joy).get_name() == self.db.config['ButtonAssignments']['NextMulti']['Joystick']:
            #                 if self.NMultiState == 0:
            #                     self.NMultiState = 1
            #                     if len(self.mapIRList) > 0:
            #                         self.db.dcChangedItems = [self.mapIRList[self.NCurrentMapIR]]
            #                     else:
            #                         self.NMultiState = 2
            #                 else:
            #                     if self.NMultiState == 1 and len(self.mapIRList) > 0:
            #                         NCurrentMapIR = self.NCurrentMapIR + 1
            #                         if NCurrentMapIR > len(self.mapIRList)-1:
            #                             NCurrentMapIR = NCurrentMapIR - len(self.mapIRList)
            #
            #                         self.NCurrentMapIR = NCurrentMapIR
            #                         self.db.dcChangedItems = [self.mapIRList[self.NCurrentMapIR]]
            #                     elif self.NMultiState == 2:
            #                         NCurrentMapDDU = self.NCurrentMapDDU + 1
            #                         if NCurrentMapDDU > len(self.mapDDUList)-1:
            #                             NCurrentMapDDU = NCurrentMapDDU - len(self.mapDDUList)
            #
            #                         self.NCurrentMapDDU = NCurrentMapDDU
            #
            #                         self.db.dcChangedItems = [self.mapDDUList[self.NCurrentMapDDU]]
            #
            #                 self.tMultiChange = time.time()
            #                 self.db.dcChangeTime = time.time()
            #
            #             elif event.button == self.db.config['ButtonAssignments']['PreviousMulti']['Button'] and self.pygame.joystick.Joystick(event.joy).get_name() == self.db.config['ButtonAssignments']['PreviousMulti']['Joystick']:
            #                 if self.NMultiState == 0:
            #                     self.NMultiState = 2
            #                     self.db.dcChangedItems = [self.mapDDUList[self.NCurrentMapDDU]]
            #                 else:
            #                     if self.NMultiState == 1 and len(self.mapIRList) > 0:
            #                         NCurrentMapIR = self.NCurrentMapIR - 1
            #                         if NCurrentMapIR < 0:
            #                             NCurrentMapIR = len(self.mapIRList) + NCurrentMapIR
            #
            #                         self.NCurrentMapIR = NCurrentMapIR
            #
            #                         self.db.dcChangedItems = [self.mapIRList[self.NCurrentMapIR]]
            #
            #                     elif self.NMultiState == 2:
            #                         NCurrentMapDDU = self.NCurrentMapDDU - 1
            #                         if NCurrentMapDDU < 0:
            #                             NCurrentMapDDU = len(self.mapDDUList) + NCurrentMapDDU
            #
            #                         self.NCurrentMapDDU = NCurrentMapDDU
            #
            #                         self.db.dcChangedItems = [self.mapDDUList[self.NCurrentMapDDU]]
            #
            #                 self.tMultiChange = time.time()
            #                 self.db.dcChangeTime = time.time()
            #
            #             elif event.button == self.db.config['ButtonAssignments']['MultiIncrease']['Button'] and self.pygame.joystick.Joystick(event.joy).get_name() == self.db.config['ButtonAssignments']['MultiIncrease']['Joystick']:
            #                 if self.NMultiState == 0 and 'dcBrakeBias' in self.db.car.dcList:
            #                     self.mapIR['dcBrakeBias'].increase()
            #                 elif self.NMultiState == 1:
            #                     self.mapIR[self.mapIRList[self.NCurrentMapIR]].increase()
            #                     self.db.dcChangedItems = [self.mapIRList[self.NCurrentMapIR]]
            #                 elif self.NMultiState == 2:
            #                     self.mapDDU[self.mapDDUList[self.NCurrentMapDDU]].increase()
            #                     self.db.dcChangedItems = [self.mapDDUList[self.NCurrentMapDDU]]
            #                 else:
            #                     break
            #
            #                 self.tMultiChange = time.time()
            #                 self.db.dcChangeTime = time.time()
            #
            #             elif event.button == self.db.config['ButtonAssignments']['MultiDecrease']['Button'] and self.pygame.joystick.Joystick(event.joy).get_name() == self.db.config['ButtonAssignments']['MultiDecrease']['Joystick']:
            #                 if self.NMultiState == 0 and 'dcBrakeBias' in self.db.car.dcList:
            #                     self.mapIR['dcBrakeBias'].decrease()
            #                 elif self.NMultiState == 1:
            #                     self.mapIR[self.mapIRList[self.NCurrentMapIR]].decrease()
            #                     self.db.dcChangedItems = [self.mapIRList[self.NCurrentMapIR]]
            #                 elif self.NMultiState == 2:
            #                     self.mapDDU[self.mapDDUList[self.NCurrentMapDDU]].decrease()
            #                     self.db.dcChangedItems = [self.mapDDUList[self.NCurrentMapDDU]]
            #                 else:
            #                     break
            #
            #                 self.tMultiChange = time.time()
            #                 self.db.dcChangeTime = time.time()


                if time.time() > (self.tMultiChange + 2):
                    if not self.NMultiState == 0:
                        self.NMultiState = 0

            self.db.tExecuteMulti = (time.perf_counter() - t) * 1000
            self.toc()
            time.sleep(self.rate)

    def addMapping(self, name='name', minValue=0, maxValue=1, step=1):
        if name in self.db.car.dcList:
            self.mapIR[name] = MultiSwitchMapiRControl(name, minValue , maxValue, step)
        else:
            self.mapDDU[name] = MultiSwitchMapDDUControl(name, minValue , maxValue, step)

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
