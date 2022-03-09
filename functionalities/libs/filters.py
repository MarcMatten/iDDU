import numpy as np

def movingAverage(a, n):
    temp = a[-n:]
    temp = np.append(temp, a)
    temp = np.append(temp, a[0:n])
    r = np.zeros(np.size(temp))
    for i in range(0, len(temp)):
        if i < n:
            r[i] = np.mean(temp[0:i + n])
        elif len(temp) < i + n:
            r[i] = np.mean(temp[i - n:])
        else:
            r[i] = np.mean(temp[i - n:n + i])
    return r[n:-n]