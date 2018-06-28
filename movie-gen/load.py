from sunpy.net.helioviewer import HelioviewerClient
import ssl
import os
import glob
from tqdm import tqdm, trange
import getpass
from datetime import timedelta
import sys

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

	def __init__(self, time, period, interval, observatory, instrument, detector, measurement, fps):
		ssl._create_default_https_context = ssl._create_unverified_context
		self.time = time
		self.period = period
		self.interval = interval
		self.observatory = observatory
		self.instrument = instrument
		self.detector = detector
		self.measurement = measurement
		self.fps = fps

	def processdata(self):
		clear = raw_input("Clear source folders? [y/n]\n==> ")
		if clear == "y":
			print "\nClearing source folders...\n"
			os.system("rm /Users/%s/Desktop/lmsal/movie-gen/source-images/*.jp2" % getpass.getuser())
			print ""
		else:
			print "\nPlease manually clear source folders.\n"
			sys.exit()

		ticker = 0

		for i in trange(self.period, desc = "LOADING DATA", smoothing = 1):
			f = self.hv.download_jp2("%s/%s/%s %s" % (self.time.date().year, self.time.date().month, self.time.date().day, str(self.time.time())), observatory = self.observatory, instrument = self.instrument, detector = self.detector, measurement = self.measurement)

			with open(f) as file:
				os.rename(f, "/Users/%s/Desktop/lmsal/movie-gen/source-images/img_%03d.jp2" % (getpass.getuser(), ticker))

			ticker += 1
			self.time = self.time + timedelta(minutes = self.interval)

		os.system("ffmpeg -f image2 -start_number 000 -framerate %s -i /Users/%s/Desktop/lmsal/movie-gen/source-images/img_%%3d.jp2 -pix_fmt yuv420p -s 2048x2048 /Users/%s/Desktop/lmsal/movie-gen/%s.mp4" % (self.fps, getpass.getuser(), getpass.getuser(), str(self.time.date())))

		print "\nDone. Saved to working directory.\n"
