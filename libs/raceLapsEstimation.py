# import all required packages
import threading
import time
import numpy as np
from libs import iDDUhelper


# UpShiftTone Thread
class raceLapsEstimation(threading.Thread):
    def __init__(self, RTDB, rate):
        threading.Thread.__init__(self)
        self.rate = rate
        self.db = RTDB
        self.snapshot = False
        print(self.db.timeStr + ': Starting raceLapsEstimation')

    def run(self):
        while 1:
            if self.db.BDDUexecuting:
                # if self.db.SessionInfo['Sessions'][self.db.SessionNum]['ResultsPositions']:
                if self.db.SessionInfo['Sessions'][self.db.SessionNum]['ResultsPositions'] and self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionType'] == 'Race' and self.db.TimeLimit:
                    for i in range(0, len(self.db.SessionInfo['Sessions'][self.db.SessionNum]['ResultsPositions'])):
                        CarIdx_temp = self.db.SessionInfo['Sessions'][self.db.SessionNum]['ResultsPositions'][i]['CarIdx']
                        temp_CarIdxtLap = self.db.SessionInfo['Sessions'][self.db.SessionNum]['ResultsPositions'][i]['LastTime']
                        if temp_CarIdxtLap < 0:
                            temp_CarIdxtLap = float('nan')

                        self.db.CarIdxtLap[CarIdx_temp][self.db.SessionInfo['Sessions'][self.db.SessionNum]['ResultsPositions'][i]['LapsComplete'] - 1] = temp_CarIdxtLap

                        # if self.db.TimeLimit:  # and not self.db.LapLimit:
                        # try:
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
                            self.db.NLapRaceTime[CarIdx_temp]) - NLapTimed) * iDDUhelper.meanTol(self.db.CarIdxtLap[CarIdx_temp], 0.03) + CarIdxtLapSum + (
                                                                        iDDUhelper.maxList(temp_pitstopsremain, 0) * self.db.PitStopDelta)
                        # except:
                        #     print('exception in raceLapsEstimation!')
                        #     print('i:')
                        #     print(i)
                        #     if not self.snapshot:
                        #         self.db.snapshot()
                        #         print('RTDB snapshot saved!')
                        #         self.snapshot = True

                    self.db.WinnerCarIdx = self.db.NLapRaceTime.index(max(self.db.NLapRaceTime))

                    temp_pitstopsremain_np = self.db.PitStopsRequired - np.array(self.db.CarIdxPitStops[self.db.DriverCarIdx])
                    temp_pitstopsremain = temp_pitstopsremain_np.tolist()
                    CarIdxtLap_cleaned = [x for x in self.db.CarIdxtLap[self.db.DriverCarIdx] if str(x) != 'nan']
                    CarIdxtLapSum = np.sum(CarIdxtLap_cleaned)
                    NLapTimed = np.count_nonzero(~np.isnan(self.db.CarIdxtLap[self.db.DriverCarIdx]))

                    self.db.NLapWinnerRaceTime = (self.db.TFinishPredicted[self.db.WinnerCarIdx] - CarIdxtLapSum - (
                            iDDUhelper.maxList(temp_pitstopsremain, 0) * self.db.PitStopDelta)) / iDDUhelper.meanTol(self.db.CarIdxtLap[self.db.DriverCarIdx],
                                                                                                                     0.03) + NLapTimed  # use this to find winner

                    if self.db.WinnerCarIdx == self.db.DriverCarIdx:
                        self.db.NLapDriver = float(self.db.NLapRaceTime[self.db.DriverCarIdx])
                    else:
                        self.db.NLapDriver = float(self.db.NLapWinnerRaceTime)

                    if self.db.NLapDriver > 1:
                        self.db.RaceLaps = int(self.db.NLapDriver + 1)
                    else:
                        self.db.RaceLaps = self.db.UserRaceLaps


            time.sleep(self.rate)