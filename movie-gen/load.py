from sunpy.net.helioviewer import HelioviewerClient
import ssl
import os
import glob
from tqdm import tqdm, trange
import getpass

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

	def __init__(self, start_date, start_time, period, interval, observatory, instrument, detector, measurement, fps):
		ssl._create_default_https_context = ssl._create_unverified_context
		self.start_date = start_date
		self.start_time = start_time
		self.period = period
		self.interval = interval
		self.observatory = observatory
		self.instrument = instrument
		self.detector = detector
		self.measurement = measurement
		self.fps = fps

	def loadandgendata(self):
		hour = int(self.start_time[0:2])
		day = int(self.start_date[8:])
		month = int(self.start_date[5:7])
		year = int(self.start_date[0:4])

		print "\nClearing source folders...\n"
		os.system("rm /Users/%s/Desktop/lmsal/movie-gen/source-images/*.jp2" % getpass.getuser())

		ticker = 0

		for i in trange(self.period, desc = "WORKING"):
			f = self.hv.download_jp2("%d/%02d/%02d %02d:00:00" % (year, month, day, hour), observatory = self.observatory, instrument = self.instrument, detector = self.detector, measurement = self.measurement)

			with open(f) as file:
				os.rename(f, "/Users/%s/Desktop/lmsal/movie-gen/source-images/img_%03d.jp2" % (getpass.getuser(), ticker))

			ticker += 1

			if (hour + self.interval) >= 24:
				hour = (hour + self.interval) % 24
				if (day + 1) > self.month_lengths[month]:
					day = 1
					if (month + 1) > 12:
						month = 1
						year += 1
					else:
						month += 1
				else:
					day += 1
			else:
				hour += self.interval

		print "\nFiles loaded and resized. Generating movie...\n"

		os.system("ffmpeg -f image2 -start_number 000 -framerate %s -i /Users/%s/Desktop/lmsal/movie-gen/source-images/img_%%3d.jp2 -pix_fmt yuv420p -s 1024x1024 /Users/%s/Desktop/lmsal/movie-gen/output.mp4" % (self.fps, getpass.getuser(), getpass.getuser()))

		print "\nMovie generated and saved to working directory. Clearing source folders..."

		os.system("rm /Users/%s/Desktop/lmsal/movie-gen/source-images/*.jp2" % getpass.getuser())

		print "\nDone.\n"
