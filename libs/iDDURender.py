import os
import warnings

import numpy
import pygame

from libs import iDDUhelper


class RenderMain:
    __slots__ = 'joystick'

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

    def __init__(self, db):

        self.db = db
        self.backgroundColour = self.black
        self.textColour = self.white
        self.textColourFuelAdd = self.textColour
        self.textColourDRS = self.textColour
        self.textColourP2P = self.textColour

        self.ArrowLeft = [[20, 240], [100, 20], [100, 460]]
        self.ArrowRight = [[780, 240], [700, 20], [700, 460]]

        self.pygame = pygame
        self.pygame.init()

        self.fontTiny = self.pygame.font.Font("files\KhmerUI.ttf", 12)  # Khmer UI Calibri
        self.fontSmall = self.pygame.font.Font("files\KhmerUI.ttf", 20)
        self.fontMedium = self.pygame.font.Font("files\KhmerUI.ttf", 40)
        self.fontLarge = self.pygame.font.Font("files\KhmerUI.ttf", 60)
        self.fontReallyLarge = self.pygame.font.Font("files\KhmerUI.ttf", 350)
        self.fontHuge = self.pygame.font.Font("files\KhmerUI.ttf", 480)

        self.SCLabel = self.fontHuge.render('SC', True, self.black)

        # display
        self.resolution = (800, 480)
        # self.fullscreen = False
        if os.environ['COMPUTERNAME'] == 'MARC-SURFACE':
            os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (-1920, 0)
        else:
            os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0, 1080)

        self.screen = self.pygame.display.set_mode(self.resolution, self.pygame.NOFRAME)  # self.pygame.FULLSCREEN
        self.fullscreen = True
        self.pygame.display.set_caption('iDDU')
        # self.screen = self.pygame.display.set_mode(self.resolution)
        self.joystick = None
        self.clocker = self.pygame.time.Clock()

        # background
        self.checkered = self.pygame.image.load("files\checkered.gif")
        self.dsq = self.pygame.image.load("files\dsq.gif")
        self.debry = self.pygame.image.load("files\debry.gif")
        self.pitClosed = self.pygame.image.load("files\pitClosed.gif")
        self.warning = self.pygame.image.load("files\warning.gif")

        self.track = {'dist': [], 'x': [], 'y': []}
        self.map = []

    def setTextColour(self, colour):
        self.textColour = colour

    def setBackgroundColour(self, colour):
        self.backgroundColour = colour

    def initJoystick(self, name):
        self.pygame.joystick.init()
        # joysticks = [self.pygame.joystick.Joystick(x) for x in range(self.pygame.joystick.get_count())]
        print(self.db.timeStr + ': \t' + str(pygame.joystick.get_count()) + ' joysticks detected:')

        desiredJoystick = 9999

        for i in range(self.pygame.joystick.get_count()):
            print(self.db.timeStr + ':\tJoystick ', i, ': ', self.pygame.joystick.Joystick(i).get_name())
            if self.pygame.joystick.Joystick(i).get_name() == name:
                desiredJoystick = i

        if not desiredJoystick == 9999:
            print(self.db.timeStr + ':\tConnecting to', pygame.joystick.Joystick(desiredJoystick).get_name())
            self.joystick = pygame.joystick.Joystick(desiredJoystick)
            self.joystick.get_name()
            self.joystick.init()
            print(self.db.timeStr + ':\tSuccessfully connected to', pygame.joystick.Joystick(desiredJoystick).get_name(), '!')
        else:
            print(self.db.timeStr + ':\tFANATEC ClubSport Wheel Base not found!')


class RenderScreen(RenderMain):
    def __init__(self, db):
        RenderMain.__init__(self, db)

        # initialize joystick
        self.initJoystick('FANATEC ClubSport Wheel Base')
        # self.initJoystick('Controller (Xbox 360 Wireless Receiver for Windows)')

        # frames
        self.frames = list()
        self.frames.append(Frame('Timing', 10, 10, 385, 230, self.db))
        self.frames.append(Frame('Fuel', 405, 10, 385, 280, self.db))
        self.frames.append(Frame('Control', 405, 300, 385, 170, self.db))
        self.frames.append(Frame('Session Info', 10, 250, 385, 220, self.db))

        # List of lables to display
        self.frames[0].addLabel('BestLapStr', LabeledValue('Best', 200, 50, 350, '12:34.567', self.fontSmall, self.fontLarge, self.db, 0), 0)
        self.frames[0].addLabel('LastLapStr', LabeledValue('Last', 200, 120, 350, '00:00.000', self.fontSmall, self.fontLarge, self.db, 0), 1)
        self.frames[0].addLabel('DeltaBestStr', LabeledValue('DBest', 200, 190, 350, '+00:00.000', self.fontSmall, self.fontLarge, self.db, 0), 2)

        self.frames[1].addLabel('FuelLevelStr', LabeledValue('Fuel', 607, 60, 250, '-', self.fontSmall, self.fontLarge, self.db, 0), 3)
        self.frames[1].addLabel('FuelAvgConsStr', LabeledValue('Avg', 513, 130, 180, '-', self.fontSmall, self.fontLarge, self.db, 0), 4)
        self.frames[1].addLabel('FuelLastConsStr', LabeledValue('Last', 700, 130, 180, '-', self.fontSmall, self.fontLarge, self.db, 0), 5)
        self.frames[1].addLabel('FuelLapsStr', LabeledValue('Laps', 513, 200, 180, '-', self.fontSmall, self.fontLarge, self.db, 0), 6)
        self.frames[1].addLabel('FuelAddStr', LabeledValue('Add', 700, 200, 180, '-', self.fontSmall, self.fontLarge, self.db, 1), 7)

        self.frames[2].addLabel('dcABSStr', LabeledValue('ABS', 725, 350, 105, '-', self.fontSmall, self.fontLarge, self.db, 0), 8)
        self.frames[2].addLabel('dcBrakeBiasStr', LabeledValue('BBias', 516, 350, 180, '-', self.fontSmall, self.fontLarge, self.db, 0), 9)
        self.frames[2].addLabel('dcFuelMixtureStr', LabeledValue('Mix', 725, 425, 100, '-', self.fontSmall, self.fontLarge, self.db, 0), 10)
        self.frames[2].addLabel('dcTractionControlStr', LabeledValue('TC1', 469, 425, 100, '-', self.fontSmall, self.fontLarge, self.db, 0), 11)
        self.frames[2].addLabel('dcTractionControl2Str', LabeledValue('TC2', 607, 425, 100, '-', self.fontSmall, self.fontLarge, self.db, 0), 12)

        self.frames[3].addLabel('LapStr', LabeledValue('Lap', 100, 360, 140, '-', self.fontSmall, self.fontLarge, self.db, 0), 13)
        self.frames[3].addLabel('ClockStr', LabeledValue('Clock', 350, 450, 50, '-', self.fontTiny, self.fontSmall, self.db, 0), 14)
        self.frames[3].addLabel('RemainingStr', LabeledValue('Remaining', 200, 290, 350, '-', self.fontSmall, self.fontLarge, self.db, 0), 15)
        self.frames[3].addLabel('ElapsedStr', LabeledValue('Elapsed', 200, 290, 350, '-', self.fontSmall, self.fontLarge, self.db, 0), 16)
        self.frames[3].addLabel('JokerStr', LabeledValue('Joker', 105, 425, 160, '0/0', self.fontSmall, self.fontLarge, self.db, 4), 17)
        self.frames[3].addLabel('DRSStr', LabeledValue('DRS', 105, 425, 160, '0', self.fontSmall, self.fontLarge, self.db, 2), 18)
        self.frames[3].addLabel('P2PStr', LabeledValue('P2P', 105, 425, 160, '0', self.fontSmall, self.fontLarge, self.db, 3), 19)
        # self.frames[3].addLabel('ToGoStr', LabeledValue2('To Go', 260, 399, 40, '100', self.fontSmall, self.fontLarge, self.db, 3), 20)
        self.frames[3].addLabel('ToGoStr', LabeledValue('To Go', 295, 360, 160, '100', self.fontSmall, self.fontLarge, self.db, 3), 20)
        self.frames[3].addLabel('EstStr', LabeledValue('Est', 105, 425, 160, '0.0', self.fontSmall, self.fontLarge, self.db, 0), 21)

        # misc
        self.done = False
        self.ScreenNumber = 1

        self.snapshot = False

    def stop(self):
        # self.done = True
        # self.pygame.quit()
        self.pygame.display.quit()

    def render(self):
        self.backgroundColour = self.db.backgroundColour
        self.textColour = self.db.textColour
        self.textColourFuelAdd = self.db.textColourFuelAdd

        # events ###########################################################################################################
        for event in self.pygame.event.get():
            if event.type == self.pygame.QUIT:
                self.done = True
            # if event.type == self.pygame.KEYDOWN and event.key == self.pygame.K_ESCAPE:
            #     self.done = True
            if event.type == self.pygame.MOUSEBUTTONDOWN and event.button == 3:
                self.db.StopDDU = True
                # if self.fullscreen:
                #     self.pygame.display.set_mode(self.resolution)
                #     self.fullscreen = False
                # else:
                #     self.pygame.display.set_mode(self.resolution, self.pygame.NOFRAME)  # self.pygame.FULLSCREEN
                #     self.fullscreen = True

            # if event.type == self.pygame.MOUSEBUTTONDOWN and event.button == 1 or event.type == self.pygame.JOYBUTTONDOWN and event.button == 1:
            if event.type == self.pygame.MOUSEBUTTONDOWN and event.button == 1 or event.type == self.pygame.JOYBUTTONDOWN and event.button == 25:
                if self.ScreenNumber == 1:
                    self.ScreenNumber = 2
                else:
                    self.ScreenNumber = 1

        if self.ScreenNumber == 1:

            if self.db.init:
                self.frames[2].reinitFrame(self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionType'])

            self.screen.fill(self.db.backgroundColour)
            if self.db.FlagException:
                if self.db.FlagExceptionVal == 1:
                    self.screen.blit(self.checkered, [0, 0])
                elif self.db.FlagExceptionVal == 2:
                    pygame.draw.circle(self.screen, self.orange, [400, 240], 185)
                elif self.db.FlagExceptionVal == 3:
                    self.screen.blit(self.SCLabel, (130, -35))
                elif self.db.FlagExceptionVal == 4:
                    self.screen.blit(self.dsq, [0, 0])
                elif self.db.FlagExceptionVal == 5:
                    self.screen.blit(self.debry, [0, 0])
                elif self.db.FlagExceptionVal == 6:
                    self.screen.blit(self.warning, [0, 0])

            # Radar Incicators
            if self.db.CarLeftRight == 2 or self.db.CarLeftRight > 3:
                pygame.draw.polygon(self.screen, self.orange, self.ArrowLeft, 0)
            if self.db.CarLeftRight > 2:
                pygame.draw.polygon(self.screen, self.orange, self.ArrowRight, 0)

            # alarms
            if len(self.db.Alarm) > 0:
                if [1 for i in self.db.Alarm if i in [1]]:  # Traction Control
                    pygame.draw.rect(self.screen, self.red, [413, 388, 250, 65])
                if [1 for i in self.db.Alarm if i in [2]]:  # Fuel Level
                    pygame.draw.rect(self.screen, self.red, [413, 23, 370, 65])
                if [1 for i in self.db.Alarm if i in [3]]:  # Fuel Laps 1
                    pygame.draw.rect(self.screen, self.orange, [413, 167, 195, 65])
                if [1 for i in self.db.Alarm if i in [4]]:  # Fuel Laps 2
                    pygame.draw.rect(self.screen, self.red, [413, 167, 195, 65])
                if [1 for i in self.db.Alarm if i in [5]]:  # P2P
                    self.db.textColourP2P = self.black
                    pygame.draw.rect(self.screen, self.green, [20, 395, 170, 70])
                if [1 for i in self.db.Alarm if i in [6]]:  # DRS warning
                    pygame.draw.rect(self.screen, self.orange, [20, 395, 170, 70])
                if [1 for i in self.db.Alarm if i in [7]]:  # DRS open
                    self.db.textColourDRS = self.black
                    pygame.draw.rect(self.screen, self.green, [20, 395, 170, 70])
                if [1 for i in self.db.Alarm if i in [8]]:  # Joker warning
                    pygame.draw.rect(self.screen, self.orange, [20, 395, 170, 70])
                if [1 for i in self.db.Alarm if i in [9]]:  # Joker last warning
                    pygame.draw.rect(self.screen, self.red, [20, 395, 170, 70])

            # DRS
            if self.db.DRS:
                if self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionType'] == 'Race':
                    self.db.DRSStr = str(int(self.db.DRSRemaining))
                else:
                    self.db.DRSStr = str(int(self.db.DRSCounter))
            # P2P
            if self.db.P2P:
                P2PRemaining = (self.db.P2PActivations - self.db.P2PCounter)
                if self.db.P2PActivations > 100:
                    self.db.P2PStr = str(int(self.db.P2PCounter))
                else:
                    self.db.P2PStr = str(int(P2PRemaining))

            # LabelStrings
            self.db.BestLapStr = iDDUhelper.convertTimeMMSSsss(self.db.LapBestLapTime)
            self.db.LastLapStr = iDDUhelper.convertTimeMMSSsss(self.db.LapLastLapTime)
            self.db.DeltaBestStr = iDDUhelper.convertDelta(self.db.LapDeltaToSessionBestLap)

            self.db.dcTractionControlStr = iDDUhelper.roundedStr0(self.db.dcTractionControl)
            self.db.dcTractionControl2Str = iDDUhelper.roundedStr0(self.db.dcTractionControl2)
            self.db.dcBrakeBiasStr = iDDUhelper.roundedStr1(self.db.dcBrakeBias)
            self.db.dcFuelMixtureStr = iDDUhelper.roundedStr0(self.db.dcFuelMixture)
            self.db.dcThrottleShapeStr = iDDUhelper.roundedStr0(self.db.dcThrottleShape)
            self.db.dcABSStr = iDDUhelper.roundedStr0(self.db.dcABS)

            self.db.FuelLevelStr = iDDUhelper.roundedStr2(self.db.FuelLevel)
            self.db.FuelAvgConsStr = iDDUhelper.roundedStr2(self.db.FuelAvgConsumption)
            self.db.FuelLastConsStr = iDDUhelper.roundedStr2(self.db.FuelLastCons)
            self.db.FuelLapsStr = iDDUhelper.roundedStr1(self.db.NLapRemaining)
            self.db.FuelAddStr = iDDUhelper.roundedStr1(self.db.VFuelAdd)

            if self.db.LapLimit:
                self.db.LapStr = str(self.db.Lap) + '/' + str(self.db.RaceLaps)
                self.db.ToGoStr = str(self.db.RaceLaps - self.db.Lap + 1)
            else:
                self.db.LapStr = str(self.db.Lap)
                self.db.ToGoStr = '000'
            self.db.ClockStr = self.db.timeStr
            if self.db.RX:
                self.db.JokerStr = self.db.JokerStr
            self.db.ElapsedStr = iDDUhelper.convertTimeHHMMSS(self.db.SessionTime)
            self.db.RemainingStr = iDDUhelper.convertTimeHHMMSS(self.db.SessionTimeRemain)
            self.db.EstStr = iDDUhelper.roundedStr1(self.db.NLapDriver)

            for i in range(0, len(self.frames)):
                self.frames[i].setTextColour(self.db.textColour)
                self.frames[i].drawFrame()

        elif self.ScreenNumber == 2:
            self.screen.fill(self.backgroundColour)

            if self.db.MapHighlight:
                self.highlightSection(5, self.green)
                self.highlightSection(1, self.red)

            self.pygame.draw.lines(self.screen, self.db.textColour, True, [self.db.map[-1], self.db.map[0]], 30)

            self.pygame.draw.lines(self.screen, self.db.textColour, True, self.db.map, 5)

            for n in range(0, len(self.db.DriverInfo['Drivers'])):
                temp_CarIdx = self.db.DriverInfo['Drivers'][n]['CarIdx']
                if not temp_CarIdx == self.db.DriverCarIdx:
                    self.CarOnMap(self.db.DriverInfo['Drivers'][n]['CarIdx'])
            self.CarOnMap(self.db.DriverCarIdx)

        if self.db.IsOnTrack:
            # warning and alarm messages
            if self.db.EngineWarnings & 0x10:
                self.warningLabel('PIT LIMITER', self.blue, self.white)
            if self.db.EngineWarnings & 0x1:
                self.warningLabel('WATER TEMP HIGH', self.red, self.white)
            if self.db.EngineWarnings & 0x2:
                self.warningLabel('LOW FUEL PRESSURE', self.red, self.white)
            if self.db.EngineWarnings & 0x4:
                self.warningLabel('LOW OIL PRESSURE', self.red, self.white)
            if self.db.EngineWarnings & 0x8:
                self.warningLabel('ENGINE STALLED', self.yellow, self.black)

            # if not self.db.dcBrakeBias == self.db.dcBrakeBiasOld:
            #     self.dcBrakeBiasChangeTime = self.db.SessionTime
            #     self.db.dcBrakeBiasOld = self.db.dcBrakeBias
            #
            # if self.db.SessionTime < self.dcBrakeBiasChangeTime + 0.5 and self.db.SessionTime > self.db.RunStartTime + 1:
            #     self.warningLabel('BBIAS', self.white, self.black)

            # for testing purposes....
            if self.db.SessionFlags & 0x80:
                self.warningLabel('CROSSED', self.white, self.black)
            # if self.db.SessionFlags & 0x100: # normal yellow
            #     self.warningLabel('YELLOW WAVING', self.white, self.black)
            if self.db.SessionFlags & 0x400:
                self.warningLabel('GREEN HELD', self.white, self.black)
            if self.db.SessionFlags & 0x2000:
                self.warningLabel('RANDOM WAVING', self.white, self.black)
            # if self.db.SessionFlags & 0x8000:
            #     self.warningLabel('CAUTION WAVING', self.white, self.black)
            # if self.db.SessionFlags & 0x10000:
            #     self.warningLabel('BLACK', self.white, self.black)
            if self.db.SessionFlags & 0x20000:
                self.warningLabel('DISQUALIFIED', self.white, self.black)
            # if self.db.SessionFlags & 0x80000:
            #     self.warningLabel('FURLED', self.white, self.black)
            # if self.db.SessionFlags & 0x100000:
            #     self.warningLabel('REPAIR', self.white, self.black)

            # driver control change
            if self.db.SessionTime < self.db.dcChangeTime + 0.75:
                if self.db.dcBrakeBiasChange:
                    self.changeLabel('Brake Pressure Bias', iDDUhelper.roundedStr1(self.db.dcBrakeBias))
                if self.db.dcFuelMixtureChange:
                    self.changeLabel('Mix', iDDUhelper.roundedStr0(self.db.dcFuelMixture))
                if self.db.dcThrottleShapeChange:
                    self.changeLabel('Pedal Map', iDDUhelper.roundedStr0(self.db.dcThrottleShape))
                if self.db.dcTractionControlChange:
                    self.changeLabel('TC1', iDDUhelper.roundedStr0(self.db.dcTractionControl))
                if self.db.dcTractionControl2Change:
                    self.changeLabel('TC2', iDDUhelper.roundedStr0(self.db.dcTractionControl2))
                if self.db.dcTractionControlToggleChange:
                    self.changeLabel('TC Toggle', iDDUhelper.roundedStr0(self.db.dcTractionControlToggle))
                if self.db.dcABSChange:
                    self.changeLabel('ABS', iDDUhelper.roundedStr0(self.db.dcABS))

        self.pygame.display.flip()
        self.clocker.tick(30)

        return self.done

    def CarOnMap(self, Idx):
        try:
            x = numpy.interp([float(self.db.CarIdxLapDistPct[Idx]) * 100], self.db.dist, self.db.x).tolist()[0]
            y = numpy.interp([float(self.db.CarIdxLapDistPct[Idx]) * 100], self.db.dist, self.db.y).tolist()[0]

            if self.db.DriverInfo['DriverCarIdx'] == Idx:  # if player's car
                if self.db.RX:
                    if self.db.JokerLapsRequired > 0 and (self.db.JokerLaps[Idx] == self.db.JokerLapsRequired):
                        self.drawCar(Idx, x, y, self.green, self.black)
                self.drawCar(Idx, x, y, self.red, self.white)
            else:  # other cars
                if self.db.CarIdxClassPosition[Idx] == 1:
                    if self.db.CarIdxPosition[Idx] == 1:  # overall leader
                        labelColour = self.white
                        dotColour = self.purple
                    else:
                        labelColour = self.purple  # class leaders
                        dotColour = self.bit2RBG(self.db.DriverInfo['Drivers'][Idx]['CarClassColor'])
                # elif self.db.CarIdxClassPosition[Idx] == self.db.DriverInfo['PaceCarIdx']:  # PaceCar
                elif Idx == self.db.DriverInfo['PaceCarIdx']:  # PaceCar
                    labelColour = self.black
                    dotColour = self.orange
                else:
                    labelColour = self.black
                    dotColour = self.bit2RBG(self.db.DriverInfo['Drivers'][Idx]['CarClassColor'])

                if not self.db.CarIdxOnPitRoad[Idx]:
                    if self.db.RX:
                        if self.db.JokerLapsRequired > 0 and (self.db.JokerLaps[Idx] == self.db.JokerLapsRequired):
                            self.drawCar(Idx, x, y, self.green, labelColour)
                    else:
                        self.drawCar(Idx, x, y, dotColour, labelColour)
                else:
                    return
        # except NameError:
        #     print(self.db.timeStr + ': \tNameError')
        #     warnings.warn(self.db.timeStr + ': Error in CarOnMap!')
        # except ValueError:
        #     print(self.db.timeStr + ': \tValueError')
        #     warnings.warn(self.db.timeStr + ': Error in CarOnMap!')
        # else:
        except:
            warnings.warn(self.db.timeStr + ': Error in CarOnMap!')
            print('Error in iDDURender in CarOnMap')
            if not self.snapshot:
                self.db.snapshot()
                print('RTDB snapshot saved!')
                self.snapshot = True
            

    def drawCar(self, Idx, x, y, dotColour, labelColour):
        Label = self.fontTiny.render(self.db.DriverInfo['Drivers'][Idx]['CarNumber'], True, labelColour)
        if self.db.CarIdxOnPitRoad[Idx]:
            self.pygame.draw.circle(self.screen, self.yellow, [int(x), int(y)], 12, 0)
        elif self.db.CarIdxPitStops[Idx] >= self.db.PitStopsRequired and self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionType'] == 'Race':
            self.pygame.draw.circle(self.screen, self.green, [int(x), int(y)], 12, 0)
        self.pygame.draw.circle(self.screen, dotColour, [int(x), int(y)], 10, 0)
        self.screen.blit(Label, (int(x) - 6, int(y) - 7))

    @staticmethod
    def bit2RBG(bitColor):
        hexColor = format(bitColor, '06x')
        return int('0x' + hexColor[0:2], 0), int('0x' + hexColor[2:4], 0), int('0x' + hexColor[4:6], 0)

    def highlightSection(self, width: int, colour: tuple):
        timeStamp = numpy.interp([float(self.db.CarIdxLapDistPct[self.db.DriverInfo['DriverCarIdx']]) * 100], self.db.dist, self.db.time).tolist()[0]
        timeStamp1 = timeStamp - self.db.PitStopDelta - width / 2
        while timeStamp1 < 0:
            timeStamp1 = timeStamp1 + self.db.time[-1]
        while timeStamp1 > self.db.time[-1]:
            timeStamp1 = timeStamp1 - self.db.time[-1]

        timeStamp2 = timeStamp - self.db.PitStopDelta + width / 2

        while timeStamp2 < 0:
            timeStamp2 = timeStamp2 + self.db.time[-1]
        while timeStamp2 > self.db.time[-1]:
            timeStamp2 = timeStamp2 - self.db.time[-1]

        timeStampStart = timeStamp1
        timeStampEnd = timeStamp2

        try:
            if timeStamp2 > timeStamp1:
                tempMap = [self.db.map[t] for t in range(0, len(self.db.map)) if ((self.db.time[t] < timeStampEnd) and (self.db.time[t] > timeStampStart))]
                self.pygame.draw.lines(self.screen, colour, False, tempMap, 20)
            else:

                map1 = [self.db.map[t] for t in range(0, len(self.db.map)) if
                        (self.db.time[t] <= max(timeStampEnd, self.db.time[1]))]
                map2 = [self.db.map[t] for t in range(0, len(self.db.map)) if
                        (self.db.time[t] >= min(timeStampStart, self.db.time[-1]))]

                self.pygame.draw.lines(self.screen, colour, False, map1, 20)
                self.pygame.draw.lines(self.screen, colour, False, map2, 20)
##        except NameError:
##            print(self.db.timeStr + ': \tNameError')
##            warnings.warn(self.db.timeStr + ': Error in highlightSection!')
##        except ValueError:
##            print(self.db.timeStr + ': \tValueError')
##            warnings.warn(self.db.timeStr + ': Error in highlightSection!')
        # else:
        #     warnings.warn(self.db.timeStr + ': Error in highlightSection!')
        except:
            print('Error in iDDURender in highlightSection')
            if not self.snapshot:
                self.db.snapshot()
                print('RTDB snapshot saved!')
                self.snapshot = True

    def warningLabel(self, text, colour, textcolour):
        self.pygame.draw.rect(self.screen, colour, [0, 0, 800, 100], 0)
        LabelSize = self.fontLarge.size(text)
        Label = self.fontLarge.render(text, True, textcolour)
        self.screen.blit(Label, (400 - LabelSize[0] / 2, 50 - LabelSize[1] / 2))

    def changeLabel(self, text, value):
        self.pygame.draw.rect(self.screen, self.black, [0, 0, 800, 480], 0)
        LabelSize = self.fontLarge.size(text)
        Label = self.fontLarge.render(text, True, self.white)
        self.screen.blit(Label, (400 - LabelSize[0] / 2, 50 - LabelSize[1] / 2))
        ValueSize = self.fontReallyLarge.size(value)
        Value = self.fontReallyLarge.render(value, True, self.white)
        self.screen.blit(Value, (400 - ValueSize[0] / 2, 270 - ValueSize[1] / 2))


class Frame(RenderMain):
    def __init__(self, title, x1, y1, dx, dy, db):
        RenderMain.__init__(self, db)
        self.x1 = x1
        self.x2 = x1 + dx - 1
        self.y1 = y1
        self.y2 = y1 + dy - 1
        self.title = title
        self.Title = self.fontSmall.render(self.title, True, self.textColour)
        self.textSize = self.fontSmall.size(self.title)
        self.Labels = {}

    def drawFrame(self):
        self.pygame.draw.lines(self.screen, self.textColour, False,
                               [[self.x1 + 25, self.y1], [self.x1, self.y1], [self.x1, self.y2], [self.x2, self.y2],
                                [self.x2, self.y1], [self.x1 + 35 + self.textSize[0], self.y1]], 1)
        self.screen.blit(self.Title, (self.x1 + 30, self.y1 - 10))

        for i in range(0, len(self.Labels)):
            if self.db.RenderLabel[self.Labels[i][2]]:
                self.Labels[i][1].drawLabel(self.db.get(self.Labels[i][0]))

    def reinitFrame(self, title):
        self.title = title
        self.Title = self.fontSmall.render(self.title, True, self.textColour)
        self.textSize = self.fontSmall.size(self.title)

    def setTextColour(self, colour):
        self.textColour = colour
        self.Title = self.fontSmall.render(self.title, True, self.textColour)

    def addLabel(self, name, labeledValue, ID):
        self.Labels[len(self.Labels)] = [name, labeledValue, ID]


class LabeledValue(RenderMain):
    def __init__(self, title, x, y, width, initValue, labFont, valFont, db, colourTag):
        RenderMain.__init__(self, db)
        self.x = x
        self.y = y
        self.title = title
        self.width = width
        self.value = initValue
        self.valFont = valFont
        self.labFont = labFont
        self.colourTag = colourTag
        # self.ID = ID
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
        # if self.db.RenderLabel[self.ID]:
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
        else:
            self.ValLabel = self.valFont.render(self.value, True, self.db.textColour)
            self.LabLabel = self.labFont.render(self.title, True, self.db.textColour)
        self.ValSize = self.valFont.size(self.value)

        self.screen.blit(self.LabLabel, (self.x - self.width / 2, self.y))
        self.screen.blit(self.ValLabel, (self.x + self.width / 2 - self.ValSize[0], self.y - 36))


class LabeledValue2(RenderMain):
    def __init__(self, title, x, y, width, initValue, labFont, valFont, db, colourTag):
        RenderMain.__init__(self, db)
        self.x = x
        self.y = y
        self.title = title
        self.width = width
        self.value = initValue
        self.valFont = valFont
        self.labFont = labFont
        self.colourTag = colourTag
        # self.ID = ID
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
        # if self.db.RenderLabel[self.ID]:
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
        else:
            self.ValLabel = self.valFont.render(self.value, True, self.db.textColour)
            self.LabLabel = self.labFont.render(self.title, True, self.db.textColour)
        self.ValSize = self.valFont.size(self.value)

        self.screen.blit(self.LabLabel, (self.x - self.width / 2, self.y))
        self.screen.blit(self.ValLabel, (self.x + self.width / 2, self.y + 15))

        # def setTextColour(self, colour):
        #     self.textColour = colour
        #     self.LabLabel = self.labFont.render(self.title, True, colour)
        #     self.ValLabel = self.valFont.render(self.value, True, colour)
