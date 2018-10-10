import sunpy.map as smap
from datetime import timedelta
from os import listdir
from IPython.core import debugger ; debug = debugger.Pdb().set_trace
from os.path import isfile, join

PATH = "/Volumes/Nicholas Data/"
PATH171 = "/Volumes/Nicholas Data/AIA171/"
PATHHMI = "/Volumes/Nicholas Data/HMI/"

aia171 = [f for f in listdir(PATH171) if isfile(join(PATH171, f))]
aia304 = [f for f in listdir(PATHHMI) if isfile(join(PATHHMI, f))]

t0 = timedelta(seconds = 90)

for i in range(410, len(aia171)):
	a = smap.Map(PATH171 + aia171[len(aia171) - i])
	b = smap.Map(PATHHMI + aia304[len(aia304) - i])
	print "[#%d] Comparing %s" % (len(aia304) - i + 1, b.name)
	t = a.date - b.date
	if t > t0:
		print "Mismatch at index %d" % i
		print b.name
		print "171 ahead of HMI by %s" % t
		break
