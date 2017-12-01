def convertTimeMMSSsss(sec):
    if type(sec) is float:
        if sec < 0:
            sign = '-'
            sec = -sec
        else:
            sign = ''

        m, s = divmod(sec, 60)

        if m == 0:
            return(sign + str(round(s, 3)))
        else:
            if s < 10:
                return(sign + str(int(m)) + ':' + '0' + '{0:.3f}'.format(round(s,3)))
            else:
                return(sign + str(int(m)) + ':' + '{0:.3f}'.format(round(s,3)))
    else:
        return('00:00,000')

def convertDelta(sec):
    if type(sec) is float:
        if sec < 0:
            sign = '-'
            sec = -sec
        else:
            sign = '+'

        m, s = divmod(sec, 60)

        if m == 0:
            return(sign + '{0:.2f}'.format(round(s,2)))#str(round(s, 2)))
        else:
            if s < 10:
                return(sign + str(int(m)) + ':' + '0' + '{0:.2f}'.format(round(s,2))) # str(round(s, 3)))
            else:
                return(sign + str(int(m)) + ':' + '{0:.2f}'.format(round(s,2))) #str(round(s, 3)))
    else:
        return('+00:00,00')

def convertTimeHHMMSS(sec):
    if type(sec) is float:
        if sec < 0:
            sign = '-'
            sec = -sec
        else:
            sign = ''

        m, s = divmod(sec, 60)
        h, m = divmod(m, 60)

        if m < 10:
            if s < 10:
                return(sign + str(int(h)) + ':' + '0' + str(int(m)) + ':' + '0' + str(round(s)))
            else:
                return(sign + str(int(h)) + ':' + '0' +  str(int(m)) + ':' + str(round(s)))
        else:
            if s < 10:
                return(sign + str(int(h)) + ':' + str(int(m)) + ':' + '0' + str(round(s)))
            else:
                return(sign + str(int(h)) + ':' +  str(int(m)) + ':' + str(round(s)))
    else:
        return('00:00:00')


def roundedStr1(x):
    if type(x) is float:
        return '{0:.1f}'.format(round(x,1))
    else:
        return('')

def roundedStr2(x):
    if type(x) is float:
        return '{0:.2f}'.format(round(x,2))
    else:
        return('')

def roundedStr3(x):
    if type(x) is float:
        return '{0:.3f}'.format(round(x,3))
    else:
        return('')

def getData(ir, list):

    data = {}

    for i in range(0, len(list)):
        data.update({list[i]: ir[list[i]]})

    return data


    #
    # if ir.startup() and ir['IsOnTrack']:
    #     if outlap:
    #         ZeroLap = ir['Lap']
    #         outlap = False
    #     BestLapValue = convertTimeMMSSsss(ir['LapBestLapTime'])
    #     LastLapValue = convertTimeMMSSsss(ir['LapLastLapTime'])
    #     DeltaLapValue = convertDelta(ir['LapDeltaToSessionBestLap'])
    #     dcFuelMixtureValue = str(ir['dcFuelMixture'])
    #     dcThrottleShapeValue = str(ir['dcThrottleShape'])
    #     dcTractionControlValue = str(ir['dcTractionControl'])
    #     dcTractionControl2Value = str(ir['dcTractionControl2'])
    #     dcTractionControlToggleValue = ir['dcTractionControlToggle']
    #     dcABSValue = str(ir['dcABS'])
    #     dcBrakeBiasValue = roundedStr2(ir['dcBrakeBias'])
    #     FuelLevelValue = roundedStr2(ir['FuelLevel'])
    #     Fuel = ir['FuelLevel']
    #     Lap = ir['Lap']
    #     StintLap = Lap - ZeroLap
    # else:
    #     DeltaLapValue = ' '
    #     Lap = 0
    #     oldLap = -1
    #     Fuel = 0
    #     LastFuelLevel = 0
    #     Fuel = 0
    #     FuelConsumption = []
    #     outlap = True
    #
    # if ir.startup():
    #     RemLapValue = str(round(ir['SessionLapsRemain']))
    #     RemTimeValue = convertTimeHHMMSS(ir['SessionTimeRemain'])
    # else:
    #     RemLapValue = ''
    #     RemTimeValue = ''
    #
    #     for i
