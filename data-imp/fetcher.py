from sunpy.net import Fido, attrs as a
from datetime import datetime
import astropy.units as u
import time
import re
import itertools
import threading
import sys

class Fetcher(object):

	possible_instruments = ["aia", "hmi"]
	wavmes = {
		"aia" : [94, 131, 171, 193, 211, 304, 335, 1600, 1700],
		"hmi" : [6173]
	}

	def __init__(self):
		self.instrument = ""
		self.wavelength = -1
		self.cadence = -1
		self.s_time = None
		self.e_time = None
		self.results = None

		# http://docs.sunpy.org/en/v0.9.0/code_ref/net.html#module-sunpy.net.dataretriever

	def fetch(self):
		print "\nAvailable instruments: %s" % (self.possible_instruments)
		prompt = "\nEnter instrument:\n==> "
		instrument = raw_input(prompt)
		self.instrument = instrument
		self.askstartdatetime()

	def askstartdatetime(self):
		prompt = "\nEnter start date: (MUST be in format yyyy/mm/dd)\n==> "
		date = raw_input(prompt)

		prompt = "\nEnter start time: (MUST be in format hh:mm:ss)\n==> "
		time = raw_input(prompt)

		hour = int(time[0:2])
		minute = int(time[3:5])
		second = int(time[6:])
		day = int(date[8:])
		month = int(date[5:7])
		year = int(date[0:4])

		self.s_time = datetime(year, month, day, hour, minute, second)
		self.askenddatetime()

	def askenddatetime(self):
		prompt = "\nEnter end date: (MUST be in format yyyy/mm/dd)\n==> "
		date = raw_input(prompt)

		prompt = "\nEnter end time: (MUST be in format hh:mm:ss)\n==> "
		time = raw_input(prompt)

		hour = int(time[0:2])
		minute = int(time[3:5])
		second = int(time[6:])
		day = int(date[8:])
		month = int(date[5:7])
		year = int(date[0:4])

		self.e_time = datetime(year, month, day, hour, minute, second)
		self.askwavmes()

	def askwavmes(self):
		self.displaywavmes(self.instrument)
		prompt = "\nEnter wavelength/configuration:\n==> "
		wavelength = int(raw_input(prompt))
		if(wavelength in self.wavmes[self.instrument.lower()]):
			self.wavelength = wavelength
			self.askother()
		else:
			print "\nNot available."
			self.askwavmes()

	def askother(self):
		prompt = "\nEnter cadence in seconds:\n==> "
		self.cadence = int(raw_input(prompt))

		# ask for more information, like extent, resolution, and pixels

		self.search()

	def search(self):
		t = threading.Thread(target=self.wheel)
		t.start()
		self.results = Fido.search(a.Time("%s/%s/%sT%s" % (self.s_time.date().year, self.s_time.date().month, self.s_time.date().day, str(self.s_time.time())), "%s/%s/%sT%s" % (self.e_time.date().year, self.e_time.date().month, self.e_time.date().day, str(self.e_time.time()))), a.Instrument(self.instrument), a.Wavelength(float(self.wavelength) * u.angstrom))
		self.done = True
		print self.results

	def displaywavmes(self, instrument):
		print "\nPossibilities for %s instrument:\n" % self.instrument
		print self.wavmes[instrument.lower()]

	done = False
	def wheel(self):
	    for c in itertools.cycle(["|", "/", "-", "\\"]):
	        if self.done:
	            break
	        sys.stdout.write("\rSearching... " + c)
	        sys.stdout.flush()
	        time.sleep(0.08)
	    sys.stdout.write("\rData search complete. Displaying...\n\n")

	def getsearch(self):
		return self.search
