from sunpy.net import Fido, attrs as a
import astropy.units as u
import time
import re
import itertools
import threading
import sys
import tools

class Fetcher(object):

	possible_instruments = ["aia", "hmi", "iris", "eve"]
	possible_wavelengths = {
		"aia" : ["94", "131", "171-175", "191-195", "211", "304", "335", "1600", "1700", "4500"],
		"hmi" : ["6173-6174"],
		"iris" : [],
		"eve" : []
	}

	def __init__(self):
		self.instrument = ""
		self.start_date = ""
		self.end_date = ""
		self.wavelength = ""

	def fetchdata(self):
		print "\nAvailable instruments: %s" % (self.possible_instruments)
		prompt = "Enter observation instrument: (e.g. hmi)\n==> "
		instr = raw_input(prompt)
		if instr not in self.possible_instruments:
			print "Unable to process %s data.\n" % (instr)
			time.sleep(0.15)
			self.fetchdata()
		else:
			print "Working...\n"
			time.sleep(0.15)
			self.instrument = instr
		self.askstarttime()

	def askstarttime(self):
		r = re.compile("\d{4}/\d{2}/\d{2}")
		prompt = "Enter start date: (must be in format yyyy/mm/dd)\n==> "
		date = raw_input(prompt)
		if r.match(date) is None:
			print "Invalid date format.\n"
			time.sleep(0.15)
			self.askstarttime()
		else:
			print "Working...\n"
			time.sleep(0.15)
			self.start_date = date
		self.askendtime()

	def askendtime(self):
		r = re.compile("\d{4}/\d{2}/\d{2}")
		prompt = "Enter end date: (must be in format yyyy/mm/dd)\n==> "
		date = raw_input(prompt)
		if r.match(date) is None:
			print "Invalid date format.\n"
			time.sleep(0.15)
			self.askendtime()
		else:
			if int(date[0:4]) >= int(self.start_date[0:4]) and int(date[5:7]) >= int(self.start_date[5:7]) and int(date[8:]) > int(self.start_date[8:]):
				print "Working...\n"
				time.sleep(0.15)
				self.end_date = date
			else:
				print "End date must be after start date.\n"
				time.sleep(0.15)
				self.askendtime()
		self.askwavelength()

	def askwavelength(self):
		print "Available wavelengths (in angstroms) for %s instrument:\n%s" % (self.instrument, self.possible_wavelengths[self.instrument])
		prompt = "Enter desired wavelength: (entering an invalid wavelength will return no search results)\n==> "
		wave = raw_input(prompt)
		print "Working...\n"
		time.sleep(0.15)
		self.wavelength = wave
		self.querysearch()

	def querysearch(self):
		t = threading.Thread(target=self.wheel)
		t.start()
		self.search_results = Fido.search(a.Time(self.start_date, self.end_date), a.Instrument(self.instrument), a.Wavelength(float(self.wavelength) * u.angstrom))
		self.done = True
		time.sleep(1)
		print self.search_results

	done = False
	def wheel(self):
	    for c in itertools.cycle(["|", "/", "-", "\\"]):
	        if self.done:
	            break
	        sys.stdout.write("\rSearching... " + c)
	        sys.stdout.flush()
	        time.sleep(0.1)
	    sys.stdout.write("\rData search complete. Displaying...\n\n")

	def getsearchresults(self):
		return self.search_results
