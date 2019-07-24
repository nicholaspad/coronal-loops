import warnings
warnings.filterwarnings("ignore", message = "divide by zero encountered in log")
warnings.filterwarnings("ignore", message = "From scipy 0.13.0, the output shape of")
warnings.filterwarnings("ignore", message = "invalid value encountered in greater")
warnings.filterwarnings("ignore", message = "invalid value encountered in less")
warnings.filterwarnings("ignore", message = "invalid value encountered in log")
warnings.filterwarnings("ignore", message = "invalid value encountered in multiply")
warnings.filterwarnings("ignore", message = "numpy.dtype size changed")

from IPython.core import debugger; debug = debugger.Pdb().set_trace
from matplotlib.colors import LogNorm
from matplotlib.path import Path
from os import listdir
from os.path import isfile, join
from PIL import Image, ImageEnhance
from recorder import Recorder
from scipy import ndimage
from scipy.stats import iqr
from skimage import feature
from skimage import measure
from sunpy.map import Map
from timeit import default_timer as timer
from tqdm import tqdm
import argparse
import astropy.units as u
import cv2 as cv
import imageio
import matplotlib.pyplot as plt
import numpy as np
import os

RECORDER = Recorder()
RECORDER.display_start_time("structure")

parser = argparse.ArgumentParser()
parser.add_argument("--cleardirs", nargs = "?", const = True, type = bool)
args = parser.parse_args()

RECORDER.sys_text("Importing data directories")
SAVEPATH = "data/outputs/"
PATH131 = "data/AIA131/"; PATH171 = "data/AIA171/"; PATH193 = "data/AIA193/"; PATH211 = "data/AIA211/"; PATH304 = "data/AIA304/"; PATH335 = "data/AIA335/"; PATHHMI = "data/HMI/"

DIR131 = [f for f in listdir(PATH131) if isfile(join(PATH131, f))]; DIR131.sort()
DIR171 = [f for f in listdir(PATH171) if isfile(join(PATH171, f))]; DIR171.sort()
DIR193 = [f for f in listdir(PATH193) if isfile(join(PATH193, f))]; DIR193.sort()
DIR211 = [f for f in listdir(PATH211) if isfile(join(PATH211, f))]; DIR211.sort()
DIR304 = [f for f in listdir(PATH304) if isfile(join(PATH304, f))]; DIR304.sort()
DIR335 = [f for f in listdir(PATH335) if isfile(join(PATH335, f))]; DIR335.sort()
DIRHMI = [f for f in listdir(PATHHMI) if isfile(join(PATHHMI, f))]; DIRHMI.sort()

if DIR131[0] == ".DS_Store":
	DIR131 = DIR131[1:]
if DIR171[0] == ".DS_Store":
	DIR171 = DIR171[1:]
if DIR193[0] == ".DS_Store":
	DIR193 = DIR193[1:]
if DIR211[0] == ".DS_Store":
	DIR211 = DIR211[1:]
if DIR304[0] == ".DS_Store":
	DIR304 = DIR304[1:]
if DIR335[0] == ".DS_Store":
	DIR335 = DIR335[1:]
if DIRHMI[0] == ".DS_Store":
	DIRHMI = DIRHMI[1:]

K131 = []; t131 = []
K171 = []; t171 = []
K193 = []; t193 = []
K211 = []; t211 = []
K304 = []; t304 = []
K335 = []; t335 = []
KHMI = []

if args.cleardirs:
	RECORDER.sys_text("Clearing image directories")
	os.system("rm %sraw/AIA131/*" % SAVEPATH); os.system("rm %senhanced/AIA131/*" % SAVEPATH); os.system("rm %sedge/AIA131/*" % SAVEPATH); os.system("rm %sbinary/AIA131/*" % SAVEPATH)
	os.system("rm %sraw/AIA171/*" % SAVEPATH); os.system("rm %senhanced/AIA171/*" % SAVEPATH); os.system("rm %sedge/AIA171/*" % SAVEPATH); os.system("rm %sbinary/AIA171/*" % SAVEPATH)
	os.system("rm %sraw/AIA193/*" % SAVEPATH); os.system("rm %senhanced/AIA193/*" % SAVEPATH); os.system("rm %sedge/AIA193/*" % SAVEPATH); os.system("rm %sbinary/AIA193/*" % SAVEPATH)
	os.system("rm %sraw/AIA211/*" % SAVEPATH); os.system("rm %senhanced/AIA211/*" % SAVEPATH); os.system("rm %sedge/AIA211/*" % SAVEPATH); os.system("rm %sbinary/AIA211/*" % SAVEPATH)
	os.system("rm %sraw/AIA304/*" % SAVEPATH); os.system("rm %senhanced/AIA304/*" % SAVEPATH); os.system("rm %sedge/AIA304/*" % SAVEPATH); os.system("rm %sbinary/AIA304/*" % SAVEPATH)
	os.system("rm %sraw/AIA335/*" % SAVEPATH); os.system("rm %senhanced/AIA335/*" % SAVEPATH); os.system("rm %sedge/AIA335/*" % SAVEPATH); os.system("rm %sbinary/AIA335/*" % SAVEPATH)
	os.system("rm %sraw/HMI/*" % SAVEPATH); os.system("rm %senhanced/HMI/*" % SAVEPATH); os.system("rm %sedge/HMI/*" % SAVEPATH); os.system("rm %sbinary/HMI/*" % SAVEPATH)
	RECORDER.sys_text("Image directories successfully emptied")

def print_raw_info(fits, avg):
	tqdm.write("\t\t\t%s %s %d" % (fits.observatory, fits.detector, int(fits.measurement.value)))
	tqdm.write("\t\t\tDatetime:\t%s" % (fits.date))
	tqdm.write("\t\t\tExposure time:\t%s s" % (fits.exposure_time.value))
	tqdm.write("\t\t\tLocation:\t(%d, %d) arcsec" % ((fits.top_right_coord.Tx.value + fits.bottom_left_coord.Tx.value) / 2, (fits.top_right_coord.Ty.value + fits.bottom_left_coord.Ty.value) / 2))
	tqdm.write("\t\t\tMed val:\t%.3f" % (np.median(fits.data)))
	tqdm.write("\t\t\tRunning med:\t%.3f" % avg)

def print_sdata(sx, sy, e):
	sx = sx.round(decimals = 1)
	sy = sy.round(decimals = 1)
	e = e.round(decimals = 1)
	tqdm.write("\n\t*** sobel_x ***")
	tqdm.write("%s" % sx)
	tqdm.write("\n\t*** sobel_y ***")
	tqdm.write("%s" % sy)
	tqdm.write("\n\t*** sobel_hypot ***")
	tqdm.write("%s" % e)
	tqdm.write("\tMed sobel_hypot val:\t%.3f\n" % (np.median(e)))

def print_bin_info(img):
	blackcount = np.count_nonzero(img == 0)/4.
	blackpercent = 100. * blackcount / 650.**2
	tqdm.write("\t\t\t%d (%.2f%%) pixels masked" % (blackcount, blackpercent))

def print_dist(meds, iqrs):
	print "\t\t\t====================="
	print "\t\t\tID\tMED\tIQR"
	print "\t\t\t131\t%.3f\t%.3f" % (meds[0], iqrs[0])
	print "\t\t\t171\t%.3f\t%.3f" % (meds[1], iqrs[1])
	print "\t\t\t193\t%.3f\t%.3f" % (meds[2], iqrs[2])
	print "\t\t\t211\t%.3f\t%.3f" % (meds[3], iqrs[3])
	print "\t\t\t304\t%.3f\t%.3f" % (meds[4], iqrs[4])
	print "\t\t\t335\t%.3f\t%.3f" % (meds[5], iqrs[5])
	print "\t\t\t====================="

def rgb2gray(rgb):
	return np.dot(rgb[...,:3], [0.2989, 0.5870, 0.1140])

def make_raw_img(map, data, wav, id, vmax):
	plt.imsave("%sraw/AIA%d/raw_%04d" % (SAVEPATH, wav, id), tempdata, cmap = "sdoaia%d" % wav, vmin = 2, vmax = vmax, origin = "lower")
	RECORDER.info_text("%sraw/AIA%d/raw_%04d saved" % (SAVEPATH, wav, id))
	print_raw_info(map, vmax)

def make_enh_img(sx, sy, wav, id, vmax):
	e = np.hypot(sx, sy)
	print_sdata(sx, sy, e)
	# MORE ENHANCEMENT
	if wav == 171:
		debug()
	plt.imsave("%senhanced/AIA%d/enhanced_%04d" % (SAVEPATH, wav, id), e, cmap = "sdoaia%d" % wav, vmin = 5, vmax = vmax, origin = "lower")
	RECORDER.info_text("%senhanced/AIA%d/enhanced_%04d saved" % (SAVEPATH, wav, id))

def make_bin_img(img, wav, id, lowpercentile, highpercentile=100.):
	inten_ar = rgb2gray(img)
	low_cut = np.percentile(inten_ar, lowpercentile)
	high_cut = np.percentile(inten_ar, highpercentile)
	inten_ar[inten_ar <= low_cut] = 0.
	inten_ar[inten_ar >= high_cut] = 0.
	inten_ar[inten_ar != 0] = 1.
	plt.imsave("%sbinary/AIA%d/binary_%04d" % (SAVEPATH, wav, id), inten_ar, cmap = "gray")
	RECORDER.info_text("%sbinary/AIA%d/binary_%04d saved" % (SAVEPATH, wav, id))
	print_bin_info(inten_ar)

##### ----- #####
##### ----- #####
N = 1
##### ----- #####
##### ----- #####

C = 0.6
med_131 = []; med_171 = []; med_193 = []; med_211 = []; med_304 = []; med_335 = []

for K in tqdm(range(N), desc = "Generating raw images"):
	temp = Map(PATH131 + DIR131[K])
	RECORDER.sys_text("|===================== Processing datetime %s =====================|" % temp.date)
	K131.append([temp.data, temp.exposure_time.value, temp.date, temp.meta])
	tempdata = K131[-1][0] / K131[-1][1]
	med_131.append(tempdata.max())
	if len(med_131) == 16:
		med_131.pop(0)
	make_raw_img(temp, tempdata, 131, K, C * np.median(med_131))

	temp = Map(PATH171 + DIR171[K])
	K171.append([temp.data, temp.exposure_time.value, temp.date, temp.meta])
	tempdata = K171[-1][0] / K171[-1][1]
	med_171.append(tempdata.max())
	if len(med_171) == 16:
		med_171.pop(0)
	make_raw_img(temp, tempdata, 171, K, C * np.median(med_171))

	temp = Map(PATH193 + DIR193[K])
	K193.append([temp.data, temp.exposure_time.value, temp.date, temp.meta])
	tempdata = K193[-1][0] / K193[-1][1]
	med_193.append(tempdata.max())
	if len(med_193) == 16:
		med_193.pop(0)
	make_raw_img(temp, tempdata, 193, K, C * np.median(med_193))

	temp = Map(PATH211 + DIR211[K])
	K211.append([temp.data, temp.exposure_time.value, temp.date, temp.meta])
	tempdata = K211[-1][0] / K211[-1][1]
	med_211.append(tempdata.max())
	if len(med_211) == 16:
		med_211.pop(0)
	make_raw_img(temp, tempdata, 211, K, C * np.median(med_211))

	temp = Map(PATH304 + DIR304[K])
	K304.append([temp.data, temp.exposure_time.value, temp.date, temp.meta])
	tempdata = K304[-1][0] / K304[-1][1]
	med_304.append(tempdata.max())
	if len(med_304) == 16:
		med_304.pop(0)
	make_raw_img(temp, tempdata, 304, K, C * np.median(med_304))

	temp = Map(PATH335 + DIR335[K])
	K335.append([temp.data, temp.exposure_time.value, temp.date, temp.meta])
	tempdata = K335[-1][0] / K335[-1][1]
	med_335.append(tempdata.max())
	if len(med_335) == 16:
		med_335.pop(0)
	make_raw_img(temp, tempdata, 335, K, C * np.median(med_335))

	tempdata = Map(PATHHMI + DIRHMI[K]).data
	KHMI.append(tempdata)
	plt.imsave("%sraw/HMI/raw_%04d" % (SAVEPATH, K), tempdata, cmap = "gray", vmin = -125, vmax = 125, origin = "lower")
	RECORDER.info_text("%sraw/HMI/raw_%04d saved" % (SAVEPATH, K))

for K in tqdm(range(N), desc = "Generating intensity distribution"):
	if K131[K][1] > 0:
		t131 = np.append(t131, np.median(K131[K][0] / K131[K][1]))
	if K171[K][1] > 0:
		t171 = np.append(t171, np.median(K171[K][0] / K171[K][1]))
	if K193[K][1] > 0:
		t193 = np.append(t193, np.median(K193[K][0] / K193[K][1]))
	if K211[K][1] > 0:
		t211 = np.append(t211, np.median(K211[K][0] / K211[K][1]))
	if K304[K][1] > 0:
		t304 = np.append(t304, np.median(K304[K][0] / K304[K][1]))
	if K335[K][1] > 0:
		t335 = np.append(t335, np.median(K335[K][0] / K335[K][1]))

meds = [np.median(t131), np.median(t171), np.median(t193), np.median(t211), np.median(t304), np.median(t335)]
iqrs = [iqr(t131), iqr(t171), iqr(t193), iqr(t211), iqr(t304), iqr(t335)]
print_dist(meds, iqrs)

for K in tqdm(range(N), desc = "Generating enhanced images"):
	RECORDER.sys_text("|===================== Processing datetime %s (#%d) =====================|" % (K131[K][2], K))

	sx = ndimage.sobel(K131[K][0], axis = 0, mode = "constant")
	sy = ndimage.sobel(K131[K][0], axis = 1, mode = "constant")
	make_enh_img(sx, sy, 131, K, 125)

	sx = ndimage.sobel(K171[K][0], axis = 0, mode = "constant")
	sy = ndimage.sobel(K171[K][0], axis = 1, mode = "constant")
	make_enh_img(sx, sy, 171, K, 1100)

	sx = ndimage.sobel(K193[K][0], axis = 0, mode = "constant")
	sy = ndimage.sobel(K193[K][0], axis = 1, mode = "constant")
	make_enh_img(sx, sy, 193, K, 1250)

	sx = ndimage.sobel(K211[K][0], axis = 0, mode = "constant")
	sy = ndimage.sobel(K211[K][0], axis = 1, mode = "constant")
	make_enh_img(sx, sy, 211, K, 815)

	sx = ndimage.sobel(K304[K][0], axis = 0, mode = "constant")
	sy = ndimage.sobel(K304[K][0], axis = 1, mode = "constant")
	make_enh_img(sx, sy, 304, K, 615)

	sx = ndimage.sobel(K335[K][0], axis = 0, mode = "constant")
	sy = ndimage.sobel(K335[K][0], axis = 1, mode = "constant")
	make_enh_img(sx, sy, 335, K, 210)

	hmi_absthresh_mask = np.logical_or(KHMI[K] > 600, KHMI[K] < -600)
	KHMI.append(hmi_absthresh_mask)
	hmi_thresh_data = hmi_absthresh_mask * KHMI[K]
	# debug()
	plt.imsave("%senhanced/HMI/enhanced_%04d" % (SAVEPATH, K), hmi_thresh_data, cmap = "gray", vmin = -125, vmax = 125, origin = "lower")
	RECORDER.info_text("%senhanced/HMI/enhanced_%04d saved" % (SAVEPATH, K))

# percentile corresponding to 50:
# 85.4, 85.9, 89.65, 91.55, 96.18, 99.65

for K in tqdm(range(N), desc = "Generating binary images"):
	img = imageio.imread("%senhanced/AIA131/enhanced_%04d.png" % (SAVEPATH, K))
	make_bin_img(img, 131, K, 94.4 - 0.02*K)

	img = imageio.imread("%senhanced/AIA171/enhanced_%04d.png" % (SAVEPATH, K))
	make_bin_img(img, 171, K, 94.9 - 0.02*K)

	img = imageio.imread("%senhanced/AIA193/enhanced_%04d.png" % (SAVEPATH, K))
	make_bin_img(img, 193, K, 95.4 - 0.02*K)

	img = imageio.imread("%senhanced/AIA211/enhanced_%04d.png" % (SAVEPATH, K))
	make_bin_img(img, 211, K, 96.1 - 0.02*K)

	img = imageio.imread("%senhanced/AIA304/enhanced_%04d.png" % (SAVEPATH, K))
	make_bin_img(img, 304, K, 97.2 - 0.02*K)

	img = imageio.imread("%senhanced/AIA335/enhanced_%04d.png" % (SAVEPATH, K))
	make_bin_img(img, 335, K, 99.6 - 0.02*K)

	plt.imsave("%sbinary/HMI/binary_%04d" % (SAVEPATH, K), KHMI[K], cmap = "gray", origin = "lower")
	RECORDER.info_text("%sbinary/HMI/binary_%04d saved" % (SAVEPATH, K))

for K in tqdm(range(N), desc = "Generating traced images"):
	pass

FPS = 24

RECORDER.sys_text("|================ Generating raw videos =====================|")
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sraw/AIA131/raw_%%04d.png -vframes %d -q:v 2 -vcodec mpeg4 -b:v 800k %sraw/AIA131_raw.mp4" % (FPS, SAVEPATH, N, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sraw/AIA171/raw_%%04d.png -vframes %d -q:v 2 -vcodec mpeg4 -b:v 800k %sraw/AIA171_raw.mp4" % (FPS, SAVEPATH, N, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sraw/AIA193/raw_%%04d.png -vframes %d -q:v 2 -vcodec mpeg4 -b:v 800k %sraw/AIA193_raw.mp4" % (FPS, SAVEPATH, N, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sraw/AIA211/raw_%%04d.png -vframes %d -q:v 2 -vcodec mpeg4 -b:v 800k %sraw/AIA211_raw.mp4" % (FPS, SAVEPATH, N, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sraw/AIA304/raw_%%04d.png -vframes %d -q:v 2 -vcodec mpeg4 -b:v 800k %sraw/AIA304_raw.mp4" % (FPS, SAVEPATH, N, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sraw/AIA335/raw_%%04d.png -vframes %d -q:v 2 -vcodec mpeg4 -b:v 800k %sraw/AIA335_raw.mp4" % (FPS, SAVEPATH, N, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sraw/HMI/raw_%%04d.png -vframes %d -q:v 2 -vcodec mpeg4 -b:v 800k %sraw/HMI_raw.mp4" % (FPS, SAVEPATH, N, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -i %sraw/AIA131_raw.mp4 -i %sraw/AIA171_raw.mp4 -i %sraw/AIA193_raw.mp4 -i %sraw/AIA211_raw.mp4 -i %sraw/AIA304_raw.mp4 -i %sraw/AIA335_raw.mp4 -i %sraw/HMI_raw.mp4 -filter_complex hstack=inputs=7 %sraw/COMBINED_raw.mp4" % (SAVEPATH, SAVEPATH, SAVEPATH, SAVEPATH, SAVEPATH, SAVEPATH, SAVEPATH, SAVEPATH))

RECORDER.sys_text("|================ Generating enhanced videos ================|")
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %senhanced/AIA131/enhanced_%%04d.png -vframes %d -q:v 2 -vcodec mpeg4 -b:v 800k %senhanced/AIA131_enhanced.mp4" % (FPS, SAVEPATH, N, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %senhanced/AIA171/enhanced_%%04d.png -vframes %d -q:v 2 -vcodec mpeg4 -b:v 800k %senhanced/AIA171_enhanced.mp4" % (FPS, SAVEPATH, N, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %senhanced/AIA193/enhanced_%%04d.png -vframes %d -q:v 2 -vcodec mpeg4 -b:v 800k %senhanced/AIA193_enhanced.mp4" % (FPS, SAVEPATH, N, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %senhanced/AIA211/enhanced_%%04d.png -vframes %d -q:v 2 -vcodec mpeg4 -b:v 800k %senhanced/AIA211_enhanced.mp4" % (FPS, SAVEPATH, N, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %senhanced/AIA304/enhanced_%%04d.png -vframes %d -q:v 2 -vcodec mpeg4 -b:v 800k %senhanced/AIA304_enhanced.mp4" % (FPS, SAVEPATH, N, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %senhanced/AIA335/enhanced_%%04d.png -vframes %d -q:v 2 -vcodec mpeg4 -b:v 800k %senhanced/AIA335_enhanced.mp4" % (FPS, SAVEPATH, N, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %senhanced/HMI/enhanced_%%04d.png -vframes %d -q:v 2 -vcodec mpeg4 -b:v 800k %senhanced/HMI_enhanced.mp4" % (FPS, SAVEPATH, N, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -i %senhanced/AIA131_enhanced.mp4 -i %senhanced/AIA171_enhanced.mp4 -i %senhanced/AIA193_enhanced.mp4 -i %senhanced/AIA211_enhanced.mp4 -i %senhanced/AIA304_enhanced.mp4 -i %senhanced/AIA335_enhanced.mp4 -i %senhanced/HMI_enhanced.mp4 -filter_complex hstack=inputs=7 %senhanced/COMBINED_enhanced.mp4" % (SAVEPATH, SAVEPATH, SAVEPATH, SAVEPATH, SAVEPATH, SAVEPATH, SAVEPATH, SAVEPATH))

RECORDER.sys_text("|================ Generating binary videos ==================|")
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sbinary/AIA131/binary_%%04d.png -vframes %d -q:v 2 -vcodec mpeg4 -b:v 800k %sbinary/AIA131_binary.mp4" % (FPS, SAVEPATH, N, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sbinary/AIA171/binary_%%04d.png -vframes %d -q:v 2 -vcodec mpeg4 -b:v 800k %sbinary/AIA171_binary.mp4" % (FPS, SAVEPATH, N, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sbinary/AIA193/binary_%%04d.png -vframes %d -q:v 2 -vcodec mpeg4 -b:v 800k %sbinary/AIA193_binary.mp4" % (FPS, SAVEPATH, N, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sbinary/AIA211/binary_%%04d.png -vframes %d -q:v 2 -vcodec mpeg4 -b:v 800k %sbinary/AIA211_binary.mp4" % (FPS, SAVEPATH, N, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sbinary/AIA304/binary_%%04d.png -vframes %d -q:v 2 -vcodec mpeg4 -b:v 800k %sbinary/AIA304_binary.mp4" % (FPS, SAVEPATH, N, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sbinary/AIA335/binary_%%04d.png -vframes %d -q:v 2 -vcodec mpeg4 -b:v 800k %sbinary/AIA335_binary.mp4" % (FPS, SAVEPATH, N, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sbinary/HMI/binary_%%04d.png -vframes %d -q:v 2 -vcodec mpeg4 -b:v 800k %sbinary/HMI_binary.mp4" % (FPS, SAVEPATH, N, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -i %sbinary/AIA131_binary.mp4 -i %sbinary/AIA171_binary.mp4 -i %sbinary/AIA193_binary.mp4 -i %sbinary/AIA211_binary.mp4 -i %sbinary/AIA304_binary.mp4 -i %sbinary/AIA335_binary.mp4 -i %sbinary/HMI_binary.mp4 -filter_complex hstack=inputs=7 %sbinary/COMBINED_binary.mp4" % (SAVEPATH, SAVEPATH, SAVEPATH, SAVEPATH, SAVEPATH, SAVEPATH, SAVEPATH, SAVEPATH))

RECORDER.sys_text("|================ Generating stacked video ================|")
os.system("ffmpeg -loglevel panic -y -i %sraw/COMBINED_raw.mp4 -i %senhanced/COMBINED_enhanced.mp4 -i %sbinary/COMBINED_binary.mp4 -filter_complex vstack=inputs=3 %s/STACKED.mp4" % (SAVEPATH, SAVEPATH, SAVEPATH, SAVEPATH))

# RECORDER.sys_text("|================ Generating edge videos ====================|")
# os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sedge/AIA94/edge_%%04d.png -vframes %d -q:v 2 -vcodec mpeg4 -b:v 800k %sedge/AIA94_edge.mp4" % (FPS, SAVEPATH, N, SAVEPATH))
# os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sedge/AIA131/edge_%%04d.png -vframes %d -q:v 2 -vcodec mpeg4 -b:v 800k %sedge/AIA131_edge.mp4" % (FPS, SAVEPATH, N, SAVEPATH))
# os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sedge/AIA171/edge_%%04d.png -vframes %d -q:v 2 -vcodec mpeg4 -b:v 800k %sedge/AIA171_edge.mp4" % (FPS, SAVEPATH, N, SAVEPATH))
# os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sedge/AIA193/edge_%%04d.png -vframes %d -q:v 2 -vcodec mpeg4 -b:v 800k %sedge/AIA193_edge.mp4" % (FPS, SAVEPATH, N, SAVEPATH))
# os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sedge/AIA211/edge_%%04d.png -vframes %d -q:v 2 -vcodec mpeg4 -b:v 800k %sedge/AIA211_edge.mp4" % (FPS, SAVEPATH, N, SAVEPATH))
# os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sedge/AIA304/edge_%%04d.png -vframes %d -q:v 2 -vcodec mpeg4 -b:v 800k %sedge/AIA304_edge.mp4" % (FPS, SAVEPATH, N, SAVEPATH))
# os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sedge/AIA335/edge_%%04d.png -vframes %d -q:v 2 -vcodec mpeg4 -b:v 800k %sedge/AIA335_edge.mp4" % (FPS, SAVEPATH, N, SAVEPATH))

# os.system("ffmpeg -loglevel panic -y -i %sedge/AIA94_edge.mp4 -i %sedge/AIA131_edge.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast %sedge/temp1.mp4" % (SAVEPATH, SAVEPATH, SAVEPATH))
# os.system("ffmpeg -loglevel panic -y -i %sedge/AIA171_edge.mp4 -i %sedge/AIA193_edge.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast %sedge/temp2.mp4" % (SAVEPATH, SAVEPATH, SAVEPATH))
# os.system("ffmpeg -loglevel panic -y -i %sedge/AIA211_edge.mp4 -i %sedge/AIA304_edge.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast %sedge/temp3.mp4" % (SAVEPATH, SAVEPATH, SAVEPATH))
# os.system("ffmpeg -loglevel panic -y -i %sedge/temp1.mp4 -i %sedge/temp2.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast %sedge/temp4.mp4" % (SAVEPATH, SAVEPATH, SAVEPATH))
# os.system("ffmpeg -loglevel panic -y -i %sedge/temp3.mp4 -i %sedge/AIA335_edge.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast %sedge/temp5.mp4" % (SAVEPATH, SAVEPATH, SAVEPATH))
# os.system("ffmpeg -loglevel panic -y -i %sedge/temp4.mp4 -i %sedge/temp5.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast %sedge/temp6.mp4" % (SAVEPATH, SAVEPATH, SAVEPATH))
# os.system("ffmpeg -loglevel panic -y -i %sedge/temp6.mp4 -filter:v 'crop=4550:650:0:0' %sedge/COMBINED_edge.mp4" % (SAVEPATH, SAVEPATH))
# os.system("rm %sedge/temp1.mp4 %sedge/temp2.mp4 %sedge/temp3.mp4 %sedge/temp4.mp4 %sedge/temp5.mp4 %sedge/temp6.mp4" % (SAVEPATH, SAVEPATH, SAVEPATH, SAVEPATH, SAVEPATH, SAVEPATH))

RECORDER.display_end_time("structure")
