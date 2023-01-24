import numpy as np
import matplotlib.pyplot as plt


def getGearRatios(d, resultsDirPath):
    NGearMax = np.max(d['Gear'])
    rGearRatioList = [None] * (NGearMax + 1)
    vCarList = [None] * (NGearMax + 1)

    for i in range(0, NGearMax):
        vCarList[i+1] = [d['vCar'][d['BGear'][i]]]
        rGearRatioList[i+1] = [d['RPM'][d['BGear'][i]] / 60 * np.pi / ((d['vWheelRL'][d['BGear'][i]] + d['vWheelRR'][d['BGear'][i]]) / 2 / 0.3)]

    rGearRatios = [None] * (NGearMax + 1)
    plt.figure()  # TODO: make plot nice (legend but only for black and red dots)
    plt.grid()
    plt.xlabel('vCar [m/s]')
    plt.ylabel('rGearRatio [-]')
    for k in range(len(rGearRatioList)):
        if None is rGearRatioList[k]:
            rGearRatios[k] = None
        else:
            rGearRatios[k] = np.mean(rGearRatioList[k])
            plt.scatter(vCarList[k], rGearRatioList[k], zorder=90, label='Gear {}: {}'.format(k, rGearRatios[k]), marker=".")
            plt.plot([10, 100], [rGearRatios[k], rGearRatios[k]], zorder=95)

    plt.legend()
    plt.savefig(resultsDirPath + '/rGearRatio.png', dpi=300, orientation='landscape', progressive=True)

    return rGearRatios
