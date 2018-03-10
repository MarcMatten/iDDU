import iDDUhelper
import pygame
import math
import csv
# from scipy.interpolate import interp1d
# f = interp1d(x, y)
import numpy

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

        self.pygame = pygame
        self.pygame.init()

        self.backgroundColour = self.black
        self.textColour = self.grey
        self.textColourFuelAdd = self.textColour

        self.fontTiny = self.pygame.font.Font("files\KhmerUI.ttf", 12)  # Khmer UI Calibri
        self.fontSmall = self.pygame.font.Font("files\KhmerUI.ttf", 20)
        self.fontMedium = self.pygame.font.Font("files\KhmerUI.ttf", 40)
        self.fontLarge = self.pygame.font.Font("files\KhmerUI.ttf", 60)
        self.fontHuge = self.pygame.font.Font("files\KhmerUI.ttf", 480)

        self.SCLabel = self.fontHuge.render('SC', True, self.textColour)

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

        self.track={'dist': [], 'x': [], 'y': []}
        self.map=[]

        # # track map
        # with open("track\dummie_track.csv") as csv_file:
        #     csv_reader = csv.reader(csv_file)
        #     #self.track{'dist':0, 'x':0, 'y': 0}
        #     for line in csv_reader:
        #         # print(float(line[0]))
        #         self.track['dist'].append(float(line[0]))
        #         self.track['x'].append(float(line[1])+400)
        #         self.track['y'].append(float(line[2])+240)
        #
        #         self.map.append([float(line[1])+400, float(line[2])+240])

            # print(self.track['dist'])

    def setTextColour(self, colour):
        self.textColour = colour

    def setBackgroundColour(self, colour):
        self.backgroundColour = colour


class RenderScreen(RenderMain):
    def __init__(self):
        RenderMain.__init__(self)

        # frames
        self.frames = {}
        self.frames[0] = Frame('Timing', 10, 10, 385, 230)
        self.frames[1] = Frame('Fuel', 405, 10, 385, 280)
        self.frames[2] = Frame('Session Info', 10, 250, 385, 220)
        self.frames[3] = Frame('Control', 405, 300, 385, 170)

        self.Labels1 = {}
        self.Labels1[0] = ['BestLap', LabeledValue('Best', 200, 50, 350, '00:00.000', self.fontSmall, self.fontLarge)]
        self.Labels1[1] = ['LastLap', LabeledValue('Last', 200, 120, 350, '00:00.000', self.fontSmall, self.fontLarge)]
        self.Labels1[2] = ['DeltaBest', LabeledValue('DBest', 200, 190, 350, '+00:00.000', self.fontSmall, self.fontLarge)]

        self.Labels1[3] = ['dcTractionControl', LabeledValue('TC1', 469, 425, 100, '-', self.fontSmall, self.fontLarge)]
        self.Labels1[4] = ['dcABS', LabeledValue('ABS', 725, 350, 105, '-', self.fontSmall, self.fontLarge)]
        self.Labels1[5] = ['dcBrakeBias', LabeledValue('BBias', 516, 350, 180, '-', self.fontSmall, self.fontLarge)]
        self.Labels1[6] = ['dcFuelMixture', LabeledValue('Mix', 725, 425, 100, '-', self.fontSmall, self.fontLarge)]
        self.Labels1[7] = ['dcTractionControl2', LabeledValue('TC2', 607, 425, 100, '-', self.fontSmall, self.fontLarge)]

        self.Labels1[8] = ['FuelLevel', LabeledValue('Fuel', 607, 60, 250, '-', self.fontSmall, self.fontLarge)]
        self.Labels1[9] = ['FuelCons', LabeledValue('Avg', 513, 130, 180, '-', self.fontSmall, self.fontLarge)]
        self.Labels1[10] = ['FuelLastCons', LabeledValue('Last', 700, 130, 180, '-', self.fontSmall, self.fontLarge)]
        self.Labels1[11] = ['FuelLaps', LabeledValue('Laps', 513, 200, 180, '-', self.fontSmall, self.fontLarge)]
        self.Labels1[12] = ['FuelAdd', LabeledValue('Add', 700, 200, 180, '-', self.fontSmall, self.fontLarge)]

        self.LabelsSession = {}
        self.LabelsSession[0] = ['Lap', LabeledValue('Lap', 100, 360, 140, '123', self.fontSmall, self.fontLarge)]
        self.LabelsSession[1] = ['Clock', LabeledValue('Clock', 350, 450, 50, '123', self.fontTiny, self.fontSmall)]
        self.LabelsSession[2] = ['Remaining', LabeledValue('Remaining', 200, 290, 350, '123', self.fontSmall, self.fontLarge)]
        self.LabelsSession[3] = ['Elapsed', LabeledValue('Elapsed', 200, 290, 350, '123', self.fontSmall, self.fontLarge)]
        self.LabelsSession[4] = ['ToGo', LabeledValue('To Go', 300, 360, 160, '123.4', self.fontSmall, self.fontLarge)]
        self.LabelsSession[5] = ['Joker', LabeledValue('Joker', 105, 425, 160, '5/3', self.fontSmall, self.fontLarge)]

        self.Labels2 = {}
        self.Labels2[0] = LabeledValue('LapsToGo', 400, 240, 200, '0.0', self.fontSmall, self.fontLarge)

        # misc
        self.done = False
        self.ScreenNumber = 1

        # lables
        # Timing
        # self.BestLapLabel = self.fontSmall.render('Best', True, self.textColour)
        # self.LastLapLabel = self.fontSmall.render('Last', True, self.textColour)
        # self.DeltaLapLabel = self.fontSmall.render('DBest', True, self.textColour)
        # SessionInfo
        # self.ClockLabel = self.fontTiny.render('Clock', True, self.textColour)
        # self.RemTimeLabel = self.fontSmall.render('Rem. Time', True, self.textColour)
        # self.ElTimeLabel = self.fontSmall.render('Time', True, self.textColour)
        # self.RemLapLabel = self.fontSmall.render('To go', True, self.textColour)
        # self.LapLabel = self.fontSmall.render('Lap', True, self.textColour)
        # Fuel
        # self.dcTractionControlLabel = self.fontSmall.render('TC1', True, self.textColour)
        # self.dcTractionControl2Label = self.fontSmall.render('TC2', True, self.textColour)
        # self.dcBrakeBiasLabel = self.fontSmall.render('BBias', True, self.textColour)
        # self.dcFuelMixtureLabel = self.fontSmall.render('Mix', True, self.textColour)
        # self.dcThrottleShapeLabel = self.fontSmall.render('Map', True, self.textColour)
        # self.dcABSLabel = self.fontSmall.render('ABS', True, self.textColour)
        # Control
        # self.FuelLevelLabel = self.fontSmall.render('Fuel', True, self.textColour)
        # self.FuelConsLabel = self.fontSmall.render('Avg.', True, self.textColour)
        # self.FuelLastConsLabel = self.fontSmall.render('Last', True, self.textColour)
        # self.FuelLapsLabel = self.fontSmall.render('Laps', True, self.textColour)
        # self.FuelAddLabel = self.fontSmall.render('Add', True, self.textColour)

    def render(self, iRData, calcData):

        ##### events ###########################################################################################################
        for event in self.pygame.event.get():
            if event.type == self.pygame.QUIT:
                self.done = True
            if event.type == self.pygame.KEYDOWN and event.key == self.pygame.K_ESCAPE:
                self.done = True
            if event.type == self.pygame.MOUSEBUTTONDOWN and event.button == 3:
                if self.fullscreen:
                    self.pygame.display.set_mode(self.resolution)
                    self.fullscreen = False
                else:
                    self.pygame.display.set_mode(self.resolution, self.pygame.NOFRAME)  # self.pygame.FULLSCREEN
                    self.fullscreen = True
            if event.type == self.pygame.MOUSEBUTTONDOWN and event.button == 1:
                # self.setBackgroundColour(self.red)
                # self.setTextColour(self.green)
                if self.ScreenNumber == 1:
                    self.ScreenNumber = 2
                else:
                    self.ScreenNumber = 1

        if self.ScreenNumber == 1:

            if calcData['init']:
                self.frames[2].reinitFrame(calcData['SessionInfo']['Sessions'][iRData['SessionNum']]['SessionType'])

            # prepare strings to display
            # Timing
            # BestLap = self.fontLarge.render(
            #     iDDUhelper.convertTimeMMSSsss(iRData['LapBestLapTime']), True,
            #     self.textColour)
            # LastLap = self.fontLarge.render(
            #     iDDUhelper.convertTimeMMSSsss(iRData['LapLastLapTime']), True,
            #     self.textColour)
            # DeltaBest = self.fontLarge.render(
            #     iDDUhelper.convertDelta(iRData['LapDeltaToSessionBestLap']), True,
            #     self.textColour)
            # Session Info
            RemTime = self.fontLarge.render(str(calcData['RemTimeValue']), True, self.textColour)
            RemLap = self.fontLarge.render(calcData['RemLapValueStr'], True, self.textColour)
            Lap = self.fontLarge.render(str(iRData['Lap']), True, self.textColour)
            Time = self.fontLarge.render(
                iDDUhelper.convertTimeHHMMSS(
                    iRData['SessionTime'] - calcData['GreenTime']), True,
                self.textColour)
            # Clock = self.fontSmall.render(iRData['clockValue'], True, self.textColour)

            # Control
            # dcTractionControl = self.fontLarge.render(
            #     iDDUhelper.roundedStr0(iRData['dcTractionControl']), True,
            #     self.textColour)
            # dcTractionControl2 = self.fontLarge.render(
            #     iDDUhelper.roundedStr0(iRData['dcTractionControl2']), True,
            #     self.textColour)
            # dcBrakeBias = self.fontLarge.render(iDDUhelper.roundedStr2(iRData['dcBrakeBias']),
            #                                     True, self.textColour)
            # dcFuelMixture = self.fontLarge.render(iDDUhelper.roundedStr0(iRData['dcFuelMixture']),
            #                                       True,
            #                                       self.textColour)
            # dcThrottleShape = self.fontLarge.render(
            #     iDDUhelper.roundedStr0(iRData['dcThrottleShape']), True,
            #     self.textColour)
            # dcABS = self.fontLarge.render(iDDUhelper.roundedStr0(iRData['dcABS']), True,
            #                               self.textColour)


            # Fuel
            FuelLevel = self.fontLarge.render(iDDUhelper.roundedStr2(iRData['FuelLevel']), True,
                                              self.textColour)
            FuelCons = self.fontLarge.render(calcData['FuelConsumptionStr'], True, self.textColour)
            FuelLastCons = self.fontLarge.render(iDDUhelper.roundedStr2(calcData['FuelLastCons']),
                                                 True, self.textColour)
            FuelLap = self.fontLarge.render(calcData['FuelLapStr'], True, self.textColour)
            FuelAdd = self.fontLarge.render(calcData['FuelAddStr'], True, self.textColourFuelAdd)

            self.screen.fill(self.backgroundColour)

            # define frames
            # self.Frame1.drawFrame()
            # self.Frame2.drawFrame()
            # self.Frame3.drawFrame()
            # self.Frame4.drawFrame()
            for i in range(0, len(self.frames)):
                self.frames[i].drawFrame()

            BestLap = iDDUhelper.convertTimeMMSSsss(iRData['LapBestLapTime'])
            LastLap = iDDUhelper.convertTimeMMSSsss(iRData['LapLastLapTime'])
            DeltaBest = iDDUhelper.convertDelta(iRData['LapDeltaToSessionBestLap'])

            dcTractionControl = iDDUhelper.roundedStr0(iRData['dcTractionControl'])
            dcTractionControl2 = iDDUhelper.roundedStr0(iRData['dcTractionControl2'])
            dcBrakeBias = iDDUhelper.roundedStr1(iRData['dcBrakeBias'])
            dcFuelMixture = iDDUhelper.roundedStr0(iRData['dcFuelMixture'])
            dcThrottleShape = iDDUhelper.roundedStr0(iRData['dcThrottleShape'])
            dcABS = iDDUhelper.roundedStr0(iRData['dcABS'])

            FuelLevel = iDDUhelper.roundedStr2(iRData['FuelLevel'])
            FuelCons = calcData['FuelConsumptionStr']
            FuelLastCons = iDDUhelper.roundedStr2(calcData['FuelLastCons'])
            FuelLaps = calcData['FuelLapStr']
            FuelAdd = calcData['FuelAddStr']

            # frame input
            for i in range(0, len(self.Labels1)):
                self.Labels1[i][1].drawLabel(eval(self.Labels1[i][0]))

            Lap = str(iRData['Lap'])
            ToGo = str(calcData['LapsToGo'])
            Clock = str(iRData['clockValue'])
            Joker = '1/7'#str(iRData[self.LabelsSession[i][0]])
            # Joker2Go = str(iRData[self.LabelsSession[i][0]])
            Elapsed = iDDUhelper.convertTimeHHMMSS(iRData['SessionTime'])
            Remaining = iDDUhelper.convertTimeHHMMSS(iRData['SessionTimeRemain'])


            for i in range(0, len(self.LabelsSession)):
                if calcData['LabelSessionDisplay'][i]:
                    self.LabelsSession[i][1].drawLabel(eval(self.LabelsSession[i][0]))

            # Timing
            # self.screen.blit(self.BestLapLabel, (30, 60))
            # self.screen.blit(BestLap, (115, 30))
            # self.screen.blit(self.LastLapLabel, (30, 130))
            # self.screen.blit(LastLap, (115, 100))
            # self.screen.blit(self.DeltaLapLabel, (30, 200))
            # self.screen.blit(DeltaBest, (115, 170))
            # Session Info
            # self.screen.blit(self.ClockLabel, (30, 450))
            # self.screen.blit(Clock, (80, 442))

            # if not data['SessionInfo']['Sessions'][SessionNum]['SessionTime'] == 'unlimited':
            #         self.screen.blit(RemTimeLabel, (30, 310))
            #         self.screen.blit(RemTime, (150, 280))
            # else:
            #         self.screen.blit(ElTimeLabel, (30, 310))
            #         self.screen.blit(Time, (150, 280))

            # if data['SessionInfo']['Sessions'][SessionNum]['SessionTime'] == 'unlimited' or data['SessionInfo']['Sessions'][SessionNum]['SessionTime'] > 10000:
            # if data['SessionTimeRemain']:
            # else:
            # if not data['SessionInfo']['Sessions'][SessionNum]['SessionLaps'] == 'unlimited':
            #         self.screen.blit(RemLapLabel, (220, 380))
            #         self.screen.blit(RemLap, (280, 350))

            # self.screen.blit(self.LapLabel, (30, 380))
            # self.screen.blit(self.Lap, (80, 350))
            # Control
            # self.screen.blit(self.dcBrakeBiasLabel, (425, 350))
            # self.screen.blit(dcBrakeBias, (505, 315))
            # self.screen.blit(self.dcABSLabel, (665, 350))
            # self.screen.blit(dcABS, (710, 315))
            # self.screen.blit(self.dcTractionControlLabel, (425, 420))
            # self.screen.blit(dcTractionControl, (470, 385))
            # self.screen.blit(self.dcTractionControl2Label, (555, 420))
            # self.screen.blit(dcTractionControl2, (600, 385))
            # self.screen.blit(self.dcFuelMixtureLabel, (665, 420))
            # self.screen.blit(dcFuelMixture, (710, 385))

            # Fuel
            # self.screen.blit(self.FuelLevelLabel, (425, 60))
            # self.screen.blit(FuelLevel, (505, 30))
            # self.screen.blit(self.FuelConsLabel, (425, 130))
            # self.screen.blit(FuelCons, (475, 100))
            # self.screen.blit(self.FuelLastConsLabel, (605, 130))
            # self.screen.blit(FuelLastCons, (660, 100))
            # self.screen.blit(self.FuelLapsLabel, (425, 200))
            # self.screen.blit(FuelLap, (475, 170))
            # self.screen.blit(self.FuelAddLabel, (605, 200))
            # self.screen.blit(FuelAdd, (660, 170))

            # self.timestr = time.strftime("%H:%M:%S", time.localtime())
            # self.screen.blit(self.ClockLabel, (30, 450))


            # clock = self.fontSmall.render(iRData['clockValue'], True, self.self.textColour)
            # self.screen.blit(clock, (80, 442))

        elif self.ScreenNumber == 2:
            self.screen.fill(self.backgroundColour)
            # self.pygame.draw.line(self.screen, self.textColour, [400, 25], [400, 55], 5)
            # self.pygame.draw.circle(self.screen, self.textColour, [400,
            #                                                        240], 200, 5)
            #
            # x = 400 + 198 * math.sin(2 * math.pi * iRData['LapDistPct'])
            # y = 240 - 198 * math.cos(2 * math.pi * iRData['LapDistPct'])

            x = numpy.interp(iRData['LapDistPct']*100, calcData['dist'], calcData['x'])
            y = numpy.interp(iRData['LapDistPct']*100, calcData['dist'], calcData['y'])

            self.pygame.draw.lines(self.screen, self.textColour, True, calcData['map'], 5)

            Label = self.fontTiny.render('23', True, self.white)
            self.pygame.draw.circle(self.screen, self.red, [int(x), int(y)], 10, 0)
            self.screen.blit(Label, (int(x) - 6, int(y) - 7))
            #
            # for i in range(0, len(self.Labels2)):
            #     self.Labels2[i].drawLabel(iDDUhelper.roundedStr1(iRData['LapDistPct'] * 100))

        self.pygame.display.flip()
        self.clocker.tick(30)


class Frame(RenderMain):
    def __init__(self, title, x1, y1, dx, dy):
        RenderMain.__init__(self)
        self.x1 = x1
        self.x2 = x1 + dx - 1
        self.y1 = y1
        self.y2 = y1 + dy - 1
        self.Label = self.fontSmall.render(title, True, self.textColour)
        self.textSize = self.fontSmall.size(title)

    def drawFrame(self):
        self.pygame.draw.lines(self.screen, self.textColour, False,
                               [[self.x1 + 25, self.y1], [self.x1, self.y1], [self.x1, self.y2], [self.x2, self.y2],
                                [self.x2, self.y1], [self.x1 + 35 + self.textSize[0], self.y1]], 1)
        self.screen.blit(self.Label, (self.x1 + 30, self.y1 - 10))

    def reinitFrame(self, title):
        self.Label = self.fontSmall.render(title, True, self.textColour)
        self.textSize = self.fontSmall.size(title)



class LabeledValue(RenderMain):
    def __init__(self, title, x, y, width, initValue, labFont, valFont):
        RenderMain.__init__(self)
        self.x = x
        self.y = y
        self.width = width
        self.value = initValue
        self.valFont = valFont
        self.LabLabel = labFont.render(title, True, self.textColour)
        self.ValLabel = valFont.render(self.value, True, self.textColour)
        self.LabSize = labFont.size(title)
        self.ValSize = self.valFont.size(self.value)

    def drawLabel(self, value):
        self.value = value
        self.ValLabel = self.valFont.render(self.value, True, self.textColour)
        self.ValSize = self.valFont.size(self.value)

        self.screen.blit(self.LabLabel, (self.x - self.width / 2, self.y))
        self.screen.blit(self.ValLabel, (self.x + self.width / 2 - self.ValSize[0], self.y - 36))
