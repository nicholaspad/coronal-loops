import os
from os import listdir
from os.path import isfile, join

PATH131 = "/Users/padman/Desktop/AIA335"

aia131 = [f for f in listdir(PATH131) if isfile(join(PATH131, f))]
bad_dates = ["015402", "015602", "020202", "020802", "043802", "194502", "194602", "194702", "194802", "194902", "195002", "200002"]

for i in range(len(aia131)):
	for date in bad_dates:
		if date in aia131[i]:
			os.system("rm /Users/padman/Desktop/AIA335/%s" % aia131[i])
			print "%s deleted" % aia131[i]
