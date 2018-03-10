import pygame
# import time
# import irsdk
# import iDDUhelper
import iRefresh
import threading
# clock = pygame.time.Clock()
import render
import iDDUcalc

listLap = ['LapBestLapTime', 'LapLastLapTime', 'LapDeltaToSessionBestLap', 'dcFuelMixture', 'dcThrottleShape',
           'dcTractionControl', 'dcTractionControl2', 'dcTractionControlToggle', 'dcABS', 'dcBrakeBias', 'FuelLevel',
           'Lap', 'IsInGarage', 'LapDistPct', 'OnPitRoad', 'PlayerCarClassPosition', 'PlayerCarPosition', 'RaceLaps',
           'SessionLapsRemain', 'SessionTimeRemain', 'SessionTime', 'SessionFlags', 'OnPitRoad', 'SessionNum',
           'IsOnTrack', 'Gear', 'Speed', 'LapDistPct']

init_data = {'LapBestLapTime': 0, 'LapLastLapTime': 0, 'LapDeltaToSessionBestLap': 0, 'dcFuelMixture': 0,
             'dcThrottleShape': 0, 'dcTractionControl': 0, 'dcTractionControl2': 0, 'dcTractionControlToggle': 0,
             'dcABS': 0, 'dcBrakeBias': 0, 'FuelLevel': 0, 'Lap': 123, 'IsInGarage': 0, 'LapDistPct': 0, 'OnPitRoad': 0,
             'PlayerCarClassPosition': 0, 'PlayerCarPosition': 0, 'RaceLaps': 0, 'SessionLapsRemain': 0,
             'SessionTimeRemain': 0, 'SessionTime': 0, 'SessionFlags': 0, 'SessionNum': 0, 'IsOnTrack': 0, 'Gear': 0,
             'Speed': 0}

iRUpdate = iRefresh.IRUpdate(listLap, init_data)
iCalc = iDDUcalc.IDDUCalc()
iRRender = render.RenderScreen()

while 1:
    iRData = iRUpdate.update()
    calcData = iCalc.calc(iRData)
    iRRender.render(iRData, calcData)
