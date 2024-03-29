import time
import copy
import traceback
from libs import Track, Car
from libs.auxiliaries import importExport, importIBT, convertString, maths
from tkinter import filedialog
import numpy as np
import tkinter as tk
import os, sys
from libs.MyLogger import MyLogger


def setReferenceLap(dirPath: str, TelemPath: str, ibtPath: str = None, ibtFile: dict = None):

    myLogger = MyLogger()

    try:

        root = tk.Tk()
        root.withdraw()

        print(time.strftime("%H:%M:%S", time.localtime()) + ':\tImporting reference lap')

        if not ibtPath and not ibtFile:
            ibtPath = filedialog.askopenfilename(initialdir=TelemPath, title="Select IBT file",
                                             filetypes=(("IBT files", "*.ibt"), ("all files", "*.*")))

        if ibtPath == ('', '') and not ibtFile:
            print(time.strftime("%H:%M:%S", time.localtime()) + ':\t\tNo valid path to ibt file provided...aborting!')
            return

        if not ibtFile:
            d, _ = importIBT.importIBT(ibtPath,
                                       lap='f',
                                       channels=['zTrack', 'LapDistPct', 'rThrottle', 'rBrake', 'QFuel', 'SessionTime', 'VelocityX', 'VelocityY', 'Yaw', 'Gear', 'YawNorth'],
                                       channelMapPath=dirPath + '/libs/auxiliaries/iRacingChannelMap.csv')
        else:
            d = copy.deepcopy(ibtFile)

        if not d:
            print(time.strftime("%H:%M:%S", time.localtime()) + ':\t\tNo valid lap found...aborting!')
            return

        d['x'], d['y'] = maths.createTrack(d)

        # check for monotonic behaviour
        idxRmv = []
        if not maths.strictly_increasing(d['tLap']):
            idxRmv = np.argwhere(np.diff(d['tLap']) <= 0)
        if not maths.strictly_increasing(d['LapDistPct']):
            idxRmv = np.append(idxRmv, np.argwhere(np.diff(d['LapDistPct']) <= 0))

        if any(idxRmv):
            idxRmv = np.unique(idxRmv)
            d['tLap'] = np.delete(d['tLap'], idxRmv)
            d['LapDistPct'] = np.delete(d['LapDistPct'], idxRmv)
            d['x'] = np.delete(d['x'], idxRmv)
            d['y'] = np.delete(d['y'], idxRmv)


        # check if car available
        carList = importExport.getFiles(dirPath + '/data/car', 'json')
        carName = d['DriverInfo']['Drivers'][d['DriverInfo']['DriverCarIdx']]['CarScreenNameShort']
        carPath = d['DriverInfo']['Drivers'][d['DriverInfo']['DriverCarIdx']]['CarPath']

        # load or create car
        car = Car.Car(name=carName, carPath=carPath)
        if carName + '.json' in carList:
            car.load(dirPath + '/data/car/' + carName + '.json')
        else:
            car.createCar(d)
            car.save(dirPath)
            print(time.strftime("%H:%M:%S", time.localtime()) + ':\tCar has been successfully created')

        # create track
        TrackName = d['WeekendInfo']['TrackName']
        track = Track.Track(TrackName)
        aNorth = d['YawNorth'][0]
        track.createTrack(d['x'], d['y'], d['LapDistPct'] * 100, aNorth, float(d['WeekendInfo']['TrackLength'].split(' ')[0]) * 1000)
        track.setLapTime(carName, d['tLap'][-1])
        track.save(dirPath)

        print(time.strftime("%H:%M:%S", time.localtime()) + ':\t\tTrack {} has been successfully created.'.format(TrackName))
        print(time.strftime("%H:%M:%S", time.localtime()) + ':\t\tAdding reference lap time to car {}'.format(carName))

        # add lap time to car
        car.addLapTime(TrackName, d['tLap'], d['LapDistPct'] * 100, track.LapDistPct, d['VFuelLap'])
        car.save(dirPath)
        print(time.strftime("%H:%M:%S", time.localtime()) + ':\t\tReference lap time set successfully!')

        myLogger.info('Set reference lap for {} at {}: {} s'.format(carName, d['WeekendInfo']['TrackDisplayName'], convertString.convertTimeMMSSsss(d['tLap'][-1])))

    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        s = traceback.format_exception(exc_type, exc_value, exc_traceback, limit=2, chain=True)
        S = '\n'
        for i in s:
            S = S + i
        myLogger.error(S)



if __name__ == "__main__":
    setReferenceLap(dirPath='C:/Users/marc/Documents/iDDU', TelemPath='C:/Users/marc/Documents/iRacing/telemetry')