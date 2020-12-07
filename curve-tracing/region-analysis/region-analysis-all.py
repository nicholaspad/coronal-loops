import warnings
warnings.filterwarnings("ignore", message = "numpy.dtype size changed")

from astropy.coordinates import SkyCoord
from datetime import datetime
from IPython.core import debugger ; debug = debugger.Pdb().set_trace
from recorder import Recorder
from skimage.transform import resize
from scipy.ndimage import zoom as interpolate
from scipy.ndimage.morphology import binary_dilation as grow_mask
from scipy.spatial import distance
import astropy.units as u
import getpass
import matplotlib.pyplot as plt
import numpy as np
import os
import scipy
import scipy.ndimage as ndimage
import scipy.ndimage.filters as filters
import sunpy.map as smap

MAIN_DIR = "/Users/%s/Desktop/lmsal" % getpass.getuser()
RECORDER = Recorder("database.csv")
RECORDER.display_start_time("loop-analysis")

os.system("rm -rf resources/region-data/raw-images && mkdir resources/region-data/raw-images")
os.system("rm -rf resources/region-data/binary-images && mkdir resources/region-data/binary-images")
os.system("rm -rf resources/region-data/threshold-images && mkdir resources/region-data/threshold-images")
os.system("rm -rf resources/region-data/magnetogram-images && mkdir resources/region-data/magnetogram-images")
os.system("rm -rf resources/region-data/masked-magnetogram-images && mkdir resources/region-data/masked-magnetogram-images")

RECORDER.info_text("Importing AIA94 data")
MAPCUBE_AIA_94 = smap.Map("%s/resources/aia-fits-files/*.94.image_lev1.fits" % MAIN_DIR, sequence = True)

RECORDER.info_text("Importing AIA131 data")
MAPCUBE_AIA_131 = smap.Map("%s/resources/aia-fits-files/*.131.image_lev1.fits" % MAIN_DIR, sequence = True)

RECORDER.info_text("Importing AIA171 data")
MAPCUBE_AIA_171 = smap.Map("%s/resources/aia-fits-files/*.171.image_lev1.fits" % MAIN_DIR, sequence = True)

RECORDER.info_text("Importing AIA193 data")
MAPCUBE_AIA_193 = smap.Map("%s/resources/aia-fits-files/*.193.image_lev1.fits" % MAIN_DIR, sequence = True)

RECORDER.info_text("Importing AIA211 data")
MAPCUBE_AIA_211 = smap.Map("%s/resources/aia-fits-files/*.211.image_lev1.fits" % MAIN_DIR, sequence = True)

RECORDER.info_text("Importing AIA304 data")
MAPCUBE_AIA_304 = smap.Map("%s/resources/aia-fits-files/*.304.image_lev1.fits" % MAIN_DIR, sequence = True)

RECORDER.info_text("Importing AIA335 data")
MAPCUBE_AIA_335 = smap.Map("%s/resources/aia-fits-files/*.335.image_lev1.fits" % MAIN_DIR, sequence = True)

RECORDER.info_text("Importing HMI magnetogram data\n")
MAPCUBE_HMI = smap.Map("%s/resources/hmi-fits-files/*.fits" % MAIN_DIR, sequence = True)

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
				"AIA211", "AIA335",
				"AIA304"]

LOOP_ID = 1
NUM_LOOPS = 0
NUM_OFF_DISK = 0
NUM_SMALL = 0
# NUM_UNIPOLAR = 0
ADD_OFFDISK = False
ADD_SMALL = False
# ADD_UNIPOLAR = False

for i in range(len(MAPCUBE["AIA171"])):

	raw_data_171 = MAPCUBE["AIA171"][i].data
	raw_data_304 = MAPCUBE["AIA304"][i].data

	MIN_DISTANCE_FROM_OTHER_REGIONS = 1000 # larger value --> fewer regions
	MIN_THRESHOLD_OF_REGION = 0.6 * raw_data_171.max() # larger decimal --> select increasingly brighter regions

	data_max = filters.maximum_filter(raw_data_171,
									  MIN_DISTANCE_FROM_OTHER_REGIONS)
	maxima = (raw_data_171 == data_max)
	data_min = filters.minimum_filter(raw_data_171,
									  MIN_DISTANCE_FROM_OTHER_REGIONS)
	diff = ((data_max - data_min) > MIN_THRESHOLD_OF_REGION)
	maxima[diff == 0] = 0

	labeled, num_objects = ndimage.label(maxima)
	xy_maxima = np.array(ndimage.center_of_mass(raw_data_171,
												labeled,
												range(1, num_objects + 1)))
	xy_maxima = xy_maxima.astype(int)

	if xy_maxima.shape[0] == 0:
		hp_maxima = np.array([])

	else:
		hp_maxima = MAPCUBE["AIA171"][i].pixel_to_world(xy_maxima[:, 1] * u.pixel,
														xy_maxima[:, 0] * u.pixel)

	for j in range(len(hp_maxima)):

		for MEAS in MEASUREMENTS:

			OFF_DISK_THRESHOLD = 100 # pixels; regions farther than (RADIUS - OFF_DISK_THRESHOLD) pixels from the solar center are ignored
			MIN_AVERAGE = 240.0 # larger value --> smaller region dimensions
			LOW_THRESHOLD_304 = 530 # larger value --> fewer region pixels

			RECORDER.show_instr(MEAS)
			RECORDER.write_ID(LOOP_ID)

			when = MAPCUBE[MEAS][i].date
			RECORDER.write_datetime(when)

			where_xy = xy_maxima[j]
			RECORDER.write_xywhere(where_xy)

			center = np.array([int(MAPCUBE[MEAS][i].reference_pixel[0].value),
							   int(MAPCUBE[MEAS][i].reference_pixel[1].value)])

			radius = (MAPCUBE[MEAS][i].rsun_obs / MAPCUBE[MEAS][i].scale[0]).value

			if distance.euclidean(center, where_xy) > (radius - OFF_DISK_THRESHOLD):
				RECORDER.off_disk()
				ADD_OFFDISK = True
				break

			where_hpc = hp_maxima[j]
			RECORDER.write_hpcwhere(where_hpc)

			HALF_DIM_PXL = 1

			while np.average(raw_data_304[xy_maxima[j][0] - HALF_DIM_PXL : xy_maxima[j][0] + HALF_DIM_PXL,
							 xy_maxima[j][1] - HALF_DIM_PXL: xy_maxima[j][1] + HALF_DIM_PXL]) > MIN_AVERAGE:
				HALF_DIM_PXL += 1

			if HALF_DIM_PXL < 50.0:
				RECORDER.too_small()
				ADD_SMALL = True
				break

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

			cd_data_304 = MAPCUBE["AIA304"][i].data[xy_maxima[j][0] - HALF_DIM_PXL : xy_maxima[j][0] + HALF_DIM_PXL,
													xy_maxima[j][1] - HALF_DIM_PXL: xy_maxima[j][1] + HALF_DIM_PXL]
			
			HIGH_THRESHOLD = np.inf
			LOW_THRESHOLD = 0
			previous_low = 0
			new_low = 0
			target = len(cd_data_304[np.where(cd_data_304 > LOW_THRESHOLD_304)])

			while len(cd_data[np.where(cd_data > LOW_THRESHOLD)]) > target:
				previous_low = len(cd_data[np.where(cd_data > LOW_THRESHOLD)])
				LOW_THRESHOLD += 1
				new_low = len(cd_data[np.where(cd_data > LOW_THRESHOLD)])
			
			if np.abs(target - new_low) > np.abs(target - previous_low):
				LOW_THRESHOLD -= 1

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
								 cd_data,
								 MAPCUBE[MEAS][i].detector,
								 MAPCUBE[MEAS][i].wavelength)
			RECORDER.write_image(1,
								 LOOP_ID,
								 binary_image_data,
								 MAPCUBE[MEAS][i].detector,
								 MAPCUBE[MEAS][i].wavelength)
			RECORDER.write_image(2,
								 LOOP_ID,
								 threshold_image_data,
								 MAPCUBE[MEAS][i].detector,
								 MAPCUBE[MEAS][i].wavelength)
			
			hmi_raw_data = MAPCUBE["HMI"][i].data

			casted_hmi_data = np.zeros((4096, 4096))
			casted_hmi_data[casted_hmi_data == 0] = 99999
			scale = (MAPCUBE["HMI"][i].scale[0]/MAPCUBE[MEAS][i].scale[0]).value
			scale = float("%.3f" % scale)

			interpolated_hmi_data = interpolate(hmi_raw_data, scale, order = 1)
			interpolated_hmi_data = np.flip(interpolated_hmi_data, (0,1))

			x_size = interpolated_hmi_data.shape[0]
			y_size = interpolated_hmi_data.shape[1]
			x_center = int(MAPCUBE[MEAS][i].reference_pixel.x.value + 0.5) - 12
			y_center = int(MAPCUBE[MEAS][i].reference_pixel.y.value + 0.5) + 4

			casted_hmi_data[(y_center - 1 - y_size/2) : (y_center + y_size/2), (x_center - 1 - x_size/2) : (x_center + x_size/2)] = interpolated_hmi_data

			hmi_cd_data = casted_hmi_data[x1 : x2,
										  y1 : y2]

			RECORDER.write_image(3,
								 LOOP_ID,
								 hmi_cd_data,
								 MAPCUBE["HMI"][i].detector,
								 MAPCUBE["HMI"][i].wavelength)

			LOW_THRESHOLD_HMI = -10000
			HIGH_THRESHOLD_HMI = 10000

			hmi_threshold_image_data = hmi_cd_data[np.where(np.logical_and(hmi_cd_data > LOW_THRESHOLD_HMI,
																		   hmi_cd_data < HIGH_THRESHOLD_HMI))]

			hmi_threshold_image_data = hmi_cd_data * binary_image_data

			unsig_gauss = np.sum(np.abs(hmi_threshold_image_data))
			avg_gauss = np.average(hmi_threshold_image_data)

			RECORDER.write_gauss(unsig_gauss, avg_gauss)

			# if np.abs(avg_gauss) > 4.0:
			# 	RECORDER.unipolar()
			# 	ADD_UNIPOLAR = True
			# 	break

			RECORDER.write_image(4,
								 LOOP_ID,
								 hmi_threshold_image_data,
								 MAPCUBE[MEAS][i].detector,
								 MAPCUBE[MEAS][i].wavelength)

			RECORDER.new_line()

		if ADD_SMALL:
			NUM_SMALL += 1
			ADD_SMALL = False
		if ADD_OFFDISK:
			NUM_OFF_DISK += 1
			ADD_OFFDISK = False
		# if ADD_UNIPOLAR:
		# 	NUM_UNIPOLAR += 1
		# 	ADD_UNIPOLAR = False

		NUM_LOOPS += 1
		LOOP_ID += 1

RECORDER.remove_duplicates()

RECORDER.info_text("Compressing database\n")
os.chdir("resources/")
os.system("zip -r -X data_%s.zip region-data" % str(datetime.now().strftime("%Y-%m-%d_%H.%M.%S")))
os.chdir("../")
RECORDER.info_text("Done:\t%s regions analyzed\n\t\t%s regions off-disk\n\t\t%s regions too small\n\t\t%s regions unipolar" % (NUM_LOOPS, NUM_OFF_DISK, NUM_SMALL, NUM_UNIPOLAR))
RECORDER.line()
RECORDER.display_end_time("loop-analysis")
