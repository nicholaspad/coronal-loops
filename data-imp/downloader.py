from sunpy.net import Fido, attrs as a
import astropy.units as u
import getpass
import threading
import itertools
import sys
import time
import os

class Downloader(object):

	def __init__(self, search):
		self.search = search
		self.dir = "/Users/%s/Desktop/lmsal/data-imp/source-fits" % getpass.getuser()

	def pipe(self):
		time.sleep(0.05)
		clear = raw_input("Clear source folders? [y/n]\n==> ")
		if clear == "y":
			print "\nClearing source folders...\n"
			os.system("rm /Users/%s/Desktop/lmsal/data-imp/source-fits/*.fits" % getpass.getuser())
		else:
			print "\nProgram will not overwrite. Exiting...\n"
			sys.exit()
		raw_input("\nPress ENTER to begin download of file(s):\n==> ")
		print ""
		t = threading.Thread(target=self.wheel)
		t.start()
		Fido.fetch(self.search, path = self.dir)
		self.done = True

	done = False
	def wheel(self):
	    for c in itertools.cycle(["|", "/", "-", "\\"]):
	        if self.done:
	            break
	        sys.stdout.write("\rDownloading... " + c + " ")
	        sys.stdout.flush()
	        time.sleep(0.08)
	    sys.stdout.write("\rDownload complete.\n")
