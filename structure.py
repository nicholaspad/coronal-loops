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
from recorder import Recorder
from scipy import ndimage
from scipy.stats import iqr
from skimage import feature
from skimage import measure
from sunpy.map import Map
from timeit import default_timer as timer
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

DIR94 = [f for f in listdir(PATH94) if isfile(join(PATH94, f))]; DIR94.sort(); DIR94 = DIR94[1:]
DIR131 = [f for f in listdir(PATH131) if isfile(join(PATH131, f))]; DIR131.sort(); DIR131 = DIR131[1:]
DIR171 = [f for f in listdir(PATH171) if isfile(join(PATH171, f))]; DIR171.sort(); DIR171 = DIR171[1:]
DIR193 = [f for f in listdir(PATH193) if isfile(join(PATH193, f))]; DIR193.sort(); DIR193 = DIR193[1:]
DIR211 = [f for f in listdir(PATH211) if isfile(join(PATH211, f))]; DIR211.sort(); DIR211 = DIR211[1:]
DIR304 = [f for f in listdir(PATH304) if isfile(join(PATH304, f))]; DIR304.sort(); DIR304 = DIR304[1:]
DIR335 = [f for f in listdir(PATH335) if isfile(join(PATH335, f))]; DIR335.sort(); DIR335 = DIR335[1:]

K94 = []; t94 = []
K131 = []; t131 = []
K171 = []; t171 = []
K193 = []; t193 = []
K211 = []; t211 = []
K304 = []; t304 = []
K335 = []; t335 = []

def save_images(type, imgs, vmax_C):
	if type != "edge":
		cmaps = ["sdoaia94", "sdoaia131", "sdoaia171", "sdoaia193", "sdoaia211", "sdoaia304", "sdoaia335"]
	else:
		cmaps = ["gray", "gray", "gray", "gray", "gray", "gray", "gray"]

	plt.imsave(SAVEPATH + "%s/AIA94/%s_%04d" % (type, type, K - offset), imgs[0], origin = "lower", cmap = cmaps[0], vmin = int(imgs[0].min() + 0.5), vmax =  vmax_C * int(imgs[0].max()))
	plt.imsave(SAVEPATH + "%s/AIA131/%s_%04d" % (type, type, K - offset), imgs[1], origin = "lower", cmap = cmaps[1], vmin = int(imgs[1].min() + 0.5), vmax =  vmax_C * int(imgs[1].max()))
	plt.imsave(SAVEPATH + "%s/AIA171/%s_%04d" % (type, type, K - offset), imgs[2], origin = "lower", cmap = cmaps[2], vmin = int(imgs[2].min() + 0.5), vmax =  vmax_C * int(imgs[2].max()))
	plt.imsave(SAVEPATH + "%s/AIA193/%s_%04d" % (type, type, K - offset), imgs[3], origin = "lower", cmap = cmaps[3], vmin = int(imgs[3].min() + 0.5), vmax =  vmax_C * int(imgs[3].max()))
	plt.imsave(SAVEPATH + "%s/AIA211/%s_%04d" % (type, type, K - offset), imgs[4], origin = "lower", cmap = cmaps[4], vmin = int(imgs[4].min() + 0.5), vmax =  vmax_C * int(imgs[4].max()))
	plt.imsave(SAVEPATH + "%s/AIA304/%s_%04d" % (type, type, K - offset), imgs[5], origin = "lower", cmap = cmaps[5], vmin = int(imgs[5].min() + 0.5), vmax =  vmax_C * int(imgs[5].max()))
	plt.imsave(SAVEPATH + "%s/AIA335/%s_%04d" % (type, type, K - offset), imgs[6], origin = "lower", cmap = cmaps[6], vmin = int(imgs[6].min() + 0.5), vmax =  vmax_C * int(imgs[6].max()))

N = 5 #len(DIR94)

for K in tqdm(range(N), desc = "Importing data"):
	temp = Map(PATH94 + DIR94[K]); K94.append([temp.data, temp.exposure_time.value, temp.date])
	temp = Map(PATH131 + DIR131[K]); K131.append([temp.data, temp.exposure_time.value, temp.date])
	temp = Map(PATH171 + DIR171[K]); K171.append([temp.data, temp.exposure_time.value, temp.date])
	temp = Map(PATH193 + DIR193[K]); K193.append([temp.data, temp.exposure_time.value, temp.date])
	temp = Map(PATH211 + DIR211[K]); K211.append([temp.data, temp.exposure_time.value, temp.date])
	temp = Map(PATH304 + DIR304[K]); K304.append([temp.data, temp.exposure_time.value, temp.date])
	temp = Map(PATH335 + DIR335[K]); K335.append([temp.data, temp.exposure_time.value, temp.date])

for K in tqdm(range(N), desc = "Generating intensity distribution"):
	if K94[K][1] > 0:
		t94 = np.append(t94, np.median(K94[K][0] / K94[K][1]))
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

MED94 = np.median(t94); IQR94 = iqr(t94)
MED131 = np.median(t131); IQR131 = iqr(t131)
MED171 = np.median(t171); IQR171 = iqr(t171)
MED193 = np.median(t193); IQR193 = iqr(t193)
MED211 = np.median(t211); IQR211 = iqr(t211)
MED304 = np.median(t304); IQR304 = iqr(t304)
MED335 = np.median(t335); IQR335 = iqr(t335)

print "\t********************"
print "\tID\tMED\tIQR"
print "\t94\t%d\t%.1f" % (MED94, IQR94)
print "\t131\t%d\t%.1f" % (MED131, IQR131)
print "\t171\t%d\t%.1f" % (MED171, IQR171)
print "\t193\t%d\t%.1f" % (MED193, IQR193)
print "\t211\t%d\t%.1f" % (MED211, IQR211)
print "\t304\t%d\t%.1f" % (MED304, IQR304)
print "\t335\t%d\t%.1f" % (MED335, IQR335)
print "\t********************"

"""
[ID]: [MED] [SDEV]
94: X 9.992
131: X 44.985
171: X 32.219
193: X 360.449
211: X 23.465
304: X 24.411
335: X 6.197
"""

offset = 0
for K in tqdm(range(N), desc = "Processing dataset"):
	RECORDER.info_text("Processing datetime %s" % K94[K][2])

	RECORDER.info_text("Reading raw image data")

	corrected_D94 = K94[K][0] / K94[K][1]
	corrected_D131 = K131[K][0] / K131[K][1]
	corrected_D171 = K171[K][0] / K171[K][1]
	corrected_D193 = K193[K][0] / K193[K][1]
	corrected_D211 = K211[K][0] / K211[K][1]
	corrected_D304 = K304[K][0] / K304[K][1]
	corrected_D335 = K335[K][0] / K335[K][1]

	RECORDER.info_text("Checking for brightness")
	CRITVALUE = 2.5
	if np.abs(MED94 - np.median(corrected_D94)) > CRITVALUE * IQR94 or np.abs(MED131 - np.median(corrected_D131)) > CRITVALUE * IQR131 or np.abs(MED171 - np.median(corrected_D171)) > CRITVALUE * IQR171 or np.abs(MED193 - np.median(corrected_D193)) > CRITVALUE * IQR193 or np.abs(MED211 - np.median(corrected_D211)) > CRITVALUE * IQR211 or np.abs(MED304 - np.median(corrected_D304)) > CRITVALUE * IQR304 or np.abs(MED335 - np.median(corrected_D335)) > CRITVALUE * IQR335:
		RECORDER.warn_text("Bright image %04d" % K)
		offset += 1
		continue

	RECORDER.info_text("Correcting raw image data")
	corrected_D94[corrected_D94 < 1] = 1
	corrected_D94 = np.log(corrected_D94)
	corrected_D131[corrected_D131 < 1] = 1
	corrected_D131 = np.log(corrected_D131)
	corrected_D171[corrected_D171 < 1] = 1
	corrected_D171 = np.log(corrected_D171)
	corrected_D193[corrected_D193 < 1] = 1
	corrected_D193 = np.log(corrected_D193)
	corrected_D211[corrected_D211 < 1] = 1
	corrected_D211 = np.log(corrected_D211)
	corrected_D304[corrected_D304 < 1] = 1
	corrected_D304 = np.log(corrected_D304)
	corrected_D335[corrected_D335 < 1] = 1
	corrected_D335 = np.log(corrected_D335)

	RECORDER.sys_text("Exporting corrected raw images")
	save_images("raw", [corrected_D94, corrected_D131, corrected_D171, corrected_D193, corrected_D211, corrected_D304, corrected_D335], 1.25)

	RECORDER.info_text("Generating enhanced images")
	###############
	threshold_94 = MED94 - 1.5 * IQR94
	threshold_131 = MED131 - 1.5 * IQR131
	threshold_171 = MED171 - 1.5 * IQR171
	threshold_193 = MED193 - 1.5 * IQR193
	threshold_211 = MED211 - 1.5 * IQR211
	threshold_304 = MED304 - 1.5 * IQR304
	threshold_335 = MED335 - 1.5 * IQR335

	b_mask94 = np.logical_and(corrected_D94 > threshold_94, corrected_D94 < np.inf).astype(np.uint8)
	corrected_E94 = corrected_D94 * b_mask94

	b_mask131 = np.logical_and(corrected_D131 > threshold_131, corrected_D131 < np.inf).astype(np.uint8)
	corrected_E131 = corrected_D131 * b_mask131

	b_mask171 = np.logical_and(corrected_D171 > threshold_171, corrected_D171 < np.inf).astype(np.uint8)
	corrected_E171 = corrected_D171 * b_mask171

	b_mask193 = np.logical_and(corrected_D193 > threshold_193, corrected_D193 < np.inf).astype(np.uint8)
	corrected_E193 = corrected_D193 * b_mask193

	b_mask211 = np.logical_and(corrected_D211 > threshold_211, corrected_D211 < np.inf).astype(np.uint8)
	corrected_E211 = corrected_D211 * b_mask211

	b_mask304 = np.logical_and(corrected_D304 > threshold_304, corrected_D304 < np.inf).astype(np.uint8)
	corrected_E304 = corrected_D304 * b_mask304

	b_mask335 = np.logical_and(corrected_D335 > threshold_335, corrected_D335 < np.inf).astype(np.uint8)
	corrected_E335 = corrected_D335 * b_mask335

	RECORDER.sys_text("Exporting enhanced images")
	save_images("enhanced", [corrected_E94, corrected_E131, corrected_E171, corrected_E193, corrected_E211, corrected_E304, corrected_E335], 1.25)

	RECORDER.info_text("Generating edge images")
	SIGMA = 20
	# CHANGE D TO E LATER
	edge94 = feature.canny(corrected_D94, sigma = SIGMA)
	edge131 = feature.canny(corrected_D131, sigma = SIGMA)
	edge171 = feature.canny(corrected_D171, sigma = SIGMA)
	edge193 = feature.canny(corrected_D193, sigma = SIGMA)
	edge211 = feature.canny(corrected_D211, sigma = SIGMA)
	edge304 = feature.canny(corrected_D304, sigma = SIGMA)
	edge335 = feature.canny(corrected_D335, sigma = SIGMA)

	RECORDER.sys_text("Exporting edge images")
	save_images("edge", [edge94, edge131, edge171, edge193, edge211, edge304, edge335], 1.25)

	RECORDER.info_text("================ Processing completed on image %04d ================" % K)

FPS = 15

RECORDER.sys_text("================ Generating raw videos ================")
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sraw/AIA94/raw_%%04d.png -vframes %d -q:v 2 -vcodec mpeg4 -b:v 800k %sraw/AIA94_raw.mp4" % (FPS, SAVEPATH, N, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sraw/AIA131/raw_%%04d.png -vframes %d -q:v 2 -vcodec mpeg4 -b:v 800k %sraw/AIA131_raw.mp4" % (FPS, SAVEPATH, N, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sraw/AIA171/raw_%%04d.png -vframes %d -q:v 2 -vcodec mpeg4 -b:v 800k %sraw/AIA171_raw.mp4" % (FPS, SAVEPATH, N, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sraw/AIA193/raw_%%04d.png -vframes %d -q:v 2 -vcodec mpeg4 -b:v 800k %sraw/AIA193_raw.mp4" % (FPS, SAVEPATH, N, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sraw/AIA211/raw_%%04d.png -vframes %d -q:v 2 -vcodec mpeg4 -b:v 800k %sraw/AIA211_raw.mp4" % (FPS, SAVEPATH, N, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sraw/AIA304/raw_%%04d.png -vframes %d -q:v 2 -vcodec mpeg4 -b:v 800k %sraw/AIA304_raw.mp4" % (FPS, SAVEPATH, N, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sraw/AIA335/raw_%%04d.png -vframes %d -q:v 2 -vcodec mpeg4 -b:v 800k %sraw/AIA335_raw.mp4" % (FPS, SAVEPATH, N, SAVEPATH))

os.system("ffmpeg -loglevel panic -y -i %sraw/AIA94_raw.mp4 -i %sraw/AIA131_raw.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast %sraw/temp1.mp4" % (SAVEPATH, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -i %sraw/AIA171_raw.mp4 -i %sraw/AIA193_raw.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast %sraw/temp2.mp4" % (SAVEPATH, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -i %sraw/AIA211_raw.mp4 -i %sraw/AIA304_raw.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast %sraw/temp3.mp4" % (SAVEPATH, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -i %sraw/temp1.mp4 -i %sraw/temp2.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast %sraw/temp4.mp4" % (SAVEPATH, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -i %sraw/temp3.mp4 -i %sraw/AIA335_raw.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast %sraw/temp5.mp4" % (SAVEPATH, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -i %sraw/temp4.mp4 -i %sraw/temp5.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast %sraw/temp6.mp4" % (SAVEPATH, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -i %sraw/temp6.mp4 -filter:v 'crop=4200:600:0:0' %sraw/COMBINED_raw.mp4" % (SAVEPATH, SAVEPATH))
os.system("rm %sraw/temp1.mp4 %sraw/temp2.mp4 %sraw/temp3.mp4 %sraw/temp4.mp4 %sraw/temp5.mp4 %sraw/temp6.mp4" % (SAVEPATH, SAVEPATH, SAVEPATH, SAVEPATH, SAVEPATH, SAVEPATH))

RECORDER.sys_text("================ Generating enhanced videos ================")
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %senhanced/AIA94/enhanced_%%04d.png -vframes %d -q:v 2 -vcodec mpeg4 -b:v 800k %senhanced/AIA94_enhanced.mp4" % (FPS, SAVEPATH, N, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %senhanced/AIA131/enhanced_%%04d.png -vframes %d -q:v 2 -vcodec mpeg4 -b:v 800k %senhanced/AIA131_enhanced.mp4" % (FPS, SAVEPATH, N, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %senhanced/AIA171/enhanced_%%04d.png -vframes %d -q:v 2 -vcodec mpeg4 -b:v 800k %senhanced/AIA171_enhanced.mp4" % (FPS, SAVEPATH, N, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %senhanced/AIA193/enhanced_%%04d.png -vframes %d -q:v 2 -vcodec mpeg4 -b:v 800k %senhanced/AIA193_enhanced.mp4" % (FPS, SAVEPATH, N, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %senhanced/AIA211/enhanced_%%04d.png -vframes %d -q:v 2 -vcodec mpeg4 -b:v 800k %senhanced/AIA211_enhanced.mp4" % (FPS, SAVEPATH, N, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %senhanced/AIA304/enhanced_%%04d.png -vframes %d -q:v 2 -vcodec mpeg4 -b:v 800k %senhanced/AIA304_enhanced.mp4" % (FPS, SAVEPATH, N, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %senhanced/AIA335/enhanced_%%04d.png -vframes %d -q:v 2 -vcodec mpeg4 -b:v 800k %senhanced/AIA335_enhanced.mp4" % (FPS, SAVEPATH, N, SAVEPATH))

os.system("ffmpeg -loglevel panic -y -i %senhanced/AIA94_enhanced.mp4 -i %senhanced/AIA131_enhanced.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast %senhanced/temp1.mp4" % (SAVEPATH, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -i %senhanced/AIA171_enhanced.mp4 -i %senhanced/AIA193_enhanced.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast %senhanced/temp2.mp4" % (SAVEPATH, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -i %senhanced/AIA211_enhanced.mp4 -i %senhanced/AIA304_enhanced.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast %senhanced/temp3.mp4" % (SAVEPATH, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -i %senhanced/temp1.mp4 -i %senhanced/temp2.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast %senhanced/temp4.mp4" % (SAVEPATH, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -i %senhanced/temp3.mp4 -i %senhanced/AIA335_enhanced.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast %senhanced/temp5.mp4" % (SAVEPATH, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -i %senhanced/temp4.mp4 -i %senhanced/temp5.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast %senhanced/temp6.mp4" % (SAVEPATH, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -i %senhanced/temp6.mp4 -filter:v 'crop=4200:600:0:0' %senhanced/COMBINED_enhanced.mp4" % (SAVEPATH, SAVEPATH))
os.system("rm %senhanced/temp1.mp4 %senhanced/temp2.mp4 %senhanced/temp3.mp4 %senhanced/temp4.mp4 %senhanced/temp5.mp4 %senhanced/temp6.mp4" % (SAVEPATH, SAVEPATH, SAVEPATH, SAVEPATH, SAVEPATH, SAVEPATH))

RECORDER.sys_text("================ Generating edge videos ================")
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sedge/AIA94/edge_%%04d.png -vframes %d -q:v 2 -vcodec mpeg4 -b:v 800k %sedge/AIA94_edge.mp4" % (FPS, SAVEPATH, N, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sedge/AIA131/edge_%%04d.png -vframes %d -q:v 2 -vcodec mpeg4 -b:v 800k %sedge/AIA131_edge.mp4" % (FPS, SAVEPATH, N, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sedge/AIA171/edge_%%04d.png -vframes %d -q:v 2 -vcodec mpeg4 -b:v 800k %sedge/AIA171_edge.mp4" % (FPS, SAVEPATH, N, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sedge/AIA193/edge_%%04d.png -vframes %d -q:v 2 -vcodec mpeg4 -b:v 800k %sedge/AIA193_edge.mp4" % (FPS, SAVEPATH, N, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sedge/AIA211/edge_%%04d.png -vframes %d -q:v 2 -vcodec mpeg4 -b:v 800k %sedge/AIA211_edge.mp4" % (FPS, SAVEPATH, N, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sedge/AIA304/edge_%%04d.png -vframes %d -q:v 2 -vcodec mpeg4 -b:v 800k %sedge/AIA304_edge.mp4" % (FPS, SAVEPATH, N, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sedge/AIA335/edge_%%04d.png -vframes %d -q:v 2 -vcodec mpeg4 -b:v 800k %sedge/AIA335_edge.mp4" % (FPS, SAVEPATH, N, SAVEPATH))

os.system("ffmpeg -loglevel panic -y -i %sedge/AIA94_edge.mp4 -i %sedge/AIA131_edge.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast %sedge/temp1.mp4" % (SAVEPATH, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -i %sedge/AIA171_edge.mp4 -i %sedge/AIA193_edge.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast %sedge/temp2.mp4" % (SAVEPATH, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -i %sedge/AIA211_edge.mp4 -i %sedge/AIA304_edge.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast %sedge/temp3.mp4" % (SAVEPATH, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -i %sedge/temp1.mp4 -i %sedge/temp2.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast %sedge/temp4.mp4" % (SAVEPATH, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -i %sedge/temp3.mp4 -i %sedge/AIA335_edge.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast %sedge/temp5.mp4" % (SAVEPATH, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -i %sedge/temp4.mp4 -i %sedge/temp5.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast %sedge/temp6.mp4" % (SAVEPATH, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -i %sedge/temp6.mp4 -filter:v 'crop=4200:600:0:0' %sedge/COMBINED_edge.mp4" % (SAVEPATH, SAVEPATH))
os.system("rm %sedge/temp1.mp4 %sedge/temp2.mp4 %sedge/temp3.mp4 %sedge/temp4.mp4 %sedge/temp5.mp4 %sedge/temp6.mp4" % (SAVEPATH, SAVEPATH, SAVEPATH, SAVEPATH, SAVEPATH, SAVEPATH))

RECORDER.display_end_time("structure")
