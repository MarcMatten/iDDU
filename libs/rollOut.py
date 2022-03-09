import os
import time
import tkinter as tk
from tkinter import filedialog

import matplotlib.pyplot as plt
import numpy as np
import scipy.optimize
import scipy.signal

from libs.RTDB import RTDB
from libs.auxiliaries import importExport, filters, importIBT, maths
from libs.Car import Car
from datetime import datetime


def getRollOutCurve(dirPath, TelemPath, MotecProjectPath):
    root = tk.Tk()
    root.withdraw()

    # get ibt path
    ibtPath = filedialog.askopenfilename(initialdir=TelemPath, title="Select IBT file",
                                         filetypes=(("IBT files", "*.ibt"), ("all files", "*.*")))

    if not ibtPath:
        print(time.strftime("%H:%M:%S", time.localtime()) + ':\tNo valid path to ibt file provided...aborting!')
        return

    # imoport ibt file
    d, var_headers_names = importIBT.importIBT(ibtPath,
                                               channels=['zTrack', 'LapDistPct', 'rThrottle', 'rBrake', 'dmFuel', 'RPM', 'SteeringWheelAngle', 'Gear', 'gLong', 'gLat', 'QFuel', 'rClutch', 'vWheelRL', 'vWheelRR', 'vCarX'],
                                               channelMapPath=dirPath + '/functionalities/libs/iRacingChannelMap.csv')


    # If car file exists, load it. Otherwise, create new car object TODO: whole section is duplicate with getShiftRPM
    car = Car(Driver=d['DriverInfo']['Drivers'][d['DriverInfo']['DriverCarIdx']])
    carFilePath = dirPath + '/data/car/' + car.name + '.json'

    if car.name + '.json' in importExport.getFiles(dirPath + '/data/car', 'json'):
        car.load(carFilePath)
    else:
        tempDB = RTDB.RTDB()
        tempDB.initialise(d, False, False)
        UserShiftRPM = [0] * 7
        UserShiftFlag = [False] * 7

        for k in range(0, np.max(d['Gear']) - 1):
            UserShiftRPM[k] = d['DriverInfo']['DriverCarSLShiftRPM']
            UserShiftFlag[k] = True

        tempDB.initialise({'UserShiftRPM': UserShiftRPM, 'UpshiftStrategy': 5, 'UserShiftFlag': UserShiftFlag}, False, False)

        car.createCar(tempDB, var_headers_names=var_headers_names)

        del tempDB

    print(time.strftime("%H:%M:%S", time.localtime()) + ':\tStarting roll-out curve calculation for: ' + car.name)

    # TODO: check it telemetry file is suitable

    # create results directory
    now = datetime.now()
    dt_string = now.strftime("%Y-%m-%d_%H-%M-%S")
    resultsDirPath = dirPath + "/data/rollOut/" + dt_string + '_' + car.carPath + '_' + d['WeekendInfo']['TrackName']
    if not os.path.exists(resultsDirPath):
        os.mkdir(resultsDirPath)

    maxRPM = np.max(d['RPM'])

    d['BStraightLine'] = np.logical_and(np.abs(d['gLat']) < 1, np.abs(d['SteeringWheelAngle']) < 10)
    d['BStraightLine'] = np.logical_and(d['BStraightLine'], d['vCar'] > 10)
    d['BCoasting'] = np.logical_and(filters.movingAverage(d['rThrottle'], 25) == 0, filters.movingAverage(d['rBrake'], 25) == 0)
    d['BCoasting'] = np.logical_and(d['BCoasting'], d['RPM'] < (maxRPM - 250))
    d['BCoasting'] = np.logical_and(d['BCoasting'], d['BStraightLine'])
    d['BCoastingInGear'] = np.logical_and(d['BCoasting'], d['rClutch'] > 0.5)

    cmap = plt.get_cmap("tab10")

    plt.ioff()
    plt.figure()  # TODO: make plot nice
    plt.grid()
    plt.xlabel('vCar [m/s]')
    plt.ylabel('gLong [m/s²]')
    plt.xlim(0, np.max(d['vCar'][d['BCoasting']]) + 5)
    plt.ylim(np.min(d['gLong'][d['BCoasting']]) * 1.1, 0)

    NGearMax = np.max(d['Gear'])
    d['BGear'] = [None] * (NGearMax + 1)
    gLongPolyFit = [None] * (NGearMax + 1)
    QFuelPolyFit = [None] * (NGearMax + 1)
    vCar = np.linspace(0, np.max(d['vCar']) + 10, 100)
    NGear = np.linspace(0, np.max(d['Gear']), np.max(d['Gear'])+1, dtype=int)
    rGearRatioList = [None] * (NGearMax + 1)
    vCarList = [None] * (NGearMax + 1)

    for i in range(0, np.max(d['Gear'])+1):
        d['BGear'][i] = np.logical_and(d['BCoastingInGear'], d['Gear'] == NGear[i])

        if i == 0:
            gLongPolyFit[i] = np.array([0, 0, 0])
            QFuelPolyFit[i] = np.array([0, 0, 0])
        else:
            gLongPolyFit[i], _ = scipy.optimize.curve_fit(maths.polyVal, d['vCar'][d['BGear'][i]], d['gLong'][d['BGear'][i]], [0, 0, 0])
            QFuelPolyFit[i], _ = scipy.optimize.curve_fit(maths.polyVal, d['vCar'][d['BGear'][i]], d['QFuel'][d['BGear'][i]], [0, 0, 0])

            # Gear Ratio
            vCarList[i] = [d['vCar'][d['BGear'][i]]]
            rGearRatioList[i] = [d['RPM'][d['BGear'][i]] / 60 * np.pi / ((d['vWheelRL'][d['BGear'][i]] + d['vWheelRR'][d['BGear'][i]]) / 2 / 0.3)]

        # plot gLong vs vCar
        if i > 0:
            plt.scatter(d['vCar'][d['BGear'][i]], d['gLong'][d['BGear'][i]], color=cmap(i), marker=".")
            plt.plot(vCar, maths.polyVal(vCar, gLongPolyFit[i]), color=cmap(i + 1), label='Gear {}'.format(i))

    plt.legend()
    plt.savefig(resultsDirPath + '/roll_out_curve.png', dpi=300, orientation='landscape', progressive=True)

    plt.figure()  # TODO: make plot nice
    plt.grid()
    plt.xlabel('vCar [m/s]')
    plt.ylabel('QFuel [l/s]')
    plt.xlim(0, np.max(d['vCar'][d['BCoasting']]) + 5)
    plt.ylim(0, np.max(d['QFuel'][d['BCoasting']]) * 1.5)

    # plot QFuel vs vCar
    for i in range(0, NGearMax + 1):
        if i > 0 or any(d['BGear'][i]):
            plt.scatter(d['vCar'][d['BGear'][i]], d['QFuel'][d['BGear'][i]], color=cmap(i), marker=".")
            plt.plot(vCar, maths.polyVal(vCar, QFuelPolyFit[i]), color=cmap(i + 1), label='Gear {}'.format(i))

    plt.legend()
    plt.savefig(resultsDirPath + '/coasting_fuel_consumption.png', dpi=300, orientation='landscape', progressive=True)

    # Gear Ratios
    rGearRatios = [None] * (NGearMax + 1)
    plt.figure()  # TODO: make plot nice (legend but only for black and red dots)
    plt.grid()
    plt.xlabel('vCar [m/s]')
    plt.ylabel('rGearRatio [-]')
    for i in range(len(rGearRatioList)):
        if None is rGearRatioList[i]:
            rGearRatios[i] = None
        else:
            rGearRatios[i] = np.mean(rGearRatioList[i])
            plt.scatter(vCarList[i], rGearRatioList[i], zorder=99, label='Gear {}: {}'.format(i, rGearRatios[i]), marker=".")

    plt.legend()
    plt.savefig(resultsDirPath + '/rGearRatio.png', dpi=300, orientation='landscape', progressive=True)

    # save so car file
    car.setCoastingData(gLongPolyFit, QFuelPolyFit, NGear, d['DriverInfo']['DriverSetupName'], d['CarSetup'])
    car.setGearRatios(rGearRatios)
    car.save(carFilePath)
    car.MotecXMLexport(dirPath, MotecProjectPath)

    print(time.strftime("%H:%M:%S", time.localtime()) + ':\tCompleted roll-out calculation!')


if __name__ == "__main__":
    getRollOutCurve('C:/Users/marc/Documents/iDDU', 'C:/Users/marc/Documents/iRacing/telemetry', 'C:/Users/marc/Documents/MoTeC/i2/Workspaces/Circuit 1')