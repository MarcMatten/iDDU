# import all required packages
import threading
import time
import numpy as np
from libs import iDDUhelper


class raceLapsEstimation(threading.Thread):
    def __init__(self, RTDB, rate):
        threading.Thread.__init__(self)
        self.rate = rate
        self.db = RTDB
        self.snapshot = False
        print(self.db.timeStr + ': Starting raceLapsEstimation')

    def run(self):
        while 1:
            t = time.time()
            if self.db.BDDUexecuting:
                # if self.db.SessionInfo['Sessions'][self.db.SessionNum]['ResultsPositions'] and self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionType'] == 'Race' and self.db.TimeLimit and\
                #          not self.db.LapLimit:
                if self.db.SessionInfo['Sessions'][self.db.SessionNum]['ResultsPositions'] and self.db.BEnableRaceLapEstimation:
                    for i in range(0, len(self.db.SessionInfo['Sessions'][self.db.SessionNum]['ResultsPositions'])):
                        CarIdx_temp = self.db.SessionInfo['Sessions'][self.db.SessionNum]['ResultsPositions'][i]['CarIdx']
                        temp_CarIdxtLap = self.db.SessionInfo['Sessions'][self.db.SessionNum]['ResultsPositions'][i]['LastTime']
                        if temp_CarIdxtLap < 0:
                            temp_CarIdxtLap = float('nan')

                        self.db.CarIdxtLap[CarIdx_temp][self.db.SessionInfo['Sessions'][self.db.SessionNum]['ResultsPositions'][i]['LapsComplete'] - 1] = temp_CarIdxtLap

                        temp_pitstopsremain_np = self.db.PitStopsRequired - np.array(self.db.CarIdxPitStops[CarIdx_temp])
                        temp_pitstopsremain = temp_pitstopsremain_np.tolist()
                        NLapTimed = np.count_nonzero(~np.isnan(self.db.CarIdxtLap[CarIdx_temp]))

                        # summed up laptime - remove nan first
                        CarIdxtLap_cleaned = [x for x in self.db.CarIdxtLap[CarIdx_temp] if str(x) != 'nan']
                        CarIdxtLapSum = np.sum(CarIdxtLap_cleaned)

                        # use this to find winner
                        self.db.NLapRaceTime[CarIdx_temp] = (self.db.SessionLength - CarIdxtLapSum - (
                                iDDUhelper.maxList(temp_pitstopsremain,
                                                   0) * self.db.PitStopDelta)) / iDDUhelper.meanTol(
                            self.db.CarIdxtLap[CarIdx_temp], 0.03) + NLapTimed - self.db.SessionInfo['Sessions'][self.db.SessionNum]['ResultsPositions'][i]['Lap']  # use this to find winner

                        # if my value lower than the winners, then + 1 lap
                        self.db.TFinishPredicted[CarIdx_temp] = (np.ceil(
                            self.db.NLapRaceTime[CarIdx_temp]) - NLapTimed) * iDDUhelper.meanTol(self.db.CarIdxtLap[CarIdx_temp], 0.05) + CarIdxtLapSum + (
                                                                        iDDUhelper.maxList(temp_pitstopsremain, 0) * self.db.PitStopDelta)

                    self.db.WinnerCarIdx = self.db.NLapRaceTime.index(max(self.db.NLapRaceTime))

                    temp_pitstopsremain_np = self.db.PitStopsRequired - np.array(self.db.CarIdxPitStops[self.db.DriverCarIdx])
                    temp_pitstopsremain = temp_pitstopsremain_np.tolist()
                    CarIdxtLap_cleaned = [x for x in self.db.CarIdxtLap[self.db.DriverCarIdx] if str(x) != 'nan']
                    CarIdxtLapSum = np.sum(CarIdxtLap_cleaned)
                    NLapTimed = np.count_nonzero(~np.isnan(self.db.CarIdxtLap[self.db.DriverCarIdx]))

                    self.db.NLapWinnerRaceTime = (self.db.TFinishPredicted[self.db.WinnerCarIdx] - CarIdxtLapSum - (
                            iDDUhelper.maxList(temp_pitstopsremain, 0) * self.db.PitStopDelta)) / iDDUhelper.meanTol(self.db.CarIdxtLap[self.db.DriverCarIdx],
                                                                                                                     0.05) + NLapTimed  # use this to find winner

                    if self.db.WinnerCarIdx == self.db.DriverCarIdx:
                        self.db.NLapDriver = float(self.db.NLapRaceTime[self.db.DriverCarIdx])
                    else:
                        self.db.NLapDriver = np.float64(self.db.NLapWinnerRaceTime)

                    if self.db.NLapDriver > 1:
                        self.db.RaceLaps = int(self.db.NLapDriver + 1)
                    else:
                        self.db.RaceLaps = self.db.UserRaceLaps

                if self.db.NClasses > 1:
                    temp = 'SOF: ' + iDDUhelper.roundedStr0(self.db.SOF) + ' ('
                    keys = list(self.db.classStruct.keys())
                    for i in range(0, self.db.NClasses):
                        temp = temp + keys[i] + ': ' + iDDUhelper.roundedStr0(self.db.classStruct[keys[i]]['SOF'])
                        if i < self.db.NClasses - 1:
                            temp = temp + ', '
                    self.db.SOFstr = temp + ')'
                else:
                    self.db.SOFstr = 'SOF: ' + iDDUhelper.roundedStr0(self.db.SOF)

                if self.db.SessionInfo['Sessions'][self.db.SessionNum]['ResultsPositions']:
                    self.db.classStruct = {}

                    for i in range(0, len(self.db.DriverInfo['Drivers'])):
                        if not str(self.db.DriverInfo['Drivers'][i]['UserName']) == 'Pace Car':
                            if i == 0:
                                self.db.classStruct[str(self.db.DriverInfo['Drivers'][i]['CarClassShortName'])] = {'ID': self.db.DriverInfo['Drivers'][i]['CarClassID'],
                                                                                                                   'CarClassRelSpeed': self.db.DriverInfo['Drivers'][i]['CarClassRelSpeed'],
                                                                                                                   'CarClassColor': self.db.DriverInfo['Drivers'][i]['CarClassColor'],
                                                                                                                   'Drivers': [{'Name': self.db.DriverInfo['Drivers'][i]['UserName'],
                                                                                                                                'IRating': self.db.DriverInfo['Drivers'][i]['IRating']}]}
                            else:
                                if str(self.db.DriverInfo['Drivers'][i]['CarClassShortName']) in self.db.classStruct:
                                    self.db.classStruct[str(self.db.DriverInfo['Drivers'][i]['CarClassShortName'])]['Drivers'].append({'Name': self.db.DriverInfo['Drivers'][i]['UserName'],
                                                                                                                                       'IRating': self.db.DriverInfo['Drivers'][i]['IRating']})
                                else:
                                    self.db.classStruct[str(self.db.DriverInfo['Drivers'][i]['CarClassShortName'])] = {'ID': self.db.DriverInfo['Drivers'][i]['CarClassID'],
                                                                                                                       'CarClassRelSpeed': self.db.DriverInfo['Drivers'][i]['CarClassRelSpeed'],
                                                                                                                       'CarClassColor': self.db.DriverInfo['Drivers'][i]['CarClassColor'],
                                                                                                                       'Drivers': [{'Name': self.db.DriverInfo['Drivers'][i]['UserName'],
                                                                                                                                    'IRating': self.db.DriverInfo['Drivers'][i]['IRating']}]}

                    self.db.NClasses = len(self.db.classStruct)
                    classNames = list(self.db.classStruct.keys())
                    self.db.NDrivers = 0
                    tempSOF = 0
                    for j in range(0, self.db.NClasses):
                        self.db.classStruct[classNames[j]]['NDrivers'] = len(self.db.classStruct[classNames[j]]['Drivers'])
                        tempSOFClass = 0

                        for k in range(0, self.db.classStruct[classNames[j]]['NDrivers']):
                            tempSOFClass = tempSOFClass + self.db.classStruct[classNames[j]]['Drivers'][k]['IRating']

                        self.db.classStruct[classNames[j]]['SOF'] = tempSOFClass / self.db.classStruct[classNames[j]]['NDrivers']
                        self.db.NDrivers = self.db.NDrivers + self.db.classStruct[classNames[j]]['NDrivers']
                        tempSOF = tempSOF + tempSOFClass

                    self.db.SOF = tempSOF / self.db.NDrivers

                    self.db.SOFMyClass = self.db.classStruct[str(self.db.DriverInfo['Drivers'][self.db.DriverCarIdx]['CarClassShortName'])]['SOF']
                    self.db.NDriversMyClass = self.db.classStruct[str(self.db.DriverInfo['Drivers'][self.db.DriverCarIdx]['CarClassShortName'])]['NDrivers']

            self.db.tExecuteRaceLapsEstimation = time.time() - t

            time.sleep(self.rate)
