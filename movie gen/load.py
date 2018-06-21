from sunpy.net.helioviewer import HelioviewerClient
import ssl
import os
import glob
from tqdm import trange
import getpass
from multiprocessing import Pool

class Load(object):

	hv = HelioviewerClient()
	month_lengths = {
		1 : 31,
		2 : 28,
		3 : 31,
		4 : 30,
		5 : 31,
		6 : 30,
		7 : 31,
		8 : 31,
		9 : 30,
		10 : 31,
		11 : 30,
		12 : 31
	}

	def __init__(self, start_date, start_time, period, interval, observatory, instrument, detector, measurement):
		ssl._create_default_https_context = ssl._create_unverified_context
		self.start_date = start_date
		self.start_time = start_time
		self.period = period
		self.interval = interval
		self.observatory = observatory
		self.instrument = instrument
		self.detector = detector
		self.measurement = measurement

	def loaddata(self):
		hour = int(self.start_time[0:2])
		day = int(self.start_date[8:])
		month = int(self.start_date[5:7])
		year = int(self.start_date[0:4])
		ticker = 1

		for i in trange(self.period, desc = "LOADING FILES"):
			self.hv.download_jp2("%d/%02d/%02d %02d:00:00" % (year, month, day, hour), observatory = self.observatory, instrument = self.instrument, detector = self.detector, measurement = self.measurement)

			files = glob.glob("/Users/%s/sunpy/data/*.jp2" % getpass.getuser())
			interest = max(files, key = os.path.getctime)

			os.rename(interest, "/Users/%s/Desktop/lmsal/movie gen/source images/source_%03d.jp2" % (getpass.getuser(), ticker))
			ticker += 1

			if (hour + self.interval) >= 24:
				hour = (hour + self.interval) % 24
				if (day + 1) > self.month_lengths[month]:
					day = 1
					if (month + 1) > 12:
						month = 1
						year += 1
					else:
						months += 1
				else:
					day += 1
			else:
				hour += self.interval

		print "\nFiles loaded. Processing starting...\n"
