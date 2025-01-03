import sys
import os
import time
import numpy as np
import pygame
import traceback
from libs.auxiliaries import convertString
from libs.IDDU import IDDUItem
from libs.MyLogger import ExceptionHandler


class RenderMain(IDDUItem):
    __slots__ = 'joystick'
    BDisplayCreated = False
    screen = None

    ArrowLeft = [[20, 240], [100, 20], [100, 460]]
    ArrowRight = [[780, 240], [700, 20], [700, 460]]
    ArrowLeft2 = [[120, 240], [200, 20], [200, 460]]
    ArrowRight2 = [[680, 240], [600, 20], [600, 460]]

    ABSActivityLF = [[0, 0], [400, 0], [400, 20], [20, 20], [20, 240], [0, 240]]
    ABSActivityRF = [[800, 0], [400, 0], [400, 20], [780, 20], [780, 240], [800, 240]]
    ABSActivityLR = [[0, 480], [0, 240], [20, 240], [20, 460], [400, 460], [400, 480]]
    ABSActivityRR = [[400, 480], [800, 480], [800, 240], [780, 240], [780, 460], [400, 460]]

    ABSIndicationPoly = [ABSActivityLF, ABSActivityRF, ABSActivityLR, ABSActivityRR]

    RearPoly = [[0, 480], [0, 240], [20, 240], [20, 460], [780, 460], [780, 240], [800, 240], [800, 480]]

    ABSColourCode = [IDDUItem.black, IDDUItem.green, IDDUItem.yellow, IDDUItem.red, IDDUItem.blue]
    WheelSpinColourCode = [IDDUItem.black, IDDUItem.green, IDDUItem.yellow, IDDUItem.red, IDDUItem.blue]
    RearLockingColourCode = [IDDUItem.black, IDDUItem.green, IDDUItem.yellow, IDDUItem.red, IDDUItem.blue]

    fontTiny = pygame.font.Font("files/KhmerUI.ttf", 12)  # Khmer UI Calibri
    fontTiny2 = pygame.font.Font("files/KhmerUI.ttf", 18)
    fontSmall = pygame.font.Font("files/KhmerUI.ttf", 20)
    fontMedium = pygame.font.Font("files/KhmerUI.ttf", 40)
    fontLarge = pygame.font.Font("files/KhmerUI.ttf", 60)
    fontChangeLabel2 = pygame.font.Font("files/KhmerUI.ttf", 100)
    fontGear = pygame.font.Font("files/KhmerUI.ttf", 163)
    fontChangeLabel = pygame.font.Font("files/KhmerUI.ttf", 225)
    fontReallyLarge = pygame.font.Font("files/KhmerUI.ttf", 300)
    fontHuge = pygame.font.Font("files/KhmerUI.ttf", 480)
    SCLabel = fontHuge.render('SC', True, IDDUItem.black)

    # display
    resolution = (800, 480)
    if os.environ['COMPUTERNAME'] == 'MARC-SURFACE':
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (-1920, 0)
    else:
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0, 1080)

    fullscreen = True
    pygame.display.set_caption('iDDU')
    pygame.display.init()
    clocker = pygame.time.Clock()

    # background
    checkered = pygame.image.load("files/checkered.gif")
    dsq = pygame.image.load("files/dsq.gif")
    debry = pygame.image.load("files/debry.gif")
    pitClosed = pygame.image.load("files/pitClosed.gif")
    warning = pygame.image.load("files/warning.gif")
    arrow = pygame.image.load("files/arrow.gif")
    car = pygame.image.load("files/car.png")
    gas_white = pygame.image.load("files/gas_white.gif")
    gas_green = pygame.image.load("files/gas_green.gif")
    gas_orange = pygame.image.load("files/gas_orange.gif")
    sun = pygame.image.load("files/sun.png")
    rain1 = pygame.image.load("files/rain1.png")
    rain2 = pygame.image.load("files/rain2.png")
    rain3 = pygame.image.load("files/rain2.png")
    rain4 = pygame.image.load("files/rain4.png")
    rain5 = pygame.image.load("files/rain5.png")
    rain6 = pygame.image.load("files/rain6.png")
    yellow1 = pygame.image.load("files/yellow1.gif")
    yellow2 = pygame.image.load("files/yellow2.gif")
    blue1 = pygame.image.load("files/blue1.gif")
    blue2 = pygame.image.load("files/blue2.gif")

    BError = False

    tWarningLabel = 0
    NCalls = 0
    tMin = 1000
    tMax = 0
    tAvg = 0
    tBlue = 0

    def __init__(self):
        IDDUItem.__init__(self)

        # display
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (self.db.config['rDDU'][0], self.db.config['rDDU'][1])


class RenderScreen(RenderMain):
    def __init__(self):

        RenderMain.__init__(self)

        # initialize joystick
        # if os.environ['COMPUTERNAME'] == 'MARC-SURFACE':
        #     # self.initJoystick('vJoy Device')
        #     self.initJoystick('Controller (Xbox 360 Wireless Receiver for Windows)')
        # else:
        #     self.initJoystick('Arduino Leonardo')

        # frames
        self.frames = list()

        self.frames.append(Frame('Timing', 10, 10, 287, 267, False))
        self.frames.append(Frame('Gear', 307, 39, 114, 155, True))
        self.frames.append(Frame('Session Info', 431, 10, 359, 267, False))
        self.frames.append(Frame('Speed', 307, 204, 114, 73, True))
        self.frames.append(Frame('Control', 10, 287, 287, 183, False))
        self.frames.append(Frame('Fuel', 307, 287, 483, 183, False))

        # List of lables to display
        # textColourTag: 1 = FuelAdd, 2 = DRS, 3 = P2P, 4 = Joker, 5 = FuelDelta, 6 = Last Consumption Delta
        # alarmTag: 1 = TC1, 2 = Fuel Level, 3 = Fuel laps, 4 = P2P, 5 = DRS, 6 = Joker, 7 = Shift, 8 = ABS, 9 = TC2

        self.frames[0].addLabel('BestLapStr', LabeledValue2('Best', 21, 26, 265, '12:34.567', self.fontSmall, self.fontLarge, 0, 0), 0)
        self.frames[0].addLabel('LastLapStr', LabeledValue2('Last', 21, 110, 265, '00:00.000', self.fontSmall, self.fontLarge, 0, 0), 1)
        self.frames[0].addLabel('DeltaBestStr', LabeledValue2('DBest', 21, 194, 265, '+00:00.000', self.fontSmall, self.fontLarge, 0, 0), 2)

        self.frames[1].addLabel('ClockStr', SimpleValue(318, -10, 92, '-', self.fontSmall, 0, 0, 1), 14)
        self.frames[1].addLabel('GearStr', SimpleValue(318, 12, 92, '-', self.fontGear, 0, 10, 1), 22) # here color

        self.frames[2].addLabel('SpeedStr', SimpleValue(318, 194, 92, '-', self.fontLarge, 0, 0, 0), 23)

        self.frames[3].addLabel('RemainingStr', LabeledValue2('Remaining', 442, 26, 220, '-', self.fontSmall, self.fontLarge, 0, 0), 15)
        self.frames[3].addLabel('ElapsedStr', LabeledValue2('Elapsed', 442, 26, 220, '-', self.fontSmall, self.fontLarge, 0, 0), 16)
        self.frames[3].addLabel('JokerStr', LabeledValue2('Joker', 689, 26, 90, '0/0', self.fontSmall, self.fontLarge, 4, 6), 17)
        self.frames[3].addLabel('LapStr', LabeledValue2('Lap', 442, 110, 160, '-', self.fontSmall, self.fontLarge, 0, 0), 13)
        self.frames[3].addLabel('ToGoStr', LabeledValue2('To Go', 662, 110, 117, '100', self.fontSmall, self.fontLarge, 0, 0), 20)
        self.frames[3].addLabel('PosStr', LabeledValue2('Pos', 442, 194, 160, '0.0', self.fontSmall, self.fontLarge, 0, 0), 24)
        self.frames[3].addLabel('EstStr', LabeledValue2('Est', 654, 194, 125, '0.0', self.fontSmall, self.fontLarge, 0, 0), 21)

        self.frames[4].addLabel('dcBrakeBiasStr', LabeledValue2('BBias', 21, 303, 125, '-', self.fontSmall, self.fontLarge, 0, 0), 9)
        self.frames[4].addLabel('dcABSStr', LabeledValue2('ABS', 219, 303, 67, '-', self.fontSmall, self.fontLarge, 0, 8), 8)
        self.frames[4].addLabel('dcFARBStr', LabeledValue2('FARB', 219, 303, 67, '-', self.fontSmall, self.fontLarge, 0, 0), 30)
        self.frames[4].addLabel('dcTractionControlStr', LabeledValue2('TC1', 21, 387, 67, '-', self.fontSmall, self.fontLarge, 0, 1), 11)
        self.frames[4].addLabel('dcWeightJackerStr', LabeledValue2('Jacker', 21, 387, 67, '-', self.fontSmall, self.fontLarge, 0, 0), 32)
        self.frames[4].addLabel('dcTractionControl2Str', LabeledValue2('TC2', 120, 387, 67, '-', self.fontSmall, self.fontLarge, 0, 9), 12)
        self.frames[4].addLabel('dcRARBStr', LabeledValue2('RARB', 219, 387, 67, '-', self.fontSmall, self.fontLarge, 0, 0), 31)
        self.frames[4].addLabel('DRSStr', LabeledValue2('DRS', 219, 387, 67, '0', self.fontSmall, self.fontLarge, 2, 5), 18)
        self.frames[4].addLabel('P2PStr', LabeledValue2('P2P', 21, 387, 67, '0', self.fontSmall, self.fontLarge, 3, 4), 19)

        self.frames[5].addLabel('FuelLevelStr', LabeledValue2('Remaining', 318, 303, 125, '-', self.fontSmall, self.fontLarge, 0, 2), 3)
        self.frames[5].addLabel('FuelAddStr', LabeledValue2('Add', 481, 303, 125, '-', self.fontSmall, self.fontLarge, 1, 0), 7)
        self.frames[5].addLabel('FuelLapsStr', LabeledValue2('Laps', 644, 303, 135, '-', self.fontSmall, self.fontLarge, 0, 3), 6)
        self.frames[5].addLabel('dcFuelMixtureStr', LabeledValue2('Mix', 318, 387, 67, '-', self.fontSmall, self.fontLarge, 0, 0), 10)
        self.frames[5].addLabel('FuelLastConsStr', LabeledValue2('Last', 447, 387, 135, '-', self.fontSmall, self.fontLarge, 6, 0), 5)
        self.frames[5].addLabel('FuelAvgConsStr', LabeledValue2('Avg', 649, 387, 135, '-', self.fontSmall, self.fontLarge, 0, 0), 4)
        self.frames[5].addLabel('VFuelDeltaStr', LabeledValue2('Delta', 447, 387, 135, '-', self.fontSmall, self.fontLarge, 5, 0), 29)
        self.frames[5].addLabel('VFuelTgtStr', LabeledValue2('TGT', 649, 387, 135, '-', self.fontSmall, self.fontLarge, 0, 0), 28)

        self.frames2 = list()

        self.frames2.append(Frame('Gear', 10, 370, 114, 82, True))
        self.frames2.append(Frame('Speed', 607, 370, 183, 82, True))
        self.frames2[0].addLabel('GearStr', SimpleValue(7, 365, 114, '-', self.fontLarge, 0, 7, 1), 26)
        self.frames2[0].addLabel('SpeedStr', SimpleValue(612, 365, 173, '-', self.fontLarge, 0, 0, 1), 27)

        self.frames3 = list()

        self.frames3.append(Frame('Distance to Pit', 54, 110, 317, 155, True))
        self.frames3.append(Frame('Gear', 54, 280, 114, 82, True))
        self.frames3.append(Frame('Speed', 188, 280, 183, 82, True))
        self.frames3[0].addLabel('sToPitStallStr', SimpleValue(141, 83, 155, '-', self.fontGear, 0, 0, 1), 25)
        self.frames3[0].addLabel('GearStr', SimpleValue(51, 275, 114, '-', self.fontLarge, 0, 7, 1), 26)
        self.frames3[0].addLabel('SpeedStr', SimpleValue(193, 275, 173, '-', self.fontLarge, 0, 0, 1), 27)

        # Start Page
        self.frames4 = list()

        self.frames4.append(Frame('Gear', 343, 19, 114, 155, True))
        self.frames4.append(Frame('Speed', 157, 104, 114, 73, True))
        self.frames4.append(Frame('Clutch', 20, 220, 760, 80, True))
        self.frames4.append(Frame('tStartReaction', 80, 340, 200, 120, True))
        self.frames4.append(Frame('tStart100', 520, 340, 200, 120, True))

        self.frames4[0].addLabel('GearStr', SimpleValue(354, 12, 92, '-', self.fontGear, 0, 7, 1), 22)
        self.frames4[0].addLabel('SpeedStr', SimpleValue(168, 94, 92, '-', self.fontLarge, 0, 0, 0), 23)
        self.frames4[0].addLabel('tStartReactionStr', SimpleValue(80, 340, 200, '-', self.fontLarge, 0, 0, 1), 27)
        self.frames4[0].addLabel('tStart100Str', SimpleValue(520, 340, 200, '-', self.fontLarge, 0, 0, 1), 27)

        self.frames4[0].addLabel('RemainingStr', LabeledValue2('Remaining', 442, 26, 220, '-', self.fontSmall, self.fontLarge, 0, 0), 15)

        # misc
        self.done = False
        self.db.NDDUPage = 1

        self.snapshot = False

    @staticmethod
    def stopRendering():
        pygame.display.quit()

    # @ExceptionHandler
    def render(self):
        try:
            t = time.perf_counter()
            self.NCalls += np.uint64(self.NCalls + 1)

            if self.db.DDUrunning and self.db.StartDDU and not self.BDisplayCreated:
                RenderMain.screen = pygame.display.set_mode(self.resolution, pygame.NOFRAME)
                self.BDisplayCreated = True

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.done = True
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                    self.db.StopDDU = True

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.db.NDDUPage == 1:
                        self.db.NDDUPage = 2
                    else:
                        self.db.NDDUPage = 1

            if self.db.startUp:
                RenderMain.screen.fill(self.db.backgroundColour)

                if self.db.Gear > 0:
                    self.db.GearStr = str(int(self.db.Gear))
                elif self.db.Gear == 0:
                    self.db.GearStr = 'N'
                elif self.db.Gear < 0:
                    self.db.GearStr = 'R'

                if self.db.FlagException:
                    if self.db.FlagExceptionVal == 1:
                        RenderMain.screen.blit(self.checkered, [0, 0])
                    elif self.db.FlagExceptionVal == 2:
                        pygame.draw.circle(RenderMain.screen, self.orange, [400, 240], 185)
                    elif self.db.FlagExceptionVal == 3:
                        RenderMain.screen.blit(self.SCLabel, (130, -35))
                    elif self.db.FlagExceptionVal == 4:
                        RenderMain.screen.blit(self.dsq, [0, 0])
                    elif self.db.FlagExceptionVal == 5:
                        RenderMain.screen.blit(self.debry, [0, 0])
                    elif self.db.FlagExceptionVal == 6:
                        RenderMain.screen.blit(self.warning, [0, 0])
                    elif self.db.FlagExceptionVal == 11:
                        RenderMain.screen.blit(self.sun, [0, 0])
                    elif self.db.FlagExceptionVal == 12:
                        RenderMain.screen.blit(self.rain1, [0, 0])
                    elif self.db.FlagExceptionVal == 13:
                        RenderMain.screen.blit(self.rain2, [0, 0])
                    elif self.db.FlagExceptionVal == 14:
                        RenderMain.screen.blit(self.rain3, [0, 0])
                    elif self.db.FlagExceptionVal == 15:
                        RenderMain.screen.blit(self.rain4, [0, 0])
                    elif self.db.FlagExceptionVal == 16:
                        RenderMain.screen.blit(self.rain5, [0, 0])
                    elif self.db.FlagExceptionVal == 17:
                        RenderMain.screen.blit(self.rain6, [0, 0])
                
                if self.db.BYellow:
                    f = 0.25 
                    if self.db.tYellow == 0:
                        self.db.tYellow = time.time()                                           
                    
                    if (time.time() - self.db.tYellow) % f < f/2:
                        RenderMain.screen.blit(self.yellow1, [0, 0]) 
                    elif (time.time() - self.db.tYellow) % f >= f/2:
                        RenderMain.screen.blit(self.yellow2, [0, 0]) 

                if self.db.IsOnTrack:
                    # Radar Incicators
                    CarLeftRight = self.db.CarLeftRight
                    if np.isin(CarLeftRight, [2, 4, 5]):
                        pygame.draw.polygon(RenderMain.screen, self.orange, self.ArrowLeft, 0)
                        if CarLeftRight == 5:
                            pygame.draw.polygon(RenderMain.screen, self.orange, self.ArrowLeft2, 0)
                    if np.isin(CarLeftRight, [3, 4, 6]):
                        pygame.draw.polygon(RenderMain.screen, self.orange, self.ArrowRight, 0)
                        if CarLeftRight == 6:
                            pygame.draw.polygon(RenderMain.screen, self.orange, self.ArrowRight2, 0)

                    # my blue flag
                    if self.db.NLappingCars:
                        if any(np.array([i['sDiff'] for i in self.db.NLappingCars]) > -40):                        
                            f = 0.25 
                            if self.tBlue == 0:
                                self.tBlue = time.time()                                           
                            
                            if (time.time() - self.tBlue) % f < f/2:
                                RenderMain.screen.blit(self.blue1, [0, 0]) 
                            elif (time.time() - self.tBlue) % f >= f/2:
                                RenderMain.screen.blit(self.blue2, [0, 0]) 
                    
                    if self.db.WeekendInfo['NumCarClasses'] > 1 and self.db.PlayerTrackSurface == 3 and not self.db.FlagException:
                        if len(self.db.NLappingCars) == 1:
                            text = str(self.db.NLappingCars[0]['NCars']) + " x " + self.db.NLappingCars[0]['Class']
                            LabelSize = self.fontGear.size(text)
                            Label = self.fontGear.render(text, True, self.db.NLappingCars[0]['Color'])
                            RenderMain.screen.blit(Label, (400 - LabelSize[0] / 2, 240 - LabelSize[1] / 2))
                        elif len(self.db.NLappingCars) >= 1:
                            text0 = str(self.db.NLappingCars[0]['NCars']) + " x " + self.db.NLappingCars[0]['Class']
                            text1 = str(self.db.NLappingCars[1]['NCars']) + " x " + self.db.NLappingCars[1]['Class']
                            LabelSize0 = self.fontGear.size(text0)
                            Label0 = self.fontGear.render(text0, True, self.db.NLappingCars[0]['Color'])
                            LabelSize1 = self.fontGear.size(text1)
                            Label1 = self.fontGear.render(text1, True, self.db.NLappingCars[1]['Color'])

                            gap = (480 - LabelSize0[1] - LabelSize1[1]) / 3

                            RenderMain.screen.blit(Label0, (400 - LabelSize0[0] / 2, gap))
                            RenderMain.screen.blit(Label1, (400 - LabelSize1[0] / 2, 2 * gap + LabelSize0[1]))
                    

                if self.db.NDDUPage == 1:
                    self.page1()
                elif self.db.NDDUPage == 2:
                    self.page2()
                elif self.db.NDDUPage == 3:
                    self.page3()
                elif self.db.NDDUPage == 4:
                    self.page4()
            else:
                self.page0()    

            if self.db.BLoadRaceSetupWarning:
                # self.warningLabel('LOAD RACE SETUP!', self.yellow, self.black, 3)
                self.db.AM.LOADRACESETUP.raiseAlert()

            if self.db.startUp and self.db.IsOnTrack:

                EngineWarnings = self.db.EngineWarnings
                # warning and alarm messages
                if EngineWarnings & 0x10 and 'dcPitSpeedLimiterToggle' in self.db.car.dcList:
                    self.db.AM.PITLIMITERACTIVE.raiseAlert()
                if EngineWarnings & 0x1:
                    # self.warningLabel('WATER TEMP HIGH', self.red, self.white, 4)
                    self.db.AM.WATERTEMP.raiseAlert()
                if EngineWarnings & 0x2:
                    self.db.AM.FUELPRESSURE.raiseAlert()
                if EngineWarnings & 0x4:
                    self.db.AM.OILPRESSURE.raiseAlert()
                if EngineWarnings & 0x8:
                    self.db.AM.ENGINESTALLED.raiseAlert()

                if self.db.SessionTime < self.db.tdcHeadlightFlash + 1:
                    if self.db.BdcHeadlightFlash:
                        self.db.AM.FLASH.raiseAlert()

                # for testing purposes....
                SessionFlags = self.db.SessionFlags
                if SessionFlags & 0x80:
                    self.db.AM.CROSSED.raiseAlert()
                # if SessionFlags & 0x100: # normal yellow
                #     self.warningLabel('YELLOW WAVING', self.white, self.black)
                # if SessionFlags & 0x400:
                #     self.warningLabel('GREEN HELD', self.white, self.black)
                if SessionFlags & 0x2000:
                    self.db.AM.RANDOMWAVING.raiseAlert()
                # if SessionFlags & 0x8000:
                #     self.warningLabel('CAUTION WAVING', self.white, self.black)
                # if SessionFlags & 0x10000:
                #     self.warningLabel('BLACK', self.white, self.black)
                if SessionFlags & 0x20000:
                    self.db.AM.DISQUALIFIED.raiseAlert()
                # if SessionFlags & 0x80000:
                #     self.warningLabel('FURLED', self.white, self.black)
                # if SessionFlags & 0x100000:
                #     self.warningLabel('REPAIR', self.white, self.black)

                if self.db.OnPitRoad and self.db.Speed > 5 and not self.db.EngineWarnings & 0x10 and 'dcPitSpeedLimiterToggle' in self.db.car.dcList:
                    self.db.AM.PITLIMITEROFF.raiseAlert()

                if self.db.BThumbWheelActive:
                    if self.db.BThumbWheelErrorL:
                        self.db.AM.THUMBWHEELERRORL.raiseAlert()
                    if self.db.BThumbWheelErrorR:
                        self.db.AM.THUMBWHEELERRORR.raiseAlert()
                else:
                    self.db.AM.THUMBWHEELOFF.raiseAlert()

                # driver control change
                if time.time() < self.db.dcChangeTime + 1:
                    if self.db.dcChangedItems[0] in self.db.car.dcList: #  self.db.car.dcList: ## self.db.inCarControls
                        if self.db.car.dcList[self.db.dcChangedItems[0]][1]:
                            if self.db.car.dcList[self.db.dcChangedItems[0]][2] == 0:
                                valueStr = convertString.roundedStr0(self.db.get(self.db.dcChangedItems[0]))
                            elif self.db.car.dcList[self.db.dcChangedItems[0]][2] == 1:
                                valueStr = convertString.roundedStr1(self.db.get(self.db.dcChangedItems[0]), 3)
                            elif self.db.car.dcList[self.db.dcChangedItems[0]][2] == 2:
                                valueStr = convertString.roundedStr2(self.db.get(self.db.dcChangedItems[0]))
                            else:
                                valueStr = str(self.db.get(self.db.dcChangedItems[0]))
                            commentList = self.db.car.dcList[self.db.dcChangedItems[0]][3]
                            NComment = int(self.db.get(self.db.dcChangedItems[0])) - 1
                            commentText = self.db.car.dcList[self.db.dcChangedItems[0]][3][min(len(commentList)-1, abs(NComment))]                        
                            self.changeLabel(self.db.car.dcList[self.db.dcChangedItems[0]][0], valueStr, self.red, commentText, frame=self.db.BEnableSectorMode)
                    else:
                        if self.db.dcChangedItems[0] == 'Push':
                            self.changeLabel('VFuelTgt', 'Push', self.blue)
                        elif self.db.dcChangedItems[0] in self.db.iDDUControls:
                            if self.db.iDDUControls[self.db.dcChangedItems[0]]:
                                if self.db.iDDUControls[self.db.dcChangedItems[0]][1]:
                                    if len(self.db.iDDUControls[self.db.dcChangedItems[0]]) == 8:
                                        valueStr = self.db.iDDUControls[self.db.dcChangedItems[0]][7][int(self.db.config[(self.db.dcChangedItems[0])])]
                                    else:
                                        if self.db.iDDUControls[self.db.dcChangedItems[0]][2] == 0:
                                            valueStr = convertString.roundedStr0(self.db.config[(self.db.dcChangedItems[0])])
                                        elif self.db.iDDUControls[self.db.dcChangedItems[0]][2] == 1:
                                            valueStr = convertString.roundedStr1(self.db.config[(self.db.dcChangedItems[0])], 3)
                                        elif self.db.iDDUControls[self.db.dcChangedItems[0]][2] == 2:
                                            valueStr = convertString.roundedStr2(self.db.config[(self.db.dcChangedItems[0])])
                                        else:
                                            valueStr = str(self.db.get(self.db.dcChangedItems[0]))
                                    self.changeLabel(self.db.iDDUControls[self.db.dcChangedItems[0]][0], valueStr, self.blue)
                        elif self.db.dcChangedItems[0] in self.db.iDDUControls2:
                            if self.db.iDDUControls2[self.db.dcChangedItems[0]]:
                                if self.db.iDDUControls2[self.db.dcChangedItems[0]][1]:
                                    if len(self.db.iDDUControls2[self.db.dcChangedItems[0]]) == 8:
                                        valueStr = self.db.iDDUControls2[self.db.dcChangedItems[0]][7][int(self.db.config[(self.db.dcChangedItems[0])])]
                                    else:
                                        if self.db.iDDUControls2[self.db.dcChangedItems[0]][2] == 0:
                                            valueStr = convertString.roundedStr0(self.db.config[(self.db.dcChangedItems[0])])
                                        elif self.db.iDDUControls2[self.db.dcChangedItems[0]][2] == 1:
                                            valueStr = convertString.roundedStr1(self.db.config[(self.db.dcChangedItems[0])], 3)
                                        elif self.db.iDDUControls2[self.db.dcChangedItems[0]][2] == 2:
                                            valueStr = convertString.roundedStr2(self.db.config[(self.db.dcChangedItems[0])])
                                        else:
                                            valueStr = str(self.db.get(self.db.dcChangedItems[0]))
                                    self.changeLabel(self.db.iDDUControls2[self.db.dcChangedItems[0]][0], valueStr, self.blue)

                        self.db.backgroundColour = self.blue

            self.db.AM.update()
            a = self.db.AM.display()
            if a[0]:
                self.warningLabel(a[0][0], a[0][1], a[0][2], a[0][3])

            pygame.display.flip()   
            self.db.tExecuteRender = (time.perf_counter() - t) * 1000
            self.tMin = np.min([self.tMin, self.db.tExecuteRender])
            self.tMax = np.max([self.tMax, self.db.tExecuteRender])
            self.tAvg = (self.tAvg * (self.NCalls - 1) + self.db.tExecuteRender) / self.NCalls

            self.clocker.tick(30)

            return self.done

        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            s = traceback.format_exception(exc_type, exc_value, exc_traceback, limit=2, chain=True)
            S = '\n'
            for i in s:
                S = S + i
            self.logger.error(S)
            self.db.tExecuteRender = (time.perf_counter() - t) * 1000
            self.tMin = np.min([self.tMin, self.db.tExecuteRender])
            self.tMax = np.max([self.tMax, self.db.tExecuteRender])
            self.tAvg = (self.tAvg * (self.NCalls - 1) + self.db.tExecuteRender) / self.NCalls
            self.clocker.tick(30)
            return self.done

    def page0(self):

        RenderMain.screen.fill(self.db.backgroundColour)
        
        Label = self.fontMedium.render('Waiting for iRacing ...', True, self.db.textColour)
        LabelSize = self.fontMedium.size('Waiting for iRacing ...')
        Label2 = self.fontMedium.render(self.db.timeStr, True, self.db.textColour)
        Label2Size = self.fontMedium.size(self.db.timeStr)
        RenderMain.screen.blit(Label, (400 - LabelSize[0]/2, 120))
        RenderMain.screen.blit(Label2, (400 - Label2Size[0]/2, 240))

    def page1(self):

        if self.db.init:
            self.frames[2].reinitFrame(self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionType'])

        # DRS
        if self.db.DRS:
            if self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionType'] == 'Race':
                self.db.DRSStr = str(int(self.db.DRSRemaining))
            else:
                self.db.DRSStr = str(int(self.db.DRSCounter))
        # P2P
        if self.db.P2P:
            if self.db.car.name == 'IR18':
                self.db.P2PStr = convertString.roundedStr1(self.db.P2P_Count, 1)
            else:
                P2PRemaining = (self.db.config['P2PActivations'] - self.db.P2PCounter)
                if self.db.config['P2PActivations'] > 100:
                    self.db.P2PStr = str(int(self.db.P2PCounter))
                else:
                    self.db.P2PStr = str(int(P2PRemaining))

        # LabelStrings
        self.db.BestLapStr = convertString.convertTimeMMSSsss(max(0, self.db.LapBestLapTime))
        self.db.LastLapStr = convertString.convertTimeMMSSsss(max(0, self.db.LapLastLapTime))
        self.db.DeltaBestStr = convertString.convertDelta(self.db.LapDeltaToSessionBestLap)

        self.db.dcTractionControlStr = convertString.roundedStr0(self.db.dcTractionControl)
        self.db.dcTractionControl2Str = convertString.roundedStr0(self.db.dcTractionControl2)
        self.db.dcBrakeBiasStr = convertString.roundedStr1(self.db.dcBrakeBias, 3)
        self.db.dcFuelMixtureStr = convertString.roundedStr0(self.db.dcFuelMixture)
        self.db.dcThrottleShapeStr = convertString.roundedStr0(self.db.dcThrottleShape)
        self.db.dcABSStr = convertString.roundedStr0(self.db.dcABS)
        self.db.dcFARBStr = convertString.roundedStr0(self.db.dcAntiRollFront)
        self.db.dcRARBStr = convertString.roundedStr0(self.db.dcAntiRollRear)
        self.db.dcWeightJackerStr = convertString.roundedStr0(self.db.dcWeightJackerRight)

        self.db.FuelLevelStr = convertString.roundedStr1(self.db.FuelLevelDisp, 3)
        self.db.FuelAvgConsStr = convertString.roundedStr2(max(0, self.db.FuelAvgConsumption))
        self.db.VFuelTgtStr = convertString.roundedStr2(self.db.config['VFuelTgt'])
        self.db.FuelLastConsStr = convertString.roundedStr2(max(0, self.db.FuelLastCons))
        self.db.VFuelDeltaStr = convertString.roundedStr2(self.db.VFuelDelta, BPlus=True)
        self.db.FuelLapsStr = convertString.roundedStr1(self.db.NLapRemaining, 3)
        self.db.FuelAddStr = convertString.roundedStr1(max(0, self.db.VFuelAdd), 3)

        self.db.SpeedStr = convertString.roundedStr0(max(0.0, self.db.Speed * 3.6))

        RaceLapsDisplay = 0
        if self.db.config['NRaceLapsSource'] == 0:
            RaceLapsDisplay = self.db.config['RaceLaps']
        elif self.db.config['NRaceLapsSource'] == 1:
            RaceLapsDisplay = self.db.config['UserRaceLaps']

        if RaceLapsDisplay >= 100:
            self.db.LapStr = str(max(0, self.db.NLapsTotal))
        else:
            self.db.LapStr = str(max(0, self.db.NLapsTotal)) + '/' + str(RaceLapsDisplay)

        self.db.ToGoStr = '0'


        if (self.db.LapLimit and not self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionType'] == 'Race') or self.db.config['BEnableRaceLapEstimation']:
            self.db.ToGoStr = convertString.roundedStr1(max(0, RaceLapsDisplay - self.db.Lap + 1 - self.db.LapDistPct), 3)
        else:
            if self.db.LapLimit:
                self.db.ToGoStr = convertString.roundedStr1(max(0, RaceLapsDisplay - self.db.Lap + 1 - self.db.LapDistPct), 3)
            else:
                if not self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionType'] == 'Race':
                    self.db.LapStr = str(max(0, self.db.NLapsTotal))


        self.db.ClockStr = self.db.timeStr

        if self.db.RX:
            self.db.JokerStr = self.db.JokerStr

        if not self.db.GreenTime and self.db.TimeLimit:
            self.db.RenderLabel[15] = True
            self.db.RenderLabel[16] = False
        if self.db.TimeLimit and self.db.LapLimit:
            self.db.ElapsedStr = convertString.convertTimeHHMMSS(max(0, self.db.SessionTime - self.db.GreenTime))
        else:
            self.db.ElapsedStr = convertString.convertTimeHHMMSS(max(0, self.db.SessionTime))
        self.db.RemainingStr = convertString.convertTimeHHMMSS(max(0, self.db.SessionTimeRemain))
        self.db.EstStr = convertString.roundedStr1(self.db.NLapDriver, 3)

        for i in range(0, len(self.frames)):
            self.frames[i].setTextColour(self.db.textColour)
            self.frames[i].drawFrame()

    def page2(self):

        # Wind arrow
        aWind = (-self.db.WindDir + self.db.track.aNorth - self.db.track.a) * 180 / np.pi - 180
        dx = abs(82.8427 * np.cos(2 * (45 / 180 * np.pi + aWind / 180 * np.pi)))
        RenderMain.screen.blit(pygame.transform.rotate(self.arrow, int(aWind)), [200 - dx, 40 - dx])

        if self.db.config['MapHighlight']:
            self.highlightSection(5, self.green)
            self.highlightSection(1, self.red)

        # SFLine
        pygame.draw.polygon(RenderMain.screen, self.db.textColour, self.db.track.SFLine, 0)
        pygame.draw.lines(RenderMain.screen, self.db.textColour, True, self.db.track.map, 5)

        for n in range(1, len(self.db.DriverInfo['Drivers'])):
            temp_CarIdx = self.db.DriverInfo['Drivers'][n]['CarIdx']
            if not temp_CarIdx == self.db.DriverCarIdx:
                self.CarOnMap(temp_CarIdx)
        self.CarOnMap(self.db.DriverCarIdx)
        self.CarOnMap(0)

        self.db.SpeedStr = convertString.roundedStr1(max(0.0, self.db.Speed * 3.6), 3)

        if self.db.OnPitRoad:
            for i in range(0, len(self.frames2)):
                self.frames2[i].setTextColour(self.db.textColour)
                self.frames2[i].drawFrame()
        
        if self.db.WeatherDeclaredWet:
            tempWetnessStr = 'Track: Wet ({}/6)     Precipitation: {}'.format(self.db.TrackWetness, convertString.roundedStr0(self.db.Precipitation*100))
        else:
            tempWetnessStr = 'Track: Dry ({}/6)     Precipitation: {}'.format(self.db.TrackWetness, convertString.roundedStr0(self.db.Precipitation*100))
        weatherStr = 'TAir: {}°C     TTrack: {}°C     {}     vWind: {} km/h'.format(convertString.roundedStr0(self.db.AirTemp),
                                                                                            convertString.roundedStr0(self.db.TrackTemp), 
                                                                                            tempWetnessStr, 
                                                                                            convertString.roundedStr0(self.db.WindVel * 3.6))
        
        Label = self.fontTiny2.render(weatherStr, True, self.db.textColour)
        RenderMain.screen.blit(Label, (5, 1))

        Label3 = self.fontTiny2.render(self.db.SOFstr, True, self.db.textColour)

        RenderMain.screen.blit(Label3, (5, 458))

    def page3(self):

        self.db.SpeedStr = convertString.roundedStr1(max(0.0, self.db.Speed * 3.6), 3)
        self.db.sToPitStallStr = convertString.roundedStr0(self.db.sToPitStall)

        for i in range(0, len(self.frames3)):
            self.frames3[i].setTextColour(self.db.textColour)
            self.frames3[i].drawFrame()

        # tyres
        if self.db.BTyreChangeCompleted[0]:
            pygame.draw.rect(RenderMain.screen, self.green, [429, 155, 35, 76], 0)
        elif self.db.BTyreChangeRequest[0]:
            pygame.draw.rect(RenderMain.screen, self.orange, [429, 155, 35, 76], 0)

        if self.db.BTyreChangeCompleted[1]:
            pygame.draw.rect(RenderMain.screen, self.green, [597, 155, 35, 76], 0)
        elif self.db.BTyreChangeRequest[1]:
            pygame.draw.rect(RenderMain.screen, self.orange, [597, 155, 35, 76], 0)

        if self.db.BTyreChangeCompleted[2]:
            pygame.draw.rect(RenderMain.screen, self.green, [429, 345, 35, 76], 0)
        elif self.db.BTyreChangeRequest[2]:
            pygame.draw.rect(RenderMain.screen, self.orange, [429, 345, 35, 76], 0)

        if self.db.BTyreChangeCompleted[3]:
            pygame.draw.rect(RenderMain.screen, self.green, [597, 345, 35, 76], 0)
        elif self.db.BTyreChangeRequest[3]:
            pygame.draw.rect(RenderMain.screen, self.orange, [597, 345, 35, 76], 0)

        RenderMain.screen.blit(self.car, [425, 120])

        # fuel
        if self.db.BFuelCompleted:
            RenderMain.screen.blit(self.gas_green, [696, 120])
        elif self.db.BFuelRequest:
            RenderMain.screen.blit(self.gas_orange, [696, 120])
        else:
            RenderMain.screen.blit(self.gas_white, [696, 120])

        if not self.db.PitstopActive:
            FuelStr = convertString.roundedStr1(self.db.PitSvFuel, 3)
            FueledPct = 0
        else:
            if self.db.PitSvFuel > 0:
                FueledPct = (self.db.FuelLevel - self.db.VFuelPitStopStart) / self.db.PitSvFuel
            else:
                FueledPct = 0

            FuelStr = convertString.roundedStr1(self.db.PitSvFuel - (self.db.FuelLevel - self.db.VFuelPitStopStart), 3)

        LabelFuel = self.fontMedium.render(FuelStr, True, self.db.textColour)
        LabelSize = self.fontMedium.size(FuelStr)
        RenderMain.screen.blit(LabelFuel, (720-LabelSize[0]/2, 181))

        pygame.draw.rect(RenderMain.screen, self.green, [693, 241 + int(216*(1-FueledPct)), 50, int(216*FueledPct)], 0)

        pygame.draw.lines(RenderMain.screen, self.white, True, [[693, 241],  [743, 241],  [743, 457],  [693, 457]], 5)

    def page4(self):
        try:
            RenderMain.screen.fill(self.db.backgroundColour)

            self.db.SpeedStr = convertString.roundedStr0(max(0.0, self.db.Speed * 3.6))
            self.db.tStartReactionStr = convertString.roundedStr2(max(0.0, self.db.tStartReaction), False)
            self.db.tStart100Str = convertString.roundedStr2(max(0.0, self.db.tStart100), False)
            self.db.RemainingStr = convertString.convertTimeHHMMSS(max(0, self.db.SessionTimeRemain))

            for i in range(0, len(self.frames4)):
                self.frames4[i].setTextColour(self.db.textColour)
                self.frames4[i].drawFrame()

            # Clutch
            pygame.draw.rect(RenderMain.screen, self.blue, [40, 240, int(720*(1-self.db.Clutch)), 40], 0)
            pygame.draw.lines(RenderMain.screen, self.white, True, [[40, 240],  [760, 240],  [760, 280],  [40, 280]], 5)
            pygame.draw.line(RenderMain.screen, self.yellow, [40+int(720*self.db.config['rBitePoint']/100), 240],  [40+int(720*self.db.config['rBitePoint']/100), 280], 5)

            # Label = self.fontMedium.render('Clutch Bite Point ...', True, self.db.textColour)
            # LabelSize = self.fontMedium.size('Clutch Bite Point ...')
            # RenderMain.screen.blit(Label, (400 - LabelSize[0]/2, 40))

        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            s = traceback.format_exception(exc_type, exc_value, exc_traceback, limit=2, chain=True)
            S = '\n'
            for i in s:
                S = S + i
            self.logger.error(S)

    def CarOnMap(self, Idx):
        CarIdxLapDistPct = self.db.CarIdxLapDistPct
        if CarIdxLapDistPct[Idx] == -1.0:
            return

        x = np.interp([float(CarIdxLapDistPct[Idx]) * 100], self.db.track.LapDistPct, self.db.track.x).tolist()[0]
        y = np.interp([float(CarIdxLapDistPct[Idx]) * 100], self.db.track.LapDistPct, self.db.track.y).tolist()[0]

        if self.db.DriverInfo['DriverCarIdx'] == Idx:  # if player's car
            if self.db.RX:
                if self.db.config['JokerLaps'][Idx] == self.db.config['JokerLapsRequired']:
                    self.drawCar(Idx, x, y, self.green, self.black)
            self.drawCar(Idx, x, y, self.red, self.white)
        else:  # other cars
            if self.db.CarIdxMap[Idx] is None:
                return
            else:
                if self.db.CarIdxClassPosition[Idx] == 1:
                    if self.db.CarIdxPosition[Idx] == 1:  # overall leader
                        labelColour = self.white
                        dotColour = self.purple
                    else:
                        labelColour = self.purple  # class leaders
                        dotColour = self.bit2RBG(self.db.DriverInfo['Drivers'][self.db.CarIdxMap[Idx]]['CarClassColor'])
                elif Idx == self.db.DriverInfo['PaceCarIdx']:  # PaceCar
                    labelColour = self.black
                    dotColour = self.orange
                    if not self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionType'] == 'Race':
                        return
                    else:
                        if self.db.SessionState > 3:
                            if not self.db.SessionFlags & 0x4000 or not self.db.SessionFlags & 0x8000:
                                return
                else:
                    labelColour = self.black
                    dotColour = self.bit2RBG(self.db.DriverInfo['Drivers'][self.db.CarIdxMap[Idx]]['CarClassColor'])

            if not self.db.CarIdxOnPitRoad[Idx]:
                if self.db.RX:
                    if self.db.config['JokerLaps'][Idx] == self.db.config['JokerLapsRequired']:
                        self.drawCar(Idx, x, y, self.green, labelColour)
                else:
                    self.drawCar(Idx, x, y, dotColour, labelColour)
            else:
                return

    def drawCar(self, Idx, x, y, dotColour, labelColour):
        if self.db.CarIdxMap[Idx] is None:
            return
        else:
            Label = self.fontTiny.render(self.db.DriverInfo['Drivers'][self.db.CarIdxMap[Idx]]['CarNumber'], True, labelColour)
            if self.db.CarIdxOnPitRoad[Idx]:
                pygame.draw.circle(RenderMain.screen, self.yellow, [int(x), int(y)], 12, 0)
            elif self.db.CarIdxPitStops[Idx] >= self.db.config['PitStopsRequired'] > 0 and self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionType'] == 'Race':
                pygame.draw.circle(RenderMain.screen, self.green, [int(x), int(y)], 12, 0)
            pygame.draw.circle(RenderMain.screen, dotColour, [int(x), int(y)], 10, 0)

            LabelSize = self.fontTiny.size(self.db.DriverInfo['Drivers'][self.db.CarIdxMap[Idx]]['CarNumber'])
            RenderMain.screen.blit(Label, (int(x) - LabelSize[0]/2, int(y) - 7))

    @staticmethod
    def bit2RBG(bitColor):
        hexColor = format(bitColor, '06x')
        return int('0x' + hexColor[0:2], 0), int('0x' + hexColor[2:4], 0), int('0x' + hexColor[4:6], 0)

    def highlightSection(self, width: int, colour: tuple):
        if self.db.WeekendInfo['TrackName'] in self.db.car.tLap:
            tLap = self.db.car.tLap[self.db.WeekendInfo['TrackName']]
            timeStamp = np.interp([float(self.db.CarIdxLapDistPct[self.db.DriverInfo['DriverCarIdx']]) * 100], self.db.track.LapDistPct, tLap).tolist()[0]
            timeStamp1 = timeStamp - self.db.config['PitStopDelta'] - width / 2
            while timeStamp1 < 0:
                timeStamp1 = timeStamp1 + tLap[-1]
            while timeStamp1 > tLap[-1]:
                timeStamp1 = timeStamp1 - tLap[-1]

            timeStamp2 = timeStamp - self.db.config['PitStopDelta'] + width / 2

            while timeStamp2 < 0:
                timeStamp2 = timeStamp2 + tLap[-1]
            while timeStamp2 > tLap[-1]:
                timeStamp2 = timeStamp2 - tLap[-1]

            timeStampStart = timeStamp1
            timeStampEnd = timeStamp2

            if timeStamp2 > timeStamp1:
                tempMap = [self.db.track.map[t] for t in range(0, len(self.db.track.map)) if ((tLap[t] < timeStampEnd) and (tLap[t] > timeStampStart))]
                if len(tempMap) < 2:
                    return

                pygame.draw.lines(RenderMain.screen, colour, False, tempMap, 20)

            else:
                indices1 = np.argwhere(np.array(tLap) <= max(timeStampEnd, tLap[1]))
                if len(indices1) == 1:
                    indices1 = np.append(indices1, indices1[0]+1)

                ind1 = []
                for i in range(0, len(indices1)):
                    ind1.append(int(indices1[i]))

                map1 = np.array(self.db.track.map)[ind1].tolist()

                indices2 = np.argwhere(np.array(tLap) >= min(timeStampStart, tLap[-1]))
                if len(indices2) == 1:
                    indices2 = np.append(indices2, indices2[0]-1)

                ind2 = []
                for i in range(0, len(indices2)):
                    ind2.append(int(indices2[i]))

                map2 = np.array(self.db.track.map)[ind2].tolist()

                pygame.draw.lines(RenderMain.screen, colour, False, map1, 20)
                pygame.draw.lines(RenderMain.screen, colour, False, map2, 20)
        else:
            return

    def warningLabel(self, text, colour, textcolour, f):
        if f:
            if (time.time() - self.tWarningLabel) < 1/f:
                pygame.draw.rect(RenderMain.screen, colour, [0, 0, 800, 100], 0)
                LabelSize = self.fontLarge.size(text)
                Label = self.fontLarge.render(text, True, textcolour)
                RenderMain.screen.blit(Label, (400 - LabelSize[0] / 2, 50 - LabelSize[1] / 2))
            elif (time.time() - self.tWarningLabel) >= 2/f:
                self.tWarningLabel = time.time()
        else:
            pygame.draw.rect(RenderMain.screen, colour, [0, 0, 800, 100], 0)
            LabelSize = self.fontLarge.size(text)
            Label = self.fontLarge.render(text, True, textcolour)
            RenderMain.screen.blit(Label, (400 - LabelSize[0] / 2, 50 - LabelSize[1] / 2))

    def changeLabel(self, text, value, color, comment=None, frame=False):
        pygame.draw.rect(RenderMain.screen, color, [0, 0, 800, 480], 0)
        if frame:
            pygame.draw.rect(RenderMain.screen, self.green, [5, 1, 795, 475], 13)
        LabelSize = self.fontLarge.size(text)
        Label = self.fontLarge.render(text, True, self.white)
        # if len(text) < 7:
        #     LabelSize = self.fontLarge.size(text)
        #     Label = self.fontLarge.render(text, True, self.white)
        # elif len(text) < 11:
        #     LabelSize = self.fontMedium.size(text)
        #     Label = self.fontMedium.render(text, True, self.white)
        # else:
        #     LabelSize = self.fontSmall.size(text)
        #     Label = self.fontSmall.render(text, True, self.white)

        RenderMain.screen.blit(Label, (400 - LabelSize[0] / 2, 50 - LabelSize[1] / 2))
        # ValueSize = self.fontReallyLarge.size(value)
        # Value = self.fontReallyLarge.render(value, True, self.white)

        if len(value) < 7:
            ValueSize = self.fontReallyLarge.size(value)
            Value = self.fontReallyLarge.render(value, True, self.white)
        elif len(value) < 11:
            ValueSize = self.fontGear.size(value)
            Value = self.fontGear.render(value, True, self.white)
        else:
            ValueSize = self.fontChangeLabel2.size(value)
            Value = self.fontChangeLabel2.render(value, True, self.white)

        RenderMain.screen.blit(Value, (400 - ValueSize[0] / 2, 270 - ValueSize[1] / 2))

        if comment:
            CommentSize = self.fontMedium.size(comment)
            Comment = self.fontMedium.render(comment, True, self.white)
            RenderMain.screen.blit(Comment, (400 - CommentSize[0] / 2, 420 - CommentSize[1] / 2)) 


    def stop(self):
        if self.NCalls > 0:
            self.logger.info('{} - Avg: {} ms | Min: {} ms | Max: {} ms'.format(type(self).__name__, np.round(self.tAvg, 3), np.round(self.tMin, 3), np.round(self.tMax, 3)))


class Frame(RenderMain):
    def __init__(self, title, x1, y1, dx, dy, center):
        RenderMain.__init__(self)
        self.x1 = x1
        self.x2 = x1 + dx - 1
        self.dx = dx
        self.y1 = y1
        self.y2 = y1 + dy - 1
        self.dy = dy
        self.title = title
        self.Title = self.fontSmall.render(self.title, True, self.db.textColour)
        self.textSize = self.fontSmall.size(self.title)
        self.textColour = self.db.textColour
        self.center = center
        self.Labels = {}

    def drawFrame(self):
        if self.center:
            pygame.draw.lines(RenderMain.screen, self.db.textColour, False, [[self.x1 + self.dx/2 - self.textSize[0]/2 - 5, self.y1], [self.x1, self.y1], [self.x1, self.y2],
                                                                             [self.x2, self.y2], [self.x2, self.y1], [self.x1 + self.dx/2 + self.textSize[0]/2 + 5, self.y1]], 1)
            RenderMain.screen.blit(self.Title, (self.x1 + self.dx/2 - self.textSize[0]/2, self.y1 - 10))
        else:
            pygame.draw.lines(RenderMain.screen, self.db.textColour, False, [[self.x1 + 25, self.y1], [self.x1, self.y1], [self.x1, self.y2], [self.x2, self.y2], [self.x2, self.y1],
                                                                             [self.x1 + 35 + self.textSize[0], self.y1]], 1)
            RenderMain.screen.blit(self.Title, (self.x1 + 30, self.y1 - 10))

        for i in range(0, len(self.Labels)):
            if self.db.RenderLabel[self.Labels[i][2]]:
                self.Labels[i][1].drawLabel(self.db.get(self.Labels[i][0]))

    def reinitFrame(self, title):
        self.title = title
        self.Title = self.fontSmall.render(self.title, True, self.db.textColour)
        self.textSize = self.fontSmall.size(self.title)

    def setTextColour(self, colour):
        self.textColour = colour
        self.Title = self.fontSmall.render(self.title, True, self.textColour)

    def addLabel(self, name, labeledValue, ID):
        self.Labels[len(self.Labels)] = [name, labeledValue, ID]


class LabeledValue(RenderMain):
    def __init__(self, title, x, y, width, initValue, labFont, valFont, colourTag):
        RenderMain.__init__(self)
        self.x = x
        self.y = y
        self.title = title
        self.width = width
        self.value = initValue
        self.valFont = valFont
        self.labFont = labFont
        self.colourTag = colourTag
        if self.colourTag == 1:
            self.LabLabel = self.labFont.render(self.title, True, self.db.textColourFuelAdd)
            self.ValLabel = self.valFont.render(self.value, True, self.db.textColourFuelAdd)
        elif self.colourTag == 2:
            self.ValLabel = self.valFont.render(self.value, True, self.db.textColourDRS)
            self.LabLabel = self.labFont.render(self.title, True, self.db.textColourDRS)
        elif self.colourTag == 3:
            self.ValLabel = self.valFont.render(self.value, True, self.db.textColourP2P)
            self.LabLabel = self.labFont.render(self.title, True, self.db.textColourP2P)
        else:
            self.LabLabel = self.labFont.render(self.title, True, self.db.textColour)
            self.ValLabel = self.valFont.render(self.value, True, self.db.textColour)
        self.LabSize = labFont.size(self.title)
        self.ValSize = self.valFont.size(self.value)

    def drawLabel(self, value):
        self.value = value
        if self.colourTag == 1:
            self.ValLabel = self.valFont.render(self.value, True, self.db.textColourFuelAdd)
            self.LabLabel = self.labFont.render(self.title, True, self.db.textColourFuelAdd)
        elif self.colourTag == 2:
            self.ValLabel = self.valFont.render(self.value, True, self.db.textColourDRS)
            self.LabLabel = self.labFont.render(self.title, True, self.db.textColourDRS)
        elif self.colourTag == 3:
            self.ValLabel = self.valFont.render(self.value, True, self.db.textColourP2P)
            self.LabLabel = self.labFont.render(self.title, True, self.db.textColourP2P)
        elif self.colourTag == 4:
            self.ValLabel = self.valFont.render(self.value, True, self.db.textColourJoker)
            self.LabLabel = self.labFont.render(self.title, True, self.db.textColourJoker)
        elif self.colourTag == 5:
            self.ValLabel = self.valFont.render(self.value, True, self.db.textColourDelta)
            self.LabLabel = self.labFont.render(self.title, True, self.db.textColourDelta)
        elif self.colourTag == 6:
            self.ValLabel = self.valFont.render(self.value, True, self.db.textColourLapCons)
            self.LabLabel = self.labFont.render(self.title, True, self.db.textColourLapCons)
        else:
            self.ValLabel = self.valFont.render(self.value, True, self.db.textColour)
            self.LabLabel = self.labFont.render(self.title, True, self.db.textColour)
        self.ValSize = self.valFont.size(self.value)

        RenderMain.screen.blit(self.LabLabel, (self.x - self.width / 2, self.y))
        RenderMain.screen.blit(self.ValLabel, (self.x + self.width / 2 - self.ValSize[0], self.y - 36))


class LabeledValue2(RenderMain):
    def __init__(self, title, x, y, width, initValue, labFont, valFont, colourTag, alarmTag):
        RenderMain.__init__(self)
        self.x = x-2
        self.y = y
        self.title = title
        self.width = width+4
        self.value = initValue
        self.valFont = valFont
        self.labFont = labFont
        self.colourTag = colourTag
        self.alarmTag = alarmTag
        if self.colourTag == 1:
            self.ValLabel = self.valFont.render(self.value, True, self.db.textColourFuelAdd)
            self.LabLabel = self.labFont.render(self.title, True, self.db.textColourFuelAdd)
        elif self.colourTag == 2:
            self.ValLabel = self.valFont.render(self.value, True, self.db.textColourDRS)
            self.LabLabel = self.labFont.render(self.title, True, self.db.textColourDRS)
        elif self.colourTag == 3:
            self.ValLabel = self.valFont.render(self.value, True, self.db.textColourP2P)
            self.LabLabel = self.labFont.render(self.title, True, self.db.textColourP2P)
        elif self.colourTag == 4:
            self.ValLabel = self.valFont.render(self.value, True, self.db.textColourJoker)
            self.LabLabel = self.labFont.render(self.title, True, self.db.textColourJoker)
        elif self.colourTag == 5:
            self.ValLabel = self.valFont.render(self.value, True, self.db.textColourDelta)
            self.LabLabel = self.labFont.render(self.title, True, self.db.textColourDelta)
        elif self.colourTag == 6:
            self.ValLabel = self.valFont.render(self.value, True, self.db.textColourLapCons)
            self.LabLabel = self.labFont.render(self.title, True, self.db.textColourLapCons)
        else:
            self.ValLabel = self.valFont.render(self.value, True, self.db.textColour)
            self.LabLabel = self.labFont.render(self.title, True, self.db.textColour)
        self.LabSize = labFont.size(self.title)
        self.ValSize = self.valFont.size(self.value)

    def drawLabel(self, value):
        self.value = value
        if self.colourTag == 1:
            self.ValLabel = self.valFont.render(self.value, True, self.db.textColourFuelAdd)
            self.LabLabel = self.labFont.render(self.title, True, self.db.textColourFuelAdd)
        elif self.colourTag == 2:
            self.ValLabel = self.valFont.render(self.value, True, self.db.textColourDRS)
            self.LabLabel = self.labFont.render(self.title, True, self.db.textColourDRS)
        elif self.colourTag == 3:
            self.ValLabel = self.valFont.render(self.value, True, self.db.textColourP2P)
            self.LabLabel = self.labFont.render(self.title, True, self.db.textColourP2P)
        elif self.colourTag == 4:
            self.ValLabel = self.valFont.render(self.value, True, self.db.textColourJoker)
            self.LabLabel = self.labFont.render(self.title, True, self.db.textColourJoker)
        elif self.colourTag == 5:
            self.ValLabel = self.valFont.render(self.value, True, self.db.textColourDelta)
            self.LabLabel = self.labFont.render(self.title, True, self.db.textColourDelta)
        elif self.colourTag == 6:
            self.ValLabel = self.valFont.render(self.value, True, self.db.textColourLapCons)
            self.LabLabel = self.labFont.render(self.title, True, self.db.textColourLapCons)
        else:
            self.ValLabel = self.valFont.render(self.value, True, self.db.textColour)
            self.LabLabel = self.labFont.render(self.title, True, self.db.textColour)
        self.ValSize = self.valFont.size(self.value)

        if not self.alarmTag == 0:
            if self.db.Alarm[self.alarmTag] == 1:
                pygame.draw.rect(RenderMain.screen, self.green, [self.x - 3, self.y, self.width + 6, 8 + self.ValSize[1]], 0)
            elif self.db.Alarm[self.alarmTag] == 2:
                pygame.draw.rect(RenderMain.screen, self.orange, [self.x - 3, self.y, self.width + 6, 8 + self.ValSize[1]], 0)
            elif self.db.Alarm[self.alarmTag] == 3:
                pygame.draw.rect(RenderMain.screen, self.red, [self.x - 3, self.y, self.width + 6, 8 + self.ValSize[1]], 0)
            elif self.db.Alarm[self.alarmTag] == 4:
                pygame.draw.rect(RenderMain.screen, self.blue, [self.x - 3, self.y, self.width + 6, 8 + self.ValSize[1]], 0)

        RenderMain.screen.blit(self.LabLabel, (self.x, self.y))
        RenderMain.screen.blit(self.ValLabel, (self.x + self.width - self.ValSize[0], self.y + 15))


class SimpleValue(RenderMain):
    def __init__(self, x, y, width, initValue, valFont, colourTag, alarmTag, center):
        RenderMain.__init__(self)
        self.x = x-2
        self.y = y
        self.width = width+4
        self.value = initValue
        self.valFont = valFont
        self.colourTag = colourTag
        self.alarmTag = alarmTag
        self.center = center
        if self.colourTag == 1:
            self.ValLabel = self.valFont.render(self.value, True, self.db.textColourFuelAdd)
        elif self.colourTag == 2:
            self.ValLabel = self.valFont.render(self.value, True, self.db.textColourDRS)
        elif self.colourTag == 3:
            self.ValLabel = self.valFont.render(self.value, True, self.db.textColourP2P)
        elif self.colourTag == 4:
            self.ValLabel = self.valFont.render(self.value, True, self.db.textColourJoker)
        else:
            self.ValLabel = self.valFont.render(self.value, True, self.db.textColour)
        self.ValSize = self.valFont.size(self.value)

    def drawLabel(self, value):
        self.value = value
        if self.colourTag == 1:
            self.ValLabel = self.valFont.render(self.value, True, self.db.textColourFuelAdd)
        elif self.colourTag == 2:
            self.ValLabel = self.valFont.render(self.value, True, self.db.textColourDRS)
        elif self.colourTag == 3:
            self.ValLabel = self.valFont.render(self.value, True, self.db.textColourP2P)
        elif self.colourTag == 4:
            self.ValLabel = self.valFont.render(self.value, True, self.db.textColourJoker)
        else:
            self.ValLabel = self.valFont.render(self.value, True, self.db.textColour)
        self.ValSize = self.valFont.size(self.value)

        if not self.alarmTag == 0:
            if self.db.Alarm[self.alarmTag] == 1:
                pygame.draw.rect(RenderMain.screen, self.green, [self.x - 3, self.y + 41, self.width + 6, 135], 0)
            elif self.db.Alarm[self.alarmTag] == 2:
                pygame.draw.rect(RenderMain.screen, self.orange, [self.x - 3, self.y + 41, self.width + 6, 135], 0)
            elif self.db.Alarm[self.alarmTag] == 3:
                pygame.draw.rect(RenderMain.screen, self.red, [self.x - 3, self.y + 41, self.width + 6, 135], 0)
            elif self.db.Alarm[self.alarmTag] == 4:
                pygame.draw.rect(RenderMain.screen, self.blue, [self.x - 3, self.y + 41, self.width + 6, 135], 0)
        if self.center:
            RenderMain.screen.blit(self.ValLabel, (self.x + self.width/2 - self.ValSize[0]/2, self.y + 15))
        else:
            RenderMain.screen.blit(self.ValLabel, (self.x + self.width - self.ValSize[0], self.y + 15))


class AlarmHandler:
    def __init__(self):
        pass

    def registerAlarm(self, name, priority, text, colour, textcolour, f):
        pass

    def raiseAlarm(self):
        pass

    def suppressAlarm(self):
        pass
