import pygame
import time
import irsdk
import iDDUhelper

##### data and list initialisation #####################################################################################
listLap = ['LapBestLapTime','LapLastLapTime','LapDeltaToSessionBestLap','dcFuelMixture','dcThrottleShape',
           'dcTractionControl','dcTractionControl2','dcTractionControlToggle','dcABS','dcBrakeBias','FuelLevel','Lap',
           'IsInGarage','LapDistPct', 'OnPitRoad', 'PlayerCarClassPosition','PlayerCarPosition', 'RaceLaps',
           'SessionLapsRemain', 'SessionTimeRemain']

listStart = ['SessionLapsRemain', 'IsOnTrack', 'SessionTimeRemain', 'IsInGarage', 'OnPitRoad', 'PlayerCarClassPosition',
             'PlayerCarPosition', 'RaceLaps']

data = {}
for i in range(0, len(listLap)):
    data.update({listLap[i]: ''})

data.update({'Lap': 0})
data.update({'StintLap': 0})
data.update({'oldLap': 0.1})
data.update({'FuelConsumption':  []})
data.update({'LastFuelLevel':  []})
data.update({'OutLap':  True})

##### pygame initialisation #############################################################################################
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)

resolution = (800, 480)
fullscreen = False
pygame.init()
#os.environ['SDL_VIDEO_WINDOW_POS'] = '0, 0'
pygame.display.set_caption('iDDU')
screen = pygame.display.set_mode(resolution)
clock = pygame.time.Clock()
done = False

# font definition
fontTiny = pygame.font.SysFont("Khmer UI", 12) # Khmer UI Calibri
fontSmall = pygame.font.SysFont("Khmer UI", 20)
fontMedium = pygame.font.SysFont("Khmer UI", 40)
fontLarge = pygame.font.SysFont("Khmer UI", 60)

# frame labels
TimingLabel = fontSmall.render(' Timing ', True, white, black)
FuelLabel = fontSmall.render(' Fuel ', True, white, black)
SessionLabel = fontSmall.render(' Session Info ', True, white, black)
ControlLabel = fontSmall.render(' Control ', True, white, black)

# Labels to display
BestLapLabel = fontSmall.render('Best', True, white)
LastLapLabel = fontSmall.render('Last', True, white)
DeltaLapLabel = fontSmall.render('DBest', True, white)
ClockLabel = fontTiny.render('Clock', True, white)
RemTimeLabel = fontSmall.render('Rem. Time', True, white)
RemLapLabel = fontSmall.render('Rem. Laps', True, white)
dcTractionControlLabel = fontSmall.render('TC1', True, white)
dcTractionControl2Label = fontSmall.render('TC2', True, white)
dcBrakeBiasLabel = fontSmall.render('BBias', True, white)
FuelLevelLabel = fontSmall.render('Fuel', True, white)
FuelConsLabel = fontSmall.render('Cons.', True, white)
dcFuelMixtureLabel = fontSmall.render('Mix', True, white)
dcThrottleShapeLabel = fontSmall.render('Map', True, white)
dcABSLabel = fontSmall.render('ABS', True, white)


##### iRacing loop #####################################################################################################
ir = irsdk.IRSDK()

while not done:
    # do permanently
    ClockValue = time.strftime("%H:%M:%S", time.localtime())

    if ir.startup():
        # do if sim is running before updating data --------------------------------------------------------------------

        if ir['IsOnTrack']:
            # do if car is on track ------------------------------------------------------------------------------------
            data.update(iDDUhelper.getData(ir, listLap))

            # check if new lap
            if data['Lap'] > data['oldLap']:
                data['StintLap'] = data['StintLap'] + 1
                data['oldLap'] = data['Lap']

                if not data['OutLap']:
                    data['FuelConsumption'].extend([data['LastFuelLevel'] - data['FuelLevel']])
                else:
                    data['OutLap'] = False

                data['LastFuelLevel'] = data['FuelLevel']

            # fuel consumption -----------------------------------------------------------------------------------------
            if len(data['FuelConsumption']) >= 1:
                FuelConsumptionStr = iDDUhelper.roundedStr2(sum(data['FuelConsumption']) / len(data['FuelConsumption']))
            else:
                FuelConsumptionStr = '-'

            # warnings
            if data['dcTractionControlToggle']:
                pygame.draw.rect(screen, red, [413, 288, 250, 65])

            if type(data['FuelLevel']) is float:
                if data['FuelLevel'] <= 5:
                    pygame.draw.rect(screen, red, [413, 32, 215, 65])
        else:
            # do if car is not on track but don't do if car is on track ------------------------------------------------
            data.update(iDDUhelper.getData(ir, listStart))

        # do if sim is running after updating data ---------------------------------------------------------------------
        RemLapValue = str(data['SessionLapsRemain'])
        RemTimeValue = iDDUhelper.convertTimeHHMMSS(data['SessionTimeRemain'])
    else:
        # do if sim is not running -------------------------------------------------------------------------------------
        RemLapValue = ''
        RemTimeValue = ''
        FuelConsumptionStr = ''

    # prepare strings to display
    BestLap = fontLarge.render(iDDUhelper.convertTimeMMSSsss(data['LapBestLapTime']), True, white)
    LastLap = fontLarge.render(iDDUhelper.convertTimeMMSSsss(data['LapLastLapTime']), True, white)
    DeltaBest = fontLarge.render(iDDUhelper.convertDelta(data['LapDeltaToSessionBestLap']), True, white)
    RemTime = fontLarge.render(RemTimeValue, True, white)
    RemLap = fontLarge.render(RemLapValue, True, white)
    Clock = fontSmall.render(ClockValue, True, white)
    dcTractionControl = fontLarge.render(iDDUhelper.roundedStr0(data['dcTractionControl']), True, white)
    dcTractionControl2 = fontLarge.render(iDDUhelper.roundedStr0(data['dcTractionControl2']), True, white)
    dcBrakeBias = fontLarge.render(iDDUhelper.roundedStr2(data['dcBrakeBias']), True, white)
    dcFuelMixture = fontLarge.render(iDDUhelper.roundedStr0(data['dcFuelMixture']), True, white)
    dcThrottleShape = fontLarge.render(iDDUhelper.roundedStr0(data['dcThrottleShape']), True, white)
    dcABS = fontLarge.render(iDDUhelper.roundedStr0(data['dcABS']), True, white)
    FuelLevel = fontLarge.render(iDDUhelper.roundedStr2(data['FuelLevel']), True, white)
    FuelCons = fontLarge.render(FuelConsumptionStr, True, white)

##### events ###########################################################################################################
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            done = True
        if event.type == pygame.MOUSEBUTTONDOWN:
            if fullscreen:
                pygame.display.set_mode(resolution)
                fullscreen = False
            else:
                pygame.display.set_mode(resolution, pygame.NOFRAME) # pygame.FULLSCREEN
                fullscreen = True

##### render screen ####################################################################################################
    screen.fill(black)

    # define frames
    pygame.draw.rect(screen, white, [10, 10, 385, 240], 1)
    screen.blit(TimingLabel, (40,0))
    pygame.draw.rect(screen, white, [405, 10, 385, 180], 1)
    screen.blit(FuelLabel, (435,0))
    pygame.draw.rect(screen, white, [10, 260 , 385, 210], 1)
    screen.blit(SessionLabel, (40, 250))
    pygame.draw.rect(screen, white, [405, 200, 385, 270], 1)
    screen.blit(ControlLabel, (435, 190))

    # frame input
    screen.blit(BestLapLabel, (30, 60))
    screen.blit(BestLap, (115, 30))
    screen.blit(LastLapLabel, (30, 130))
    screen.blit(LastLap, (115, 100))
    screen.blit(DeltaLapLabel, (30, 200))
    screen.blit(DeltaBest, (115, 170))
    screen.blit(ClockLabel, (30, 450))
    screen.blit(Clock, (80, 442))
    screen.blit(RemTimeLabel, (30, 310))
    screen.blit(RemTime, (150, 280))
    screen.blit(RemLapLabel, (30, 380))
    screen.blit(RemLap, (150, 350))
    screen.blit(dcBrakeBiasLabel, (425, 250))
    screen.blit(dcBrakeBias, (505, 215))
    screen.blit(dcTractionControlLabel, (425, 320))
    screen.blit(dcTractionControl, (460, 285))
    screen.blit(dcTractionControl2Label, (555, 320))
    screen.blit(dcTractionControl2, (590, 285))
    screen.blit(FuelLevelLabel, (425, 60))
    screen.blit(FuelLevel, (505, 30))
    screen.blit(FuelConsLabel, (425, 130))
    screen.blit(FuelCons, (505, 100))

##### render again at 30 Hz ############################################################################################
    pygame.display.flip()
    clock.tick(30)
