import os
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
        self.fontTiny2 = self.pygame.font.Font("files\KhmerUI.ttf", 18)
        self.fontSmall = self.pygame.font.Font("files\KhmerUI.ttf", 20)
        self.fontMedium = self.pygame.font.Font("files\KhmerUI.ttf", 40)
        self.fontLarge = self.pygame.font.Font("files\KhmerUI.ttf", 60)
        self.fontGear = self.pygame.font.Font("files\KhmerUI.ttf", 163)
        self.fontReallyLarge = self.pygame.font.Font("files\KhmerUI.ttf", 350)
        self.fontHuge = self.pygame.font.Font("files\KhmerUI.ttf", 480)

        self.SCLabel = self.fontHuge.render('SC', True, self.black)

        # display
        self.resolution = (800, 480)
        if os.environ['COMPUTERNAME'] == 'MARC-SURFACE':
            os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (-1920, 0)
        else:
            os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0, 1080)

        self.screen = self.pygame.display.set_mode(self.resolution, self.pygame.NOFRAME)
        self.fullscreen = True
        self.pygame.display.set_caption('iDDU')
        self.joystick = None
        self.clocker = self.pygame.time.Clock()

        # background
        self.checkered = self.pygame.image.load("files/checkered.gif")
        self.dsq = self.pygame.image.load("files/dsq.gif")
        self.debry = self.pygame.image.load("files/debry.gif")
        self.pitClosed = self.pygame.image.load("files/pitClosed.gif")
        self.warning = self.pygame.image.load("files/warning.gif")
        self.arrow = self.pygame.image.load("files/arrow.gif")

        self.track = {'dist': [], 'x': [], 'y': []}
        self.map = []

    def setTextColour(self, colour):
        self.textColour = colour

    def setBackgroundColour(self, colour):
        self.backgroundColour = colour

    def initJoystick(self, name):
        self.pygame.joystick.init()
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

        # frames
        self.frames = list()

        self.frames.append(Frame('Timing', 10, 10, 287, 267, self.db, False))
        self.frames.append(Frame('Gear', 307, 39, 114, 155, self.db, True))
        self.frames.append(Frame('Session Info', 431, 10, 359, 267, self.db, False))
        self.frames.append(Frame('Speed', 307, 204, 114, 73, self.db, True))
        self.frames.append(Frame('Control', 10, 287, 287, 183, self.db, False))
        self.frames.append(Frame('Fuel', 307, 287, 483, 183, self.db, False))

        # List of lables to display
        # textColourTag: 1 = FuelAdd, 2 = DRS, 3 = P2P, 4 = Joker
        # alarmTag: 1 = TC, 2 = Fuel Level, 3 = Fuel laps, 4 = P2P, 5 = DRS, 6 = Joker, 7 = Shift

        self.frames[0].addLabel('BestLapStr', LabeledValue2('Best', 21, 26, 265, '12:34.567', self.fontSmall, self.fontLarge, self.db, 0, 0), 0)
        self.frames[0].addLabel('LastLapStr', LabeledValue2('Last', 21, 110, 265, '00:00.000', self.fontSmall, self.fontLarge, self.db, 0, 0), 1)
        self.frames[0].addLabel('DeltaBestStr', LabeledValue2('DBest', 21, 194, 265, '+00:00.000', self.fontSmall, self.fontLarge, self.db, 0, 0), 2)

        self.frames[1].addLabel('ClockStr', SimpleValue(318, -10, 92, '-', self.fontSmall, self.db, 0, 0, 1), 14)
        self.frames[1].addLabel('GearStr', SimpleValue(318, 12, 92, '-', self.fontGear, self.db, 0, 7, 1), 22)

        self.frames[2].addLabel('SpeedStr', SimpleValue(318, 194, 92, '-', self.fontLarge, self.db, 0, 0, 0), 23)

        self.frames[3].addLabel('RemainingStr', LabeledValue2('Remaining', 442, 26, 220, '-', self.fontSmall, self.fontLarge, self.db, 0, 0), 15)
        self.frames[3].addLabel('ElapsedStr', LabeledValue2('Elapsed', 442, 26, 220, '-', self.fontSmall, self.fontLarge, self.db, 0, 0), 16)
        self.frames[3].addLabel('JokerStr', LabeledValue2('Joker', 689, 26, 90, '0/0', self.fontSmall, self.fontLarge, self.db, 4, 6), 17)
        self.frames[3].addLabel('LapStr', LabeledValue2('Lap', 442, 110, 160, '-', self.fontSmall, self.fontLarge, self.db, 0, 0), 13)
        self.frames[3].addLabel('ToGoStr', LabeledValue2('To Go', 662, 110, 117, '100', self.fontSmall, self.fontLarge, self.db, 0, 0), 20)
        self.frames[3].addLabel('PosStr', LabeledValue2('Pos', 442, 194, 160, '0.0', self.fontSmall, self.fontLarge, self.db, 0, 0), 24)
        self.frames[3].addLabel('EstStr', LabeledValue2('Est', 654, 194, 125, '0.0', self.fontSmall, self.fontLarge, self.db, 0, 0), 21)

        self.frames[4].addLabel('dcBrakeBiasStr', LabeledValue2('BBias', 21, 303, 125, '-', self.fontSmall, self.fontLarge, self.db, 0, 0), 9)
        self.frames[4].addLabel('dcABSStr', LabeledValue2('ABS', 219, 303, 67, '-', self.fontSmall, self.fontLarge, self.db, 0, 0), 8)
        self.frames[4].addLabel('dcTractionControlStr', LabeledValue2('TC1', 21, 387, 67, '-', self.fontSmall, self.fontLarge, self.db, 0, 1), 11)
        self.frames[4].addLabel('dcTractionControl2Str', LabeledValue2('TC2', 120, 387, 67, '-', self.fontSmall, self.fontLarge, self.db, 0, 1), 12)
        self.frames[4].addLabel('DRSStr', LabeledValue2('DRS', 219, 387, 67, '0', self.fontSmall, self.fontLarge, self.db, 2, 5), 18)
        self.frames[4].addLabel('P2PStr', LabeledValue2('P2P', 219, 387, 67, '0', self.fontSmall, self.fontLarge, self.db, 3, 4), 19)

        self.frames[5].addLabel('FuelLevelStr', LabeledValue2('Remaining', 318, 303, 125, '-', self.fontSmall, self.fontLarge, self.db, 0, 2), 3)
        self.frames[5].addLabel('FuelAddStr', LabeledValue2('Add', 481, 303, 125, '-', self.fontSmall, self.fontLarge, self.db, 1, 0), 7) # 515
        self.frames[5].addLabel('FuelLapsStr', LabeledValue2('Laps', 644, 303, 135, '-', self.fontSmall, self.fontLarge, self.db, 0, 3), 6) # 318
        self.frames[5].addLabel('dcFuelMixtureStr', LabeledValue2('Mix', 318, 387, 67, '-', self.fontSmall, self.fontLarge, self.db, 0, 0), 10) # 712
        self.frames[5].addLabel('FuelLastConsStr', LabeledValue2('Last', 447, 387, 135, '-', self.fontSmall, self.fontLarge, self.db, 0, 0), 5) # 481
        self.frames[5].addLabel('FuelAvgConsStr', LabeledValue2('Avg', 649, 387, 135, '-', self.fontSmall, self.fontLarge, self.db, 0, 0), 4) # 644

        # misc
        self.done = False
        self.ScreenNumber = 1

        self.snapshot = False

    def stop(self):
        self.pygame.display.quit()

    def render(self):
        self.backgroundColour = self.db.backgroundColour
        self.textColour = self.db.textColour
        self.textColourFuelAdd = self.db.textColourFuelAdd

        # events ###########################################################################################################
        for event in self.pygame.event.get():
            if event.type == self.pygame.QUIT:
                self.done = True
            if event.type == self.pygame.MOUSEBUTTONDOWN and event.button == 3:
                self.db.StopDDU = True

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
            self.db.BestLapStr = iDDUhelper.convertTimeMMSSsss(max(0, self.db.LapBestLapTime))
            self.db.LastLapStr = iDDUhelper.convertTimeMMSSsss(max(0, self.db.LapLastLapTime))
            self.db.DeltaBestStr = iDDUhelper.convertDelta(self.db.LapDeltaToSessionBestLap)

            self.db.dcTractionControlStr = iDDUhelper.roundedStr0(self.db.dcTractionControl)
            self.db.dcTractionControl2Str = iDDUhelper.roundedStr0(self.db.dcTractionControl2)
            self.db.dcBrakeBiasStr = iDDUhelper.roundedStr1(self.db.dcBrakeBias)
            self.db.dcFuelMixtureStr = iDDUhelper.roundedStr0(self.db.dcFuelMixture)
            self.db.dcThrottleShapeStr = iDDUhelper.roundedStr0(self.db.dcThrottleShape)
            self.db.dcABSStr = iDDUhelper.roundedStr0(self.db.dcABS)

            self.db.FuelLevelStr = iDDUhelper.roundedStr1(self.db.FuelLevel)
            self.db.FuelAvgConsStr = iDDUhelper.roundedStr2(max(0, self.db.FuelAvgConsumption))
            self.db.FuelLastConsStr = iDDUhelper.roundedStr2(max(0, self.db.FuelLastCons))
            self.db.FuelLapsStr = iDDUhelper.roundedStr1(self.db.NLapRemaining)
            self.db.FuelAddStr = iDDUhelper.roundedStr1(max(0, self.db.VFuelAdd))

            self.db.SpeedStr = iDDUhelper.roundedStr0(max(0.0, self.db.Speed*3.6))
            if self.db.Gear > 0:
                self.db.GearStr = str(int(self.db.Gear))
            elif self.db.Gear == 0:
                self.db.GearStr = 'N'
            elif self.db.Gear < 0:
                self.db.GearStr = 'R'

            if self.db.LapLimit:
                self.db.LapStr = str(max(0, self.db.Lap)) + '/' + str(self.db.RaceLaps)
                self.db.ToGoStr = iDDUhelper.roundedStr1(max(0, self.db.RaceLaps - self.db.Lap + 1 - self.db.CarIdxLapDistPct[self.db.DriverCarIdx]))

            else:
                self.db.LapStr = str(max(0, self.db.Lap))
                self.db.ToGoStr = '0'
            self.db.ClockStr = self.db.timeStr
            if self.db.RX:
                self.db.JokerStr = self.db.JokerStr
            self.db.ElapsedStr = iDDUhelper.convertTimeHHMMSS(max(0, self.db.SessionTime))
            self.db.RemainingStr = iDDUhelper.convertTimeHHMMSS(max(0, self.db.SessionTimeRemain))
            self.db.EstStr = iDDUhelper.roundedStr1(self.db.NLapDriver)

            for i in range(0, len(self.frames)):
                self.frames[i].setTextColour(self.db.textColour)
                self.frames[i].drawFrame()

        elif self.ScreenNumber == 2:
            self.screen.fill(self.backgroundColour)
            angleDeg = int(((float(self.db.WeekendInfo['TrackNorthOffset'].split(' ')[0])) - self.db.aOffsetTrack - self.db.WindDir - numpy.pi)*180/numpy.pi)
            angleRad = angleDeg/180*numpy.pi
            dx = abs(82.8427 * numpy.cos(2 * (45/180*numpy.pi + angleRad)))

            self.screen.blit(self.pygame.transform.rotate(self.arrow, angleDeg), [200-dx, 40-dx])

            if self.db.MapHighlight:
                self.highlightSection(5, self.green)
                self.highlightSection(1, self.red)

            self.pygame.draw.lines(self.screen, self.db.textColour, True, [self.db.map[-1], self.db.map[0]], 30)

            self.pygame.draw.lines(self.screen, self.db.textColour, True, self.db.map, 5)

            for n in range(1, len(self.db.DriverInfo['Drivers'])):
                temp_CarIdx = self.db.DriverInfo['Drivers'][n]['CarIdx']
                if not temp_CarIdx == self.db.DriverCarIdx:
                    self.CarOnMap(n)
            self.CarOnMap(self.db.DriverCarIdx)
            self.CarOnMap(0)

            Label = self.fontTiny2.render(self.db.weatherStr + iDDUhelper.roundedStr0(self.db.WindVel*3.6) + ' km/h', True, self.db.textColour)
            self.screen.blit(Label, (5, 1))

            Label2 = self.fontTiny2.render(self.db.SOFstr, True, self.db.textColour)

            self.screen.blit(Label2, (5, 458))


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

            if self.db.SessionTime < self.db.tdcHeadlightFlash + 0.5:
                if self.db.BdcHeadlightFlash:
                    self.warningLabel('FLASH', self.green, self.white)

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
        # try:
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

    def drawCar(self, Idx, x, y, dotColour, labelColour):
        Label = self.fontTiny.render(self.db.DriverInfo['Drivers'][Idx]['CarNumber'], True, labelColour)
        if self.db.CarIdxOnPitRoad[Idx]:
            self.pygame.draw.circle(self.screen, self.yellow, [int(x), int(y)], 12, 0)
        elif self.db.CarIdxPitStops[Idx] >= self.db.PitStopsRequired > 0 and self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionType'] == 'Race':
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

        # try:
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
    def __init__(self, title, x1, y1, dx, dy, db, center):
        RenderMain.__init__(self, db)
        self.x1 = x1
        self.x2 = x1 + dx - 1
        self.dx = dx
        self.y1 = y1
        self.y2 = y1 + dy - 1
        self.dy = dy
        self.title = title
        self.Title = self.fontSmall.render(self.title, True, self.textColour)
        self.textSize = self.fontSmall.size(self.title)
        self.center = center
        self.Labels = {}

    def drawFrame(self):
        if self.center:
            self.pygame.draw.lines(self.screen, self.textColour, False,
                                   [[self.x1 + self.dx/2 - self.textSize[0]/2 - 5, self.y1], [self.x1, self.y1], [self.x1, self.y2], [self.x2, self.y2],
                                    [self.x2, self.y1], [self.x1 + self.dx/2 + self.textSize[0]/2 + 5, self.y1]], 1)
            self.screen.blit(self.Title, (self.x1 + self.dx/2 - self.textSize[0]/2 , self.y1 - 10))
        else:
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
    def __init__(self, title, x, y, width, initValue, labFont, valFont, db, colourTag, alarmTag):
        RenderMain.__init__(self, db)
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
        else:
            self.ValLabel = self.valFont.render(self.value, True, self.db.textColour)
            self.LabLabel = self.labFont.render(self.title, True, self.db.textColour)
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

        if not self.alarmTag == 0:
            if self.db.Alarm[self.alarmTag] == 1:
                self.pygame.draw.rect(self.screen, self.green, [self.x - 3, self.y, self.width + 6, 8 + self.ValSize[1]], 0)
            elif self.db.Alarm[self.alarmTag] == 2:
                self.pygame.draw.rect(self.screen, self.orange, [self.x - 3, self.y, self.width + 6, 8 + self.ValSize[1]], 0)
            elif self.db.Alarm[self.alarmTag] == 3:
                self.pygame.draw.rect(self.screen, self.red, [self.x - 3, self.y, self.width + 6, 8 + self.ValSize[1]], 0)

        self.screen.blit(self.LabLabel, (self.x, self.y))
        self.screen.blit(self.ValLabel, (self.x + self.width - self.ValSize[0], self.y + 15))


class SimpleValue(RenderMain):
    def __init__(self, x, y, width, initValue, valFont, db, colourTag, alarmTag, center):
        RenderMain.__init__(self, db)
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
                self.pygame.draw.rect(self.screen, self.green, [self.x - 3, self.y + 41, self.width + 6, 135], 0)
            elif self.db.Alarm[self.alarmTag] == 2:
                self.pygame.draw.rect(self.screen, self.orange, [self.x - 3, self.y + 41, self.width + 6, 135], 0)
            elif self.db.Alarm[self.alarmTag] == 3:
                self.pygame.draw.rect(self.screen, self.red, [self.x - 3, self.y + 41, self.width + 6, 135], 0)
        if self.center:
            self.screen.blit(self.ValLabel, (self.x + self.width/2 - self.ValSize[0]/2, self.y + 15))
        else:
            self.screen.blit(self.ValLabel, (self.x + self.width - self.ValSize[0], self.y + 15))

