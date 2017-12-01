import time

def convertTimeMMSSsss(sec):
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

def convertDelta(sec):
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

def convertTimeHHMMSS(sec):
    if sec < 0:
        sign = '-'
        sec = -sec
    else:
        sign = ''

    m, s = divmod(sec, 60)
    h, m = divmod(m, 60)

    if m < 10:
        if s < 10:
            return (sign + str(int(h)) + ':' + '0' + str(int(m)) + ':' + '0' + str(round(s)))
        else:
            return (sign + str(int(h)) + ':' + '0' +  str(int(m)) + ':' + str(round(s)))
    else:
        if s < 10:
            return (sign + str(int(h)) + ':' + str(int(m)) + ':' + '0' + str(round(s)))
        else:
            return (sign + str(int(h)) + ':' +  str(int(m)) + ':' + str(round(s)))


def roundedStr1(x):
    return '{0:.1f}'.format(round(x,1))

def roundedStr2(x):
    return '{0:.2f}'.format(round(x,2))

def roundedStr3(x):
    return '{0:.3f}'.format(round(x,3))