import irsdk
import numpy as np
import scipy.signal
from libs.auxiliaries import importExport, convertString
# import importExport, convertString

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
        channels = var_headers_names
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

    # # fuel calcs
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



def importIBT2(ibtPath, channels=None, lap=None):

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

    # meta data
    l = ['type', 'offset', 'count', 'count_as_time', 'name', 'desc', 'unit','_offset']

    metadata = {}

    for i in ir_ibt._IBT__var_headers:
        metadata[i.name] = {a:i.__getattribute__(a) for a in l}

    # define telemetry channels to import
    channelsExport = []

    if channels is None:
        channelsExport = var_headers_names
        channels = var_headers_names
    else:
        for i in range(0, len(channels)):
            if channels[i] in var_headers_names:
                channelsExport.append(channels[i])
            else:
                print('Error: <{}> neihter in list of iRacing channels nor in channel map! - Skipping this channel!'.format(channels[i]))

    channelsExport.extend(defaultChannels)
    channelsExport = list(set(channelsExport))

    # import channels
    for i in range(0, len(channelsExport)):
        if channelsExport[i] in var_headers_names:
            temp[channelsExport[i]] = np.array(ir_ibt.get_all(channelsExport[i]), dtype=np.dtype(np.float32))
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
        c[channelsExport[i]] = s[channelsExport[i]]

    # setting start and end value for LapDistPct
    c['LapDistPct'][0] = 0
    c['LapDistPct'][-1] = 1

    return c, list(c.keys()), metadata

if __name__ == "__main__":
    data, channelNames, metadata = importIBT2("C:/Users/marc/Documents/iRacing/telemetry/porsche911rgt3_daytona 2011 road 2023-01-14 18-35-41.ibt")

    channelNames = ['Gear', 'SessionTick', 'EngineWarnings', 'OnPitRoad']

    # import importlib.util
    # import sys
    # spec = importlib.util.spec_from_file_location("ldparser", "C:/Users/marc/Documents/iDDU/ldparser\ldparser.py")
    # ld = importlib.util.module_from_spec(spec)
    # sys.modules["ldparser"] = ld
    # spec.loader.exec_module(ld)

    import numpy as np
    from datetime import datetime
    import ldparser.ldparser as ld

    NChannels = len(channelNames)

    aux_ptr = 1762
    venue_ptr = 4918
    vehicle_ptr = 8020
    meta_ptr = 13384
    data_ptr = meta_ptr + NChannels * 124

    vehicle = ld.ldVehicle('123', 1234, 'type', 'vehicleComment')
    venue = ld.ldVenue('venueName', vehicle_ptr, vehicle)
    event = ld.ldEvent('EvnetName', 'session', 'EventComment', venue_ptr, venue)

    head = ld.ldHead(meta_ptr, data_ptr, aux_ptr, event, 'dirver', '0123', 'venue', datetime.now(), 'short_comment', 'event', 'Test')

    channs = []
    prev_meta_ptr = meta_ptr

    for i in channelNames:
        if not isinstance(data[i], np.ndarray):
            continue

        data_len = len(data[i])
        
        next_meta_ptr = meta_ptr + 124

        if metadata[i]['type'] == 1:
            dataType = np.int8
            bytesPerTimestep = 1
            dec = 0
        elif metadata[i]['type'] == 2:
            dataType = np.float32
            bytesPerTimestep = 4
            dec = 0
        elif metadata[i]['type'] == 5:
            dataType = np.float64
            bytesPerTimestep = 8
            dec = 0
        else:
            dataType = np.float32
            bytesPerTimestep = 4
            dec = 0

        ch = ld.ldChan(None, meta_ptr, prev_meta_ptr, next_meta_ptr, data_ptr, 
                        data_len,
                        dataType,  # dtype
                        60,  #*metadata[i]['count'],  # freq
                        0,  # shift
                        1,  # mul
                        1,  # scale
                        dec,  # dec
                        metadata[i]['name'],  # name
                        '',  # short name
                        metadata[i]['unit'])
       
        
        ch._data = data[i]

        channs.append(ch)
        
        prev_meta_ptr = meta_ptr
        meta_ptr += 124

        data_ptr += bytesPerTimestep * data_len

    l = ld.ldData(head, channs)

    l.write('test.ld')
