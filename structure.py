import warnings
warnings.filterwarnings("ignore", message = "From scipy 0.13.0, the output shape of")
warnings.filterwarnings("ignore", message = "invalid value encountered in greater")
warnings.filterwarnings("ignore", message = "invalid value encountered in less")
warnings.filterwarnings("ignore", message = "numpy.dtype size changed")

from IPython.core import debugger; debug = debugger.Pdb().set_trace
from os import listdir
from os.path import isfile, join
from recorder import Recorder
from sunpy.map import Map
from tqdm import tqdm
import astropy.units as u
import matplotlib.pyplot as plt
import numpy as np
import os

RECORDER = Recorder()
RECORDER.display_start_time("structure")

RECORDER.sys_text("Importing data directories")
SAVEPATH = "data/outputs/"
PATH94 = "data/AIA94/"
PATH131 = "data/AIA131/"
PATH171 = "data/AIA171/"
PATH193 = "data/AIA193/"
PATH211 = "data/AIA211/"
PATH304 = "data/AIA304/"
PATH335 = "data/AIA335/"

DIR94 = [f for f in listdir(PATH94) if isfile(join(PATH94, f))]
DIR131 = [f for f in listdir(PATH131) if isfile(join(PATH131, f))]
DIR171 = [f for f in listdir(PATH171) if isfile(join(PATH171, f))]
DIR193 = [f for f in listdir(PATH193) if isfile(join(PATH193, f))]
DIR211 = [f for f in listdir(PATH211) if isfile(join(PATH211, f))]
DIR304 = [f for f in listdir(PATH304) if isfile(join(PATH304, f))]
DIR335 = [f for f in listdir(PATH335) if isfile(join(PATH335, f))]

DIR94.sort()
DIR131.sort()
DIR171.sort()
DIR193.sort()
DIR211.sort()
DIR304.sort()
DIR335.sort()

DIR94 = DIR94[1:]
DIR131 = DIR131[1:]
DIR171 = DIR171[1:]
DIR193 = DIR193[1:]
DIR211 = DIR211[1:]
DIR304 = DIR304[1:]
DIR335 = DIR335[1:]

N = len(DIR94)

for K in tqdm(range(24), desc = "Working"):
	RECORDER.sys_text("Importing FITS data")
	K94 = Map(PATH94 + DIR94[K])
	K131 = Map(PATH131 + DIR131[K])
	K171 = Map(PATH171 + DIR171[K])
	K193 = Map(PATH193 + DIR193[K])
	K211 = Map(PATH211 + DIR211[K])
	K304 = Map(PATH304 + DIR304[K])
	K335 = Map(PATH335 + DIR335[K])

	RECORDER.info_text("Current datetime - %s" % K94.date)
	
	RECORDER.info_text("Reading raw image data")
	D94 = K94.data
	D131 = K131.data
	D171 = K171.data
	D193 = K193.data
	D211 = K211.data
	D304 = K304.data
	D335 = K335.data

	RECORDER.info_text("Correcting raw image data")
	corrected_D94 = np.sqrt(np.abs(D94)) / K94.exposure_time.value
	corrected_D131 = np.sqrt(np.abs(D131)) / K131.exposure_time.value
	corrected_D171 = np.sqrt(np.abs(D171)) / K171.exposure_time.value
	corrected_D193 = np.sqrt(np.abs(D193)) / K193.exposure_time.value
	corrected_D211 = np.sqrt(np.abs(D211)) / K211.exposure_time.value
	corrected_D304 = np.sqrt(np.abs(D304)) / K304.exposure_time.value
	corrected_D335 = np.sqrt(np.abs(D335)) / K335.exposure_time.value

	RECORDER.sys_text("Exporting corrected raw images")
	plt.imsave(SAVEPATH + "raw/AIA94/raw_%04d" % K, corrected_D94, origin = "lower", cmap = "sdoaia94", vmin = 0, vmax = 15)
	plt.imsave(SAVEPATH + "raw/AIA131/raw_%04d" % K, corrected_D131, origin = "lower", cmap = "sdoaia131", vmin = 0, vmax = 18)
	plt.imsave(SAVEPATH + "raw/AIA171/raw_%04d" % K, corrected_D171, origin = "lower", cmap = "sdoaia171", vmin = 0, vmax = 40)
	plt.imsave(SAVEPATH + "raw/AIA193/raw_%04d" % K, corrected_D193, origin = "lower", cmap = "sdoaia193", vmin = 0, vmax = 45)
	plt.imsave(SAVEPATH + "raw/AIA211/raw_%04d" % K, corrected_D211, origin = "lower", cmap = "sdoaia211", vmin = 0, vmax = 30)
	plt.imsave(SAVEPATH + "raw/AIA304/raw_%04d" % K, corrected_D304, origin = "lower", cmap = "sdoaia304", vmin = 0, vmax = 25)
	plt.imsave(SAVEPATH + "raw/AIA335/raw_%04d" % K, corrected_D335, origin = "lower", cmap = "sdoaia335", vmin = 0, vmax = 12)

	# RECORDER.info_text("Generating binary-masked images")

	# LBS = 400
	# r_mask = np.logical_and(img304 > LBS, img304 < np.inf)
	# r_mask = r_mask.astype(np.uint8)
	# r_mask = cv.dilate(r_mask, np.ones((3,3)).astype(bool).astype(int), iterations = 1)

	# img304 *= r_mask

	RECORDER.info_text("===== Processing completed on image %04d =====" % K)

	"""
	1. Corrected raw images [X]
	2. Binary masked images
	3. Contour masked images
	4. Structural images
	"""

FPS = 24

RECORDER.sys_text("Generating raw videos")
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sraw/AIA94/raw_%%04d.png -q:v 2 -vcodec mpeg4 -b:v 800k %sraw/AIA94_raw.mp4" % (FPS, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sraw/AIA131/raw_%%04d.png -q:v 2 -vcodec mpeg4 -b:v 800k %sraw/AIA131_raw.mp4" % (FPS, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sraw/AIA171/raw_%%04d.png -q:v 2 -vcodec mpeg4 -b:v 800k %sraw/AIA171_raw.mp4" % (FPS, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sraw/AIA193/raw_%%04d.png -q:v 2 -vcodec mpeg4 -b:v 800k %sraw/AIA193_raw.mp4" % (FPS, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sraw/AIA211/raw_%%04d.png -q:v 2 -vcodec mpeg4 -b:v 800k %sraw/AIA211_raw.mp4" % (FPS, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sraw/AIA304/raw_%%04d.png -q:v 2 -vcodec mpeg4 -b:v 800k %sraw/AIA304_raw.mp4" % (FPS, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sraw/AIA335/raw_%%04d.png -q:v 2 -vcodec mpeg4 -b:v 800k %sraw/AIA335_raw.mp4" % (FPS, SAVEPATH, SAVEPATH))

RECORDER.sys_text("Generating binary-mask videos")
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sbinary/AIA94/raw_%%04d.png -q:v 2 -vcodec mpeg4 -b:v 800k %sbinary/AIA94_binary.mp4" % (FPS, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sbinary/AIA131/raw_%%04d.png -q:v 2 -vcodec mpeg4 -b:v 800k %sbinary/AIA131_binary.mp4" % (FPS, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sbinary/AIA171/raw_%%04d.png -q:v 2 -vcodec mpeg4 -b:v 800k %sbinary/AIA171_binary.mp4" % (FPS, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sbinary/AIA193/raw_%%04d.png -q:v 2 -vcodec mpeg4 -b:v 800k %sbinary/AIA193_binary.mp4" % (FPS, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sbinary/AIA211/raw_%%04d.png -q:v 2 -vcodec mpeg4 -b:v 800k %sbinary/AIA211_binary.mp4" % (FPS, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sbinary/AIA304/raw_%%04d.png -q:v 2 -vcodec mpeg4 -b:v 800k %sbinary/AIA304_binary.mp4" % (FPS, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sbinary/AIA335/raw_%%04d.png -q:v 2 -vcodec mpeg4 -b:v 800k %sbinary/AIA335_binary.mp4" % (FPS, SAVEPATH, SAVEPATH))

RECORDER.display_end_time("structure")
