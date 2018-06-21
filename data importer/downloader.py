from sunpy.net import Fido, attrs as a
import astropy.units as u
import time

class Downloader(object):

	def __init__(self, searchresults):
		self.searchresults = searchresults
		print searchresults
		self.dir = ""

	def pipedata(self):
		prompt = "\nEnter a valid directory to download the above data: (e.g. /Users/<user>/Downloads)\n==> "
		dir = raw_input(prompt)
		self.dir = dir
		self.download()

	def download(self):
		raw_input("Press ENTER to begin download of file(s):\n==> ")
		print "\nDownloading..."
		Fido.fetch(self.searchresults, path = self.dir)
		print "\rFinished."
		time.sleep(1)
