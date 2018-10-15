import warnings
warnings.filterwarnings("ignore", message = "numpy.dtype size changed")

from IPython.core import debugger; debug = debugger.Pdb().set_trace
from os import listdir
from os.path import isfile, join
from recorder import Recorder
from scipy.ndimage.measurements import center_of_mass as com
import matplotlib.pyplot as plt
import numpy as np
import sunpy.map as smap
from scipy.ndimage import zoom as interpolate

RECORDER = Recorder()
RECORDER.display_start_time("go")

RECORDER.sys_text("Importing data...")

# IMAGE_SAVEPATH = "/Volumes/Nicholas Data/images/"
IMAGE_SAVEPATH = "/Users/lockheedmartin/Desktop/images/"
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

ID = 0
PREFLARE_COUNT = 1920

for i in range(PREFLARE_COUNT):
	AIA171 = smap.Map(PATH171 + AIA171_DIR[i])
	AIA304 = smap.Map(PATH304 + AIA304_DIR[i])
	HMI = smap.Map(PATHHMI + HMI_DIR[i])

	RECORDER.info_text("Current timestamp: %s" % AIA171.date)

	img = AIA171.data
	img[img < 1] = 1
	img = np.sqrt(img)

	RECORDER.sys_text("Writing full-disk AIA171 image (sqrt-adj) #%05d..." % ID)
	plt.imsave(IMAGE_SAVEPATH + "aia171-images/%05d" % ID, img, cmap = "sdoaia171", origin = "lower")

	img = AIA304.data
	img[img < 1] = 1
	img = np.log(img)

	RECORDER.sys_text("Writing full-disk AIA304 image (log-adj) #%05d..." % ID)
	plt.imsave(IMAGE_SAVEPATH + "aia304-images/%05d" % ID, img, cmap = "sdoaia304", origin = "lower")

	RECORDER.info_text("Aligning HMI full-disk image #%05d" % ID)
	scale = (HMI.scale[0] / AIA304.scale[0]).value
	scale = float("%.3f" % scale)
	ALIGNED_RAW_HMI = hmialign(HMI.data, scale)

	RECORDER.sys_text("Writing full-disk HMI image #%05d..." % ID)
	plt.imsave(IMAGE_SAVEPATH + "hmi-images/%05d" % ID, ALIGNED_RAW_HMI, cmap = "bwr", origin = "lower", vmin = -120, vmax = 120)

	ID += 1

#################################################
#################################################
#################################################

RECORDER.info_text("Preparing for zoom animation...")

AIA171 = smap.Map(PATH171 + AIA171_DIR[ID])
AIA304 = smap.Map(PATH304 + AIA304_DIR[ID])
HMI = smap.Map(PATHHMI + HMI_DIR[ID])

aia171_img = AIA171.data
aia171_img[aia171_img < 1] = 1
aia171_img = np.sqrt(aia171_img)

aia304_img = AIA304.data
aia304_img[aia304_img < 1] = 1
aia304_img = np.log(aia304_img)

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

NEW_ID = ID

for i in range(N):
	RECORDER.info_text("Iterating zoom on AIA171 image...")
	img = aia171_img[int(i * v_bot) : int(4096 - i * v_top),
					 int(i * v_left) : int(4096 - i * v_right)]
	RECORDER.sys_text("Writing zoomed AIA171 image #%05d..." % NEW_ID)
	plt.imsave(IMAGE_SAVEPATH + "aia171-images/%05d" % NEW_ID, img, cmap = "sdoaia171", origin = "lower")

	RECORDER.info_text("Iterating zoom on AIA304 image...")
	img = aia304_img[int(i * v_bot) : int(4096 - i * v_top),
					 int(i * v_left) : int(4096 - i * v_right)]
	RECORDER.sys_text("Writing zoomed AIA304 image #%05d..." % NEW_ID)
	plt.imsave(IMAGE_SAVEPATH + "aia304-images/%05d" % NEW_ID, img, cmap = "sdoaia304", origin = "lower")

	RECORDER.info_text("Iterating zoom on HMI image...")
	img = hmi_img[int(i * v_bot) : int(4096 - i * v_top),
				  int(i * v_left) : int(4096 - i * v_right)]
	RECORDER.sys_text("Writing zoomed HMI image #%05d..." % NEW_ID)
	plt.imsave(IMAGE_SAVEPATH + "hmi-images/%05d" % NEW_ID, img, cmap = "bwr", origin = "lower", vmin = -120, vmax = 120)

	TEMP_ID += 1

#################################################
#################################################
#################################################

# animations run only on 304 and HMI image
# maybe apply sobel algorithm to 171 image

RECORDER.info_text("Generating raw mask animations...")

RECORDER.info_text("Generating elliptical mask animations...")

RECORDER.info_text("Generating contour mask animations...")

# RUN MASK ANIMATIONS
# USE SUNPY SOLAR ROTATE COORDINATE TO FOLLOW AR
