import time
# import irsdk
import iDDUhelper
import pygame
import threading
import iRefresh
import csv
import math
import numpy as np
import os
import glob


class IDDUCalc(iRefresh.IRClass):
    def __init__(self):
        self.white = (255, 255, 255)
        self.red = (255, 0, 0)
        self.green = (0, 255, 0)
        self.blue = (0, 0, 255)
        self.yellow = (255, 255, 0)
        self.orange = (255, 133, 13)
        self.grey = (141, 141, 141)
        self.black = (0, 0, 0)
        # self.iRUpdate = iRUpdate
        self.data = {}

        self.data['done'] = False
        self.SessionInfo = False
        self.data['SessionNum'] = 0
        self.data['init'] = True
        self.data['onPitRoad'] = True

        self.data['Lap'] = 123
        self.data['StintLap'] = 0
        self.data['SessionTime'] = 0
        self.data['SessionNum'] = 0
        self.data['oldSessionNum'] = -1
        self.data['oldLap'] = 0.1
        self.data['FuelConsumption'] = []
        self.data['FuelLastCons'] = 0
        self.data['LastFuelLevel'] = 0
        self.data['OutLap'] = True
        self.data['SessionFlags'] = 0
        self.data['oldSessionlags'] = 0
        self.data['LapsToGo'] = 431
        self.data['SessionInfo'] = {
            'Sessions': [{'SessionType': 'Session', 'SessionTime': 'unlimited',
                          'SessionLaps': 5}]}
        self.data['SessionLapRemain'] = 32767

        self.data['FuelConsumptionStr'] = '5.34'
        self.data['RemLapValueStr'] = '10'
        self.data['FuelLapStr'] = '67.2'
        self.data['FuelAddStr'] = '23.2'
        self.data['FlagCallTime'] = 0
        self.data['FlagException'] = False
        self.data['FlagExceptionVal'] = 0
        self.data['Alarm'] = []
        self.data['RaceLaps'] = 431
        self.data['oldFuelAdd'] = 1
        self.data['GreenTime'] = 0
        self.data['SessionNum'] = 0
        self.data['RemTimeValue'] = 0
        self.data['init'] = True
        self.data['LabelSessionDisplay']=[1, 1, 1, 0, 1, 1]
        self.data['JokerLapsRequired'] = 0

        self.data['dist'] = []
        self.data['x'] = []
        self.data['y'] = []
        self.data['map'] = []

        self.createTrack = True

        self.VelocityY = []
        self.VelocityX = []
        self.Yaw = []
        self.YawNorth = []
        self.dist = []
        self.x = []
        self.y = []
        self.dx = []
        self.dy = []

        self.dir = cwd = os.getcwd()
        self.trackdir = self.dir + r"\track"

        self.trackList = []

        # get list of trackfiles
        os.chdir(self.trackdir)
        for file in glob.glob("*.csv"):
            self.trackList.append(file)
        os.chdir(self.dir)

        self.loadTrack('dummie_track')

    def calc(self, iRData):

        if iRData['startUp']:
            # do if sim is running before updating data --------------------------------------------------------------------
            # if not self.SessionInfo or self.data['oldSessionNum'] < self.data['SessionNum']:
            if self.data['oldSessionNum'] < self.data['SessionNum']:
                self.data['oldSessionNum'] = self.data['SessionNum']
                self.data['SessionInfo'] = self.ir['SessionInfo']
                self.SessionInfo = True
                self.data['DriverInfo'] = self.ir['DriverInfo']
                self.data['WeekendInfo'] = self.ir['WeekendInfo']
                self.data['DriverCarFuelMaxLtr'] = self.data['DriverInfo']['DriverCarFuelMaxLtr'] * \
                                                   self.data['DriverInfo']['DriverCarMaxFuelPct']
                if self.data['WeekendInfo']['TrackName']+'.csv' in  self.trackList:
                    self.loadTrack(self.data['WeekendInfo']['TrackName'])
                    self.createTrack = False
                else:
                    self.loadTrack('dummie_track')
                    self.createTrack = True


                if self.data['SessionInfo']['Sessions'][iRData['SessionNum']]['SessionLaps'] == 'unlimited':
                    self.data['LabelSessionDisplay'][4] = 0 # ToGo
                    if self.data['SessionInfo']['Sessions'][iRData['SessionNum']]['SessionTime'] == 'unlimited':
                        self.data['LabelSessionDisplay'][3] = 1 # Elapsed
                        self.data['LabelSessionDisplay'][2] = 0 # Remain
                    else:
                        self.data['LabelSessionDisplay'][2] = 1 # Remain
                        self.data['LabelSessionDisplay'][3] = 0 # Elapsed
                else:
                    self.data['LabelSessionDisplay'][4] = 1 # ToGo
                    if self.data['SessionInfo']['Sessions'][iRData['SessionNum']]['SessionTime'] == 'unlimited':
                        self.data['LabelSessionDisplay'][4] = 0 # ToGo
                        self.data['LabelSessionDisplay'][3] = 1  # Elapsed
                    else:
                        self.data['LabelSessionDisplay'][4] = 1 # ToGo
                        self.data['LabelSessionDisplay'][3] = 0  # Elapsed

                if self.data['WeekendInfo']['Category'] == 'DirtRoad':
                    self.data['LabelSessionDisplay'][5] = 1 # Joker
                else:
                    self.data['LabelSessionDisplay'][5] = 0 # Joker

                    # 'SessionTime': 'unlimited'
                    # 'SessionType': 'Offline Testing'
                    # 'SessionLaps': 'unlimited'

                # if self.data['SessionInfo']['Sessions'][iRData['SessionNum']['SessionType'] == 'Offline Testing' or self.data['SessionInfo']['Sessions'][iRData['SessionNum']['SessionType'] == 'Practice':
                #     self.data['LabelSessionDisplay'][5] = 1
                # else:
                #     self.data['LabelSessionDisplay'][5] = 0

            if iRData['IsOnTrack']:
                # do if car is on track ------------------------------------------------------------------------------------

                self.data['Alarm'] = []

                if self.data['init']:  # do when getting into the car
                    self.data['init'] = False
                    self.data['OutLap'] = True
                    self.data['LastFuelLevel'] = iRData['FuelLevel']
                    self.data['FuelConsumption'] = []
                    if self.data['WeekendInfo']['Category'] == 'Rally Cross':
                        self.data['JokerLapsRequired'] = self.data['WeekendInfo']['WeekendOptions']['NumJokerLaps']

                    self.ir.pit_command(7)

                if iRData['OnPitRoad']:
                    self.data['onPitRoad'] = True
                elif (not iRData['OnPitRoad']) and self.data['onPitRoad'] == True:  # pit exit
                    self.data['onPitRoad'] = False
                    self.data['OutLap'] = True

                # check if new lap
                if iRData['Lap'] > self.data['oldLap']:
                    newLap = True
                    self.data['StintLap'] = self.data['StintLap'] + 1
                    self.data['oldLap'] = iRData['Lap']
                    self.data['LapsToGo'] = self.data['RaceLaps'] - iRData['Lap']  # at the end of the current lap

                    self.data['FuelLastCons'] = self.data['LastFuelLevel'] - iRData['FuelLevel']

                    if (not self.data['OutLap']) and (not self.data['onPitRoad']):
                        self.data['FuelConsumption'].extend([self.data['FuelLastCons']])
                    else:
                        self.data['OutLap'] = False

                    self.data['LastFuelLevel'] = iRData['FuelLevel']

                else:
                    newLap = False

                #print(self.data['StintLap'])

                if self.createTrack and self.data['StintLap'] == 2:
                    self.Yaw.append(self.ir['Yaw'])
                    self.YawNorth.append(self.ir['YawNorth'])
                    self.VelocityX.append(self.ir['VelocityX'])
                    self.VelocityY.append(self.ir['VelocityY'])
                    self.dist.append(iRData['LapDistPct']*100)

                    self.dx.append(math.cos(self.ir['Yaw'])*self.ir['VelocityX']*0.033 - math.sin(self.ir['Yaw'])*self.ir['VelocityY']*0.033)
                    self.dy.append(math.cos(self.ir['Yaw'])*self.ir['VelocityY']*0.033 + math.sin(self.ir['Yaw'])*self.ir['VelocityX']*0.033)



                if self.createTrack and self.data['StintLap'] == 3 and newLap:
                    tempx = np.cumsum(self.dx, dtype=float)
                    tempy = np.cumsum(self.dy, dtype=float)

                    dx = tempx[-1] - tempx[0]
                    dy = tempy[-1] - tempy[0]

                    self.x = np.cumsum(self.dx - dx/len(tempx), dtype=float)
                    self.y = np.cumsum(self.dy - dy/len(tempy), dtype=float)

                    width = max(self.x)-min(self.x)
                    height = max(self.y)-min(self.y)

                    scalingFactor = min(400/height,  720/width)

                    self.x = scalingFactor * self.x + (400 - min(scalingFactor * self.x) - 360)
                    self.y = scalingFactor * -self.y + (240 - min(scalingFactor * -self.y) - 200)
                    with open(r"track/" + self.data['WeekendInfo']['TrackName'] + ".csv", 'w', newline='') as f:
                        thewriter = csv.writer(f)
                        for l in range(0, len(self.dist)):
                            thewriter.writerow([self.dist[l], self.x[l], self.y[l]])

                    self.data['map'] = []
                    self.data['x'] = []
                    self.data['y'] = []
                    for i in range(0, len(self.x)):
                        self.data['map'].append([float(self.x[i]), float(self.y[i])])
                    self.data['dist'] = self.dist
                    self.data['x'] = self.x
                    self.data['y'] = self.y

                    self.createTrack =False



                        # fuel consumption -----------------------------------------------------------------------------------------
                if len(self.data['FuelConsumption']) >= 1:
                    avg = sum(self.data['FuelConsumption']) / len(self.data['FuelConsumption'])
                    self.data['FuelConsumptionStr'] = iDDUhelper.roundedStr2(avg)
                    LapRem = iRData['FuelLevel'] / avg
                    if LapRem < 3:
                        self.data['Alarm'].extend([3])
                    if LapRem < 1:
                        self.data['Alarm'].extend([4])
                        self.data['FuelLapStr'] = iDDUhelper.roundedStr1(LapRem)
                    if newLap and not self.data['onPitRoad']:
                        fuelNeed = avg * self.data['LapsToGo']
                        fuelAdd = min(max(fuelNeed - iRData['FuelLevel'] + avg, 0), self.data['DriverInfo']['DriverCarFuelMaxLtr'])
                        self.data['fuelAddStr'] = iDDUhelper.roundedStr1(fuelAdd)
                        if fuelAdd == 0:
                            self.ir.pit_command(2, 1)
                            self.ir.pit_command(11)
                            self.data['textColourFuelAdd'] = 'textColour'
                        else:
                            if not round(fuelAdd) == round(self.data['oldFuelAdd']):
                                self.ir.pit_command(2, round(fuelAdd + 0.5 + 1e-10))
                            if fuelAdd < self.data['DriverInfo']['DriverCarFuelMaxLtr'] - iRData['FuelLevel'] - avg:
                                self.data['textColourFuelAdd'] = 'green'
                            elif fuelAdd < self.data['DriverInfo']['DriverCarFuelMaxLtr'] - iRData['FuelLevel'] + avg:
                                self.data['textColourFuelAdd'] = 'orange'
                            else:
                                self.data['textColourFuelAdd'] = 'grey'
                        self.data['oldFuelAdd'] = fuelAdd
                else:
                    self.data['FuelConsumptionStr'] = '6.34'
                    self.data['FuelLapStr'] = '238.3'
                    self.data['fuelAddStr'] = '124.2'

                # alarm
                if iRData['dcTractionControlToggle']:
                    self.data['Alarm'].extend([1])

                if type(iRData['FuelLevel']) is float:
                    if iRData['FuelLevel'] <= 5:
                        self.data['Alarm'].extend([2])
            else:
                # do if car is not on track but don't do if car is on track ------------------------------------------------
                # data.update(iDDUhelper.getData(ir, listStart))
                self.init = True

            # do if sim is running after updating data ---------------------------------------------------------------------
            if not self.data['SessionInfo']['Sessions'][iRData['SessionNum']]['SessionLaps'] == 'unlimited':
                self.data['RemLapValue'] = max(min(self.data['SessionInfo']['Sessions'][iRData['SessionNum']]['SessionLaps'] - iRData['Lap'] + 1,
                                      self.data['SessionInfo']['Sessions'][iRData['SessionNum']]['SessionLaps']), 0)
                self.data['RemLapValueStr'] = str(self.data['RemLapValue'])
            else:
                self.data['RemLapValue'] = 0
                self.data['RemLapValueStr'] = '0'
            RemTimeValue = iDDUhelper.convertTimeHHMMSS(iRData['SessionTimeRemain'])

            # if (not data['SessionFlags'] == data['oldSessionFlags']):
            #     FlagCallTime = data['SessionTime']
            #     Flags = str(("0x%x" % ir['SessionFlags'])[2:11])
            #
            #     if Flags[0] == '8':  # Flags[7] == '4' or Flags[0] == '1':
            #         backgroundColour = green
            #         GreenTime = data['SessionTimeRemain']
            #     if Flags[7] == '1':  # or Flags[0] == '4'
            #         backgroundColour = red
            #     if Flags[7] == '8' or Flags[5] == '1' or Flags[4] == '4' or Flags[4] == '8':  # or Flags[0] == '2'
            #         backgroundColour = yellow
            #     if Flags[6] == '2':
            #         backgroundColour = blue
            #     if Flags[7] == '2':
            #         backgroundColour = white
            #         # set font color to black
            #     if Flags[7] == '1':  # checkered
            #         FlagExceptionVal = 1
            #         FlagException = True
            #         # set font color to grey
            #     if Flags[2] == '1':  # repair
            #         FlagException = True
            #         FlagExceptionVal = 2
            #         color = black
            #         # set Control Label Background Color to orange
            #     if Flags[4] == '4' or Flags[4] == '8':  # SC
            #         FlagException = True
            #         color = yellow
            #         FlagExceptionVal = 3
            #     if Flags[3] == '1' or Flags[3] == '2' or Flags[3] == '5':  # disqualified or Flags[3] == '4'
            #         FlagException = True
            #         FlagExceptionVal = 4
            #         # set font color to grey
            #         # set Control Label Background Color to white
            #         FlagException = True
            #     if Flags[6] == '4':  # debry
            #         FlagExceptionVal = 5
            #     if Flags[3] == '8' or Flags[3] == 'c':  # warning
            #         FlagException = True
            #         FlagExceptionVal = 6
            #         # set Control Label Background Color to white
            #         # set font color to gray
            #
            #     data['oldSessionFlags'] = data['SessionFlags']
            # elif data['SessionTime'] > (FlagCallTime + 3):
            #     backgroundColour = black
            #     FlagException = False
        else:
            # do if sim is not running -------------------------------------------------------------------------------------
            self.data['RemLapValueStr'] = '-'
            self.data['RemLapValue'] = '-'
            self.data['FuelConsumptionStr'] = '-'
            if self.SessionInfo:
                self.SessionInfo = False
                self.backgroundColour = self.black

        return self.data

    def loadTrack(self, name):

        # print( r"/track/" + name + ".csv")

        self.data['map'] = []
        self.data['x'] = []
        self.data['y'] = []
        self.data['dist'] = []

        with open(r"track/" + name + '.csv') as csv_file:
            csv_reader = csv.reader(csv_file)
            for line in csv_reader:
                self.data['dist'].append(float(line[0]))
                self.data['x'].append(float(line[1]))
                self.data['y'].append(float(line[2]))

                self.data['map'].append([float(line[1]), float(line[2])])
