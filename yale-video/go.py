import warnings
warnings.filterwarnings("ignore", message = "numpy.dtype size changed")

from astropy.coordinates import SkyCoord
from copy import copy
from datetime import datetime
from IPython.core import debugger; debug = debugger.Pdb().set_trace
from matplotlib.path import Path
from os import listdir
from os.path import isfile, join
from recorder import Recorder
from scipy.ndimage import zoom as interpolate
from scipy.ndimage.measurements import center_of_mass as com
from scipy.spatial import distance
from skimage import measure
from sunpy.physics.differential_rotation import solar_rotate_coordinate as rot
from tqdm import tqdm
import astropy.units as u
import cv2 as cv
import getpass
import matplotlib.pyplot as plt
import numpy as np
import os
import scipy.ndimage as ndimage
import scipy.ndimage.filters as filters
import sunpy.map as smap

RECORDER = Recorder()
RECORDER.display_start_time("go")

RECORDER.sys_text("Importing data...")

IMAGE_SAVEPATH = "/Users/padman/Desktop/images/"
PATH171 = "/Volumes/Nicholas Data/AIA171/"
PATH304 = "/Volumes/Nicholas Data/AIA304/"
PATHHMI = "/Volumes/Nicholas Data/HMI/"

AIA171_DIR = [f for f in listdir(PATH171) if isfile(join(PATH171, f))]
AIA304_DIR = [f for f in listdir(PATH304) if isfile(join(PATH304, f))]
HMI_DIR = [f for f in listdir(PATHHMI) if isfile(join(PATHHMI, f))]

def hmialign(data, scale):
	ALIGNED_RAW_HMI = np.zeros((4096, 4096)).astype(float)
	ALIGNED_RAW_HMI[ALIGNED_RAW_HMI == 0] = -10000000

	RECORDER.info_text("Interpolating HMI data with %.6f scale factor..." % scale)
	interpolated_hmi_data = interpolate(data, scale, order = 1)
	interpolated_hmi_data = np.flip(interpolated_hmi_data, (0,1))

	x_size = interpolated_hmi_data.shape[1]
	y_size = interpolated_hmi_data.shape[0]
	x_center = int(AIA304.reference_pixel.y.value + 0.5)
	y_center = int(AIA304.reference_pixel.x.value + 0.5)

	RECORDER.info_text("Casting interpolated HMI data to 4k by 4k empty image...")
	ALIGNED_RAW_HMI[(y_center - 1 - y_size / 2) : (y_center + y_size / 2),
					(x_center - 1 - x_size / 2) : (x_center + x_size / 2)] = interpolated_hmi_data

	ALIGNED_RAW_HMI[np.isnan(ALIGNED_RAW_HMI)] = -10000000

	return ALIGNED_RAW_HMI

#################################################
#################################################
#################################################

RECORDER.info_text("Generating pre-flare full-disk images...")
p = 1760

ID = 0
PREFLARE_COUNT = 1920

for i in tqdm(range(PREFLARE_COUNT), desc = "Working..."):
	AIA171 = smap.Map(PATH171 + AIA171_DIR[i])
	AIA304 = smap.Map(PATH304 + AIA304_DIR[i])
	HMI = smap.Map(PATHHMI + HMI_DIR[i])

	RECORDER.info_text("Current timestamp: %s" % AIA171.date)

	img = AIA171.data
	img[img < 1] = 1
	img = np.sqrt(img)/AIA171.exposure_time.value

	RECORDER.sys_text("Writing full-disk AIA171 image (sqrt-adj) #%05d..." % ID)
	plt.imsave(IMAGE_SAVEPATH + "aia171-images/%05d" % ID, img, cmap = "sdoaia171", origin = "lower", vmin = 0, vmax = 40)

	img = AIA304.data
	img[img < 1] = 1
	img = np.log(img)/AIA304.exposure_time.value

	RECORDER.sys_text("Writing full-disk AIA304 image (log-adj) #%05d..." % ID)
	plt.imsave(IMAGE_SAVEPATH + "aia304-images/%05d" % ID, img, cmap = "sdoaia304", origin = "lower", vmin = 0, vmax = 3)

	RECORDER.info_text("Aligning HMI full-disk image #%05d" % ID)
	scale = (HMI.scale[0] / AIA304.scale[0]).value
	scale = float("%.3f" % scale)
	ALIGNED_RAW_HMI = hmialign(HMI.data, scale)

	RECORDER.sys_text("Writing full-disk HMI image #%05d..." % ID)
	plt.imsave(IMAGE_SAVEPATH + "hmi-images/%05d" % ID, ALIGNED_RAW_HMI, cmap = "gray", origin = "lower", vmin = -120, vmax = 120)

	ID += 1

RECORDER.sys_text("**** START-PRE %d" % p)
RECORDER.sys_text("**** VFRAMES %d" % ID - 1 - p)
p = copy(ID)

# #################################################
# #################################################
# #################################################

RECORDER.info_text("Preparing for zoom animation...")

AIA171 = smap.Map(PATH171 + AIA171_DIR[ID])
AIA304 = smap.Map(PATH304 + AIA304_DIR[ID])
HMI = smap.Map(PATHHMI + HMI_DIR[ID])

aia171_img = AIA171.data
aia171_img[aia171_img < 1] = 1
aia171_img = np.sqrt(aia171_img)/AIA171.exposure_time.value

aia304_img = AIA304.data
aia304_img_o = AIA304.data
aia304_img[aia304_img < 1] = 1
aia304_img = np.log(aia304_img)/AIA304.exposure_time.value

scale = (HMI.scale[0] / AIA304.scale[0]).value
scale = float("%.3f" % scale)
hmi_img = hmialign(HMI.data, scale)

RECORDER.info_text("Generating zoom animation...")

x_center = 1652
y_center = 2381
dim = 200

d_bot = x_center-dim
d_top = 4096 - 2*dim - d_bot
d_left = y_center-dim
d_right = 4096 - 2*dim - d_left

N = min(d_top, d_bot, d_left, d_right)

v_bot = float(d_bot) / N
v_top = float(d_top) / N
v_left = float(d_left) / N
v_right = float(d_right) / N

NEW_ID = ID # ID becomes the index tracker
img171 = None
img304 = None
imghmi = None

for i in tqdm(range(N), desc = "Working..."):
	RECORDER.info_text("Iterating zoom on AIA171 image...")
	img171 = aia171_img[int(i * v_bot) : int(4096 - i * v_top),
						int(i * v_left) : int(4096 - i * v_right)]
	RECORDER.sys_text("Writing zoomed AIA171 image #%05d..." % NEW_ID)
	plt.imsave(IMAGE_SAVEPATH + "aia171-images/%05d" % NEW_ID, img171, cmap = "sdoaia171", origin = "lower", vmin = 0, vmax = 40)

	RECORDER.info_text("Iterating zoom on AIA304 image...")
	img304 = aia304_img[int(i * v_bot) : int(4096 - i * v_top),
						int(i * v_left) : int(4096 - i * v_right)]
	RECORDER.sys_text("Writing zoomed AIA304 image #%05d..." % NEW_ID)
	plt.imsave(IMAGE_SAVEPATH + "aia304-images/%05d" % NEW_ID, img304, cmap = "sdoaia304", origin = "lower", vmin = 0, vmax = 3)

	if i == N - 1:
		img304 = aia304_img_o[int(i * v_bot) : int(4096 - i * v_top),
							  int(i * v_left) : int(4096 - i * v_right)]

	RECORDER.info_text("Iterating zoom on HMI image...")
	imghmi = hmi_img[int(i * v_bot) : int(4096 - i * v_top),
					 int(i * v_left) : int(4096 - i * v_right)]
	RECORDER.sys_text("Writing zoomed HMI image #%05d..." % NEW_ID)
	plt.imsave(IMAGE_SAVEPATH + "hmi-images/%05d" % NEW_ID, imghmi, cmap = "gray", origin = "lower", vmin = -120, vmax = 120)

	NEW_ID += 1

s = min(img304.shape[0], img304.shape[1])
img304 = img304[0:s, 0:s]
img171 = img171[0:s, 0:s]
imghmi = imghmi[0:s, 0:s]
r_mask = r_mask[0:s, 0:s]

RECORDER.sys_text("**** START-ZOOM-IN %d" % p)
RECORDER.sys_text("**** VFRAMES %d" % NEW_ID - 1 - p)
p = copy(NEW_ID)

#################################################
#################################################
#################################################

# prerequisite code
# ID = 1920
# NEW_ID = 3372

# AIA171 = smap.Map(PATH171 + AIA171_DIR[ID])
# AIA304 = smap.Map(PATH304 + AIA304_DIR[ID])
# HMI = smap.Map(PATHHMI + HMI_DIR[ID])

# aia171_img = AIA171.data
# aia171_img[aia171_img < 1] = 1
# aia171_img = np.sqrt(aia171_img)

# aia304_img = AIA304.data
# aia304_img_o = AIA304.data
# aia304_img[aia304_img < 1] = 1
# aia304_img = np.log(aia304_img)

# scale = (HMI.scale[0] / AIA304.scale[0]).value
# scale = float("%.3f" % scale)
# hmi_img = hmialign(HMI.data, scale)

# x_center = 1652
# y_center = 2381
# dim = 200

# d_bot = x_center-dim
# d_top = 4096 - 2*dim - d_bot
# d_left = y_center-dim
# d_right = 4096 - 2*dim - d_left

# N = min(d_top, d_bot, d_left, d_right)
# i = N - 1

# v_bot = float(d_bot) / N
# v_top = float(d_top) / N
# v_left = float(d_left) / N
# v_right = float(d_right) / N

# img171 = None
# img304 = None
# imghmi = None

# img171 = aia171_img[int(i * v_bot) : int(4096 - i * v_top),
# 					int(i * v_left) : int(4096 - i * v_right)]

# img304 = aia304_img_o[int(i * v_bot) : int(4096 - i * v_top),
# 					  int(i * v_left) : int(4096 - i * v_right)]

# imghmi = hmi_img[int(i * v_bot) : int(4096 - i * v_top),
# 				 int(i * v_left) : int(4096 - i * v_right)]

#

RECORDER.info_text("Generating AIA304 binary mask animation...")

LOW_BRIGHTNESS_THRESHOLD = 600
r_mask = None

for i in tqdm(range(LOW_BRIGHTNESS_THRESHOLD + 1), desc = "Working..."):
	r_mask = np.logical_and(img304 > i, img304 < np.inf)
	temp = img304 * r_mask
	temp[temp < 1] = 1
	plt.imsave(IMAGE_SAVEPATH + "aia304-images/%05d" % NEW_ID, np.log(temp)/AIA304.exposure_time.value, cmap = "sdoaia304", origin = "lower", vmin = 0, vmax = 3)
	plt.imsave(IMAGE_SAVEPATH + "aia171-images/%05d" % NEW_ID, img171, cmap = "sdoaia171", origin = "lower", vmin = 0, vmax = 40)
	plt.imsave(IMAGE_SAVEPATH + "hmi-images/%05d" % NEW_ID, imghmi, cmap = "gray", origin = "lower", vmin = -120, vmax = 120)

	NEW_ID += 1

r_mask = np.logical_and(img304 > LOW_BRIGHTNESS_THRESHOLD, img304 < np.inf)
r_mask = r_mask.astype(np.uint8)
r_mask = cv.dilate(r_mask,
					np.ones((3,3)).astype(bool).astype(int),
					iterations = 1)

img304 = img304 * r_mask
img304[img304 < 1] = 1

plt.imsave(IMAGE_SAVEPATH + "aia304-images/%05d" % NEW_ID, np.log(img304)/AIA304.exposure_time.value, cmap = "sdoaia304", origin = "lower", vmin = 0, vmax = 3)
plt.imsave(IMAGE_SAVEPATH + "aia171-images/%05d" % NEW_ID, img171, cmap = "sdoaia171", origin = "lower", vmin = 0, vmax = 40)
plt.imsave(IMAGE_SAVEPATH + "hmi-images/%05d" % NEW_ID, imghmi, cmap = "gray", origin = "lower", vmin = -120, vmax = 120)

NEW_ID += 1

RECORDER.sys_text("**** START-AIA304-RMASK %d" % p)
RECORDER.sys_text("**** VFRAMES %d" % NEW_ID - 1 - p)
p = copy(NEW_ID)

#################################################
#################################################
#################################################

RECORDER.info_text("Generating AIA304 elliptical mask animation...")

dim = img304.shape[0]
threshold_percent_1 = 0.98
threshold_percent_2 = 0.96
threshold_percent_3 = 0.85

x_center = 215
y_center = 200

total = float(len(np.where(r_mask == 1)[0]))
rad = 300.0
y, x = np.ogrid[-x_center:dim - x_center, -y_center:dim - y_center]
mask_in = None
mask_out = None

RECORDER.info_text("Fitting elliptical mask to binary AIA304 data...")

while True:
	temp_in = x**2 + y**2 <= rad**2
	temp_out = x**2 + y**2 > rad**2
	img = copy(img304).astype(float)
	img = img * temp_in
	img[temp_out] = np.nan
	plt.imsave(IMAGE_SAVEPATH + "aia304-images/%05d" % NEW_ID, np.log(img)/AIA304.exposure_time.value, cmap = "sdoaia304", origin = "lower", vmin = 0, vmax = 3)
	plt.imsave(IMAGE_SAVEPATH + "aia171-images/%05d" % NEW_ID, img171, cmap = "sdoaia171", origin = "lower", vmin = 0, vmax = 40)
	plt.imsave(IMAGE_SAVEPATH + "hmi-images/%05d" % NEW_ID, imghmi, cmap = "gray", origin = "lower", vmin = -120, vmax = 120)
	if len(np.where(r_mask * temp_in == 1)[0]) / total <= threshold_percent_1:
		mask_in = temp_in
		NEW_ID += 1
		break
	rad -= 1.0

	NEW_ID += 1

RECORDER.info_text("Adjusting horizontal axis...")

a = b = rad

while True:
	temp_in = x**2/a**2 + y**2/b**2 <= 1
	temp_out = x**2/a**2 + y**2/b**2 > 1
	img = copy(img304).astype(float)
	img = img * temp_in
	img[temp_out] = np.nan
	plt.imsave(IMAGE_SAVEPATH + "aia304-images/%05d" % NEW_ID, np.log(img)/AIA304.exposure_time.value, cmap = "sdoaia304", origin = "lower", vmin = 0, vmax = 3)
	plt.imsave(IMAGE_SAVEPATH + "aia171-images/%05d" % NEW_ID, img171, cmap = "sdoaia171", origin = "lower", vmin = 0, vmax = 40)
	plt.imsave(IMAGE_SAVEPATH + "hmi-images/%05d" % NEW_ID, imghmi, cmap = "gray", origin = "lower", vmin = -120, vmax = 120)
	if len(np.where(r_mask * temp_in == 1)[0]) / total <= threshold_percent_2:
		mask_in = temp_in
		NEW_ID += 1
		break
	a -= 1.0

	NEW_ID += 1

RECORDER.info_text("Adjusting vertical axis...")

while True:
	temp_in = x**2/a**2 + y**2/b**2 <= 1
	temp_out = x**2/a**2 + y**2/b**2 > 1
	img = copy(img304).astype(float)
	img = img * temp_in
	img[temp_out] = np.nan
	plt.imsave(IMAGE_SAVEPATH + "aia304-images/%05d" % NEW_ID, np.log(img)/AIA304.exposure_time.value, cmap = "sdoaia304", origin = "lower", vmin = 0, vmax = 3)
	plt.imsave(IMAGE_SAVEPATH + "aia171-images/%05d" % NEW_ID, img171, cmap = "sdoaia171", origin = "lower", vmin = 0, vmax = 40)
	plt.imsave(IMAGE_SAVEPATH + "hmi-images/%05d" % NEW_ID, imghmi, cmap = "gray", origin = "lower", vmin = -120, vmax = 120)
	if len(np.where(r_mask * temp_in == 1)[0]) / total < threshold_percent_3:
		mask_in = temp_in
		mask_out = temp_out
		NEW_ID += 1
		break
	b -= 1.0

	NEW_ID += 1

RECORDER.info_text("Finalizing elliptical mask...")

img304_o = copy(img304)
img304 = (img304 * mask_in).astype(float)
img304[mask_out] = np.nan

plt.imsave(IMAGE_SAVEPATH + "aia304-images/%05d" % NEW_ID, np.log(img304)/AIA304.exposure_time.value, cmap = "sdoaia304", origin = "lower", vmin = 0, vmax = 3)
plt.imsave(IMAGE_SAVEPATH + "aia171-images/%05d" % NEW_ID, img171, cmap = "sdoaia171", origin = "lower", vmin = 0, vmax = 40)
plt.imsave(IMAGE_SAVEPATH + "hmi-images/%05d" % NEW_ID, imghmi, cmap = "gray", origin = "lower", vmin = -120, vmax = 120)

NEW_ID += 1

RECORDER.sys_text("**** START-AIA304-EMASK %d" % p)
RECORDER.sys_text("**** VFRAMES %d" % NEW_ID - 1 - p)
p = copy(NEW_ID)

#################################################
#################################################
#################################################

RECORDER.info_text("Generating AIA304 contour mask animation...")

contours = np.array(measure.find_contours(r_mask, 0.5))

L = len(contours)
max_area = 0.0
max_index = 0

for i in tqdm(range(L), desc = "Working..."):
	n = len(contours[i])
	area = 0.0
	for j in range(n):
		k = (j + 1) % n
		area += contours[i][j][0] * contours[i][k][1]
		area -= contours[i][k][0] * contours[i][j][1]
	area = abs(area) / 2.0
	if area > max_area:
		max_area = area
		max_index = i

contour = np.array([contours[max_index]])

x_dim = img304.shape[0]
y_dim = img304.shape[1]

x, y = np.meshgrid(np.arange(x_dim), np.arange(y_dim))
x, y = x.flatten(), y.flatten()

points = np.vstack((x,y)).T

vertices = contour[0]
L = len(vertices)

temp = copy(img304).astype(float)
temp[temp <= 1] = 1.

for i in tqdm(range(L), desc = "Working..."):
	temp[int(vertices[i][0] + 0.5), int(vertices[i][1] + 0.5)] = np.nan
	temp[int(vertices[i][0] + 0.5) - 1, int(vertices[i][1] + 0.5) - 1] = np.nan
	temp[int(vertices[i][0] + 0.5) - 1, int(vertices[i][1] + 0.5)] = np.nan
	temp[int(vertices[i][0] + 0.5) - 1, int(vertices[i][1] + 0.5) + 1] = np.nan
	temp[int(vertices[i][0] + 0.5), int(vertices[i][1] + 0.5) - 1] = np.nan
	temp[int(vertices[i][0] + 0.5), int(vertices[i][1] + 0.5) + 1] = np.nan
	temp[int(vertices[i][0] + 0.5) + 1, int(vertices[i][1] + 0.5) - 1] = np.nan
	temp[int(vertices[i][0] + 0.5) + 1, int(vertices[i][1] + 0.5)] = np.nan
	temp[int(vertices[i][0] + 0.5) + 1, int(vertices[i][1] + 0.5) + 1] = np.nan
	plt.imsave(IMAGE_SAVEPATH + "aia304-images/%05d" % NEW_ID, np.log(temp)/AIA304.exposure_time.value, cmap = "sdoaia304", origin = "lower", vmin = 0, vmax = 3)
	plt.imsave(IMAGE_SAVEPATH + "aia171-images/%05d" % NEW_ID, img171, cmap = "sdoaia171", origin = "lower", vmin = 0, vmax = 40)
	plt.imsave(IMAGE_SAVEPATH + "hmi-images/%05d" % NEW_ID, imghmi, cmap = "gray", origin = "lower", vmin = -120, vmax = 120)
	NEW_ID += 1

path = Path(vertices)
c_mask = path.contains_points(points)
c_mask = np.rot90(np.flip(c_mask.reshape((y_dim,x_dim)), 1))

c_mask = c_mask.astype(np.uint8)
c_mask = cv.morphologyEx(c_mask, cv.MORPH_CLOSE, np.ones((3,3)).astype(bool).astype(int))

RECORDER.info_text("Finalizing contour mask...")
img304 = img304_o * c_mask
img304[img304 < 1] = 1

plt.imsave(IMAGE_SAVEPATH + "aia304-images/%05d" % NEW_ID, np.log(temp)/AIA304.exposure_time.value, cmap = "sdoaia304", origin = "lower", vmin = 0, vmax = 3)
plt.imsave(IMAGE_SAVEPATH + "aia171-images/%05d" % NEW_ID, img171, cmap = "sdoaia171", origin = "lower", vmin = 0, vmax = 40)
plt.imsave(IMAGE_SAVEPATH + "hmi-images/%05d" % NEW_ID, imghmi, cmap = "gray", origin = "lower", vmin = -120, vmax = 120)

img304 = np.log(img304)/AIA304.exposure_time.value

NEW_ID += 1

RECORDER.sys_text("**** START-AIA304-CMASK %d" % p)
RECORDER.sys_text("**** VFRAMES %d" % NEW_ID - 1 - p)
p = copy(NEW_ID)

#################################################
#################################################
#################################################

RECORDER.info_text("Generating HMI binary mask animation...")

POS_GAUSS_THRESHOLD = 125
NEG_GAUSS_THRESHOLD = POS_GAUSS_THRESHOLD * -1
r_mask = None

for i in tqdm(range(POS_GAUSS_THRESHOLD + 1), desc = "Working..."):
	r_mask_1 = np.logical_and(imghmi < -1 * i, imghmi > -10000000)
	r_mask_2 = np.logical_and(imghmi > i, imghmi < 10000000)
	r_mask = r_mask_1.astype(float) + r_mask_2.astype(float)
	r_mask[r_mask == 2.] = 1.
	plt.imsave(IMAGE_SAVEPATH + "aia304-images/%05d" % NEW_ID, img304, cmap = "sdoaia304", origin = "lower", vmin = 0, vmax = 3)
	plt.imsave(IMAGE_SAVEPATH + "aia171-images/%05d" % NEW_ID, img171, cmap = "sdoaia171", origin = "lower", vmin = 0, vmax = 40)
	plt.imsave(IMAGE_SAVEPATH + "hmi-images/%05d" % NEW_ID, imghmi * r_mask, cmap = "gray", origin = "lower", vmin = -120, vmax = 120)

	NEW_ID += 1

r_mask = r_mask.astype(np.uint8)
r_mask = cv.dilate(r_mask, np.ones((3,3)).astype(bool).astype(int), iterations = 1)
r_mask = cv.morphologyEx(r_mask, cv.MORPH_CLOSE, np.ones((3,3)).astype(bool).astype(int))
r_mask = cv.dilate(r_mask, np.ones((3,3)).astype(bool).astype(int), iterations = 1)

imghmi = imghmi * r_mask

plt.imsave(IMAGE_SAVEPATH + "aia304-images/%05d" % NEW_ID, img304, cmap = "sdoaia304", origin = "lower", vmin = 0, vmax = 3)
plt.imsave(IMAGE_SAVEPATH + "aia171-images/%05d" % NEW_ID, img171, cmap = "sdoaia171", origin = "lower", vmin = 0, vmax = 40)
plt.imsave(IMAGE_SAVEPATH + "hmi-images/%05d" % NEW_ID, imghmi, cmap = "gray", origin = "lower", vmin = -120, vmax = 120)

NEW_ID += 1

RECORDER.sys_text("**** START-HMI-RMASK %d" % p)
RECORDER.sys_text("**** VFRAMES %d" % NEW_ID - 1 - p)
p = copy(NEW_ID)

#################################################
#################################################
#################################################

RECORDER.info_text("Generating HMI elliptical mask animation...")

dim = imghmi.shape[0]
threshold_percent_1 = 0.98
threshold_percent_2 = 0.96
threshold_percent_3 = 0.90

total = float(len(np.where(r_mask == 1)[0]))
rad = 300.0
x_center = 200
y_center = 200

y, x = np.ogrid[-x_center:dim - x_center, -y_center:dim - y_center]
mask_in = None
mask_out = None

RECORDER.info_text("Fitting elliptical mask to binary HMI data...")

while True:
	temp_in = x**2 + y**2 <= rad**2
	temp_out = x**2 + y**2 > rad**2
	img = copy(imghmi).astype(float)
	img = img * temp_in
	img[temp_out] = -10000000
	plt.imsave(IMAGE_SAVEPATH + "aia304-images/%05d" % NEW_ID, img304, cmap = "sdoaia304", origin = "lower", vmin = 0, vmax = 3)
	plt.imsave(IMAGE_SAVEPATH + "aia171-images/%05d" % NEW_ID, img171, cmap = "sdoaia171", origin = "lower", vmin = 0, vmax = 40)
	plt.imsave(IMAGE_SAVEPATH + "hmi-images/%05d" % NEW_ID, img, cmap = "gray", origin = "lower", vmin = -120, vmax = 120)
	if len(np.where(r_mask * temp_in == 1)[0]) / total <= threshold_percent_1:
		mask_in = temp_in
		NEW_ID += 1
		break
	rad -= 1.0

	NEW_ID += 1

RECORDER.info_text("Adjusting horizontal axis...")

a = b = rad

while True:
	temp_in = x**2/a**2 + y**2/b**2 <= 1
	temp_out = x**2/a**2 + y**2/b**2 > 1
	img = copy(imghmi)
	img = img * temp_in
	img[temp_out] = -10000000
	plt.imsave(IMAGE_SAVEPATH + "aia304-images/%05d" % NEW_ID, img304, cmap = "sdoaia304", origin = "lower", vmin = 0, vmax = 3)
	plt.imsave(IMAGE_SAVEPATH + "aia171-images/%05d" % NEW_ID, img171, cmap = "sdoaia171", origin = "lower", vmin = 0, vmax = 40)
	plt.imsave(IMAGE_SAVEPATH + "hmi-images/%05d" % NEW_ID, img, cmap = "gray", origin = "lower", vmin = -120, vmax = 120)
	if len(np.where(r_mask * temp_in == 1)[0]) / total < threshold_percent_2:
		mask_in = temp_in
		NEW_ID += 1
		break
	a -= 1.0

	NEW_ID += 1

RECORDER.info_text("Adjusting vertical axis...")

while True:
	temp_in = x**2/a**2 + y**2/b**2 <= 1
	temp_out = x**2/a**2 + y**2/b**2 > 1
	img = copy(imghmi)
	img = img * temp_in
	img[temp_out] = -10000000
	plt.imsave(IMAGE_SAVEPATH + "aia304-images/%05d" % NEW_ID, img304, cmap = "sdoaia304", origin = "lower", vmin = 0, vmax = 3)
	plt.imsave(IMAGE_SAVEPATH + "aia171-images/%05d" % NEW_ID, img171, cmap = "sdoaia171", origin = "lower", vmin = 0, vmax = 40)
	plt.imsave(IMAGE_SAVEPATH + "hmi-images/%05d" % NEW_ID, img, cmap = "gray", origin = "lower", vmin = -120, vmax = 120)
	if len(np.where(r_mask * temp_in == 1)[0]) / total < threshold_percent_3:
		mask_in = temp_in
		mask_out = temp_out
		NEW_ID += 1
		break
	b -= 1.0

	NEW_ID += 1

RECORDER.info_text("Finalizing elliptical mask...")

imghmi = imghmi * mask_in
imghmi[mask_out] = -10000000

plt.imsave(IMAGE_SAVEPATH + "aia304-images/%05d" % NEW_ID, img304, cmap = "sdoaia304", origin = "lower", vmin = 0, vmax = 3)
plt.imsave(IMAGE_SAVEPATH + "aia171-images/%05d" % NEW_ID, img171, cmap = "sdoaia171", origin = "lower", vmin = 0, vmax = 40)
plt.imsave(IMAGE_SAVEPATH + "hmi-images/%05d" % NEW_ID, imghmi, cmap = "gray", origin = "lower", vmin = -120, vmax = 120)

NEW_ID += 1

RECORDER.sys_text("**** START-HMI-EMASK %d" % p)
RECORDER.sys_text("**** VFRAMES %d" % NEW_ID - 1 - p)
p = copy(NEW_ID)

#################################################
#################################################
#################################################

RECORDER.info_text("Generating HMI contour mask animation...")

contours = np.array(measure.find_contours(r_mask, 0.5))

L = len(contours)
max_area = 0.0
max_index = 0

for i in range(L):
	n = len(contours[i])
	area = 0.0
	for j in range(n):
		k = (j + 1) % n
		area += contours[i][j][0] * contours[i][k][1]
		area -= contours[i][k][0] * contours[i][j][1]
	area = abs(area) / 2.0
	if area > max_area:
		max_area = area
		max_index = i

second_max_area = 0.0
second_max_index = 0

for i in range(L):
	n = len(contours[i])
	area = 0.0
	for j in range(n):
		k = (j + 1) % n
		area += contours[i][j][0] * contours[i][k][1]
		area -= contours[i][k][0] * contours[i][j][1]
	area = abs(area) / 2.0
	if area > second_max_area and area < max_area:
		second_max_area = area
		second_max_index = i

third_max_area = 0.0
third_max_index = 0

for i in range(L):
	n = len(contours[i])
	area = 0.0
	for j in range(n):
		k = (j + 1) % n
		area += contours[i][j][0] * contours[i][k][1]
		area -= contours[i][k][0] * contours[i][j][1]
	area = abs(area) / 2.0
	if area > third_max_area and area < second_max_area:
		third_max_area = area
		third_max_index = i

fourth_max_area = 0.0
fourth_max_index = 0

for i in range(L):
	n = len(contours[i])
	area = 0.0
	for j in range(n):
		k = (j + 1) % n
		area += contours[i][j][0] * contours[i][k][1]
		area -= contours[i][k][0] * contours[i][j][1]
	area = abs(area) / 2.0
	if area > fourth_max_area and area < third_max_area:
		fourth_max_area = area
		fourth_max_index = i

contour1 = np.array([contours[max_index]])
contour2 = np.array([contours[second_max_index]])
contour3 = np.array([contours[third_max_index]])
contour4 = np.array([contours[fourth_max_index]])

x_dim = imghmi.shape[0]
y_dim = imghmi.shape[1]

x, y = np.meshgrid(np.arange(x_dim), np.arange(y_dim))
x, y = x.flatten(), y.flatten()

points = np.vstack((x,y)).T

vertices1 = contour1[0]
vertices2 = contour2[0]
vertices3 = contour3[0]
vertices4 = contour4[0]

L = len(vertices1)

temp = copy(imghmi).astype(float)

for i in tqdm(range(L), desc = "Working..."):
	temp[int(vertices1[i][0] + 0.5), int(vertices1[i][1] + 0.5)] = -10000000
	temp[int(vertices1[i][0] + 0.5) - 1, int(vertices1[i][1] + 0.5) - 1] = -10000000
	temp[int(vertices1[i][0] + 0.5) - 1, int(vertices1[i][1] + 0.5)] = -10000000
	temp[int(vertices1[i][0] + 0.5) - 1, int(vertices1[i][1] + 0.5) + 1] = -10000000
	temp[int(vertices1[i][0] + 0.5), int(vertices1[i][1] + 0.5) - 1] = -10000000
	temp[int(vertices1[i][0] + 0.5), int(vertices1[i][1] + 0.5) + 1] = -10000000
	temp[int(vertices1[i][0] + 0.5) + 1, int(vertices1[i][1] + 0.5) - 1] = -10000000
	temp[int(vertices1[i][0] + 0.5) + 1, int(vertices1[i][1] + 0.5)] = -10000000
	temp[int(vertices1[i][0] + 0.5) + 1, int(vertices1[i][1] + 0.5) + 1] = -10000000
	plt.imsave(IMAGE_SAVEPATH + "aia304-images/%05d" % NEW_ID, img304, cmap = "sdoaia304", origin = "lower", vmin = 0, vmax = 3)
	plt.imsave(IMAGE_SAVEPATH + "aia171-images/%05d" % NEW_ID, img171, cmap = "sdoaia171", origin = "lower", vmin = 0, vmax = 40)
	plt.imsave(IMAGE_SAVEPATH + "hmi-images/%05d" % NEW_ID, temp, cmap = "gray", origin = "lower", vmin = -120, vmax = 120)
	NEW_ID += 1

L = len(vertices2)

for i in tqdm(range(L), desc = "Working..."):
	temp[int(vertices2[i][0] + 0.5), int(vertices2[i][1] + 0.5)] = -10000000
	temp[int(vertices2[i][0] + 0.5) - 1, int(vertices2[i][1] + 0.5) - 1] = -10000000
	temp[int(vertices2[i][0] + 0.5) - 1, int(vertices2[i][1] + 0.5)] = -10000000
	temp[int(vertices2[i][0] + 0.5) - 1, int(vertices2[i][1] + 0.5) + 1] = -10000000
	temp[int(vertices2[i][0] + 0.5), int(vertices2[i][1] + 0.5) - 1] = -10000000
	temp[int(vertices2[i][0] + 0.5), int(vertices2[i][1] + 0.5) + 1] = -10000000
	temp[int(vertices2[i][0] + 0.5) + 1, int(vertices2[i][1] + 0.5) - 1] = -10000000
	temp[int(vertices2[i][0] + 0.5) + 1, int(vertices2[i][1] + 0.5)] = -10000000
	temp[int(vertices2[i][0] + 0.5) + 1, int(vertices2[i][1] + 0.5) + 1] = -10000000
	plt.imsave(IMAGE_SAVEPATH + "aia304-images/%05d" % NEW_ID, img304, cmap = "sdoaia304", origin = "lower", vmin = 0, vmax = 3)
	plt.imsave(IMAGE_SAVEPATH + "aia171-images/%05d" % NEW_ID, img171, cmap = "sdoaia171", origin = "lower", vmin = 0, vmax = 40)
	plt.imsave(IMAGE_SAVEPATH + "hmi-images/%05d" % NEW_ID, temp, cmap = "gray", origin = "lower", vmin = -120, vmax = 120)
	NEW_ID += 1

L = len(vertices3)

for i in tqdm(range(L), desc = "Working..."):
	temp[int(vertices3[i][0] + 0.5), int(vertices3[i][1] + 0.5)] = -10000000
	temp[int(vertices3[i][0] + 0.5) - 1, int(vertices3[i][1] + 0.5) - 1] = -10000000
	temp[int(vertices3[i][0] + 0.5) - 1, int(vertices3[i][1] + 0.5)] = -10000000
	temp[int(vertices3[i][0] + 0.5) - 1, int(vertices3[i][1] + 0.5) + 1] = -10000000
	temp[int(vertices3[i][0] + 0.5), int(vertices3[i][1] + 0.5) - 1] = -10000000
	temp[int(vertices3[i][0] + 0.5), int(vertices3[i][1] + 0.5) + 1] = -10000000
	temp[int(vertices3[i][0] + 0.5) + 1, int(vertices3[i][1] + 0.5) - 1] = -10000000
	temp[int(vertices3[i][0] + 0.5) + 1, int(vertices3[i][1] + 0.5)] = -10000000
	temp[int(vertices3[i][0] + 0.5) + 1, int(vertices3[i][1] + 0.5) + 1] = -10000000
	plt.imsave(IMAGE_SAVEPATH + "aia304-images/%05d" % NEW_ID, img304, cmap = "sdoaia304", origin = "lower", vmin = 0, vmax = 3)
	plt.imsave(IMAGE_SAVEPATH + "aia171-images/%05d" % NEW_ID, img171, cmap = "sdoaia171", origin = "lower", vmin = 0, vmax = 40)
	plt.imsave(IMAGE_SAVEPATH + "hmi-images/%05d" % NEW_ID, temp, cmap = "gray", origin = "lower", vmin = -120, vmax = 120)
	NEW_ID += 1

L = len(vertices4)

for i in tqdm(range(L), desc = "Working..."):
	temp[int(vertices4[i][0] + 0.5), int(vertices4[i][1] + 0.5)] = -10000000
	temp[int(vertices4[i][0] + 0.5) - 1, int(vertices4[i][1] + 0.5) - 1] = -10000000
	temp[int(vertices4[i][0] + 0.5) - 1, int(vertices4[i][1] + 0.5)] = -10000000
	temp[int(vertices4[i][0] + 0.5) - 1, int(vertices4[i][1] + 0.5) + 1] = -10000000
	temp[int(vertices4[i][0] + 0.5), int(vertices4[i][1] + 0.5) - 1] = -10000000
	temp[int(vertices4[i][0] + 0.5), int(vertices4[i][1] + 0.5) + 1] = -10000000
	temp[int(vertices4[i][0] + 0.5) + 1, int(vertices4[i][1] + 0.5) - 1] = -10000000
	temp[int(vertices4[i][0] + 0.5) + 1, int(vertices4[i][1] + 0.5)] = -10000000
	temp[int(vertices4[i][0] + 0.5) + 1, int(vertices4[i][1] + 0.5) + 1] = -10000000
	plt.imsave(IMAGE_SAVEPATH + "aia304-images/%05d" % NEW_ID, img304, cmap = "sdoaia304", origin = "lower", vmin = 0, vmax = 3)
	plt.imsave(IMAGE_SAVEPATH + "aia171-images/%05d" % NEW_ID, img171, cmap = "sdoaia171", origin = "lower", vmin = 0, vmax = 40)
	plt.imsave(IMAGE_SAVEPATH + "hmi-images/%05d" % NEW_ID, temp, cmap = "gray", origin = "lower", vmin = -120, vmax = 120)
	NEW_ID += 1

path1 = Path(vertices1)
path2 = Path(vertices2)
path3 = Path(vertices3)
path4 = Path(vertices4)

c_mask1 = path1.contains_points(points)
c_mask1 = np.rot90(np.flip(c_mask1.reshape((y_dim,x_dim)), 1))

c_mask2 = path2.contains_points(points)
c_mask2 = np.rot90(np.flip(c_mask2.reshape((y_dim,x_dim)), 1))

c_mask3 = path3.contains_points(points)
c_mask3 = np.rot90(np.flip(c_mask3.reshape((y_dim,x_dim)), 1))

c_mask4 = path4.contains_points(points)
c_mask4 = np.rot90(np.flip(c_mask4.reshape((y_dim,x_dim)), 1))

c_mask = c_mask1.astype(float) + c_mask2.astype(float) + c_mask3.astype(float) + c_mask4.astype(float)
c_mask[c_mask == 2.] = 1.
c_mask[c_mask == 3.] = 1.
c_mask[c_mask == 4.] = 1.

c_mask = c_mask.astype(np.uint8)
c_mask = cv.morphologyEx(c_mask, cv.MORPH_CLOSE, np.ones((3,3)).astype(bool).astype(int))

RECORDER.info_text("Finalizing contour mask...")
imghmi = imghmi * c_mask
imghmi[mask_out] = -10000000

plt.imsave(IMAGE_SAVEPATH + "aia304-images/%05d" % NEW_ID, img304, cmap = "sdoaia304", origin = "lower", vmin = 0, vmax = 3)
plt.imsave(IMAGE_SAVEPATH + "aia171-images/%05d" % NEW_ID, img171, cmap = "sdoaia171", origin = "lower", vmin = 0, vmax = 40)
plt.imsave(IMAGE_SAVEPATH + "hmi-images/%05d" % NEW_ID, imghmi, cmap = "gray", origin = "lower", vmin = -120, vmax = 120)

NEW_ID += 1

RECORDER.sys_text("**** START-HMI-CMASK %d" % p)
RECORDER.sys_text("**** VFRAMES %d" % NEW_ID - 1 - p)
p = copy(NEW_ID)

#################################################
#################################################
#################################################

RECORDER.info_text("Generating flare animation...")

init_loc = None
cx = None
cy = None

for i in tqdm(range(ID, 2040), desc = "Working..."):
	AIA171 = smap.Map(PATH171 + AIA171_DIR[i])
	AIA304 = smap.Map(PATH304 + AIA304_DIR[i])
	HMI = smap.Map(PATHHMI + HMI_DIR[i])

	x_center = 1652
	y_center = 2381

	if i == ID:
		init_loc = AIA171.pixel_to_world(y_center * u.pixel, x_center * u.pixel)

	new_loc = rot(init_loc, AIA171.date)
	new_xy = AIA171.world_to_pixel(new_loc)

	cx = int(new_xy[1].value)
	cy = int(new_xy[0].value)

	scale = (HMI.scale[0] / AIA304.scale[0]).value
	scale = float("%.3f" % scale)
	ALIGNED_RAW_HMI = hmialign(HMI.data, scale)

	dim = 200

	img171 = AIA171.data[cx-dim : cx+dim, cy-dim : cy+dim]
	img304 = AIA304.data[cx-dim : cx+dim, cy-dim : cy+dim]
	imghmi = ALIGNED_RAW_HMI[cx-dim : cx+dim, cy-dim : cy+dim]

	img171[img171 < 1] = 1
	img171 = np.sqrt(img171)/AIA171.exposure_time.value

	### AIA304 mask

	r_mask = np.logical_and(img304 > LOW_BRIGHTNESS_THRESHOLD, img304 < np.inf)
	r_mask = r_mask.astype(np.uint8)
	r_mask = cv.dilate(r_mask,
					   np.ones((3,3)).astype(bool).astype(int),
					   iterations = 1)

	img304 = img304 * r_mask

	contours = np.array(measure.find_contours(r_mask, 0.5))

	L = len(contours)
	max_area = 0.0
	max_index = 0

	for i in range(L):
		n = len(contours[i])
		area = 0.0
		for j in range(n):
			k = (j + 1) % n
			area += contours[i][j][0] * contours[i][k][1]
			area -= contours[i][k][0] * contours[i][j][1]
		area = abs(area) / 2.0
		if area > max_area:
			max_area = area
			max_index = i

	contour = np.array([contours[max_index]])

	x_dim = r_mask.shape[0]
	y_dim = r_mask.shape[1]

	x, y = np.meshgrid(np.arange(x_dim), np.arange(y_dim))
	x, y = x.flatten(), y.flatten()

	points = np.vstack((x,y)).T

	vertices = contour[0]
	path = Path(vertices)
	c_mask = path.contains_points(points)
	c_mask = np.rot90(np.flip(c_mask.reshape((y_dim,x_dim)), 1))

	c_mask = c_mask.astype(np.uint8)
	c_mask = cv.morphologyEx(c_mask, cv.MORPH_CLOSE, np.ones((3,3)).astype(bool).astype(int))

	img304 = img304 * c_mask
	img304[img304 < 1] = 1
	img304 = np.log(img304)/AIA304.exposure_time.value

	### HMI mask

	r_mask_1 = np.logical_and(imghmi < -125, imghmi > -10000000)
	r_mask_2 = np.logical_and(imghmi > 125, imghmi < 10000000)
	r_mask = r_mask_1.astype(float) + r_mask_2.astype(float)
	r_mask[r_mask == 2.] = 1.

	r_mask = r_mask.astype(np.uint8)
	r_mask = cv.dilate(r_mask, np.ones((3,3)).astype(bool).astype(int), iterations = 1)
	r_mask = cv.morphologyEx(r_mask, cv.MORPH_CLOSE, np.ones((3,3)).astype(bool).astype(int))
	r_mask = cv.dilate(r_mask, np.ones((3,3)).astype(bool).astype(int), iterations = 1)

	imghmi = imghmi * r_mask

	contours = np.array(measure.find_contours(r_mask, 0.5))

	L = len(contours)
	max_area = 0.0
	max_index = 0

	for i in range(L):
		n = len(contours[i])
		area = 0.0
		for j in range(n):
			k = (j + 1) % n
			area += contours[i][j][0] * contours[i][k][1]
			area -= contours[i][k][0] * contours[i][j][1]
		area = abs(area) / 2.0
		if area > max_area:
			max_area = area
			max_index = i

	second_max_area = 0.0
	second_max_index = 0

	for i in range(L):
		n = len(contours[i])
		area = 0.0
		for j in range(n):
			k = (j + 1) % n
			area += contours[i][j][0] * contours[i][k][1]
			area -= contours[i][k][0] * contours[i][j][1]
		area = abs(area) / 2.0
		if area > second_max_area and area < max_area:
			second_max_area = area
			second_max_index = i

	third_max_area = 0.0
	third_max_index = 0

	for i in range(L):
		n = len(contours[i])
		area = 0.0
		for j in range(n):
			k = (j + 1) % n
			area += contours[i][j][0] * contours[i][k][1]
			area -= contours[i][k][0] * contours[i][j][1]
		area = abs(area) / 2.0
		if area > third_max_area and area < second_max_area:
			third_max_area = area
			third_max_index = i

	fourth_max_area = 0.0
	fourth_max_index = 0

	for i in range(L):
		n = len(contours[i])
		area = 0.0
		for j in range(n):
			k = (j + 1) % n
			area += contours[i][j][0] * contours[i][k][1]
			area -= contours[i][k][0] * contours[i][j][1]
		area = abs(area) / 2.0
		if area > fourth_max_area and area < third_max_area:
			fourth_max_area = area
			fourth_max_index = i

	contour1 = np.array([contours[max_index]])
	contour2 = np.array([contours[second_max_index]])
	contour3 = np.array([contours[third_max_index]])
	contour4 = np.array([contours[fourth_max_index]])

	x_dim = imghmi.shape[0]
	y_dim = imghmi.shape[1]

	x, y = np.meshgrid(np.arange(x_dim), np.arange(y_dim))
	x, y = x.flatten(), y.flatten()

	points = np.vstack((x,y)).T

	vertices1 = contour1[0]
	vertices2 = contour2[0]
	vertices3 = contour3[0]
	vertices4 = contour4[0]

	path1 = Path(vertices1)
	path2 = Path(vertices2)
	path3 = Path(vertices3)
	path4 = Path(vertices4)

	c_mask1 = path1.contains_points(points)
	c_mask1 = np.rot90(np.flip(c_mask1.reshape((y_dim,x_dim)), 1))

	c_mask2 = path2.contains_points(points)
	c_mask2 = np.rot90(np.flip(c_mask2.reshape((y_dim,x_dim)), 1))

	c_mask3 = path3.contains_points(points)
	c_mask3 = np.rot90(np.flip(c_mask3.reshape((y_dim,x_dim)), 1))

	c_mask4 = path4.contains_points(points)
	c_mask4 = np.rot90(np.flip(c_mask4.reshape((y_dim,x_dim)), 1))

	c_mask = c_mask1.astype(float) + c_mask2.astype(float) + c_mask3.astype(float) + c_mask4.astype(float)
	c_mask[c_mask == 2.] = 1.
	c_mask[c_mask == 3.] = 1.
	c_mask[c_mask == 4.] = 1.

	c_mask = c_mask.astype(np.uint8)
	c_mask = cv.morphologyEx(c_mask, cv.MORPH_CLOSE, np.ones((3,3)).astype(bool).astype(int))

	RECORDER.info_text("Finalizing contour mask...")
	imghmi = imghmi * c_mask

	RECORDER.info_text("Saving image #%05d" % NEW_ID)

	plt.imsave(IMAGE_SAVEPATH + "aia304-images/%05d" % NEW_ID, img304, cmap = "sdoaia304", origin = "lower", vmin = 0, vmax = 3)
	plt.imsave(IMAGE_SAVEPATH + "aia171-images/%05d" % NEW_ID, img171, cmap = "sdoaia171", origin = "lower", vmin = 0, vmax = 40)
	plt.imsave(IMAGE_SAVEPATH + "hmi-images/%05d" % NEW_ID, imghmi, cmap = "gray", origin = "lower", vmin = -120, vmax = 120)

	NEW_ID += 1

RECORDER.sys_text("**** START-FLARE %d" % p)
RECORDER.sys_text("**** VFRAMES %d" % NEW_ID - 1 - p)
p = copy(NEW_ID)

#################################################
#################################################
#################################################

RECORDER.info_text("Generating reverse zoom animation...")

AIA171 = smap.Map(PATH171 + AIA171_DIR[2040])
AIA304 = smap.Map(PATH304 + AIA304_DIR[2040])
HMI = smap.Map(PATHHMI + HMI_DIR[2040])

aia171_img = AIA171.data
aia171_img[aia171_img < 1] = 1
aia171_img = np.sqrt(aia171_img)/AIA171.exposure_time.value

aia304_img = AIA304.data
aia304_img[aia304_img < 1] = 1
aia304_img = np.log(aia304_img)/AIA304.exposure_time.value

scale = (HMI.scale[0] / AIA304.scale[0]).value
scale = float("%.3f" % scale)
hmi_img = hmialign(HMI.data, scale)

dim = 200

d_bot = cx-dim
d_top = 4096 - 2*dim - d_bot
d_left = cy-dim
d_right = 4096 - 2*dim - d_left

N = min(d_top, d_bot, d_left, d_right)

v_bot = float(d_bot) / N
v_top = float(d_top) / N
v_left = float(d_left) / N
v_right = float(d_right) / N

for i in tqdm(range(N), desc = "Working..."):
	RECORDER.info_text("Iterating zoom on AIA171 image...")
	img171 = aia171_img[int((N-i) * v_bot) : int(4096 - (N-i) * v_top),
						int((N-i) * v_left) : int(4096 - (N-i) * v_right)]
	RECORDER.sys_text("Writing zoomed AIA171 image #%05d..." % NEW_ID)
	plt.imsave(IMAGE_SAVEPATH + "aia171-images/%05d" % NEW_ID, img171, cmap = "sdoaia171", origin = "lower", vmin = 0, vmax = 40)

	RECORDER.info_text("Iterating zoom on AIA304 image...")
	img304 = aia304_img[int((N-i) * v_bot) : int(4096 - (N-i) * v_top),
						int((N-i) * v_left) : int(4096 - (N-i) * v_right)]
	RECORDER.sys_text("Writing zoomed AIA304 image #%05d..." % NEW_ID)
	plt.imsave(IMAGE_SAVEPATH + "aia304-images/%05d" % NEW_ID, img304, cmap = "sdoaia304", origin = "lower", vmin = 0, vmax = 3)

	RECORDER.info_text("Iterating zoom on HMI image...")
	imghmi = hmi_img[int((N-i) * v_bot) : int(4096 - (N-i) * v_top),
					 int((N-i) * v_left) : int(4096 - (N-i) * v_right)]
	RECORDER.sys_text("Writing zoomed HMI image #%05d..." % NEW_ID)
	plt.imsave(IMAGE_SAVEPATH + "hmi-images/%05d" % NEW_ID, imghmi, cmap = "gray", origin = "lower", vmin = -120, vmax = 120)

	NEW_ID += 1

RECORDER.sys_text("**** START-ZOOM-OUT %d" % p)
RECORDER.sys_text("**** VFRAMES %d" % NEW_ID - 1 - p)
p = copy(NEW_ID)

#################################################
#################################################
#################################################

RECORDER.info_text("Generating post-flare full-disk images...")

for i in tqdm(range(2041, len(AIA171_DIR)), desc = "Working..."):
	AIA171 = smap.Map(PATH171 + AIA171_DIR[i])
	AIA304 = smap.Map(PATH304 + AIA304_DIR[i])
	HMI = smap.Map(PATHHMI + HMI_DIR[i])

	RECORDER.info_text("Current timestamp: %s" % AIA171.date)

	img = AIA171.data
	img[img < 1] = 1
	img = np.sqrt(img)/AIA171.exposure_time.value

	RECORDER.sys_text("Writing full-disk AIA171 image (sqrt-adj) #%05d..." % NEW_ID)
	plt.imsave(IMAGE_SAVEPATH + "aia171-images/%05d" % NEW_ID, img, cmap = "sdoaia171", origin = "lower", vmin = 0, vmax = 40)

	img = AIA304.data
	img[img < 1] = 1
	img = np.log(img)/AIA304.exposure_time.value

	RECORDER.sys_text("Writing full-disk AIA304 image (log-adj) #%05d..." % NEW_ID)
	plt.imsave(IMAGE_SAVEPATH + "aia304-images/%05d" % NEW_ID, img, cmap = "sdoaia304", origin = "lower", vmin = 0, vmax = 3)

	RECORDER.info_text("Aligning HMI full-disk image #%05d" % NEW_ID)
	scale = (HMI.scale[0] / AIA304.scale[0]).value
	scale = float("%.3f" % scale)
	ALIGNED_RAW_HMI = hmialign(HMI.data, scale)

	RECORDER.sys_text("Writing full-disk HMI image #%05d..." % NEW_ID)
	plt.imsave(IMAGE_SAVEPATH + "hmi-images/%05d" % NEW_ID, ALIGNED_RAW_HMI, cmap = "gray", origin = "lower", vmin = -120, vmax = 120)

	NEW_ID += 1

RECORDER.sys_text("**** START-POST %d" % p)
RECORDER.sys_text("**** VFRAMES %d" % NEW_ID - 1 - p)
p = copy(NEW_ID)

RECORDER.display_end_time("go")
