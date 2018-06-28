from sunpy.net import Fido, attrs as a
import astropy.units as u
import getpass
import threading
import itertools
import sys
import time
import os
import fetcher as fe

class Downloader(object):

	def __init__(self, search):
		self.search = search
		self.dir = "/Users/%s/Desktop/lmsal/data-imp/source-fits" % getpass.getuser()

	def pipe(self):
		clear = raw_input("Clear source folders? [y/n]\n==> ")
		if clear == "y":
			print "\nClearing source folders..."
			os.system("rm /Users/%s/Desktop/lmsal/data-imp/source-fits/*.fits" % getpass.getuser())
		raw_input("\nPress ENTER to begin download:\n==> ")
		t = threading.Thread(target=self.wheel)
		t.start()
		Fido.fetch(self.search, path = self.dir, progress = False)
		self.done = True
		time.sleep(0.1)
		if fe.cut_vid:
			print "\nCalling find.py in ar-find..."
			os.system("python ../ar-find/find.py")
			pass
		elif fe.cut_vid == False:
			pass
		elif fe.cut_vid == None:
			print "\nExiting..."

	done = False
	def wheel(self):
	    for c in itertools.cycle(["|", "/", "-", "\\"]):
	        if self.done:
	            break
	        sys.stdout.write("\rDownloading... " + c + " ")
	        sys.stdout.flush()
	        time.sleep(0.08)
	    sys.stdout.write("\rDone.")
