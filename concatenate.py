import os

out = ''
for log in os.listdir('log'):
    f = open('log/' + log, 'r')
    texTemp = f.readlines()
    f.close()
    out += ''.join(texTemp[1:])

fileOut = open("portasBichadas.log", "w")
fileOut.write(out)
fileOut.close()

