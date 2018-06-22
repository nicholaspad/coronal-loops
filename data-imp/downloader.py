from sunpy.net import Fido, attrs as a
import astropy.units as u
import getpass
import threading
import time

class Downloader(object):

	def __init__(self, search):
		self.search = search
		self.dir = "/Users/%s/Desktop/lmsal/data-imp/source-fits"

	def pipe(self):
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
	        sys.stdout.write("\rDownloading... " + c + "\n")
	        sys.stdout.flush()
	        time.sleep(0.08)
	    sys.stdout.write("\rDownload complete.\n\n")
