import warnings
warnings.filterwarnings("ignore", message = "numpy.dtype size changed")

from astropy.coordinates import SkyCoord
from datetime import datetime
from IPython.core import debugger ; debug = debugger.Pdb().set_trace
from recorder import Recorder
from scipy.ndimage import zoom as interpolate
from scipy.spatial import distance
import astropy.units as u
import getpass
import matplotlib.pyplot as plt
import numpy as np
import os
import scipy
import scipy
import scipy.ndimage as ndimage
import scipy.ndimage.filters as filters
import sunpy.map as smap

MAIN_DIR = "/Users/%s/Desktop/lmsal" % getpass.getuser()
RECORDER = Recorder("database.csv")
RECORDER.display_start_time("loop-analysis")

def zero_padder(vector, pad_width, iaxis, kwargs):
	pad_value = kwargs.get('padder', 10)
	vector[:pad_width[0]] = pad_value
	vector[-pad_width[1]:] = pad_value
	return vector

# np.pad(a, DIM, zero_padder, padder=100)

os.system("rm -rf resources/region-data/raw-images && mkdir resources/region-data/raw-images")
os.system("rm -rf resources/region-data/binary-images && mkdir resources/region-data/binary-images")
os.system("rm -rf resources/region-data/threshold-images && mkdir resources/region-data/threshold-images")
os.system("rm -rf resources/region-data/magnetogram-images && mkdir resources/region-data/magnetogram-images")

LOOP_ID = 0
NUM_LOOPS = 0
NUM_OFF_DISK = 0
NUM_SMALL = 0

RECORDER.info_text("Importing AIA94 data")
MAPCUBE_AIA_94 = smap.Map("%s/resources/aia-fits-files/*.94.image_lev1.fits" % MAIN_DIR, cube = True)

RECORDER.info_text("Importing AIA131 data")
MAPCUBE_AIA_131 = smap.Map("%s/resources/aia-fits-files/*.131.image_lev1.fits" % MAIN_DIR, cube = True)

RECORDER.info_text("Importing AIA171 data")
MAPCUBE_AIA_171 = smap.Map("%s/resources/aia-fits-files/*.171.image_lev1.fits" % MAIN_DIR, cube = True)

RECORDER.info_text("Importing AIA193 data")
MAPCUBE_AIA_193 = smap.Map("%s/resources/aia-fits-files/*.193.image_lev1.fits" % MAIN_DIR, cube = True)

RECORDER.info_text("Importing AIA211 data")
MAPCUBE_AIA_211 = smap.Map("%s/resources/aia-fits-files/*.211.image_lev1.fits" % MAIN_DIR, cube = True)

RECORDER.info_text("Importing AIA304 data")
MAPCUBE_AIA_304 = smap.Map("%s/resources/aia-fits-files/*.304.image_lev1.fits" % MAIN_DIR, cube = True)

RECORDER.info_text("Importing AIA335 data")
MAPCUBE_AIA_335 = smap.Map("%s/resources/aia-fits-files/*.335.image_lev1.fits" % MAIN_DIR, cube = True)

RECORDER.info_text("Importing HMI magnetogram data\n")
MAPCUBE_HMI = smap.Map("%s/resources/hmi-fits-files/*.fits" % MAIN_DIR, cube = True)

MAPCUBE = {
	"AIA94" : MAPCUBE_AIA_94,
	"AIA131" : MAPCUBE_AIA_131,
	"AIA171" : MAPCUBE_AIA_171,
	"AIA193" : MAPCUBE_AIA_193,
	"AIA211" : MAPCUBE_AIA_211,
	"AIA304" : MAPCUBE_AIA_304,
	"AIA335" : MAPCUBE_AIA_335,
	"HMI" : MAPCUBE_HMI
}

MEASUREMENTS = ["AIA94", "AIA131",
				"AIA171", "AIA193",
				"AIA211", "AIA304",
				"AIA335"]

for i in range(len(MAPCUBE["AIA171"])):

	raw_data = MAPCUBE["AIA171"][i].data

	#################################
	min_distance = 1000
	threshold = 0.6 * raw_data.max()
	#################################

	data_max = filters.maximum_filter(raw_data, min_distance)
	maxima = (raw_data == data_max)
	data_min = filters.minimum_filter(raw_data, min_distance)
	diff = ((data_max - data_min) > threshold)
	maxima[diff == 0] = 0

	labeled, num_objects = ndimage.label(maxima)
	xy_maxima = np.array(ndimage.center_of_mass(raw_data, labeled, range(1, num_objects + 1)))
	xy_maxima = xy_maxima.astype(int)

	if xy_maxima.shape[0] == 0:
		hp_maxima = np.array([])

	else:
		hp_maxima = MAPCUBE["AIA171"][i].pixel_to_world(xy_maxima[:, 1] * u.pixel,
														xy_maxima[:, 0] * u.pixel)

	for j in range(len(hp_maxima)):

		for MEAS in MEASUREMENTS:

			RECORDER.write_ID(LOOP_ID)
			RECORDER.write_gen_info(MAPCUBE[MEAS][i].detector, MAPCUBE[MEAS][i].wavelength)

			when = MAPCUBE[MEAS][i].date
			RECORDER.write_datetime(when)

			where_xy = xy_maxima[j]
			RECORDER.write_xywhere(where_xy)

			center = np.array([int(MAPCUBE[MEAS][i].reference_pixel[0].value),
							   int(MAPCUBE[MEAS][i].reference_pixel[1].value)])

			radius = (MAPCUBE[MEAS][i].rsun_obs / MAPCUBE[MEAS][i].scale[0]).value

			#######################################################
			if distance.euclidean(center, where_xy) > radius - 100:
			#######################################################
				RECORDER.off_disk()
				LOOP_ID += 1
				NUM_OFF_DISK += 1
				continue

			where_hpc = hp_maxima[j]
			RECORDER.write_hpcwhere(where_hpc)

			HALF_DIM_PXL = 1

			####################
			MIN_AVERAGE = 1475.0
			####################

			while np.average(raw_data[xy_maxima[j][0] - HALF_DIM_PXL : xy_maxima[j][0] + HALF_DIM_PXL,
							 xy_maxima[j][1] - HALF_DIM_PXL: xy_maxima[j][1] + HALF_DIM_PXL]) > MIN_AVERAGE:
				HALF_DIM_PXL += 1

			########################
			if HALF_DIM_PXL < 50.0:
			########################
				RECORDER.too_small()
				LOOP_ID += 1
				NUM_SMALL += 1
				continue

			RECORDER.write_xysize(HALF_DIM_PXL * 2)

			HALF_DIM_HPC = MAPCUBE[MEAS][i].scale[0].value * HALF_DIM_PXL

			BOTTOM_LEFT = SkyCoord(where_hpc.Tx - HALF_DIM_HPC * u.arcsec,
								   where_hpc.Ty - HALF_DIM_HPC * u.arcsec,
								   frame = MAPCUBE[MEAS][i].coordinate_frame)

			TOP_RIGHT = SkyCoord(where_hpc.Tx + HALF_DIM_HPC * u.arcsec,
								 where_hpc.Ty + HALF_DIM_HPC * u.arcsec,
								 frame = MAPCUBE[MEAS][i].coordinate_frame)

			RECORDER.write_hpcsize(BOTTOM_LEFT, TOP_RIGHT)

			cd_data = MAPCUBE[MEAS][i].data[xy_maxima[j][0] - HALF_DIM_PXL : xy_maxima[j][0] + HALF_DIM_PXL,
							   xy_maxima[j][1] - HALF_DIM_PXL: xy_maxima[j][1] + HALF_DIM_PXL]

			########################
			LOW_THRESHOLD_171 = 1700
			########################

			cd_data_171 = MAPCUBE["AIA171"][i].data[xy_maxima[j][0] - HALF_DIM_PXL : xy_maxima[j][0] + HALF_DIM_PXL,
													xy_maxima[j][1] - HALF_DIM_PXL: xy_maxima[j][1] + HALF_DIM_PXL]
			LOW_THRESHOLD = 0
			previous_low = 0
			new_low = 0
			target = len(cd_data_171[np.where(cd_data_171 > LOW_THRESHOLD_171)])

			while len(cd_data[np.where(cd_data > LOW_THRESHOLD)]) > target:
				previous_low = len(cd_data[np.where(cd_data > LOW_THRESHOLD)])
				LOW_THRESHOLD += 1
				new_low = len(cd_data[np.where(cd_data > LOW_THRESHOLD)])
			
			if np.abs(target - new_low) > np.abs(target - previous_low):
				LOW_THRESHOLD -= 1

			HIGH_THRESHOLD = np.inf

			threshold_data = cd_data[np.where(cd_data > LOW_THRESHOLD)]

			average_intensity = np.average(threshold_data)
			median_intensity = np.median(threshold_data)
			maximum_intensity = np.max(threshold_data)

			RECORDER.write_inten(LOW_THRESHOLD,
								 average_intensity,
								 median_intensity,
								 maximum_intensity)

			binary_image_data = np.logical_and(cd_data > LOW_THRESHOLD,
											   cd_data < HIGH_THRESHOLD)

			threshold_image_data = cd_data * binary_image_data

			RECORDER.write_image(0,
								 LOOP_ID,
								 np.flip(cd_data, 0),
								 MAPCUBE[MEAS][i].detector,
								 MAPCUBE[MEAS][i].wavelength)
			RECORDER.write_image(1,
								 LOOP_ID,
								 np.flip(binary_image_data, 0),
								 MAPCUBE[MEAS][i].detector,
								 MAPCUBE[MEAS][i].wavelength)
			RECORDER.write_image(2,
								 LOOP_ID,
								 np.flip(threshold_image_data, 0),
								 MAPCUBE[MEAS][i].detector,
								 MAPCUBE[MEAS][i].wavelength)
			
			hmi_raw_data = MAPCUBE["HMI"][i].data

			SCALE = float("%.3f" % (MAPCUBE["HMI"][i].scale[0].value / MAPCUBE[MEAS][i].scale[0].value))

			hmi_mod_data = interpolate(hmi_raw_data,
			 						   SCALE,
			 						   order = 1)
			
			PAD = (MAPCUBE[MEAS][i].shape[0] - hmi_mod_data.shape[0]) / 2

			hmi_mod_data = np.pad(hmi_mod_data,PAD , zero_padder, padder = np.nan)

			debug()

			dim = hmi_mod_data.shape[0]
			rad = MAPCUBE[MEAS][i].rsun_obs.value / MAPCUBE[MEAS][i].scale[0].value
			center_x = MAPCUBE[MEAS][i].reference_pixel[0].value
			center_y = MAPCUBE[MEAS][i].reference_pixel[1].value

			y, x = np.ogrid[-center_x : dim - center_x, -center_y : dim - center_y]
			mask = x * x + y * y >= rad * rad
			hmi_mod_data[mask] = np.inf

			# hmi_loc = MAPCUBE["HMI"][i].world_to_pixel(where_hpc)

			if int(where_xy[0].value - HALF_DIM_PXL) < 0:
				y1 = 0
			else:
				y1 = int(where_xy[0].value - HALF_DIM_PXL)

			if int(where_xy[0].value + HALF_DIM_PXL) > MAPCUBE["HMI"][i].data.shape[0]:
				y2 = MAPCUBE["HMI"][i].data.shape[0]
			else:
				y2 = int(where_xy[0].value + HALF_DIM_PXL)

			if int(where_xy[1].value - HALF_DIM_PXL) < 0:
				x1 = 0
			else:
				x1 = int(where_xy[1].value - HALF_DIM_PXL)

			if int(where_xy[1].value + HALF_DIM_PXL) > MAPCUBE["HMI"][i].data.shape[1]:
				x2 = MAPCUBE["HMI"][i].data.shape[1]
			else:
				x2 = int(where_xy[1].value + HALF_DIM_PXL)

			hmi_cd_data = hmi_mod_data[x1 : x2,
									   y1 : y2]

			###########################
			LOW_THRESHOLD_HMI = -1500.0
			HIGH_THRESHOLD_HMI = 1500.0
			###########################

			hmi_threshold_image_data = hmi_cd_data[np.where(np.logical_and(hmi_cd_data > LOW_THRESHOLD_HMI,
																		   hmi_cd_data < HIGH_THRESHOLD_HMI))]

			unsig_flux = np.sum(np.abs(hmi_threshold_image_data))
			avg_flux = np.average(hmi_threshold_image_data)

			RECORDER.write_flux(unsig_flux, avg_flux)

			RECORDER.write_image(3,
								 LOOP_ID,
								 np.flip(hmi_cd_data, 1),
								 MAPCUBE["HMI"][i].detector,
								 MAPCUBE["HMI"][i].wavelength)

			RECORDER.new_line()
			NUM_LOOPS += 1

		LOOP_ID += 1

RECORDER.info_text("Compressing database\n")
os.chdir("resources/")
os.system("zip -r -X data_%s.zip region-data" % str(datetime.now().strftime("%Y-%m-%d_%H.%M.%S")))
os.chdir("../")
RECORDER.info_text("Done:\t%s regions analyzed\n\t\t%s regions off-disk\n\t\t%s regions too small" % (NUM_LOOPS, NUM_OFF_DISK, NUM_SMALL))
RECORDER.line()
RECORDER.display_end_time("loop-analysis")
