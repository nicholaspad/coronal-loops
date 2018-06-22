import re
import ssl
from sunpy.net.helioviewer import HelioviewerClient
from datetime import datetime

class Fetch(object):

	hv = HelioviewerClient()
	wavmes = {
		"aia" : ["94", "131", "171", "193", "211", "304", "335", "1600", "1700", "4500"],
		"hmi" : ["continuum", "magnetogram"],
		"eit" : ["171", "195", "284", "304"],
		"swap" : ["174"],
		"mdi" : ["continuum", "magnetogram"],
		"sxt" : ["almgmn", "thin-al", "white-light"],
		"lasco" : ["white-light"]
	}

	def __init__(self):
		ssl._create_default_https_context = ssl._create_unverified_context
		self.observatory = ""
		self.instrument = ""
		self.detector = ""
		self.measurement = ""
		self.interval = -1
		self.period = -1
		self.fps = -1
		self.time = None


	def fetchdata(self):
		print "Gathering data sources...\n"

		datasources = self.hv.get_data_sources()

		print "OBSERV\tINSTR\tWAVELEN/MEAS"
		for observatory, instruments in datasources.items():
			for inst, detectors in instruments.items():
				for det, measurements in detectors.items():
					for meas, params in measurements.items():
						if observatory != "STEREO_A" and observatory != "STEREO_B":
							print "%s\t%s\t%s" % (observatory, inst, meas)

		prompt = "\nEnter observatory: (case sensitive)\n==> "
		self.observatory = raw_input(prompt)
		prompt = "\nEnter instrument:\n==> "
		self.instrument = raw_input(prompt)
		self.detector = self.instrument
		self.askwavmes()
	
	def askwavmes(self):
		self.displaywavmes(self.instrument)
		prompt = "\nEnter wavelength/configuration:\n==> "
		measurement = raw_input(prompt)
		if(measurement.lower() in self.wavmes[self.instrument.lower()]):
			self.measurement = measurement
			self.askdatetime()
		else:
			print "\nWavelength/configuration not available."
			self.askwavmes()

	def askdatetime(self):
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

		self.time = datetime(year, month, day, hour, minute, second)
		self.askother()

	def askother(self):		
		prompt = "\nEnter time interval in minutes: (must be a positive whole number)\n==> "
		self.interval = int(raw_input(prompt))

		prompt = "\nEnter number of time intervals: (must be a positive whole number)\n==> "
		self.period = int(raw_input(prompt))

		prompt = "\nEnter frames per second: (must be a positive whole number)\n==> "
		self.fps = int(raw_input(prompt))

	def displaywavmes(self, instrument):
		print "\nPossibilities for %s instrument:\n" % self.instrument
		print self.wavmes[instrument.lower()]

	def getinfo(self):
		return [self.time, self.period, self.interval, self.observatory, self.instrument, self.detector, self.measurement, self.fps]
