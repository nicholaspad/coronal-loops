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
import cv2 as cv
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

K94 = np.array([])
K131 = np.array([])
K171 = np.array([])
K193 = np.array([])
K211 = np.array([])
K304 = np.array([])
K335 = np.array([])

AVG94 = np.array([])
AVG131 = np.array([])
AVG171 = np.array([])
AVG193 = np.array([])
AVG211 = np.array([])
AVG304 = np.array([])
AVG335 = np.array([])

N = len(DIR94)

for K in tqdm(range(N), desc = "Importing data"):
	K94 = np.append(K94, Map(PATH94 + DIR94[K]))
	K131 = np.append(K131, Map(PATH131 + DIR131[K]))
	K171 = np.append(K171, Map(PATH171 + DIR171[K]))
	K193 = np.append(K193, Map(PATH193 + DIR193[K]))
	K211 = np.append(K211, Map(PATH211 + DIR211[K]))
	K304 = np.append(K304, Map(PATH304 + DIR304[K]))
	K335 = np.append(K335, Map(PATH335 + DIR335[K]))

for K in tqdm(range(N), desc = "Generating intensity distribution"):
	if K94[K].exposure_time.value > 0:
		AVG94 = np.append(AVG94, np.average(K94[K].data / K94[K].exposure_time.value))
	if K131[K].exposure_time.value > 0:
		AVG131 = np.append(AVG131, np.average(K131[K].data / K131[K].exposure_time.value))
	if K171[K].exposure_time.value > 0:
		AVG171 = np.append(AVG171, np.average(K171[K].data / K171[K].exposure_time.value))
	if K193[K].exposure_time.value > 0:
		AVG193 = np.append(AVG193, np.average(K193[K].data / K193[K].exposure_time.value))
	if K211[K].exposure_time.value > 0:
		AVG211 = np.append(AVG211, np.average(K211[K].data / K211[K].exposure_time.value))
	if K304[K].exposure_time.value > 0:
		AVG304 = np.append(AVG304, np.average(K304[K].data / K304[K].exposure_time.value))
	if K335[K].exposure_time.value > 0:
		AVG335 = np.append(AVG335, np.average(K335[K].data / K335[K].exposure_time.value))

MEAN94 = np.average(AVG94)
MEAN131 = np.average(AVG131)
MEAN171 = np.average(AVG171)
MEAN193 = np.average(AVG193)
MEAN211 = np.average(AVG211)
MEAN304 = np.average(AVG304)
MEAN335 = np.average(AVG335)

SDEV94 = np.std(AVG94)
SDEV131 = np.std(AVG131)
SDEV171 = np.std(AVG171)
SDEV193 = np.std(AVG193)
SDEV211 = np.std(AVG211)
SDEV304 = np.std(AVG304)
SDEV335 = np.std(AVG335)

print MEAN94, SDEV94
print MEAN131, SDEV131
print MEAN171, SDEV171
print MEAN193, SDEV193
print MEAN211, SDEV211
print MEAN304, SDEV304
print MEAN335, SDEV335

"""
[ID]: [MEAN] [SDEV]
94:
131:
171:
193:
211:
304:
335:
"""

offset = 0
for K in tqdm(range(N), desc = "Processing dataset"):
	RECORDER.info_text("Current datetime - %s" % K94[K].date)
	
	RECORDER.info_text("Reading raw image data")
	D94 = K94[K].data
	D131 = K131[K].data
	D171 = K171[K].data
	D193 = K193[K].data
	D211 = K211[K].data
	D304 = K304[K].data
	D335 = K335[K].data

	E94 = K94[K].exposure_time.value
	E131 = K131[K].exposure_time.value
	E171 = K171[K].exposure_time.value
	E193 = K193[K].exposure_time.value
	E211 = K211[K].exposure_time.value
	E304 = K304[K].exposure_time.value
	E335 = K335[K].exposure_time.value

	RECORDER.info_text("Correcting raw image data")
	corrected_D94 = np.log(D94 / E94); corrected_D94[np.isnan(corrected_D94)] = 0
	corrected_D131 = np.log(D131 / E131); corrected_D131[np.isnan(corrected_D131)] = 0
	corrected_D171 = np.power(D171 / E171, np.e)
	corrected_D193 = np.power(D193 / E193, np.e)
	corrected_D211 = np.power(D211 / E211, np.e)
	corrected_D304 = np.power(D304 / E304, np.e)
	corrected_D335 = np.log(D335 / E335); corrected_D335[np.isnan(corrected_D335)] = 0

	if np.abs(MEAN94 - np.average(corrected_D94)) > 3 * SDEV94 or np.abs(MEAN131 - np.average(corrected_D131)) > 3 * SDEV131 or np.abs(MEAN171 - np.average(corrected_D171)) > 3 * SDEV171 or np.abs(MEAN193 - np.average(corrected_D193)) > 3 * SDEV193 or np.abs(MEAN211 - np.average(corrected_D211)) > 3 * SDEV211 or np.abs(MEAN304 - np.average(corrected_D304)) > 3 * SDEV304 or np.abs(MEAN335 - np.average(corrected_D335)) > 3 * SDEV335:
		RECORDER.warn_text("Bright image %04d" % K)
		offset += 1
		continue

	RECORDER.sys_text("Exporting corrected raw images")
	plt.imsave(SAVEPATH + "raw/AIA94/raw_%04d" % (K - offset), corrected_D94, origin = "lower", cmap = "sdoaia94", vmin = 1, vmax = 8)
	plt.imsave(SAVEPATH + "raw/AIA131/raw_%04d" % (K - offset), corrected_D131, origin = "lower", cmap = "sdoaia131", vmin = 1, vmax = 12)
	plt.imsave(SAVEPATH + "raw/AIA171/raw_%04d" % (K - offset), corrected_D171, origin = "lower", cmap = "sdoaia171", vmin = 1, vmax = 100000000)
	plt.imsave(SAVEPATH + "raw/AIA193/raw_%04d" % (K - offset), corrected_D193, origin = "lower", cmap = "sdoaia193", vmin = 1, vmax = 800000000)
	plt.imsave(SAVEPATH + "raw/AIA211/raw_%04d" % (K - offset), corrected_D211, origin = "lower", cmap = "sdoaia211", vmin = 1, vmax = 100000000)
	plt.imsave(SAVEPATH + "raw/AIA304/raw_%04d" % (K - offset), corrected_D304, origin = "lower", cmap = "sdoaia304", vmin = 1, vmax = 50000000)
	plt.imsave(SAVEPATH + "raw/AIA335/raw_%04d" % (K - offset), corrected_D335, origin = "lower", cmap = "sdoaia335", vmin = 1, vmax = 7)

	RECORDER.info_text("Generating binary-masked images")
	threshold_94 = 2
	threshold_131 = 2.5
	threshold_171 = 15000000
	threshold_193 = 30000000
	threshold_211 = 15000000
	threshold_304 = 40000000
	threshold_335 = 3.2

	b_mask = np.logical_and(corrected_D94 > threshold_94, corrected_D94 < np.inf).astype(np.uint8)
	b_mask = cv.dilate(b_mask, np.ones((3,3)).astype(bool).astype(int), iterations = 1)
	corrected_B94 = corrected_D94 * b_mask
	corrected_B94[np.isnan(corrected_B94)] = 0

	b_mask = np.logical_and(corrected_D131 > threshold_131, corrected_D131 < np.inf).astype(np.uint8)
	b_mask = cv.dilate(b_mask, np.ones((3,3)).astype(bool).astype(int), iterations = 1)
	corrected_B131 = corrected_D131 * b_mask
	corrected_B131[np.isnan(corrected_B131)] = 0

	b_mask = np.logical_and(corrected_D171 > threshold_171, corrected_D171 < np.inf).astype(np.uint8)
	b_mask = cv.dilate(b_mask, np.ones((3,3)).astype(bool).astype(int), iterations = 1)
	corrected_B171 = corrected_D171 * b_mask

	b_mask = np.logical_and(corrected_D193 > threshold_193, corrected_D193 < np.inf).astype(np.uint8)
	b_mask = cv.dilate(b_mask, np.ones((3,3)).astype(bool).astype(int), iterations = 1)
	corrected_B193 = corrected_D193 * b_mask

	b_mask = np.logical_and(corrected_D211 > threshold_211, corrected_D211 < np.inf).astype(np.uint8)
	b_mask = cv.dilate(b_mask, np.ones((3,3)).astype(bool).astype(int), iterations = 1)
	corrected_B211 = corrected_D211 * b_mask

	b_mask = np.logical_and(corrected_D304 > threshold_304, corrected_D304 < np.inf).astype(np.uint8)
	b_mask = cv.dilate(b_mask, np.ones((3,3)).astype(bool).astype(int), iterations = 1)
	corrected_B304 = corrected_D304 * b_mask

	b_mask = np.logical_and(corrected_D335 > threshold_335, corrected_D335 < np.inf).astype(np.uint8)
	b_mask = cv.dilate(b_mask, np.ones((3,3)).astype(bool).astype(int), iterations = 1)
	corrected_B335 = corrected_D335 * b_mask
	corrected_B335[np.isnan(corrected_B335)] = 0

	# L = len(contours)
	# max_area = 0.0
	# max_index = 0

	# for i in range(L):
	# 	n = len(contours[i])
	# 	area = 0.0
	# 	for j in range(n):
	# 		k = (j + 1) % n
	# 		area += contours[i][j][0] * contours[i][k][1]
	# 		area -= contours[i][k][0] * contours[i][j][1]
	# 	area = abs(area) / 2.0
	# 	if area > max_area:
	# 		max_area = area
	# 		max_index = i

	# contour = np.array([contours[max_index]])

	# x_dim = r_mask.shape[0]
	# y_dim = r_mask.shape[1]

	# x, y = np.meshgrid(np.arange(x_dim), np.arange(y_dim))
	# x, y = x.flatten(), y.flatten()

	# points = np.vstack((x,y)).T

	# vertices = contour[0]
	# path = Path(vertices)
	# c_mask = path.contains_points(points)
	# c_mask = np.rot90(np.flip(c_mask.reshape((y_dim,x_dim)), 1))

	# c_mask = c_mask.astype(np.uint8)
	# c_mask = cv.morphologyEx(c_mask, cv.MORPH_CLOSE, np.ones((3,3)).astype(bool).astype(int))

	# img304 = img304 * c_mask
	# img304[img304 < 1] = 1
	# img304 = np.log(img304)/AIA304.exposure_time.value

	plt.imsave(SAVEPATH + "binary/AIA94/binary_%04d" % (K - offset), corrected_B94, origin = "lower", cmap = "sdoaia94", vmin = 1, vmax = 8)
	plt.imsave(SAVEPATH + "binary/AIA131/binary_%04d" % (K - offset), corrected_B131, origin = "lower", cmap = "sdoaia131", vmin = 1, vmax = 12)
	plt.imsave(SAVEPATH + "binary/AIA171/binary_%04d" % (K - offset), corrected_B171, origin = "lower", cmap = "sdoaia171", vmin = 1, vmax = 100000000)
	plt.imsave(SAVEPATH + "binary/AIA193/binary_%04d" % (K - offset), corrected_B193, origin = "lower", cmap = "sdoaia193", vmin = 1, vmax = 800000000)
	plt.imsave(SAVEPATH + "binary/AIA211/binary_%04d" % (K - offset), corrected_B211, origin = "lower", cmap = "sdoaia211", vmin = 1, vmax = 100000000)
	plt.imsave(SAVEPATH + "binary/AIA304/binary_%04d" % (K - offset), corrected_B304, origin = "lower", cmap = "sdoaia304", vmin = 1, vmax = 50000000)
	plt.imsave(SAVEPATH + "binary/AIA335/binary_%04d" % (K - offset), corrected_B335, origin = "lower", cmap = "sdoaia335", vmin = 1, vmax = 7)

	RECORDER.info_text("===== Processing completed on image %04d =====" % K)

	"""
	1. Corrected raw images [X]
	2. Binary masked images [X]
	3. Contour masked images
	4. Structural images
	"""

FPS = 24

RECORDER.sys_text("===== Generating raw videos =====")
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sraw/AIA94/raw_%%04d.png -q:v 2 -vcodec mpeg4 -b:v 800k %sraw/AIA94_raw.mp4" % (FPS, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sraw/AIA131/raw_%%04d.png -q:v 2 -vcodec mpeg4 -b:v 800k %sraw/AIA131_raw.mp4" % (FPS, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sraw/AIA171/raw_%%04d.png -q:v 2 -vcodec mpeg4 -b:v 800k %sraw/AIA171_raw.mp4" % (FPS, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sraw/AIA193/raw_%%04d.png -q:v 2 -vcodec mpeg4 -b:v 800k %sraw/AIA193_raw.mp4" % (FPS, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sraw/AIA211/raw_%%04d.png -q:v 2 -vcodec mpeg4 -b:v 800k %sraw/AIA211_raw.mp4" % (FPS, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sraw/AIA304/raw_%%04d.png -q:v 2 -vcodec mpeg4 -b:v 800k %sraw/AIA304_raw.mp4" % (FPS, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sraw/AIA335/raw_%%04d.png -q:v 2 -vcodec mpeg4 -b:v 800k %sraw/AIA335_raw.mp4" % (FPS, SAVEPATH, SAVEPATH))

os.system("ffmpeg -loglevel panic -y -i %sraw/AIA94_raw.mp4 -i %sraw/AIA131_raw.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast %sraw/temp1.mp4" % (SAVEPATH, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -i %sraw/AIA171_raw.mp4 -i %sraw/AIA193_raw.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast %sraw/temp2.mp4" % (SAVEPATH, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -i %sraw/AIA211_raw.mp4 -i %sraw/AIA304_raw.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast %sraw/temp3.mp4" % (SAVEPATH, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -i %sraw/temp1.mp4 -i %sraw/temp2.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast %sraw/temp4.mp4" % (SAVEPATH, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -i %sraw/temp3.mp4 -i %sraw/AIA335_raw.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast %sraw/temp5.mp4" % (SAVEPATH, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -i %sraw/temp4.mp4 -i %sraw/temp5.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast %sraw/temp6.mp4" % (SAVEPATH, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -i %sraw/temp6.mp4 -filter:v 'crop=4200:600:0:0' %sraw/COMBINED_raw.mp4" % (SAVEPATH, SAVEPATH))
os.system("rm %sraw/temp1.mp4 %sraw/temp2.mp4 %sraw/temp3.mp4 %sraw/temp4.mp4 %sraw/temp5.mp4 %sraw/temp6.mp4" % (SAVEPATH, SAVEPATH, SAVEPATH, SAVEPATH, SAVEPATH, SAVEPATH))

RECORDER.sys_text("===== Generating binary-mask videos =====")
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sbinary/AIA94/binary_%%04d.png -q:v 2 -vcodec mpeg4 -b:v 800k %sbinary/AIA94_binary.mp4" % (FPS, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sbinary/AIA131/binary_%%04d.png -q:v 2 -vcodec mpeg4 -b:v 800k %sbinary/AIA131_binary.mp4" % (FPS, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sbinary/AIA171/binary_%%04d.png -q:v 2 -vcodec mpeg4 -b:v 800k %sbinary/AIA171_binary.mp4" % (FPS, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sbinary/AIA193/binary_%%04d.png -q:v 2 -vcodec mpeg4 -b:v 800k %sbinary/AIA193_binary.mp4" % (FPS, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sbinary/AIA211/binary_%%04d.png -q:v 2 -vcodec mpeg4 -b:v 800k %sbinary/AIA211_binary.mp4" % (FPS, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sbinary/AIA304/binary_%%04d.png -q:v 2 -vcodec mpeg4 -b:v 800k %sbinary/AIA304_binary.mp4" % (FPS, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sbinary/AIA335/binary_%%04d.png -q:v 2 -vcodec mpeg4 -b:v 800k %sbinary/AIA335_binary.mp4" % (FPS, SAVEPATH, SAVEPATH))

os.system("ffmpeg -loglevel panic -y -i %sbinary/AIA94_binary.mp4 -i %sbinary/AIA131_binary.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast %sbinary/temp1.mp4" % (SAVEPATH, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -i %sbinary/AIA171_binary.mp4 -i %sbinary/AIA193_binary.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast %sbinary/temp2.mp4" % (SAVEPATH, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -i %sbinary/AIA211_binary.mp4 -i %sbinary/AIA304_binary.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast %sbinary/temp3.mp4" % (SAVEPATH, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -i %sbinary/temp1.mp4 -i %sbinary/temp2.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast %sbinary/temp4.mp4" % (SAVEPATH, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -i %sbinary/temp3.mp4 -i %sbinary/AIA335_binary.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast %sbinary/temp5.mp4" % (SAVEPATH, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -i %sbinary/temp4.mp4 -i %sbinary/temp5.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast %sbinary/temp6.mp4" % (SAVEPATH, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -i %sbinary/temp6.mp4 -filter:v 'crop=4200:600:0:0' %sbinary/COMBINED_binary.mp4" % (SAVEPATH, SAVEPATH))
os.system("rm %sbinary/temp1.mp4 %sbinary/temp2.mp4 %sbinary/temp3.mp4 %sbinary/temp4.mp4 %sbinary/temp5.mp4 %sbinary/temp6.mp4" % (SAVEPATH, SAVEPATH, SAVEPATH, SAVEPATH, SAVEPATH, SAVEPATH))

RECORDER.display_end_time("structure")
