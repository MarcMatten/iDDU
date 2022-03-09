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

from libs.getGearRatios import getGearRatios


def getShiftRPM(dirPath=str, TelemPath=str, MotecProjectPath=str):
    tReaction = 0.3  # TODO: as input to tune from GUI
    tLEDs = np.array([1, 0.5, 0])
    BUseMaxRPM = True

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
                                               channels=['gLat', 'rThrottle', 'rBrake', 'SteeringWheelAngle', 'gLong', 'Gear', 'RPM', 'EngineWarnings', 'SessionTime', 'vWheelRL', 'vWheelRR', 'vCarX'],
                                               channelMapPath=dirPath+'/functionalities/libs/iRacingChannelMap.csv')

    # If car file exists, load it. Otherwise, create new car object TODO: whole section is duplicate with rollOut
    car = Car(Driver=d['DriverInfo']['Drivers'][d['DriverInfo']['DriverCarIdx']])
    carFilePath = dirPath + '/data/car/' + car.name + '.json'

    d['gLong'] = filters.movingAverage(d['gLong'], 5)
    d['vCar'] = filters.movingAverage(d['vCar'], 5)
    d['RPM'] = filters.movingAverage(d['RPM'], 5)

    if car.name + '.json' in importExport.getFiles(dirPath + '/data/car', 'json'):
        car.load(carFilePath)
    else:
        tempDB = RTDB.RTDB()
        tempDB.dir = dirPath
        tempDB.initialise(d, False, False)
        UserShiftRPM = [0] * 7
        UserShiftFlag = [False] * 7

        for k in range(0, np.max(d['Gear'])-1):
            UserShiftRPM[k] = d['DriverInfo']['DriverCarSLShiftRPM']
            UserShiftFlag[k] = True

        tempDB.initialise({'UserShiftRPM': UserShiftRPM, 'UpshiftStrategy': 5, 'UserShiftFlag': UserShiftFlag}, False, False)

        car.createCar(tempDB, var_headers_names=var_headers_names)

        del tempDB

    print(time.strftime("%H:%M:%S", time.localtime()) + ':\tStarting Upshift calculation for: ' + car.name)

    # TODO: check it telemetry file is suitable

    # create results directory
    resultsDirPath = dirPath + "/data/shiftTone/" + ibtPath.split('/')[-1].split('.ibt')[0]
    if not os.path.exists(resultsDirPath):
        os.mkdir(resultsDirPath)
    if d['WeekendInfo']['Category'] == 'Oval':
        d['BStraightLine'] = np.logical_and((d['gLat']) < 1, np.abs(d['SteeringWheelAngle']) < 0.05, np.abs(d['vCar']) > 10)
    else:
        d['BStraightLine'] = np.logical_and((d['gLat']) < 1, np.abs(d['SteeringWheelAngle']) < 0.03, np.abs(d['vCar']) > 10)
    d['BWOT'] = np.logical_and((d['rThrottle']) == 1, np.abs(d['rBrake']) == 0)
    d['BCoasting'] = np.logical_and((d['rThrottle']) == 0, np.abs(d['rBrake']) == 0)
    d['BShiftRPM'] = np.logical_and(d['BStraightLine'], d['BWOT'])
    if d['WeekendInfo']['Category'] == 'Oval':
        d['BShiftRPM'] = np.logical_and(d['BShiftRPM'], d['gLong'] > 0.01)
        minRPM = 0.5 * car.iRShiftRPM[0]
    else:
        d['BShiftRPM'] = np.logical_and(d['BShiftRPM'], d['gLong'] > 0.3)
        minRPM = 0.7 * car.iRShiftRPM[0]
    d['BShiftRPM'] = np.logical_and(d['BShiftRPM'], d['RPM'] > minRPM)

    plt.ioff()
    plt.figure()  # TODO: make plot nice (legend but only for black and red dots)
    plt.grid()
    cmap = plt.get_cmap("tab10")
    # plt.scatter(d['vCar'][d['BShiftRPM']], d['gLong'][d['BShiftRPM']])
    plt.xlabel('vCar [m/s]')
    plt.ylabel('gLong [m/s²]')
    plt.xlim(0, np.max(d['vCar'][d['BShiftRPM']]) + 5)
    plt.ylim(0, np.max(d['gLong'][d['BShiftRPM']]) + 1)

    d['BGear'] = list()
    d['BRPMRange'] = list()
    gLongPolyFit = list()
    RPMPolyFit = list()
    vCarMin = list()
    vCarMax = list()
    maxRPM = list()
    vCarMaxgLong = list()

    NGear = np.linspace(1, np.max(d['Gear']), np.max(d['Gear']))

    for i in range(0, np.max(d['Gear'])):

        d['BGear'].append(np.logical_and(d['BShiftRPM'], d['Gear'] == NGear[i]))

        maxRPM.append(np.max(d['RPM'][d['BGear'][i]]))
        vCarTemp = d['vCar'][d['BGear'][i]]
        vCarMaxgLong.append(vCarTemp[np.argmax(d['gLong'][d['BGear'][i]])])
        vCarMaxGear = np.max(d['vCar'][d['BGear'][i]])

        tempBRPMRange = np.logical_and(d['BGear'][i], d['RPM'] > minRPM)
        tempBRPMRange = np.logical_and(tempBRPMRange, d['RPM'] < maxRPM[i])
        tempBRPMRange = np.logical_and(tempBRPMRange, d['vCar'] > vCarMaxgLong[i])
        tempBRPMRange = np.logical_and(tempBRPMRange, d['vCar'] < vCarMaxGear - 1)
        tempBRPMRange = np.logical_and(tempBRPMRange, filters.movingAverage(d['EngineWarnings'], 6) < 1)

        d['BRPMRange'].append(tempBRPMRange)

        PolyFitTemp, temp = scipy.optimize.curve_fit(maths.polyVal, d['vCar'][d['BRPMRange'][i]], d['gLong'][d['BRPMRange'][i]], [0, 0, 0, 0])
        gLongPolyFit.append(PolyFitTemp)

        PolyFitTemp, temp = scipy.optimize.curve_fit(maths.polyVal, d['vCar'][d['BRPMRange'][i]], d['RPM'][d['BRPMRange'][i]], [0, 0, 0])
        RPMPolyFit.append(PolyFitTemp)

        vCarMin.append(np.min(d['vCar'][d['BRPMRange'][i]]))
        vCarMax.append(np.max(d['vCar'][d['BRPMRange'][i]]))
        vCar = np.linspace(vCarMin[i] - 5, vCarMax[i] + 5, 100)

        plt.scatter(d['vCar'][d['BRPMRange'][i]], d['gLong'][d['BRPMRange'][i]], marker='.', zorder=1, color=cmap(i))
        plt.plot(vCar, maths.polyVal(vCar, gLongPolyFit[i][0], gLongPolyFit[i][1], gLongPolyFit[i][2], gLongPolyFit[i][3]), label='Gear {}'.format(i + 1), zorder=2, color=cmap(i + 2))

    vCarShiftOptimal = []
    vCarShiftTarget = []
    vCarShiftLEDS = []

    for k in range(0, np.max(d['Gear']) - 1):
        f1 = lambda x: maths.polyVal(x, gLongPolyFit[k][0], gLongPolyFit[k][1], gLongPolyFit[k][2], gLongPolyFit[k][3])
        f2 = lambda x: maths.polyVal(x, gLongPolyFit[k + 1][0], gLongPolyFit[k + 1][1], gLongPolyFit[k + 1][2], gLongPolyFit[k + 1][3])

        result = maths.findIntersection(f1, f2, vCarMax[k])

        if BUseMaxRPM:
            vCarShiftOptimal.append(vCarMax[k])
        else:
            vCarShiftOptimal.append(np.min([result[0], vCarMax[k]]))

        vCarShiftTarget.append(vCarShiftOptimal[k] - tReaction * maths.polyVal(vCarShiftOptimal[k], gLongPolyFit[k][0], gLongPolyFit[k][1], gLongPolyFit[k][2], gLongPolyFit[k][3]))
        vCarShiftLEDS.append(vCarShiftOptimal[k] - (tLEDs + tReaction) * maths.polyVal(vCarShiftOptimal[k], gLongPolyFit[k][0], gLongPolyFit[k][1], gLongPolyFit[k][2], gLongPolyFit[k][3]))

        plt.scatter(vCarShiftOptimal[k], f1(vCarShiftOptimal[k]), marker='o', color='black', zorder=99)
        plt.scatter(vCarShiftTarget[k], f1(vCarShiftTarget[k]), marker='o', color='red', zorder=99)

    plt.legend()
    plt.savefig(resultsDirPath + '/gLong_vs_vCar.png', dpi=300, orientation='landscape', progressive=True)

    plt.figure()  # TODO: make plot nice (legend but only for black and red dots)
    plt.scatter(d['vCar'][d['BShiftRPM']], d['RPM'][d['BShiftRPM']], marker=".", zorder=0, color='k')
    plt.grid()
    plt.xlabel('vCar [m/s]')
    plt.ylabel('nMotor [RPM]')
    plt.xlim(0, np.max(d['vCar'][d['BShiftRPM']]) + 5)
    plt.ylim(0, np.max(d['RPM'][d['BShiftRPM']]) + 500)

    nMotorShiftOptimal = []
    nMotorShiftTarget = []
    nMotorShiftLEDs = []

    for i in range(0, np.max(d['Gear'])):
        vCar = np.linspace(vCarMin[i] - 10, vCarMax[i] + 10, 100)
        plt.plot(vCar, maths.polyVal(vCar, RPMPolyFit[i][0], RPMPolyFit[i][1], RPMPolyFit[i][2]), label='Gear {}'.format(i + 1), zorder=1)

        if i < np.max(d['Gear']) - 1:
            nMotorShiftOptimal.append(maths.polyVal(vCarShiftOptimal[i], RPMPolyFit[i][0], RPMPolyFit[i][1], RPMPolyFit[i][2]))
            nMotorShiftTarget.append(maths.polyVal(vCarShiftTarget[i], RPMPolyFit[i][0], RPMPolyFit[i][1], RPMPolyFit[i][2]))
            nMotorShiftLEDs.append(maths.polyVal(vCarShiftLEDS[i], RPMPolyFit[i][0], RPMPolyFit[i][1], RPMPolyFit[i][2]))
            plt.scatter(vCarShiftOptimal[i], nMotorShiftOptimal[i], marker='o', color='black', zorder=99)
            plt.scatter(vCarShiftTarget[i], nMotorShiftTarget[i], marker='o', color='red', zorder=99)

    plt.legend()
    plt.savefig(resultsDirPath + '/RPM_vs_vCar.png', dpi=300, orientation='landscape', progressive=True)

    rGearRatios = getGearRatios(d, resultsDirPath)

    # save so car file
    car.setShiftRPM(nMotorShiftOptimal, vCarShiftOptimal, nMotorShiftTarget, vCarShiftTarget, NGear[0:-1], d['DriverInfo']['DriverSetupName'], d['CarSetup'], int(max(NGear)), nMotorShiftLEDs)
    car.setGearRatios(rGearRatios)
    car.save(carFilePath)
    car.MotecXMLexport(dirPath, MotecProjectPath)

    print(time.strftime("%H:%M:%S", time.localtime()) + ':\tCompleted Upshift calculation!')


if __name__ == "__main__":
    getShiftRPM('C:/Users/marc/Documents/iDDU', 'C:/Users/marc/Documents/iRacing/telemetry', 'C:/Users/marc/Documents/MoTeC/i2/Workspaces/Circuit 1')
