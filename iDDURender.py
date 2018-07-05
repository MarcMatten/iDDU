import iDDUhelper
import pygame
import numpy
import warnings

class RenderMain:
    def __init__(self):
        self.white = (255, 255, 255)
        self.red = (255, 0, 0)
        self.green = (0, 255, 0)
        self.blue = (0, 0, 255)
        self.yellow = (255, 255, 0)
        self.orange = (255, 133, 13)
        self.grey = (141, 141, 141)
        self.black = (0, 0, 0)

        self.backgroundColour = self.black
        self.textColour = self.grey
        self.textColourFuelAdd = self.textColour

        self.pygame = pygame
        self.pygame.init()

        self.fontTiny = self.pygame.font.Font("files\KhmerUI.ttf", 12)  # Khmer UI Calibri
        self.fontSmall = self.pygame.font.Font("files\KhmerUI.ttf", 20)
        self.fontMedium = self.pygame.font.Font("files\KhmerUI.ttf", 40)
        self.fontLarge = self.pygame.font.Font("files\KhmerUI.ttf", 60)
        self.fontHuge = self.pygame.font.Font("files\KhmerUI.ttf", 480)

        self.SCLabel = self.fontHuge.render('SC', True, self.black)

        # display
        self.resolution = (800, 480)
        self.fullscreen = False
        # os.environ['SDL_VIDEO_WINDOW_POS'] = '0, 0'
        self.pygame.display.set_caption('iDDU')
        self.screen = self.pygame.display.set_mode(self.resolution)
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


class RenderScreen(RenderMain):
    def __init__(self, db):
        RenderMain.__init__(self)

        self.db = db

        # frames
        self.frames = {}
        self.frames[0] = Frame('Timing', 10, 10, 385, 230)
        self.frames[1] = Frame('Fuel', 405, 10, 385, 280)
        self.frames[2] = Frame('Session Info', 10, 250, 385, 220)
        self.frames[3] = Frame('Control', 405, 300, 385, 170)

        self.Labels1 = {}
        self.Labels1[0] = ['BestLap', LabeledValue('Best', 200, 50, 350, '00:00.000', self.fontSmall, self.fontLarge)]
        self.Labels1[1] = ['LastLap', LabeledValue('Last', 200, 120, 350, '00:00.000', self.fontSmall, self.fontLarge)]
        self.Labels1[2] = ['DeltaBest',
                           LabeledValue('DBest', 200, 190, 350, '+00:00.000', self.fontSmall, self.fontLarge)]

        self.Labels1[3] = ['dcTractionControl', LabeledValue('TC1', 469, 425, 100, '-', self.fontSmall, self.fontLarge)]
        self.Labels1[4] = ['dcABS', LabeledValue('ABS', 725, 350, 105, '-', self.fontSmall, self.fontLarge)]
        self.Labels1[5] = ['dcBrakeBias', LabeledValue('BBias', 516, 350, 180, '-', self.fontSmall, self.fontLarge)]
        self.Labels1[6] = ['dcFuelMixture', LabeledValue('Mix', 725, 425, 100, '-', self.fontSmall, self.fontLarge)]
        self.Labels1[7] = ['dcTractionControl2',
                           LabeledValue('TC2', 607, 425, 100, '-', self.fontSmall, self.fontLarge)]

        self.Labels1[8] = ['FuelLevel', LabeledValue('Fuel', 607, 60, 250, '-', self.fontSmall, self.fontLarge)]
        self.Labels1[9] = ['FuelCons', LabeledValue('Avg', 513, 130, 180, '-', self.fontSmall, self.fontLarge)]
        self.Labels1[10] = ['FuelLastCons', LabeledValue('Last', 700, 130, 180, '-', self.fontSmall, self.fontLarge)]
        self.Labels1[11] = ['FuelLaps', LabeledValue('Laps', 513, 200, 180, '-', self.fontSmall, self.fontLarge)]
        self.Labels1[12] = ['FuelAdd', LabeledValue('Add', 700, 200, 180, '-', self.fontSmall, self.fontLarge)]

        self.LabelsSession = {}
        self.LabelsSession[0] = ['Lap', LabeledValue('Lap', 100, 360, 140, '123', self.fontSmall, self.fontLarge)]
        self.LabelsSession[1] = ['Clock', LabeledValue('Clock', 350, 450, 50, '123', self.fontTiny, self.fontSmall)]
        self.LabelsSession[2] = ['Remaining',
                                 LabeledValue('Remaining', 200, 290, 350, '123', self.fontSmall, self.fontLarge)]
        self.LabelsSession[3] = ['Elapsed',
                                 LabeledValue('Elapsed', 200, 290, 350, '123', self.fontSmall, self.fontLarge)]
        self.LabelsSession[4] = ['ToGo', LabeledValue('To Go', 300, 360, 160, '123.4', self.fontSmall, self.fontLarge)]
        self.LabelsSession[5] = ['Joker', LabeledValue('Joker', 105, 425, 160, '5/3', self.fontSmall, self.fontLarge)]

        self.Labels2 = {}
        self.Labels2[0] = LabeledValue('LapsToGo', 400, 240, 200, '0.0', self.fontSmall, self.fontLarge)

        # misc
        self.done = False
        self.ScreenNumber = 1

    def render(self):

        self.backgroundColour = self.db.backgroundColour
        self.textColour = self.db.textColour
        self.textColourFuelAdd = self.db.textColourFuelAdd

        ##### events ###########################################################################################################
        for event in self.pygame.event.get():
            if event.type == self.pygame.QUIT:
                self.done = True
##            if event.type == self.pygame.KEYDOWN and event.key == self.pygame.K_ESCAPE:
##                self.done = True
            if event.type == self.pygame.MOUSEBUTTONDOWN and event.button == 3:
                if self.fullscreen:
                    self.pygame.display.set_mode(self.resolution)
                    self.fullscreen = False
                else:
                    self.pygame.display.set_mode(self.resolution, self.pygame.NOFRAME)  # self.pygame.FULLSCREEN
                    self.fullscreen = True
            if event.type == self.pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.ScreenNumber == 1:
                    self.ScreenNumber = 2
                else:
                    self.ScreenNumber = 1

        if self.ScreenNumber == 1:

            if self.db.init:
                self.frames[2].reinitFrame(self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionType'])

            # prepare strings to display
            # Timing
            # Session Info
            RemTime = self.fontLarge.render(str(self.db.RemTimeValue), True, self.db.textColour)
            RemLap = self.fontLarge.render(self.db.RemLapValueStr, True, self.db.textColour)
            Lap = self.fontLarge.render(str(self.db.Lap), True, self.db.textColour)
            Time = self.fontLarge.render(
                iDDUhelper.convertTimeHHMMSS(
                    self.db.SessionTime - self.db.GreenTime), True,
                self.db.textColour)

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

            # define frames
            for i in range(0, len(self.frames)):
                self.frames[i].setTextColour(self.db.textColour)
                self.frames[i].drawFrame()

            BestLap = iDDUhelper.convertTimeMMSSsss(self.db.LapBestLapTime)
            LastLap = iDDUhelper.convertTimeMMSSsss(self.db.LapLastLapTime)
            DeltaBest = iDDUhelper.convertDelta(self.db.LapDeltaToSessionBestLap)

            dcTractionControl = iDDUhelper.roundedStr0(self.db.dcTractionControl)
            dcTractionControl2 = iDDUhelper.roundedStr0(self.db.dcTractionControl2)
            dcBrakeBias = iDDUhelper.roundedStr1(self.db.dcBrakeBias)
            dcFuelMixture = iDDUhelper.roundedStr0(self.db.dcFuelMixture)
            dcThrottleShape = iDDUhelper.roundedStr0(self.db.dcThrottleShape)
            dcABS = iDDUhelper.roundedStr0(self.db.dcABS)

            FuelLevel = iDDUhelper.roundedStr2(self.db.FuelLevel)
            FuelCons = self.db.FuelConsumptionStr
            FuelLastCons = iDDUhelper.roundedStr2(self.db.FuelLastCons)
            FuelLaps = self.db.FuelLapStr
            FuelAdd = self.db.FuelAddStr

            # frame input
            for i in range(0, len(self.Labels1)):
                self.Labels1[i][1].setTextColour(self.db.textColour)
            self.Labels1[12][1].setTextColour(self.db.textColourFuelAdd)

            for i in range(0, len(self.Labels1)):
                self.Labels1[i][1].drawLabel(eval(self.Labels1[i][0]))

            Lap = str(self.db.Lap)
            ToGo = str(self.db.LapsToGo)
            Clock = self.db.timeStr
            Joker = self.db.JokerStr  # str(iRData[self.LabelsSession[i][0]])
            # Joker2Go = str(iRData[self.LabelsSession[i][0]])
            Elapsed = iDDUhelper.convertTimeHHMMSS(self.db.SessionTime)
            Remaining = iDDUhelper.convertTimeHHMMSS(self.db.SessionTimeRemain)



            for i in range(0, len(self.LabelsSession)):
                if self.db.LabelSessionDisplay[i]:
                    self.LabelsSession[i][1].setTextColour(self.db.textColour)
                    self.LabelsSession[i][1].drawLabel(eval(self.LabelsSession[i][0]))

        elif self.ScreenNumber == 2:
            self.screen.fill(self.backgroundColour)

            self.highlightSection(5, self.green)
            self.highlightSection(1, self.red)

            self.pygame.draw.lines(self.screen, self.db.textColour, True, [self.db.map[-1], self.db.map[0]], 30)

            self.pygame.draw.lines(self.screen, self.db.textColour, True, self.db.map, 5)

            for n in range(0, len(self.db.DriverInfo['Drivers'])):
                self.CarOnMap(self.db.DriverInfo['Drivers'][n]['CarIdx'])

        self.pygame.display.flip()
        self.clocker.tick(30)

        return self.done

    def CarOnMap(self, Idx):
        try:
            x = numpy.interp(float(self.db.CarIdxLapDistPct[Idx]) * 100, self.db.dist, self.db.x)
            y = numpy.interp(float(self.db.CarIdxLapDistPct[Idx]) * 100, self.db.dist, self.db.y)

            if self.db.DriverInfo['DriverCarIdx'] == Idx:
                if self.db.RX and (self.db.JokerLaps[Idx] == self.db.JokerLapsRequired + 1):
                    self.pygame.draw.circle(self.screen, self.green, [int(x), int(y)], 12, 0)
                self.drawCar(Idx, x, y, self.red, self.white)

            else:
                if not self.db.CarIdxOnPitRoad[Idx]:
                    if self.db.RX and (self.db.JokerLaps[Idx] == self.db.JokerLapsRequired + 1):
                        self.drawCar(Idx, x, y, self.green, self.black)
                    else:
                        self.drawCar(Idx, x, y, self.bit2RBG(self.db.DriverInfo['Drivers'][Idx]['CarClassColor']), self.black)
                else:
                    return
        except:
            warnings.warn('Error in CarOnMap!')

    def drawCar(self, Idx, x, y, dotColour, labelColour):
        Label = self.fontTiny.render(self.db.DriverInfo['Drivers'][Idx]['CarNumber'], True, labelColour)
        self.pygame.draw.circle(self.screen, dotColour, [int(x), int(y)], 10, 0)
        self.screen.blit(Label, (int(x) - 6, int(y) - 7))

    def bit2RBG(self, bitColor):
        hexColor = format(bitColor, '06x')
        return (int('0x' + hexColor[0:2], 0), int('0x' + hexColor[2:4], 0), int('0x' + hexColor[4:6], 0))

    def highlightSection(self, width, colour):
        timeStamp = numpy.interp(float(self.db.CarIdxLapDistPct[self.db.DriverInfo['DriverCarIdx']]) * 100, self.db.dist, self.db.time)
        timeStamp1 = timeStamp - self.db.PitStopDelta - width/2
        while timeStamp1 < 0:
            timeStamp1 = timeStamp1 + self.db.time[-1]

        timeStamp2 = timeStamp - self.db.PitStopDelta + width/2
        while timeStamp2 > self.db.time[-1]:
            timeStamp2 = timeStamp2 - self.db.time[-1]

        timeStampStart = timeStamp1
        timeStampEnd = timeStamp2

        try:
            if timeStamp2 > timeStamp1:
                map = [self.db.map[t] for t in range(0, len(self.db.map)) if
                       ((self.db.time[t] < timeStampEnd) and (self.db.time[t] > timeStampStart))]
                self.pygame.draw.lines(self.screen, colour, False, map, 20)
            else:

                map1 = [self.db.map[t] for t in range(0, len(self.db.map)) if
                       (self.db.time[t] <= max(timeStampEnd, self.db.time[1]))]
                map2 = [self.db.map[t] for t in range(0, len(self.db.map)) if
                       (self.db.time[t] >= min(timeStampStart, self.db.time[-1]))]

                self.pygame.draw.lines(self.screen, colour, False, map1, 20)
                self.pygame.draw.lines(self.screen, colour, False, map2, 20)
        except:
            warnings.warn('Error in highlightSection!')

class Frame(RenderMain):
    def __init__(self, title, x1, y1, dx, dy):
        RenderMain.__init__(self)
        self.x1 = x1
        self.x2 = x1 + dx - 1
        self.y1 = y1
        self.y2 = y1 + dy - 1
        self.title = title
        self.Label = self.fontSmall.render(self.title, True, self.textColour)
        self.textSize = self.fontSmall.size(self.title)

    def drawFrame(self):
        self.pygame.draw.lines(self.screen, self.textColour, False,
                               [[self.x1 + 25, self.y1], [self.x1, self.y1], [self.x1, self.y2], [self.x2, self.y2],
                                [self.x2, self.y1], [self.x1 + 35 + self.textSize[0], self.y1]], 1)
        self.screen.blit(self.Label, (self.x1 + 30, self.y1 - 10))

    def reinitFrame(self, title):
        self.title = title
        self.Label = self.fontSmall.render(self.title, True, self.textColour)
        self.textSize = self.fontSmall.size(self.title)

    def setTextColour(self, colour):
        self.textColour = colour
        self.Label = self.fontSmall.render(self.title, True, self.textColour)


class LabeledValue(RenderMain):
    def __init__(self, title, x, y, width, initValue, labFont, valFont):
        RenderMain.__init__(self)
        self.x = x
        self.y = y
        self.title = title
        self.width = width
        self.value = initValue
        self.valFont = valFont
        self.labFont = labFont
        self.LabLabel = self.labFont.render(self.title, True, self.textColour)
        self.ValLabel = self.valFont.render(self.value, True, self.textColour)
        self.LabSize = labFont.size(self.title)
        self.ValSize = self.valFont.size(self.value)

    def drawLabel(self, value):
        self.value = value
        self.ValLabel = self.valFont.render(self.value, True, self.textColour)
        self.LabLabel = self.labFont.render(self.title, True, self.textColour)
        self.ValSize = self.valFont.size(self.value)

        self.screen.blit(self.LabLabel, (self.x - self.width / 2, self.y))
        self.screen.blit(self.ValLabel, (self.x + self.width / 2 - self.ValSize[0], self.y - 36))

    def setTextColour(self, colour):
        self.textColour = colour
        self.LabLabel = self.labFont.render(self.title, True, colour)
        self.ValLabel = self.valFont.render(self.value, True, colour)
