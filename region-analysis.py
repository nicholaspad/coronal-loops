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

		RECORDER.show_instr(PRODUCT)
		RECORDER.write_ID(LOOP_ID)

		when = DATA[PRODUCT].date
		RECORDER.write_datetime(when)

		xy = REGIONS[i, j]
		RECORDER.write_xywhere(xy)

		center = np.array([int(DATA[PRODUCT][i].reference_pixel[0].value),
						   int(DATA[PRODUCT][i].reference_pixel[1].value)])
		radius = (DATA[PRODUCT][i].rsun_obs / DATA[PRODUCT][i].scale[0]).value

		##### algorithm to eliminate regions far from solar center

		OFF_DISK_THRESHOLD = 50.0

		if distance.euclidean(center, xy) >= (radius - OFF_DISK_THRESHOLD):
			RECORDER.off_disk()
			ADD_OFFDISK = True
			break

		hpc = REGIONS_HPC[i, j]
		RECORDER.write_hpcwhere(hpc)

		##### algorithm to determine bounds of region

		AVERAGE_BRIGHTNESS_THRESHOLD = 240.0
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

		# SAVE IMAGE
		cut_aia

		##### sets a threshold, takes a few statistics

		LOW_BRIGHTNESS_THRESHOLD = 40

		temp_threshold_data = cut_aia[np.where(cut_aia > LOW_BRIGHTNESS_THRESHOLD)]
		average_intensity = np.average(temp_threshold_data)
		median_intensity = np.median(temp_threshold_data)
		maximum_intensity = np.max(temp_threshold_data)

		RECORDER.write_inten(LOW_BRIGHTNESS_THRESHOLD,
							 average_intensity,
							 median_intensity,
							 maximum_intensity)

		##### creates and grows a binary mask based on the threshold

		binary_mask = np.logical_and(cut_aia > LOW_BRIGHTNESS_THRESHOLD,
									 cut_aia < np.inf)
		binary_mask = grow_mask(binary_mask,
								iterations = 1,
								structure = np.ones((3,3)).astype(bool)).astype(int)

		masked_aia_data = cut_aia * binary_mask

		# SAVE IMAGE
		masked_aia_data

		##### fits an ellipse to a proportion of the positive mask values

		center = com(binary_mask)
		x_center = int(center[0] + 0.5)
		y_center = int(center[1] + 0.5)
		binary_mask[x_center, y_center] = 2
		dim = cd_data.shape[0]
		threshold_percent_1 = 0.98
		threshold_percent_2 = 0.95
		threshold_percent_3 = 0.92

		total = float(len(np.where(binary_mask == 1)[0]))
		rad = 2.0
		y, x = np.ogrid[-x_center:dim - x_center, -y_center:dim - y_center]
		mask_in = None
		mask_out = None

		while True:
			temp_in = x**2 + y**2 <= rad**2
			if len(np.where(binary_mask * temp_in == 1)[0]) / total >= threshold_percent_1:
				mask_in = temp_in
				break
			rad += 1.0

		a = b = rad

		while True:
			temp_in = x**2/a**2 + y**2/b**2 <= 1
			if len(np.where(binary_mask * temp_in == 1)[0]) / total < threshold_percent_2:
				mask_in = temp_in
				break
			a -= 1.0

		while True:
			temp_in = x**2/a**2 + y**2/b**2 <= 1
			temp_out = x**2/a**2 + y**2/b**2 > 1
			if len(np.where(binary_mask * temp_in == 1)[0]) / total < threshold_percent_3:
				mask_in = temp_in
				mask_out = temp_out
				break
			b -= 1.0

		e_binary_mask = binary_mask * mask_in

		# SAVE IMAGE
		e_binary_mask

		e_masked_aia_data = cut_aia * e_binary_mask
		e_masked_aia_data[mask_out] = np.nan

		# SAVE IMAGE
		e_masked_aia_data

		# TODO: further processing on e_masked_aia_data

		casted_hmi_data = np.zeros((4096, 4096))
		casted_hmi_data[casted_hmi_data == 0] = 10000
		scale = (hmi.scale[0] / aia.scale[0]).value
		scale = float("%.3f" % scale)

		interpolated_hmi_data = interpolate(RAW_HMI,
											scale,
											order = 1)
		interpolated_hmi_data = np.flip(interpolated_hmi_data,
										(0,1))

		x_size = interpolated_hmi_data.shape[0]
		y_size = interpolated_hmi_data.shape[1]
		x_center = int(aia.reference_pixel.x.value + 0.5) - 9
		y_center = int(aia.reference_pixel.y.value + 0.5) + 4

		ALIGNED_RAW_HMI[(y_center - 1 - y_size / 2) : (y_center + y_size / 2),
						(x_center - 1 - x_size / 2) : (x_center + x_size / 2)] = interpolated_hmi_data

		cut_hmi = ALIGNED_RAW_HMI[x1 : x2,
								  y1 : y2]

		# SAVE IMAGE
		cut_hmi

		masked_hmi_data = cut_hmi * binary_mask

		# SAVE IMAGE
		masked_hmi_data

		e_masked_hmi_data = cut_hmi * e_binary_mask
		e_masked_hmi_data[mask_out] = np.nan

		# SAVE IMAGE
		e_masked_hmi_data

		# TODO: temp_threshold_data for HMI
		# run calculations on the above (in the original program)



























