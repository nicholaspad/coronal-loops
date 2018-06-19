from sunpy.net import Fido, attrs as a
import astropy.units as u
import time

class Downloader(object):

	def __init__(self, searchresults):
		self.searchresults = searchresults
		self.dir = ""

	def pipedata(self):
		prompt = "\nEnter a valid directory to download the above data: (e.g. /Users/<user>/Downloads)\n==> "
		dir = raw_input(prompt)
		print "Working...\n"
		time.sleep(0.15)
		self.dir = dir
		self.download()

	def download(self):
		raw_input("Press ENTER to begin download:\n==> ")
		t = threading.Thread(target=self.wheel)
		t.start()
		self.download = Fido.fetch(self.searchresults, path = self.dir)
		self.done = True
		time.sleep(1)
		self.viewsize()

	def viewsize(self):
		pass

	done = False
	def wheel(self):
	    for c in itertools.cycle(["|", "/", "-", "\\"]):
	        if self.done:
	            break
	        sys.stdout.write("\Downloading to " + self.dir + "... " + c)
	        sys.stdout.flush()
	        time.sleep(0.1)
	    sys.stdout.write("\rCompleted. Files saved to %s\n\n" % (self.dir))
