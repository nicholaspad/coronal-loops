import warnings
warnings.filterwarnings("ignore", message = "numpy.dtype size changed")

from astropy.coordinates import SkyCoord
from datetime import datetime
from helper import clear_filesystem
from IPython.core import debugger; debug = debugger.Pdb().set_trace
from recorder import Recorder
from scipy.ndimage import zoom as interpolate
from scipy.ndimage.morphology import binary_dilation as grow_mask
from scipy.spatial import distance
from skimage.transform import resize
import astropy.units as u
import getpass
import matplotlib.pyplot as plt
import numpy as np
import os
import scipy
import scipy.ndimage as ndimage
import scipy.ndimage.filters as filters
import sunpy.map as smap

##### initial setup #####

MAIN_DIR = "/Users/%s/Desktop/lmsal" % getpass.getuser()
RECORDER = Recorder("database.csv")
RECORDER.display_start_time("region-analysis")
clear_filesystem()

##### import data #####

RECORDER.info_text("Importing AIA171 data")
MAPCUBE_AIA_171 = smap.Map("%s/resources/aia-fits-files/*.171.image_lev1.fits" % MAIN_DIR, sequence = True)
RECORDER.info_text("Importing AIA304 data")
MAPCUBE_AIA_304 = smap.Map("%s/resources/aia-fits-files/*.304.image_lev1.fits" % MAIN_DIR, sequence = True)
RECORDER.info_text("Importing HMI magnetogram data\n")
MAPCUBE_HMI = smap.Map("%s/resources/hmi-fits-files/*.fits" % MAIN_DIR, sequence = True)

##### prepare mapcube #####

DATA = {
	"AIA171" : MAPCUBE_AIA_171,
	"AIA304" : MAPCUBE_AIA_304,
	"HMI" : MAPCUBE_HMI
}

N = len(DATA["AIA171"])

##### helper variables #####

LOOP_ID = 1
NUM_LOOPS = 0

ADD_OFFDISK = False
NUM_OFF_DISK = 0

ADD_SMALL = False
NUM_SMALL = 0

##### find and store bright regions #####

REGIONS = []
REGIONS_HPC = []

for i in range(N):

	RAW = DATA["AIA171"][i].data

	MIN_DISTANCE = 1000
	MIN_VALUE = 0.6 * RAW.max()

	max = filters.maximum_filter(RAW,
								 MIN_DISTANCE)
	temp = (RAW == max)
	min = filters.minimum_filter(RAW,
								 MIN_DISTANCE)
	diff = ((max - min) > MIN_VALUE)
	temp[diff == 0] = 0

	labeled, num_objects = ndimage.label(temp)
	xy_maxima = np.array(ndimage.center_of_mass(RAW,
												labeled,
												range(1, num_objects + 1)))

	xy_maxima = xy_maxima.astype(int)
	REGIONS.append(xy_maxima)

	if xy_maxima.shape[0] == 0:

		REGIONS_HPC.append(np.array([]))

	else:

		REGIONS_HPC.append(DATA["AIA171"][i].pixel_to_world(xy_maxima[:, 1] * u.pixel,
															xy_maxima[:, 0] * u.pixel))

##### analyze bright regions #####

M = len(REGIONS)

for i in range(N):

	RAW_AIA = DATA["AIA304"][i].data
	RAW_HMI = DATA["HMI"][i].data

	for j in range(M):

		OFF_DISK_THRESHOLD = 50.0
		AVERAGE_BRIGHTNESS_THRESHOLD = 240.0
		LOW_BRIGHTNESS_THRESHOLD = 530.0

		RECORDER.show_instr(PRODUCT)
		RECORDER.write_ID(LOOP_ID)

		when = DATA[PRODUCT].date
		RECORDER.write_datetime(when)

		xy = REGIONS[i, j]
		RECORDER.write_xywhere(xy)

		center = np.array([int(DATA[PRODUCT][i].reference_pixel[0].value),
						   int(DATA[PRODUCT][i].reference_pixel[1].value)])
		radius = (DATA[PRODUCT][i].rsun_obs / DATA[PRODUCT][i].scale[0]).value

		if distance.euclidean(center, xy) >= (radius - OFF_DISK_THRESHOLD):
			RECORDER.off_disk()
			ADD_OFFDISK = True
			break

		hpc = REGIONS_HPC[i, j]
		RECORDER.write_hpcwhere(hpc)

		HALF_DIM_PXL = 1
		while np.average(RAW_AIA[xy[0] - HALF_DIM_PXL : xy[0] + HALF_DIM_PXL,
								 xy[1] - HALF_DIM_PXL: xy[1] + HALF_DIM_PXL]) > AVERAGE_BRIGHTNESS_THRESHOLD:
			HALF_DIM_PXL += 1

		if HALF_DIM_PXL < 50.0:
			RECORDER.too_small()
			ADD_SMALL = True
			break

		RECORDER.write_xysize(HALF_DIM_PXL * 2.0)

		HALF_DIM_HPC = DATA["AIA304"][i].scale[0].value * HALF_DIM_PXL

		bl = SkyCoord(hpc.Tx - HALF_DIM_HPC * u.arcsec,
					  hpc.Ty - HALF_DIM_HPC * u.arcsec,
					  frame = DATA["AIA304"][i].coordinate_frame)

		tr = SkyCoord(hpc.Tx + HALF_DIM_HPC * u.arcsec,
					  hpc.Ty + HALF_DIM_HPC * u.arcsec,
					  frame = DATA["AIA304"][i].coordinate_frame)

		RECORDER.write_hpcsize(bl, tr)

		cut_aia = RAW_AIA[xy[0] - HALF_DIM_PXL : xy[0] + HALF_DIM_PXL,
						  xy[1] - HALF_DIM_PXL: xy[1] + HALF_DIM_PXL]

		### SEE NOTES
