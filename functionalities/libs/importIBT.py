import irsdk
import numpy as np
import scipy.signal
from functionalities.libs import importExport, convertString

defaultChannels = ['SessionTime', 'LapCurrentLapTime', 'LapDist', 'LapDistPct', 'Speed', 'Lap', 'FuelLevel', 'FuelUsePerHour']

def importIBT(ibtPath, channels=None, lap=None, channelMapPath='iRacingChannelMap.csv'):

    # read in metadata
    c = dict()

    ir = irsdk.IRSDK()
    ir.startup(test_file=ibtPath)

    c['CarSetup'] = ir['CarSetup']
    c['DriverInfo'] = ir['DriverInfo']
    c['WeekendInfo'] = ir['WeekendInfo']
    c['carPath'] = c['DriverInfo']['Drivers'][c['DriverInfo']['DriverCarIdx']]['CarPath']

    ir.shutdown()

    # read in telemetry channels
    ir_ibt = irsdk.IBT()
    ir_ibt.open(ibtPath)
    var_headers_names = ir_ibt.var_headers_names

    temp = dict()
    s = dict()

    # load channel map
    channelMap = importExport.loadCSV(channelMapPath)

    # define telemetry channels to import
    channelsExport = []

    if channels is None:
        channelsExport = var_headers_names
    else:
        for i in range(0, len(channels)):
            if channels[i] in var_headers_names:
                channelsExport.append(channels[i])
            elif channels[i] in channelMap['ChannelName']:
                index = channelMap['ChannelName'].index(channels[i])
                channelsExport.append(channelMap['iRacingChannelName'][index])
            else:
                print('Error: <{}> neihter in list of iRacing channels nor in channel map! - Skipping this channel!'.format(channels[i]))

    channelsExport.extend(defaultChannels)
    channelsExport = list(set(channelsExport))

    # import channels
    for i in range(0, len(channelsExport)):
        if channelsExport[i] in var_headers_names:
            temp[channelsExport[i]] = np.array(ir_ibt.get_all(channelsExport[i]))
        else:
            print('Error: <{}> not in the list of available channels'.format(channelsExport[i]))

    varNames = list(temp.keys())

    # cut data
    if lap is None or lap in ['a', 'A', 'all', 'ALL', 'All', 'w', 'W', 'whole', 'WHOLE']:  # complete file
        for i in range(0, len(varNames)):
            s[varNames[i]] = temp[varNames[i]]
    else:
        indices = []
        if lap in ['f', 'F', 'fastest', 'Fastest', 'FASTERST']:  # fastest lap only
            # find the fastest lap
            print('\tImporting fastest lap.')
            NLapStartIndex = scipy.signal.find_peaks(1 - np.array(temp['LapDistPct']), height=(0.98, 1.02), distance=600)

            if len(NLapStartIndex[0]) > 1:
                print('\tFound following laps:')
                tLap = []
                NLap = []
                sLap = []
                VFuelLap = []

                for q in range(0, len(NLapStartIndex[0])-1):
                    tLap.append(temp['SessionTime'][NLapStartIndex[0][q+1]-1] - temp['SessionTime'][NLapStartIndex[0][q]])
                    sLap.append(temp['LapDist'][NLapStartIndex[0][q+1]-1])
                    NLap.append(temp['Lap'][NLapStartIndex[0][q]])
                    VFuelLap.append(temp['FuelLevel'][NLapStartIndex[0][q]] - temp['FuelLevel'][NLapStartIndex[0][q+1]-1])
                    print('\t{0}\t{1} min\t{2} l'.format(NLap[q], convertString.convertTimeMMSSsss(tLap[q]), convertString.convertTimeMMSSsss(VFuelLap[q])))

                for r in range(0, len(tLap)):
                    if sLap[r] < float(c['WeekendInfo']['TrackLength'].split(' ')[0]) * 1000 * 0.95:
                        tLap.pop(r)
                        # tLap[r] = tLap[r] + 1000

                NLapFastest = NLap[np.argmin(tLap)]

                # get all indices for the fastest lap
                indices = np.argwhere(temp['Lap'] == NLapFastest)[:, 0]

                print('\tImporting Lap {} ({})'.format(NLapFastest, convertString.convertTimeMMSSsss(min(tLap))))

            else:
                print('\tNo valid lap found!')
                return None, None

        # lap number
        elif isinstance(lap, int):
            if lap < np.min(temp['Lap']) or lap > np.max(np.array(temp['Lap'])):
                print('Error: Lap number {} is out of bounds! File contains laps {} to {}'.format(lap, np.min(temp['Lap']), np.max(np.array(temp['Lap']))))
                return

            indices = np.argwhere(temp['Lap'] == lap)[:, 0]

        # actually cut the data
        for i in range(0, len(varNames)):
            s[varNames[i]] = temp[varNames[i]][indices]

    ir_ibt.close()

    # channel mapping
    for i in range(0, len(channelsExport)):
        if channelsExport[i] in channelMap['iRacingChannelName']:
            index = channelMap['iRacingChannelName'].index(channelsExport[i])
            c[channelMap['ChannelName'][index]] = np.array(s[channelsExport[i]]) * float(channelMap['ConverstionFactor'][index])
        else:
            c[channelsExport[i]] = s[channelsExport[i]]

    # fuel calcs
    if 'QFuel' in channels or 'dmFuel' in channels:
        c['QFuel'] = c['dmFuel'] / 1000 / c['DriverInfo']['DriverCarFuelKgPerLtr']  # l/s

    # replacing tLap with SessionTime derivative
    c['dt'] = np.diff(c['SessionTime'])
    c['tLap'] = np.append(0, np.cumsum([c['dt']]))
    c['VFuelLap'] = c['VFuel'][0] - c['VFuel'][-1]

    # setting start and end value for LapDistPct
    c['LapDistPct'][0] = 0
    c['LapDistPct'][-1] = 1

    return c, list(c.keys())
