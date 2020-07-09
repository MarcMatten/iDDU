def getData(ir, L):
    data = {}

    for i in range(0, len(L)):
        data.update({L[i]: ir[L[i]]})

    return data