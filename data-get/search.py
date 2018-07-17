from sunpy.net import Fido, attrs as a
import sunpy.net.vso as vso
from datetime import datetime
import astropy.units as u
import time
import re
import itertools
import threading
import os
import sys

vid = None

class Search(object):

	possible_instruments = ["aia", "hmi"]
	wavmes = {
		"aia" : [94, 131, 171, 193, 211, 304, 335, 1600, 1700],
		"hmi" : [6173]
	}

	def __init__(self):
		os.system("clear")
		self.instrument = ""
		self.wavs = []
		self.cadence = -1
		self.s_time = None
		self.e_time = None
		self.results = None

	def go(self):
		ask = raw_input("\nGenerate video? [y/n]\n==> ")
		if ask == "y":
			global vid
			vid = True

		print "\nAvailable instruments: %s" % (self.possible_instruments)
		instrument = raw_input("\nEnter instrument:\n==> ")
		self.instrument = instrument
		self.askstartdatetime()

	def askstartdatetime(self):
		date = raw_input("\nEnter start date: (MUST be in format yyyy/mm/dd)\n==> ")
		time = raw_input("\nEnter start time: (MUST be in format hh:mm:ss)\n==> ")

		hour = int(time[0:2])
		minute = int(time[3:5])
		second = int(time[6:])
		day = int(date[8:])
		month = int(date[5:7])
		year = int(date[0:4])

		self.s_time = datetime(year, month, day, hour, minute, second)
		self.askenddatetime()

	def askenddatetime(self):
		date = raw_input("\nEnter end date: (MUST be in format yyyy/mm/dd)\n==> ")
		time = raw_input("\nEnter end time: (MUST be in format hh:mm:ss)\n==> ")

		hour = int(time[0:2])
		minute = int(time[3:5])
		second = int(time[6:])
		day = int(date[8:])
		month = int(date[5:7])
		year = int(date[0:4])

		self.e_time = datetime(year, month, day, hour, minute, second)
		self.askother()

	def askwavmes(self):
		self.displaywavmes(self.instrument)
		self.num_wav = int(raw_input("\nEnter NUMBER of wavelengths (up to 4):\n==> "))
		for i in range(self.num_wav):
			self.wavs.append(int(raw_input("\nEnter wavelength/configuration:\n==> ")))
		self.search()

	def askother(self):
		self.cadence = int(raw_input("\nEnter cadence in seconds:\n==> "))
		self.askwavmes()

	def search(self):
		print ""
		t = threading.Thread(target=self.wheel)
		t.start()
		if self.num_wav == 1:
			self.results = Fido.search(a.Time("%s/%s/%sT%s" % (self.s_time.date().year, self.s_time.date().month, self.s_time.date().day, str(self.s_time.time())), "%s/%s/%sT%s" % (self.e_time.date().year, self.e_time.date().month, self.e_time.date().day, str(self.e_time.time()))), a.Instrument(self.instrument), a.Wavelength(float(self.wavs[0]) * u.angstrom), a.vso.Sample(self.cadence * u.second))
		elif self.num_wav == 2:
			self.results = Fido.search(a.Time("%s/%s/%sT%s" % (self.s_time.date().year, self.s_time.date().month, self.s_time.date().day, str(self.s_time.time())), "%s/%s/%sT%s" % (self.e_time.date().year, self.e_time.date().month, self.e_time.date().day, str(self.e_time.time()))), a.Instrument(self.instrument), a.Wavelength(float(self.wavs[0]) * u.angstrom) | a.Wavelength(float(self.wavs[1]) * u.angstrom), a.vso.Sample(self.cadence * u.second))
		elif self.num_wav == 3:
			self.results = Fido.search(a.Time("%s/%s/%sT%s" % (self.s_time.date().year, self.s_time.date().month, self.s_time.date().day, str(self.s_time.time())), "%s/%s/%sT%s" % (self.e_time.date().year, self.e_time.date().month, self.e_time.date().day, str(self.e_time.time()))), a.Instrument(self.instrument), a.Wavelength(float(self.wavs[0]) * u.angstrom) | a.Wavelength(float(self.wavs[1]) * u.angstrom) | a.Wavelength(float(self.wavs[2]) * u.angstrom), a.vso.Sample(self.cadence * u.second))
		elif self.num_wav == 4:
			self.results = Fido.search(a.Time("%s/%s/%sT%s" % (self.s_time.date().year, self.s_time.date().month, self.s_time.date().day, str(self.s_time.time())), "%s/%s/%sT%s" % (self.e_time.date().year, self.e_time.date().month, self.e_time.date().day, str(self.e_time.time()))), a.Instrument(self.instrument), a.Wavelength(float(self.wavs[0]) * u.angstrom) | a.Wavelength(float(self.wavs[1]) * u.angstrom) | a.Wavelength(float(self.wavs[2]) * u.angstrom) | a.Wavelength(float(self.wavs[3]) * u.angstrom), a.vso.Sample(self.cadence * u.second))
		self.done = True
		print self.results

	def displaywavmes(self, instrument):
		print "\nPossibilities for %s instrument:" % self.instrument
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
	    time.sleep(0.05)

	def getsearch(self):
		return self.results
