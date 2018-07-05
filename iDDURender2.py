import iDDUhelper
import pygame
import math
import csv
import numpy
import warnings


# class RenderMain:
#     def __init__(self):
#         self.pygame = pygame
#         self.pygame.init()
# 
#         # display
#         self.font = pygame.font.Font("files/KhmerUI.ttf", 20)
#         self.resolution = (200, 100)
#         self.fullscreen = False
#         self.pygame.display.set_caption('iDDU')
#         self.screen = self.pygame.display.set_mode(self.resolution)
#         self.clocker = self.pygame.time.Clock()
#         self.done = False
#         self.ScreenNumber = 1
# 
# class RenderScreen(RenderMain):
#     def __init__(self, db):
#         RenderMain.__init__(self)
# 
#         self.db = db
#         self.done = False
#         self.ScreenNumber = 1
# 
#     def render(self):
# 
#         ##### events ###########################################################################################################
#         for event in self.pygame.event.get():
#             if event.type == self.pygame.QUIT:
#                 self.done = True
#             if event.type == self.pygame.KEYDOWN and event.key == self.pygame.K_ESCAPE:
#                 self.done = True
#             if event.type == self.pygame.MOUSEBUTTONDOWN and event.button == 3:
#                 if self.fullscreen:
#                     self.pygame.display.set_mode(self.resolution)
#                     self.fullscreen = False
#                 else:
#                     self.pygame.display.set_mode(self.resolution, self.pygame.NOFRAME)
#                     self.fullscreen = True
#             if event.type == self.pygame.MOUSEBUTTONDOWN and event.button == 1:
#                 if self.ScreenNumber == 1:
#                     self.ScreenNumber = 2
#                 else:
#                     self.ScreenNumber = 1
# 
#         self.screen = self.pygame.display.set_mode(self.resolution)
#         self.screen.blit(self.font.render(str(self.db.timeStr), True, (255, 255, 255)), (25, 10))
#         self.screen.blit(self.font.render(str(self.db.startUp), True, (255, 255, 255)), (25, 60))
# 
#         self.pygame.display.flip()
#         self.clocker.tick(30)
# 
#         return self.done

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
            # BestLap = self.fontLarge.render(
            #     iDDUhelper.convertTimeMMSSsss(self.db.LapBestLapTime']), True,
            #     self.textColour)
            # LastLap = self.fontLarge.render(
            #     iDDUhelper.convertTimeMMSSsss(self.db.LapLastLapTime']), True,
            #     self.textColour)
            # DeltaBest = self.fontLarge.render(
            #     iDDUhelper.convertDelta(self.db.LapDeltaToSessionBestLap']), True,
            #     self.textColour)
            # Session Info
            RemTime = self.fontLarge.render(str(self.db.RemTimeValue), True, self.db.textColour)
            RemLap = self.fontLarge.render(self.db.RemLapValueStr, True, self.db.textColour)
            Lap = self.fontLarge.render(str(self.db.Lap), True, self.db.textColour)
            Time = self.fontLarge.render(
                iDDUhelper.convertTimeHHMMSS(
                    self.db.SessionTime - self.db.GreenTime), True,
                self.db.textColour)
            # Clock = self.fontSmall.render(self.db.clockValue'], True, self.textColour)

            # Control
            # dcTractionControl = self.fontLarge.render(
            #     iDDUhelper.roundedStr0(self.db.dcTractionControl']), True,
            #     self.textColour)
            # dcTractionControl2 = self.fontLarge.render(
            #     iDDUhelper.roundedStr0(self.db.dcTractionControl2']), True,
            #     self.textColour)
            # dcBrakeBias = self.fontLarge.render(iDDUhelper.roundedStr2(self.db.dcBrakeBias']),
            #                                     True, self.textColour)
            # dcFuelMixture = self.fontLarge.render(iDDUhelper.roundedStr0(self.db.dcFuelMixture']),
            #                                       True,
            #                                       self.textColour)
            # dcThrottleShape = self.fontLarge.render(
            #     iDDUhelper.roundedStr0(self.db.dcThrottleShape']), True,
            #     self.textColour)
            # dcABS = self.fontLarge.render(iDDUhelper.roundedStr0(self.db.dcABS']), True,
            #                               self.textColour)


            # Fuel
            # FuelLevel = self.fontLarge.render(iDDUhelper.roundedStr2(self.db.FuelLevel), True,
            #                                   self.db.textColour)
            # FuelCons = self.fontLarge.render(self.db.FuelConsumptionStr, True, self.db.textColour)
            # FuelLastCons = self.fontLarge.render(iDDUhelper.roundedStr2(self.db.FuelLastCons),
            #                                      True, self.db.textColour)
            # FuelLaps = self.fontLarge.render(self.db.FuelLapStr, True, self.db.textColour)
            # FuelAdd = self.fontLarge.render(self.db.FuelAddStr, True, self.db.textColourFuelAdd)

            # self.screen.fill(self.backgroundColour)
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
            # self.Frame1.drawFrame()
            # self.Frame2.drawFrame()
            # self.Frame3.drawFrame()
            # self.Frame4.drawFrame()
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
            # print('-- ', FuelAdd)

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


                    # clock = self.fontSmall.render(self.db.clockValue'], True, self.self.textColour)
                    # self.screen.blit(clock, (80, 442))

        elif self.ScreenNumber == 2:
            self.screen.fill(self.backgroundColour)
            # self.pygame.draw.line(self.screen, self.textColour, [400, 25], [400, 55], 5)
            # self.pygame.draw.circle(self.screen, self.textColour, [400,
            #                                                        240], 200, 5)
            #
            # x = 400 + 198 * math.sin(2 * math.pi * self.db.LapDistPct'])
            # y = 240 - 198 * math.cos(2 * math.pi * self.db.LapDistPct'])

            # x = numpy.interp(self.db.LapDistPct']*100, self.db.dist'], self.db.x'])
            # y = numpy.interp(self.db.LapDistPct']*100, self.db.dist'], self.db.y'])

            self.highlightSection(5, self.green)
            self.highlightSection(1, self.red)

            self.pygame.draw.lines(self.screen, self.db.textColour, True, [self.db.map[-1], self.db.map[0]], 30)

            self.pygame.draw.lines(self.screen, self.db.textColour, True, self.db.map, 5)


            # Label = self.fontTiny.render('23', True, self.white)
            # self.pygame.draw.circle(self.screen, self.red, [int(x), int(y)], 10, 0)
            # self.screen.blit(Label, (int(x) - 6, int(y) - 7))
            #
            # for i in range(0, len(self.Labels2)):
            #     self.Labels2[i].drawLabel(iDDUhelper.roundedStr1(self.db.LapDistPct'] * 100))

            for n in range(0, len(self.db.DriverInfo['Drivers'])):
                # ID = self.db.DriverInfo']['Drivers'][n]['CarIdx']
                # print(ID)
                # print(self.db.LapDistPct'])
                # print(self.db.LapDistPct'][ID])
                # print(self.db.LapDistPct'][ID]*100)
                self.CarOnMap(self.db.DriverInfo['Drivers'][n]['CarIdx'])

        self.pygame.display.flip()
        self.clocker.tick(30)

        return self.done

    def CarOnMap(self, Idx):
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

        # temp_lower = numpy.interp(self.db.CarIdxLapDistPct, self.db.time, self.db.dist)
        # temp_upper =

        # map = [self.db.map[t] for t in range(0, len(self.db.map)) if (
        # (self.db.dist[t] < self.db.CarIdxLapDistPct[self.db.DriverInfo['DriverCarIdx']] * 100 + 10) and (
        # self.db.dist[t] > self.db.CarIdxLapDistPct[self.db.DriverInfo['DriverCarIdx']] * 100 - 10))]
        # map = [self.db.map[t] for t in range(0, len(self.db.map)) if ((self.db.dist[t] < temp_upper) and (self.db.dist[t] > temp_lower))]

        # self.pygame.draw.lines(self.screen, self.blue, False, map, 20)


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
