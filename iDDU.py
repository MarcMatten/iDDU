import pygame
import time
import irsdk
import iDDUhelper

##### data and list initialisation #####################################################################################
listLap = ['LapBestLapTime','LapLastLapTime','LapDeltaToSessionBestLap','dcFuelMixture','dcThrottleShape',
           'dcTractionControl','dcTractionControl2','dcTractionControlToggle','dcABS','dcBrakeBias','FuelLevel','Lap',
           'IsInGarage','LapDistPct', 'OnPitRoad', 'PlayerCarClassPosition','PlayerCarPosition', 'RaceLaps',
           'SessionLapsRemain', 'SessionTimeRemain', 'SessionTime', 'SessionFlags','OnPitRoad']

listStart = ['SessionLapsRemain', 'IsOnTrack', 'SessionTimeRemain', 'IsInGarage', 'OnPitRoad', 'PlayerCarClassPosition',
             'PlayerCarPosition', 'RaceLaps', 'SessionTime', 'Lap', 'SessionFlags']

data = {}
for i in range(0, len(listLap)):
    data.update({listLap[i]: ''})

data.update({'Lap': 0})
data.update({'StintLap': 0})
data.update({'oldLap': 0.1})
data.update({'FuelConsumption':  []})
data.update({'FuelLastCons':  0})
data.update({'LastFuelLevel':  0})
data.update({'OutLap':  True})
data.update({'SessionFlags':  0})
data.update({'oldSessionFlags':  0})
data.update({'LapsToGo':  21})
data.update({'SessionInfo':  {'Sessions': [{'SessionType': 'Offline Testing', 'SessionTime': 'unlimited',
                                             'SessionLaps': 'unlimited'}] }})

FuelConsumptionStr = ''
FuelLapStr = ''
fuelAddStr = '-'
FlagCallTime = 0
FlagException = False
FlagExceptionVal = 0
Alarm = []
RaceLaps = 21

##### pygame initialisation ############################################################################################
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
yellow = (255, 255, 0)
orange = (255, 133, 13)
grey = (141, 141, 141)
colour = black

resolution = (800, 480)
fullscreen = False
pygame.init()
#os.environ['SDL_VIDEO_WINDOW_POS'] = '0, 0'
pygame.display.set_caption('iDDU')
screen = pygame.display.set_mode(resolution)
clock = pygame.time.Clock()
done = False
SessionInfo = False
SessionNum = 0
init = True
onPitRoad = True

# load background imaged
checkered = pygame.image.load("checkered.gif")
dsq = pygame.image.load("dsq.gif")
debry = pygame.image.load("debry.gif")
pitClosed = pygame.image.load("pitClosed.gif")
warning = pygame.image.load("warning.gif")

# font definition
fontTiny = pygame.font.SysFont("Khmer UI", 12) # Khmer UI Calibri
fontSmall = pygame.font.SysFont("Khmer UI", 20)
fontMedium = pygame.font.SysFont("Khmer UI", 40)
fontLarge = pygame.font.SysFont("Khmer UI", 60)
fontHuge = pygame.font.SysFont("Khmer UI", 480)

# frame labels
TimingLabel = fontSmall.render(' Timing ', True, white, black)
FuelLabel = fontSmall.render(' Fuel ', True, white, black)
SessionLabel = fontSmall.render(' Session Info ', True, white, black)
ControlLabel = fontSmall.render(' Control ', True, white, black)

# Labels to display
# Timing
BestLapLabel = fontSmall.render('Best', True, white)
LastLapLabel = fontSmall.render('Last', True, white)
DeltaLapLabel = fontSmall.render('DBest', True, white)
# SessionInfo
ClockLabel = fontTiny.render('Clock', True, white)
RemTimeLabel = fontSmall.render('Rem. Time', True, white)
ElTimeLabel = fontSmall.render('Time', True, white)
RemLapLabel = fontSmall.render('Rem. Laps', True, white)
LapLabel = fontSmall.render('Lap', True, white)
# Fuel
dcTractionControlLabel = fontSmall.render('TC1', True, white)
dcTractionControl2Label = fontSmall.render('TC2', True, white)
dcBrakeBiasLabel = fontSmall.render('BBias', True, white)
dcFuelMixtureLabel = fontSmall.render('Mix', True, white)
dcThrottleShapeLabel = fontSmall.render('Map', True, white)
dcABSLabel = fontSmall.render('ABS', True, white)
# Control
FuelLevelLabel = fontSmall.render('Fuel', True, white)
FuelConsLabel = fontSmall.render('Avg.', True, white)
FuelLastConsLabel = fontSmall.render('Last', True, white)
FuelLapsLabel = fontSmall.render('Laps', True, white)
FuelAddLabel = fontSmall.render('Add', True, white)

SCLabel = fontHuge.render('SC', True, white)


##### iRacing loop #####################################################################################################
ir = irsdk.IRSDK()

while not done:
    # do permanently
    ClockValue = time.strftime("%H:%M:%S", time.localtime())

    if ir.startup():
        # do if sim is running before updating data --------------------------------------------------------------------
        if not SessionInfo:
            data['SessionInfo'] = ir['SessionInfo']
            SessionInfo = True
            SessionNum = len(data['SessionInfo']['Sessions'])-1
            data['DriverCarFuelMaxLtr'] = ir['DriverInfo']['DriverCarFuelMaxLtr']

        if ir['IsOnTrack']:
            # do if car is on track ------------------------------------------------------------------------------------

            data.update(iDDUhelper.getData(ir, listLap))
            Alarm = []

            if init: # do when getting into the car
                init = False
                data['OutLap'] = True
                data['LastFuelLevel'] = data['FuelLevel']
                data['FuelConsumption'] = []
                ir.pit_command(7)


            if data['OnPitRoad']:
                onPitRoad = True
            elif (not data['OnPitRoad']) and onPitRoad == True: # pit exit
                onPitRoad = False
                data['OutLap'] = True

            # check if new lap
            if data['Lap'] > data['oldLap']:
                newLap = True
                data['StintLap'] = data['StintLap'] + 1
                data['oldLap'] = data['Lap']
                data['LapsToGo'] = RaceLaps - data['Lap']

                data['FuelLastCons'] = data['LastFuelLevel'] - data['FuelLevel']

                if (not data['OutLap']) and (not onPitRoad):
                    data['FuelConsumption'].extend([data['FuelLastCons']])
                else:
                    data['OutLap'] = False

                data['LastFuelLevel'] = data['FuelLevel']

            else:
                newLap = False

            # fuel consumption -----------------------------------------------------------------------------------------
            if len(data['FuelConsumption']) >= 1:
                avg = sum(data['FuelConsumption']) / len(data['FuelConsumption'])
                FuelConsumptionStr = iDDUhelper.roundedStr2(avg)
                LapRem = data['FuelLevel'] / avg
                if LapRem < 3:
                    Alarm.extend([3])
                if LapRem < 1:
                    Alarm.extend([4])
                FuelLapStr = iDDUhelper.roundedStr1(LapRem)
                if newLap and not onPitRoad:
                    fuelNeed = avg * data['LapsToGo']
                    fuelAdd = min(max(fuelNeed - data['FuelLevel'] + avg, 0),data['DriverCarFuelMaxLtr'])
                    fuelAddStr = iDDUhelper.roundedStr1(fuelAdd)
                    ir.pit_command(2, round(fuelAdd+0.5+1e-10))
                #else:
                    #   fuelAddStr = '-'
            else:
                FuelConsumptionStr = '-'
                FuelLapStr = '-'
                fuelAddStr = '-'

            # alarm
            if data['dcTractionControlToggle']:
                Alarm.extend([1])

            if type(data['FuelLevel']) is float:
                if data['FuelLevel'] <= 5:
                    Alarm.extend([2])
        else:
            # do if car is not on track but don't do if car is on track ------------------------------------------------
            data.update(iDDUhelper.getData(ir, listStart))
            init = True

        # do if sim is running after updating data ---------------------------------------------------------------------
        RemLapValue = str(data['SessionLapsRemain'])
        RemTimeValue = iDDUhelper.convertTimeHHMMSS(data['SessionTimeRemain'])

        if (not data['SessionFlags'] == data['oldSessionFlags']):
            FlagCallTime = data['SessionTime']
            Flags = str(("0x%x" % ir['SessionFlags'])[2:11])

            if Flags[0] == '8':#Flags[7] == '4' or Flags[0] == '1':
                colour = green
            if Flags[0] == '8':# or Flags[0] == '4'
                colour = red
            if Flags[7] == '8' or Flags[5] == '1' or Flags[4] == '4' or Flags[4] == '8': #  or Flags[0] == '2'
                colour = yellow
            if Flags[6] == '2':
                colour = blue
            if Flags[7] == '2':
                colour = white
                # set font color to black
            if Flags[7] == '1': # checkered
                FlagExceptionVal = 1
                FlagException = True
                # set font color to grey
            if Flags[2] == '1': # repair
                FlagException = True
                FlagExceptionVal = 2
                color = black
                # set Control Label Background Color to orange
            if Flags[4] == '4' or Flags[4] == '8': # SC
                FlagException = True
                color = yellow
                FlagExceptionVal = 3
            if Flags[3] == '1' or Flags[3] == '2' or Flags[3] == '5': # disqualified or Flags[3] == '4' 
                FlagException = True
                FlagExceptionVal = 4
                # set font color to grey
                # set Control Label Background Color to white
                FlagException = True
            if Flags[6] == '4': # debry
                FlagExceptionVal = 5
            if Flags[3] == '8' or Flags[3] == 'c': # warning
                FlagException = True
                FlagExceptionVal = 6
                # set Control Label Background Color to white
                # set font color to gray

            data['oldSessionFlags'] = data['SessionFlags']
        elif data['SessionTime'] > (FlagCallTime + 3):
            colour = black
            FlagException = False
    else:
        # do if sim is not running -------------------------------------------------------------------------------------
        RemLapValue = ''
        RemTimeValue = ''
        FuelConsumptionStr = ''
        if SessionInfo:
            SessionInfo = False
        colour = black

    # prepare strings to display
    # Timing
    BestLap = fontLarge.render(iDDUhelper.convertTimeMMSSsss(data['LapBestLapTime']), True, white)
    LastLap = fontLarge.render(iDDUhelper.convertTimeMMSSsss(data['LapLastLapTime']), True, white)
    DeltaBest = fontLarge.render(iDDUhelper.convertDelta(data['LapDeltaToSessionBestLap']), True, white)
    # Session Info
    RemTime = fontLarge.render(RemTimeValue, True, white)
    RemLap = fontLarge.render(RemLapValue, True, white)
    Lap = fontLarge.render(str(data['Lap']), True, white)
    Time = fontLarge.render(iDDUhelper.convertTimeHHMMSS(data['SessionTime']), True, white)
    Clock = fontSmall.render(ClockValue, True, white)
    # Control
    dcTractionControl = fontLarge.render(iDDUhelper.roundedStr0(data['dcTractionControl']), True, white)
    dcTractionControl2 = fontLarge.render(iDDUhelper.roundedStr0(data['dcTractionControl2']), True, white)
    dcBrakeBias = fontLarge.render(iDDUhelper.roundedStr2(data['dcBrakeBias']), True, white)
    dcFuelMixture = fontLarge.render(iDDUhelper.roundedStr0(data['dcFuelMixture']), True, white)
    dcThrottleShape = fontLarge.render(iDDUhelper.roundedStr0(data['dcThrottleShape']), True, white)
    dcABS = fontLarge.render(iDDUhelper.roundedStr0(data['dcABS']), True, white)
    # Fuel
    FuelLevel = fontLarge.render(iDDUhelper.roundedStr2(data['FuelLevel']), True, white)
    FuelCons = fontLarge.render(FuelConsumptionStr, True, white)
    FuelLastCons = fontLarge.render(iDDUhelper.roundedStr2(data['FuelLastCons']), True, white)
    FuelLap = fontLarge.render(FuelLapStr, True, white)
    FuelAdd = fontLarge.render(fuelAddStr, True, white)


##### events ###########################################################################################################
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            done = True
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            if fullscreen:
                pygame.display.set_mode(resolution)
                fullscreen = False
            else:
                pygame.display.set_mode(resolution, pygame.NOFRAME) # pygame.FULLSCREEN
                fullscreen = True

##### render screen ####################################################################################################

    screen.fill(colour)
    if FlagException:
        if FlagExceptionVal == 1:
            screen.blit(checkered, [0,0])
        elif FlagExceptionVal == 2:
            pygame.draw.circle(screen, orange, [400, 240], 185)
        elif FlagExceptionVal == 3:
            screen.blit(SCLabel, (130, -35))
        elif FlagExceptionVal == 4:
            screen.blit(dsq, [0,0])
        elif FlagExceptionVal == 5:
            screen.blit(debry, [0,0])
        elif FlagExceptionVal == 6:
            screen.blit(warning, [0,0])

    # alarms
    if len(Alarm) > 0:
        if [1 for i in Alarm if i in [1]]: # Traction Control
            pygame.draw.rect(screen, red, [413, 388, 250, 65])
        if [1 for i in Alarm if i in [2]]: # Fuel Level
            pygame.draw.rect(screen, red, [413, 32, 215, 65])
        if [1 for i in Alarm if i in [3]]: # Fuel Laps 1
            pygame.draw.rect(screen, orange, [413, 172, 155, 65])
        if [1 for i in Alarm if i in [4]]: # Fuel Laps 2
            pygame.draw.rect(screen, red, [413, 172, 155, 65])

    # define frames
    pygame.draw.rect(screen, white, [10, 10, 385, 240], 1)
    #pygame.draw.lines(screen, white, False, [[10, 10], [10, 250], [395, 250]], 1)
    screen.blit(TimingLabel, (40,0))
    pygame.draw.rect(screen, white, [405, 10, 385, 280], 1)
    screen.blit(FuelLabel, (435,0))
    pygame.draw.rect(screen, white, [10, 260 , 385, 210], 1)
    screen.blit(SessionLabel, (40, 250))
    pygame.draw.rect(screen, white, [405, 300, 385, 170], 1)
    screen.blit(ControlLabel, (435, 290))

    # frame input
    # Timing
    screen.blit(BestLapLabel, (30, 60))
    screen.blit(BestLap, (115, 30))
    screen.blit(LastLapLabel, (30, 130))
    screen.blit(LastLap, (115, 100))
    screen.blit(DeltaLapLabel, (30, 200))
    screen.blit(DeltaBest, (115, 170))
    # Session Info
    screen.blit(ClockLabel, (30, 450))
    screen.blit(Clock, (80, 442))
    if data['SessionInfo']['Sessions'][SessionNum]['SessionTime'] == 'unlimited':
        screen.blit(ElTimeLabel, (30, 310))
        screen.blit(Time, (150, 280))
    else:
        screen.blit(RemTimeLabel, (30, 310))
        screen.blit(RemTime, (150, 280))

    #if data['SessionInfo']['Sessions'][SessionNum]['SessionTime'] == 'unlimited' or data['SessionInfo']['Sessions'][SessionNum]['SessionTime'] > 10000:
    if data['SessionTimeRemain']:
        screen.blit(LapLabel, (30, 380))
        screen.blit(Lap, (150, 350))
    else:
        screen.blit(RemLapLabel, (30, 380))
        screen.blit(RemLap, (150, 350))
    # Control
    screen.blit(dcBrakeBiasLabel, (425, 350))
    screen.blit(dcBrakeBias, (505, 315))
    screen.blit(dcABSLabel, (665, 350))
    screen.blit(dcABS, (710, 315))
    screen.blit(dcTractionControlLabel, (425, 420))
    screen.blit(dcTractionControl, (470, 385))
    screen.blit(dcTractionControl2Label, (555, 420))
    screen.blit(dcTractionControl2, (600, 385))
    screen.blit(dcFuelMixtureLabel, (665, 420))
    screen.blit(dcFuelMixture, (710, 385))
    # Fuel
    screen.blit(FuelLevelLabel, (425, 60))
    screen.blit(FuelLevel, (505, 30))
    screen.blit(FuelConsLabel, (425, 130))
    screen.blit(FuelCons, (475, 100))
    screen.blit(FuelLastConsLabel, (605, 130))
    screen.blit(FuelLastCons, (660, 100))
    screen.blit(FuelLapsLabel, (425, 200))
    screen.blit(FuelLap, (475, 170))
    screen.blit(FuelAddLabel, (605, 200))
    screen.blit(FuelAdd, (660, 170))


##### render again at 30 Hz ############################################################################################
    pygame.display.flip()
    clock.tick(30)
