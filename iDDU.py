import pygame
import time
import irsdk
import time2str
import os


# list = ['LapBestLapTime','LapCurrentLapTime','LapDeltaToSessionBestLap','dcFuelMixture','dcThrottleShape',
#         'dcTractionControl','dcTractionControl2','dcTractionControlToggle','dcABS','dcBrakeBias','FuelLevel',
#         'SessionLapsRemain']



# Colour definition
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)

resolution = (800, 480)
fullscreen = False
oldLap = -1;

# initialisation
pygame.init()
#os.environ['SDL_VIDEO_WINDOW_POS'] = '0, 0'
pygame.display.set_caption('iDDU')
screen = pygame.display.set_mode(resolution)
clock = pygame.time.Clock()
done = False
outlap = True
StintLap = 0

FuelConsumption = []


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

#
BestLapValue = ' '
LastLapValue = ' '
RemLapValue = '45'
RemTimeValue = '23:45:46'
ClockValue = time.strftime("%H:%M:%S", time.localtime())
dcFuelMixtureValue = '1'
dcThrottleShapeValue = '2'
dcTractionControlValue = '13'
dcTractionControl2Value = '14'
dcTractionControlToggleValue = False
dcABSValue = '16'
dcBrakeBiasValue = '45.78'
FuelLevelValue = '45.78'
FuelConsValue = '14.78'

# Labels to display
BestLapLabel = fontSmall.render('Best', True, white)
LastLapLabel = fontSmall.render('Last', True, white)
DeltaLapLabel = fontSmall.render('Delta Best', True, white)
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

ir = irsdk.IRSDK()

# render data
while not done:
    if ir.startup() and ir['IsOnTrack']:
        if outlap:
            ZeroLap = ir['Lap']
            outlap = False
        BestLapValue = time2str.convertTimeMMSSsss(ir['LapBestLapTime'])
        LastLapValue = time2str.convertTimeMMSSsss(ir['LapLastLapTime'])
        DeltaLapValue = time2str.convertDelta(ir['LapDeltaToSessionBestLap'])
        dcFuelMixtureValue = str(ir['dcFuelMixture'])
        dcThrottleShapeValue = str(ir['dcThrottleShape'])
        dcTractionControlValue = str(ir['dcTractionControl'])
        dcTractionControl2Value = str(ir['dcTractionControl2'])
        dcTractionControlToggleValue = ir['dcTractionControlToggle']
        dcABSValue = str(ir['dcABS'])
        dcBrakeBiasValue = time2str.roundedStr2(ir['dcBrakeBias'])
        FuelLevelValue = time2str.roundedStr2(ir['FuelLevel'])
        Fuel = ir['FuelLevel']
        Lap = ir['Lap']
        StintLap = Lap - ZeroLap
    else:
        DeltaLapValue = ' '
        Lap = 0
        oldLap = -1
        Fuel = 0
        LastFuelLevel = 0
        Fuel = 0
        FuelConsumption = []
        outlap = True

    if ir.startup():
        RemLapValue = str(round(ir['SessionLapsRemain']))
        RemTimeValue = time2str.convertTimeHHMMSS(ir['SessionTimeRemain'])
    else:
        RemLapValue = ''
        RemTimeValue = ''

    if dcTractionControlValue == 'None':
        dcTractionControlValue = '-'

    if dcTractionControl2Value == 'None':
        dcTractionControl2Value = '-'

    ClockValue = time.strftime("%H:%M:%S", time.localtime())


    if Lap > oldLap:
        if StintLap > 1:
            FuelConsumption.extend([LastFuelLevel - Fuel])

        oldLap = Lap

        LastFuelLevel = Fuel



    if 'FuelConsumption' in locals():
        if len(FuelConsumption) >= 1:
            FuelConsumptionStr = time2str.roundedStr2(sum(FuelConsumption)/len(FuelConsumption))
        else:
            FuelConsumptionStr = '-'
    else:
        FuelConsumptionStr = '-'




    BestLap = fontLarge.render(BestLapValue, True, white)
    LastLap = fontLarge.render(LastLapValue, True, white)
    DeltaBest = fontLarge.render(DeltaLapValue, True, white)
    RemTime = fontLarge.render(RemTimeValue, True, white)
    RemLap = fontLarge.render(RemLapValue, True, white)
    Clock = fontSmall.render(ClockValue, True, white)
    dcTractionControl = fontLarge.render(dcTractionControlValue, True, white)
    dcTractionControl2 = fontLarge.render(dcTractionControl2Value, True, white)
    dcBrakeBias = fontLarge.render(dcBrakeBiasValue, True, white)
    dcFuelMixture = fontLarge.render(dcFuelMixtureValue, True, white)
    dcThrottleShape = fontLarge.render(dcThrottleShapeValue, True, white)
    dcABS = fontLarge.render(dcABSValue, True, white)
    FuelLevel = fontLarge.render(FuelLevelValue, True, white)
    FuelCons = fontLarge.render(FuelConsumptionStr, True, white)

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

    if dcTractionControlToggleValue:
        pygame.draw.rect(screen, red, [413, 288, 250, 65])

    if float(FuelLevelValue)<= 5:
        pygame.draw.rect(screen, red, [413, 32, 215, 65])

    # frame input
    screen.blit(BestLapLabel, (30, 60))
    screen.blit(BestLap, (115, 30))
    screen.blit(LastLapLabel, (30, 130))
    screen.blit(LastLap, (115, 100))
    screen.blit(DeltaLapLabel, (30, 200))
    screen.blit(DeltaBest, (185, 170))
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

    # render again at 10 Hz
    pygame.display.flip()
    clock.tick(30)
