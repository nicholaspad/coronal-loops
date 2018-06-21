import re

class Fetch(object):

	wavmes = {
		"aia" : ["94", "131", "171", "193", "211", "304", "335", "1600", "1700", "4500"],
		"hmi" : ["continuum", "magnetogram"]
	}

	def __init__(self):
		self.start_date = ""
		self.start_time = ""
		self.observatory = ""
		self.instrument = ""
		self.detector = ""
		self.measurement = ""
		self.interval = -1
		self.period = -1
		self.fps = -1


	def fetchdata(self):
		prompt = "\nEnter observatory: (e.g. sdo)\n==> "
		self.observatory = raw_input(prompt)
		prompt = "\nEnter instrument: (e.g. aia)\n==> "
		self.instrument = raw_input(prompt)
		self.detector = self.instrument
		self.askwavmes()
	
	def askwavmes(self):
		self.displaywavmes(self.instrument)
		prompt = "\nEnter wavelength/configuration:\n==> "
		measurement = raw_input(prompt)
		if(measurement in self.wavmes[self.instrument]):
			self.measurement = measurement
			self.askstartdate()
		else:
			print "\nWavelength/configuration not available."
			self.askwavmes()

	def askstartdate(self):
		r = re.compile("\d{4}/\d{2}/\d{2}")
		prompt = "\nEnter start date: (must be in format yyyy/mm/dd)\n==> "
		date = raw_input(prompt)
		if r.match(date) is None:
			print "\nInvalid date format."
			self.askstartdate()
		else:
			self.start_date = date
		self.askstarttime()

	def askstarttime(self):
		r = re.compile("\d{2}:\d{2}:\d{2}")
		prompt = "\nEnter start time: (must be in format hh:mm:ss)\n==> "
		s_time = raw_input(prompt)
		if r.match(s_time) is None:
			print "\nInvalid time format."
			self.askstarttime()
		else:
			self.start_time = s_time
		self.askother()

	def askother(self):		
		prompt = "\nEnter time interval in hours: (must be a positive whole number between 1 and 24, inclusive)\n==> "
		interval = int(raw_input(prompt))
		if interval <= 0 or interval >= 25:
			print "\nInvalid interval."
			self.askother()
		else:
			self.interval = interval

		while True:
			prompt = "\nEnter number of time intervals: (must be a positive whole number)\n==> "
			period = int(raw_input(prompt))
			if period <= 0:
				print "\nMust be a positive whole number."
			else:
				self.period = period
				break

		while True:
			prompt = "\nEnter desired frames per second: (default is 24)\n==> "
			fps = int(raw_input(prompt))
			if fps <= 0:
				print "\nMust be a positive whole number."
			else:
				self.fps = fps
				break

	def displaywavmes(self, instrument):
		print "\nPossibilities for %s instrument:\n" % self.instrument
		print self.wavmes[instrument]

	def getinfo(self):
		return [self.start_date, self.start_time, self.period, self.interval, self.observatory, self.instrument, self.detector, self.measurement, self.fps]
