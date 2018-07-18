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
		print "\nClearing source folders...\n"
		os.system("rm /Users/%s/Desktop/lmsal/resources/fulldisk-images/*.jp2" % getpass.getuser())

		for i in trange(self.period, desc = "LOADING DATA", smoothing = 1):
			f = self.hv.download_jp2("%s/%s/%s %s" % (self.time.date().year, self.time.date().month, self.time.date().day, str(self.time.time())), observatory = self.observatory, instrument = self.instrument, detector = self.detector, measurement = self.measurement)

			with open(f) as file:
				os.rename(f, "/Users/%s/Desktop/lmsal/resources/fulldisk-images/fulldisk%03d.jp2" % (getpass.getuser(), i))
			
			self.time = self.time + timedelta(minutes = self.interval)

		os.system("ffmpeg -y -f image2 -start_number 000 -framerate %s -i /Users/%s/Desktop/lmsal/resources/fulldisk-images/fulldisk%%3d.png -q:v 2 -vcodec mpeg4 -b:v 800k /Users/%s/Desktop/lmsal/fulldisk-video.mp4" % (self.fps, getpass.getuser(), getpass.getuser()))

		print "\nDONE: VIDEO SAVED TO /Users/%s/Desktop/lmsal" % getpass.getuser()
