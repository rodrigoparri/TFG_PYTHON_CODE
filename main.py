# from Módulos_calculo import Beams
ducts = {
        60: 2400,
        75: 3800,
        85: 5000,
        95: 6400,
        105: 7900,
        120: 10400,
        130: 12300,
        145: 15400
    }

autodict = {}

for n in range(10):
        autodict[n] = [5,
                       autodict[n][0] + 1,
                       autodict[n][1] + 1,
                       autodict[n][2] + 1
                       ]
print(autodict)
