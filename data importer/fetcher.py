from sunpy.net import Fido, attrs as a
import astropy.units as u
import time
import re
import itertools
import threading
import sys

class Fetcher(object):

	possible_instruments = ["aia", "hmi", "iris", "sot"]
	possible_wavelengths = {
		"aia" : ["94", "131", "171", "193", "211", "304", "335", "1600", "1700"],
		"hmi" : ["6173"],
		"iris" : ["1400", "2796", "2832", "1330"],
		"sot" : ["6300.8-6303.2"]
	}

	def __init__(self):
		self.instrument = ""
		self.start_date = ""
		self.end_date = ""
		self.start_time = ""
		self.end_time = ""
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
		self.askstartdate()

	def askstartdate(self):
		r = re.compile("\d{4}/\d{2}/\d{2}")
		prompt = "Enter start date: (must be in format yyyy/mm/dd)\n==> "
		date = raw_input(prompt)
		if r.match(date) is None:
			print "Invalid date format.\n"
			time.sleep(0.15)
			self.askstartdate()
		else:
			print "Working...\n"
			time.sleep(0.15)
			self.start_date = date
		self.askstarttime()

	def askstarttime(self):
		r = re.compile("\d{2}:\d{2}:\d{2}")
		prompt = "Enter start time: (must be in format hh:mm:ss)\n==> "
		s_time = raw_input(prompt)
		if r.match(s_time) is None:
			print "Invalid time format.\n"
			time.sleep(0.15)
			self.askstarttime()
		else:
			print "Working...\n"
			time.sleep(0.15)
			self.start_time = s_time
		self.askenddate()

	def askenddate(self):
		r = re.compile("\d{4}/\d{2}/\d{2}")
		prompt = "Enter end date: (must be in format yyyy/mm/dd)\n==> "
		date = raw_input(prompt)
		if r.match(date) is None:
			print "Invalid date format.\n"
			time.sleep(0.15)
			self.askenddate()
		else:
			if int(date[0:4]) >= int(self.start_date[0:4]) and int(date[5:7]) >= int(self.start_date[5:7]) and int(date[8:]) >= int(self.start_date[8:]):
				print "Working...\n"
				time.sleep(0.15)
				self.end_date = date
			else:
				print "End date must be the same as, or after, the start date.\n"
				time.sleep(0.15)
				self.askenddate()
		self.askendtime()

	def askendtime(self):
		r = re.compile("\d{2}:\d{2}:\d{2}")
		prompt = "Enter end time: (must be in format hh:mm:ss)\n==> "
		e_time = raw_input(prompt)
		if r.match(e_time) is None:
			print "Invalid time format.\n"
			time.sleep(0.15)
			self.askendtime()
		else:
			if int(e_time[0:2]) >= int(self.start_time[0:2]) and int(e_time[3:5]) >= int(self.start_time[3:5]):
				print "Working...\n"
				time.sleep(0.15)
				self.end_time = e_time
			else:
				print "End time must be the same as, or after, the start time.\n"
				time.sleep(0.15)
				self.askendtime()
		self.askwavelength()

	def askwavelength(self):
		print "Available wavelengths (in angstroms) for %s instrument:\n%s" % (self.instrument, self.possible_wavelengths[self.instrument])
		prompt = "Enter desired wavelength: (an invalid wavelength will not return search results)\n==> "
		wave = raw_input(prompt)
		print "Working...\n"
		time.sleep(0.15)
		self.wavelength = wave
		self.querysearch()

	def querysearch(self):
		t = threading.Thread(target=self.wheel)
		t.start()
		self.search_results = Fido.search(a.Time("%sT%s" % (self.start_date, self.start_time), "%sT%s" % (self.end_date, self.end_time)), a.Instrument(self.instrument), a.Wavelength(float(self.wavelength) * u.angstrom))
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
