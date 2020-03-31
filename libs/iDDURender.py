import os
import time
import numpy as np
import pygame
from libs import iDDUhelper
import irsdk

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

ir = irsdk.IRSDK()

ArrowLeft = [[20, 240], [100, 20], [100, 460]]
ArrowRight = [[780, 240], [700, 20], [700, 460]]
ArrowLeft2 = [[120, 240], [200, 20], [200, 460]]
ArrowRight2 = [[680, 240], [600, 20], [600, 460]]

pygame = pygame
pygame.init()

fontTiny = pygame.font.Font("files\KhmerUI.ttf", 12)  # Khmer UI Calibri
fontTiny2 = pygame.font.Font("files\KhmerUI.ttf", 18)
fontSmall = pygame.font.Font("files\KhmerUI.ttf", 20)
fontMedium = pygame.font.Font("files\KhmerUI.ttf", 40)
fontLarge = pygame.font.Font("files\KhmerUI.ttf", 60)
fontGear = pygame.font.Font("files\KhmerUI.ttf", 163)
fontReallyLarge = pygame.font.Font("files\KhmerUI.ttf", 350)
fontHuge = pygame.font.Font("files\KhmerUI.ttf", 480)
SCLabel = fontHuge.render('SC', True, black)

# display
resolution = (800, 480)
if os.environ['COMPUTERNAME'] == 'MARC-SURFACE':
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (-1920, 0)
else:
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0, 1080)

fullscreen = True
pygame.display.set_caption('iDDU')
pygame.display.init()
myJoystick = None
clocker = pygame.time.Clock()

# background
checkered = pygame.image.load("files/checkered.gif")
dsq = pygame.image.load("files/dsq.gif")
debry = pygame.image.load("files/debry.gif")
pitClosed = pygame.image.load("files/pitClosed.gif")
warning = pygame.image.load("files/warning.gif")
arrow = pygame.image.load("files/arrow.gif")

screen = None

class RenderMain:
    __slots__ = 'joystick'
    BDisplayCreated = False
    screen = None

    def __init__(self, db):
        self.db = db

    def initJoystick(self, name):
        pygame.joystick.init()
        print(self.db.timeStr + ': \t' + str(pygame.joystick.get_count()) + ' joysticks detected:')

        desiredJoystick = 9999

        for i in range(pygame.joystick.get_count()):
            print(self.db.timeStr + ':\tJoystick ', i, ': ', pygame.joystick.Joystick(i).get_name())
            if pygame.joystick.Joystick(i).get_name() == name:
                desiredJoystick = i

        if not desiredJoystick == 9999:
            print(self.db.timeStr + ':\tConnecting to', pygame.joystick.Joystick(desiredJoystick).get_name())
            myJoystick = pygame.joystick.Joystick(desiredJoystick)
            myJoystick.get_name()
            myJoystick.init()
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

        self.frames[0].addLabel('BestLapStr', LabeledValue2('Best', 21, 26, 265, '12:34.567', fontSmall, fontLarge, self.db, 0, 0), 0)
        self.frames[0].addLabel('LastLapStr', LabeledValue2('Last', 21, 110, 265, '00:00.000', fontSmall, fontLarge, self.db, 0, 0), 1)
        self.frames[0].addLabel('DeltaBestStr', LabeledValue2('DBest', 21, 194, 265, '+00:00.000', fontSmall, fontLarge, self.db, 0, 0), 2)

        self.frames[1].addLabel('ClockStr', SimpleValue(318, -10, 92, '-', fontSmall, self.db, 0, 0, 1), 14)
        self.frames[1].addLabel('GearStr', SimpleValue(318, 12, 92, '-', fontGear, self.db, 0, 7, 1), 22)

        self.frames[2].addLabel('SpeedStr', SimpleValue(318, 194, 92, '-', fontLarge, self.db, 0, 0, 0), 23)

        self.frames[3].addLabel('RemainingStr', LabeledValue2('Remaining', 442, 26, 220, '-', fontSmall, fontLarge, self.db, 0, 0), 15)
        self.frames[3].addLabel('ElapsedStr', LabeledValue2('Elapsed', 442, 26, 220, '-', fontSmall, fontLarge, self.db, 0, 0), 16)
        self.frames[3].addLabel('JokerStr', LabeledValue2('Joker', 689, 26, 90, '0/0', fontSmall, fontLarge, self.db, 4, 6), 17)
        self.frames[3].addLabel('LapStr', LabeledValue2('Lap', 442, 110, 160, '-', fontSmall, fontLarge, self.db, 0, 0), 13)
        self.frames[3].addLabel('ToGoStr', LabeledValue2('To Go', 662, 110, 117, '100', fontSmall, fontLarge, self.db, 0, 0), 20)
        self.frames[3].addLabel('PosStr', LabeledValue2('Pos', 442, 194, 160, '0.0', fontSmall, fontLarge, self.db, 0, 0), 24)
        self.frames[3].addLabel('EstStr', LabeledValue2('Est', 654, 194, 125, '0.0', fontSmall, fontLarge, self.db, 0, 0), 21)

        self.frames[4].addLabel('dcBrakeBiasStr', LabeledValue2('BBias', 21, 303, 125, '-', fontSmall, fontLarge, self.db, 0, 0), 9)
        self.frames[4].addLabel('dcABSStr', LabeledValue2('ABS', 219, 303, 67, '-', fontSmall, fontLarge, self.db, 0, 0), 8)
        self.frames[4].addLabel('dcTractionControlStr', LabeledValue2('TC1', 21, 387, 67, '-', fontSmall, fontLarge, self.db, 0, 1), 11)
        self.frames[4].addLabel('dcTractionControl2Str', LabeledValue2('TC2', 120, 387, 67, '-', fontSmall, fontLarge, self.db, 0, 1), 12)
        self.frames[4].addLabel('DRSStr', LabeledValue2('DRS', 219, 387, 67, '0', fontSmall, fontLarge, self.db, 2, 5), 18)
        self.frames[4].addLabel('P2PStr', LabeledValue2('P2P', 219, 387, 67, '0', fontSmall, fontLarge, self.db, 3, 4), 19)

        self.frames[5].addLabel('FuelLevelStr', LabeledValue2('Remaining', 318, 303, 125, '-', fontSmall, fontLarge, self.db, 0, 2), 3)
        self.frames[5].addLabel('FuelAddStr', LabeledValue2('Add', 481, 303, 125, '-', fontSmall, fontLarge, self.db, 1, 0), 7) # 515
        self.frames[5].addLabel('FuelLapsStr', LabeledValue2('Laps', 644, 303, 135, '-', fontSmall, fontLarge, self.db, 0, 3), 6) # 318
        self.frames[5].addLabel('dcFuelMixtureStr', LabeledValue2('Mix', 318, 387, 67, '-', fontSmall, fontLarge, self.db, 0, 0), 10) # 712
        self.frames[5].addLabel('FuelLastConsStr', LabeledValue2('Last', 447, 387, 135, '-', fontSmall, fontLarge, self.db, 0, 0), 5) # 481
        self.frames[5].addLabel('FuelAvgConsStr', LabeledValue2('Avg', 649, 387, 135, '-', fontSmall, fontLarge, self.db, 0, 0), 4) # 644

        # misc
        self.done = False
        self.db.NDDUPage = 1

        self.snapshot = False

    @staticmethod
    def stopRendering():
        pygame.display.quit()

    def render(self):
        t = time.perf_counter()

        if self.db.DDUrunning and self.db.StartDDU and not self.BDisplayCreated:
            RenderMain.screen = pygame.display.set_mode(resolution, pygame.NOFRAME)
            self.BDisplayCreated = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.done = True
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                self.db.StopDDU = True

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 or event.type == pygame.JOYBUTTONDOWN and event.button == 25:
                if self.db.NDDUPage == 1:
                    self.db.NDDUPage = 2
                else:
                    self.db.NDDUPage = 1

        if ir.startup():
            if self.db.NDDUPage == 1:

                if self.db.init:
                    self.frames[2].reinitFrame(ir['SessionInfo']['Sessions'][ir['SessionNum']]['SessionType'])

                RenderMain.screen.fill(self.db.backgroundColour)
                if self.db.FlagException:
                    if self.db.FlagExceptionVal == 1:
                        RenderMain.screen.blit(checkered, [0, 0])
                    elif self.db.FlagExceptionVal == 2:
                        pygame.draw.circle(RenderMain.screen, orange, [400, 240], 185)
                    elif self.db.FlagExceptionVal == 3:
                        RenderMain.screen.blit(SCLabel, (130, -35))
                    elif self.db.FlagExceptionVal == 4:
                        RenderMain.screen.blit(dsq, [0, 0])
                    elif self.db.FlagExceptionVal == 5:
                        RenderMain.screen.blit(debry, [0, 0])
                    elif self.db.FlagExceptionVal == 6:
                        RenderMain.screen.blit(warning, [0, 0])

                # Radar Incicators
                CarLeftRight = ir['CarLeftRight']
                if np.isin(CarLeftRight, [2, 4, 5]):
                    pygame.draw.polygon(RenderMain.screen, orange, ArrowLeft, 0)
                    if CarLeftRight == 5:
                        pygame.draw.polygon(RenderMain.screen, orange, ArrowLeft2, 0)
                if np.isin(CarLeftRight, [3, 4, 6]):
                    pygame.draw.polygon(RenderMain.screen, orange, ArrowRight, 0)
                    if CarLeftRight == 6:
                        pygame.draw.polygon(RenderMain.screen, orange, ArrowRight2, 0)

                # DRS
                if self.db.DRS:
                    if ir['SessionInfo']['Sessions'][ir['SessionNum']]['SessionType'] == 'Race':
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
                self.db.BestLapStr = iDDUhelper.convertTimeMMSSsss(max(0, ir['LapBestLapTime']))
                self.db.LastLapStr = iDDUhelper.convertTimeMMSSsss(max(0, ir['LapLastLapTime']))
                self.db.DeltaBestStr = iDDUhelper.convertDelta(ir['LapDeltaToSessionBestLap'])

                self.db.dcTractionControlStr = iDDUhelper.roundedStr0(ir['dcTractionControl'])
                self.db.dcTractionControl2Str = iDDUhelper.roundedStr0(ir['dcTractionControl2'])
                self.db.dcBrakeBiasStr = iDDUhelper.roundedStr1(ir['dcBrakeBias'], 3)
                self.db.dcFuelMixtureStr = iDDUhelper.roundedStr0(ir['dcFuelMixture'])
                self.db.dcThrottleShapeStr = iDDUhelper.roundedStr0(ir['dcThrottleShape'])
                self.db.dcABSStr = iDDUhelper.roundedStr0(ir['dcABS'])

                self.db.FuelLevelStr = iDDUhelper.roundedStr1(ir['FuelLevel'], 3)
                self.db.FuelAvgConsStr = iDDUhelper.roundedStr2(max(0, self.db.FuelAvgConsumption))
                self.db.FuelLastConsStr = iDDUhelper.roundedStr2(max(0, self.db.FuelLastCons))
                self.db.FuelLapsStr = iDDUhelper.roundedStr1(self.db.NLapRemaining, 3)
                self.db.FuelAddStr = iDDUhelper.roundedStr1(max(0, self.db.VFuelAdd), 3)

                self.db.SpeedStr = iDDUhelper.roundedStr0(max(0.0, ir['Speed']*3.6))
                if ir['Gear'] > 0:
                    self.db.GearStr = str(int(ir['Gear']))
                elif ir['Gear'] == 0:
                    self.db.GearStr = 'N'
                elif ir['Gear'] < 0:
                    self.db.GearStr = 'R'

                if self.db.LapLimit:
                    self.db.LapStr = str(max(0, ir['Lap'])) + '/' + str(self.db.RaceLaps)
                    self.db.ToGoStr = iDDUhelper.roundedStr1(max(0, self.db.RaceLaps - ir['Lap'] + 1 - ir['LapDistPct']), 3)

                else:
                    self.db.LapStr = str(max(0, ir['Lap']))
                    self.db.ToGoStr = '0'
                self.db.ClockStr = self.db.timeStr
                if self.db.RX:
                    self.db.JokerStr = self.db.JokerStr
                self.db.ElapsedStr = iDDUhelper.convertTimeHHMMSS(max(0, ir['SessionTime']))
                self.db.RemainingStr = iDDUhelper.convertTimeHHMMSS(max(0, ir['SessionTimeRemain']))
                self.db.EstStr = iDDUhelper.roundedStr1(self.db.NLapDriver, 3)

                for i in range(0, len(self.frames)):
                    self.frames[i].setTextColour(self.db.textColour)
                    self.frames[i].drawFrame()

            elif self.db.NDDUPage == 2:
                RenderMain.screen.fill(self.db.backgroundColour)

                # Wind arrow
                aWind = (-self.db.WindDir + self.db.track.aNorth - self.db.track.a)*180/np.pi-180
                dx = abs(82.8427 * np.cos(2 * (45/180*np.pi + aWind/180*np.pi)))
                RenderMain.screen.blit(pygame.transform.rotate(arrow, int(aWind)), [200-dx, 40-dx])

                if self.db.MapHighlight:
                    self.highlightSection(5, green)
                    self.highlightSection(1, red)

                # SFLine
                pygame.draw.polygon(RenderMain.screen, self.db.textColour, self.db.track.SFLine, 0)

                pygame.draw.lines(RenderMain.screen, self.db.textColour, True, self.db.track.map, 5)

                for n in range(1, len(ir['DriverInfo']['Drivers'])):
                    temp_CarIdx = ir['DriverInfo']['Drivers'][n]['CarIdx']
                    if not temp_CarIdx == self.db.DriverCarIdx:
                       self.CarOnMap(n)
                self.CarOnMap(self.db.DriverCarIdx)
                self.CarOnMap(0)

                Label = fontTiny2.render(self.db.weatherStr + iDDUhelper.roundedStr0(self.db.WindVel*3.6) + ' km/h', True, self.db.textColour)
                RenderMain.screen.blit(Label, (5, 1))

                Label2 = fontTiny2.render(self.db.SOFstr, True, self.db.textColour)

                RenderMain.screen.blit(Label2, (5, 458))

        else:
            RenderMain.screen.fill(self.db.backgroundColour)
            Label = fontMedium.render('Waiting for iRacing ...', True, self.db.textColour)
            LabelSize = fontMedium.size('Waiting for iRacing ...')
            Label2 = fontMedium.render(self.db.timeStr, True, self.db.textColour)
            Label2Size = fontMedium.size(self.db.timeStr)
            RenderMain.screen.blit(Label, (400 - LabelSize[0]/2, 120))
            RenderMain.screen.blit(Label2, (400 - Label2Size[0]/2, 240))


        if ir.startup() and ir['IsOnTrack']:
            EngineWarnings = ir['EngineWarnings']
            # warning and alarm messages
            if EngineWarnings & 0x10:
                self.warningLabel('PIT LIMITER', blue, white)
            if EngineWarnings & 0x1:
                self.warningLabel('WATER TEMP HIGH', red, white)
            if EngineWarnings & 0x2:
                self.warningLabel('LOW FUEL PRESSURE', red, white)
            if EngineWarnings & 0x4:
                self.warningLabel('LOW OIL PRESSURE', red, white)
            if EngineWarnings & 0x8:
                self.warningLabel('ENGINE STALLED', yellow, black)

            if ir['SessionTime'] < self.db.tdcHeadlightFlash + 0.5:
                if self.db.BdcHeadlightFlash:
                    self.warningLabel('FLASH', green, white)

            # for testing purposes....
            SessionFlags = ir['SessionFlags']
            if SessionFlags & 0x80:
                self.warningLabel('CROSSED', white, black)
            # if SessionFlags & 0x100: # normal yellow
            #     self.warningLabel('YELLOW WAVING', self.white, self.black)
            if SessionFlags & 0x400:
                self.warningLabel('GREEN HELD', white, black)
            if SessionFlags & 0x2000:
                self.warningLabel('RANDOM WAVING', white, black)
            # if SessionFlags & 0x8000:
            #     self.warningLabel('CAUTION WAVING', self.white, self.black)
            # if SessionFlags & 0x10000:
            #     self.warningLabel('BLACK', self.white, self.black)
            if SessionFlags & 0x20000:
                self.warningLabel('DISQUALIFIED', white, black)
            # if SessionFlags & 0x80000:
            #     self.warningLabel('FURLED', self.white, self.black)
            # if SessionFlags & 0x100000:
            #     self.warningLabel('REPAIR', self.white, self.black)

            # driver control change
            if ir['SessionTime'] < self.db.dcChangeTime + 0.75:
                if self.db.car.dcList[self.db.dcChangedItems[0]][1]:
                    if self.db.car.dcList[self.db.dcChangedItems[0]][2] == 0:
                        valueStr = iDDUhelper.roundedStr0(self.db.get(self.db.dcChangedItems[0]))
                    elif self.db.car.dcList[self.db.dcChangedItems[0]][2] == 1:
                        valueStr = iDDUhelper.roundedStr1(self.db.get(self.db.dcChangedItems[0]), 3)
                    else:
                        valueStr = str(self.db.get(self.db.dcChangedItems[0]))

                    self.changeLabel(self.db.car.dcList[self.db.dcChangedItems[0]][0], valueStr)

        pygame.display.flip()
        self.db.tExecuteRender = (time.perf_counter() - t) * 1000
        clocker.tick(30)

        return self.done

    def CarOnMap(self, Idx):
        CarIdxLapDistPct = ir['CarIdxLapDistPct']
        if CarIdxLapDistPct[Idx] == -1.0:
            return

        x = np.interp([float(CarIdxLapDistPct[Idx]) * 100], self.db.track.dist, self.db.track.x).tolist()[0]
        y = np.interp([float(CarIdxLapDistPct[Idx]) * 100], self.db.track.dist, self.db.track.y).tolist()[0]

        if ir['DriverInfo']['DriverCarIdx'] == Idx:  # if player's car
            if self.db.RX:
                if self.db.JokerLapsRequired > 0 and (self.db.JokerLaps[Idx] == self.db.JokerLapsRequired):
                    self.drawCar(Idx, x, y, green, black)
            self.drawCar(Idx, x, y, red, white)
        else:  # other cars
            if ir['CarIdxClassPosition'][Idx] == 1:
                if ir['CarIdxPosition'][Idx] == 1:  # overall leader
                    labelColour = white
                    dotColour = purple
                else:
                    labelColour = purple  # class leaders
                    dotColour = self.bit2RBG(ir['DriverInfo']['Drivers'][Idx]['CarClassColor'])
            elif Idx == ir['DriverInfo']['PaceCarIdx']:  # PaceCar
                labelColour = black
                dotColour = orange
                if not ir['SessionInfo']['Sessions'][ir['SessionNum']]['SessionType'] == 'Race':
                    return
                else:
                    if ir['SessionState'] > 3:
                        if not ir['SessionFlags'] & 0x4000 or not ir['SessionFlags'] & 0x8000:
                            return
            else:
                labelColour = black
                dotColour = self.bit2RBG(ir['DriverInfo']['Drivers'][Idx]['CarClassColor'])

            if not ir['CarIdxOnPitRoad'][Idx]:
                if self.db.RX:
                    if self.db.JokerLapsRequired > 0 and (self.db.JokerLaps[Idx] == self.db.JokerLapsRequired):
                        self.drawCar(Idx, x, y, green, labelColour)
                else:
                    self.drawCar(Idx, x, y, dotColour, labelColour)
            else:
                return

    def drawCar(self, Idx, x, y, dotColour, labelColour):
        Label = fontTiny.render(ir['DriverInfo']['Drivers'][Idx]['CarNumber'], True, labelColour)
        if ir['CarIdxOnPitRoad'][Idx]:
            pygame.draw.circle(RenderMain.screen, yellow, [int(x), int(y)], 12, 0)
        elif self.db.CarIdxPitStops[Idx] >= self.db.PitStopsRequired > 0 and ir['SessionInfo']['Sessions'][ir['SessionNum']]['SessionType'] == 'Race':
            pygame.draw.circle(RenderMain.screen, green, [int(x), int(y)], 12, 0)
        pygame.draw.circle(RenderMain.screen, dotColour, [int(x), int(y)], 10, 0)
        RenderMain.screen.blit(Label, (int(x) - 6, int(y) - 7))

    @staticmethod
    def bit2RBG(bitColor):
        hexColor = format(bitColor, '06x')
        return int('0x' + hexColor[0:2], 0), int('0x' + hexColor[2:4], 0), int('0x' + hexColor[4:6], 0)

    def highlightSection(self, width: int, colour: tuple):
        if self.db.WeekendInfo['TrackName'] in  self.db.car.tLap:
            tLap = self.db.car.tLap[self.db.WeekendInfo['TrackName']]
            timeStamp = np.interp([float(ir['CarIdxLapDistPct'][ir['DriverInfo']['DriverCarIdx']]) * 100], self.db.track.dist, tLap).tolist()[0]
            timeStamp1 = timeStamp - self.db.PitStopDelta - width / 2
            while timeStamp1 < 0:
                timeStamp1 = timeStamp1 + tLap[-1]
            while timeStamp1 > tLap[-1]:
                timeStamp1 = timeStamp1 - tLap[-1]

            timeStamp2 = timeStamp - self.db.PitStopDelta + width / 2

            while timeStamp2 < 0:
                timeStamp2 = timeStamp2 + tLap[-1]
            while timeStamp2 > tLap[-1]:
                timeStamp2 = timeStamp2 - tLap[-1]

            timeStampStart = timeStamp1
            timeStampEnd = timeStamp2

            # try:
            if timeStamp2 > timeStamp1:
                tempMap = [self.db.track.map[t] for t in range(0, len(self.db.track.map)) if ((tLap[t] < timeStampEnd) and (tLap[t] > timeStampStart))]
                if len(tempMap) < 2:
                    return

                pygame.draw.lines(RenderMain.screen, colour, False, tempMap, 20)
            else:

                # map1 = [self.db.track.map[t] for t in range(0, len(self.db.track.map)) if
                #         (tLap[t] <= max(timeStampEnd, tLap[1]))]
                # map2 = [self.db.track.map[t] for t in range(0, len(self.db.track.map)) if
                #         (tLap[t] >= min(timeStampStart, tLap[-1]))]

                indices1 = np.argwhere(np.array(tLap) <= max(timeStampEnd, tLap[1]))
                if len(indices1) == 1:
                    indices1 = np.append(indices1, indices1[0]+1)

                ind1 = []
                for i in range(0,len(indices1)):
                    # ind1.append(indices1[i][0])
                    ind1.append(int(indices1[i]))

                map1 = np.array(self.db.track.map)[ind1].tolist()

                indices2 = np.argwhere(np.array(tLap) >= min(timeStampStart, tLap[-1]))
                if len(indices2) == 1:
                    indices2 = np.append(indices2, indices2[0]-1)

                ind2 = []
                for i in range(0,len(indices2)):
                    # ind2.append(indices2[i][0])
                    ind2.append(int(indices2[i]))

                map2 = np.array(self.db.track.map)[ind2].tolist()

                pygame.draw.lines(RenderMain.screen, colour, False, map1, 20)
                pygame.draw.lines(RenderMain.screen, colour, False, map2, 20)
        else:
            return

    def warningLabel(self, text, colour, textcolour):
        pygame.draw.rect(RenderMain.screen, colour, [0, 0, 800, 100], 0)
        LabelSize = fontLarge.size(text)
        Label = fontLarge.render(text, True, textcolour)
        RenderMain.screen.blit(Label, (400 - LabelSize[0] / 2, 50 - LabelSize[1] / 2))

    def changeLabel(self, text, value):
        pygame.draw.rect(RenderMain.screen, black, [0, 0, 800, 480], 0)
        LabelSize = fontLarge.size(text)
        Label = fontLarge.render(text, True, white)
        RenderMain.screen.blit(Label, (400 - LabelSize[0] / 2, 50 - LabelSize[1] / 2))
        ValueSize = fontReallyLarge.size(value)
        Value = fontReallyLarge.render(value, True, white)
        RenderMain.screen.blit(Value, (400 - ValueSize[0] / 2, 270 - ValueSize[1] / 2))

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
        self.Title = fontSmall.render(self.title, True, self.db.textColour)
        self.textSize = fontSmall.size(self.title)
        self.textColour = self.db.textColour
        self.center = center
        self.Labels = {}

    def drawFrame(self):
        if self.center:
            pygame.draw.lines(RenderMain.screen, self.db.textColour, False,
                                   [[self.x1 + self.dx/2 - self.textSize[0]/2 - 5, self.y1], [self.x1, self.y1], [self.x1, self.y2], [self.x2, self.y2],
                                    [self.x2, self.y1], [self.x1 + self.dx/2 + self.textSize[0]/2 + 5, self.y1]], 1)
            RenderMain.screen.blit(self.Title, (self.x1 + self.dx/2 - self.textSize[0]/2 , self.y1 - 10))
        else:
            pygame.draw.lines(RenderMain.screen, self.db.textColour, False,
                                   [[self.x1 + 25, self.y1], [self.x1, self.y1], [self.x1, self.y2], [self.x2, self.y2],
                                    [self.x2, self.y1], [self.x1 + 35 + self.textSize[0], self.y1]], 1)
            RenderMain.screen.blit(self.Title, (self.x1 + 30, self.y1 - 10))

        for i in range(0, len(self.Labels)):
            if self.db.RenderLabel[self.Labels[i][2]]:
                self.Labels[i][1].drawLabel(self.db.get(self.Labels[i][0]))

    def reinitFrame(self, title):
        self.title = title
        self.Title = fontSmall.render(self.title, True, self.db.textColour)
        self.textSize = fontSmall.size(self.title)

    def setTextColour(self, colour):
        self.textColour = colour
        self.Title = fontSmall.render(self.title, True, self.textColour)

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

        RenderMain.screen.blit(self.LabLabel, (self.x - self.width / 2, self.y))
        RenderMain.screen.blit(self.ValLabel, (self.x + self.width / 2 - self.ValSize[0], self.y - 36))


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
                pygame.draw.rect(RenderMain.screen, green, [self.x - 3, self.y, self.width + 6, 8 + self.ValSize[1]], 0)
            elif self.db.Alarm[self.alarmTag] == 2:
                pygame.draw.rect(RenderMain.screen, orange, [self.x - 3, self.y, self.width + 6, 8 + self.ValSize[1]], 0)
            elif self.db.Alarm[self.alarmTag] == 3:
                pygame.draw.rect(RenderMain.screen, red, [self.x - 3, self.y, self.width + 6, 8 + self.ValSize[1]], 0)

        RenderMain.screen.blit(self.LabLabel, (self.x, self.y))
        RenderMain.screen.blit(self.ValLabel, (self.x + self.width - self.ValSize[0], self.y + 15))


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
                pygame.draw.rect(RenderMain.screen, green, [self.x - 3, self.y + 41, self.width + 6, 135], 0)
            elif self.db.Alarm[self.alarmTag] == 2:
                pygame.draw.rect(RenderMain.screen, orange, [self.x - 3, self.y + 41, self.width + 6, 135], 0)
            elif self.db.Alarm[self.alarmTag] == 3:
                pygame.draw.rect(RenderMain.screen, red, [self.x - 3, self.y + 41, self.width + 6, 135], 0)
        if self.center:
            RenderMain.screen.blit(self.ValLabel, (self.x + self.width/2 - self.ValSize[0]/2, self.y + 15))
        else:
            RenderMain.screen.blit(self.ValLabel, (self.x + self.width - self.ValSize[0], self.y + 15))

