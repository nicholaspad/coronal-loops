from sunpy.net import Fido, attrs as a
import astropy.units as u
import getpass
import threading
import itertools
import sys
import time
import os
import search as s

class Load(object):

	def __init__(self, search):
		self.search = search
		self.dir = "/Users/%s/Desktop/lmsal/resources/fits-files" % getpass.getuser()

	def go(self):
		if raw_input("Clear source folders? [y/n]\n==> ") == "y":
			print "\nClearing source folders..."
			os.system("rm /Users/%s/Desktop/lmsal/resources/fits-files/*.fits" % getpass.getuser())
		raw_input("\nPress ENTER to begin download:\n==> ")
		t = threading.Thread(target=self.wheel)
		t.start()
		Fido.fetch(self.search, path = self.dir, progress = False)
		self.done = True
		print "\nExiting..."

	done = False
	def wheel(self):
		print ""
	    for c in itertools.cycle(["|", "/", "-", "\\"]):
	        if self.done:
	            break
	        sys.stdout.write("\rDownloading... " + c + " ")
	        sys.stdout.flush()
	        time.sleep(0.08)
	    sys.stdout.write("\rDone.               ",)
