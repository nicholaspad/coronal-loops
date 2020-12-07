from datetime import timedelta
from os import listdir
from IPython.core import debugger ; debug = debugger.Pdb().set_trace
from os.path import isfile, join

PATH171 = "/Users/padman/Desktop/AIA94"
PATH304 = "/Volumes/Nicholas Data/HMI/"

aia171 = [f for f in listdir(PATH171) if isfile(join(PATH171, f))]
aia304 = [f for f in listdir(PATH304) if isfile(join(PATH304, f))]

for i in range(len(aia171)-2):
	print i, int(aia171[i+1][28:33]) - int(aia171[i][28:33]), int(aia304[i+1][19:24]) - int(aia304[i][19:24]), aia171[i][17:34], aia304[i][10:14] + "-" + aia304[i][14:16] + "-" + aia304[i][16:18] + "T" + aia304[i][19:25]
