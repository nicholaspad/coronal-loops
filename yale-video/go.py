import warnings
warnings.filterwarnings("ignore", message = "numpy.dtype size changed")

from copy import copy
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

ID = 0
PREFLARE_COUNT = 1920

RECORDER.info_text("Generating pre-flare full-disk images...")

for i in range(PREFLARE_COUNT):
	AIA171 = smap.Map(PATH171 + AIA171_DIR[i])
	AIA304 = smap.Map(PATH304 + AIA304_DIR[i])
	HMI = smap.Map(PATHHMI + HMI_DIR[i])

	RECORDER.sys_text("Writing full-disk AIA171 image (sqrt-adj) #%05d..." % ID)
	img = AIA171.data
	img[img < 1] = 1
	img = np.sqrt(img)
	plt.imsave(IMAGE_SAVEPATH + "aia171-images/%05d" % ID, img, cmap = "sdoaia171", origin = "lower")

	RECORDER.sys_text("Writing full-disk AIA304 image (log-adj) #%05d..." % ID)
	img = AIA304.data
	img[img < 1] = 1
	img = np.log(img)
	plt.imsave(IMAGE_SAVEPATH + "aia304-images/%05d" % ID, img, cmap = "sdoaia304", origin = "lower")

	RECORDER.info_text("Aligning HMI full-disk image #%05d" % ID)

	ALIGNED_RAW_HMI = np.zeros((4096, 4096)).astype(float)
	ALIGNED_RAW_HMI[ALIGNED_RAW_HMI == 0] = -10000000
	scale = (HMI.scale[0] / AIA304.scale[0]).value
	scale = float("%.3f" % scale)

	RECORDER.info_text("Interpolating HMI data with %.6f scale factor..." % scale)
	interpolated_hmi_data = interpolate(HMI.data, scale, order = 1)
	interpolated_hmi_data = np.flip(interpolated_hmi_data, (0,1))

	x_size = interpolated_hmi_data.shape[1]
	y_size = interpolated_hmi_data.shape[0]
	x_center = int(AIA304.reference_pixel.y.value + 0.5)
	y_center = int(AIA304.reference_pixel.x.value + 0.5)

	RECORDER.info_text("Casting interpolated HMI data to 4k by 4k empty image...")
	ALIGNED_RAW_HMI[(y_center - 1 - y_size / 2) : (y_center + y_size / 2),
					(x_center - 1 - x_size / 2) : (x_center + x_size / 2)] = interpolated_hmi_data

	ALIGNED_RAW_HMI[np.isnan(ALIGNED_RAW_HMI)] = -10000000

	RECORDER.sys_text("Writing full-disk HMI image #%05d..." % ID)
	plt.imsave(IMAGE_SAVEPATH + "hmi-images/%05d" % ID, ALIGNED_RAW_HMI, cmap = "gray", origin = "lower", vmin = -120, vmax = 120)

	ID += 1
