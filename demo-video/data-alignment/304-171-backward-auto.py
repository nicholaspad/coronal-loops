import sunpy.map as smap
from datetime import timedelta
from os import listdir
from IPython.core import debugger ; debug = debugger.Pdb().set_trace
from os.path import isfile, join

PATH = "/Volumes/Nicholas Data/"
PATH171 = "/Volumes/Nicholas Data/AIA171/"
PATH304 = "/Volumes/Nicholas Data/AIA304/"

aia171 = [f for f in listdir(PATH171) if isfile(join(PATH171, f))]
aia304 = [f for f in listdir(PATH304) if isfile(join(PATH304, f))]

t0 = timedelta(seconds = 5)

for i in range(len(aia171)):
	a = smap.Map(PATH171 + aia171[len(aia171) - i])
	b = smap.Map(PATH304 + aia304[len(aia304) - i])
	print "[#%d] Comparing %s" % (len(aia171) - i + 1, a.name)
	t = b.date - a.date
	if t > t0:
		print "Mismatch at index %d" % i
		print b.name
		print "304 ahead of 171 by %s" % t
		break
