import warnings
warnings.filterwarnings("ignore", message="numpy.dtype size changed")

from astropy.coordinates import SkyCoord
from colortext import Color
from IPython.core import debugger ; debug = debugger.Pdb().set_trace
from recorder import Recorder
from scipy import ndimage
from scipy.spatial import distance
from skimage import feature
from skimage.feature import peak_local_max as plm
from tqdm import tqdm
import argparse
import astropy.units as u
import getpass
import matplotlib.pyplot as plt
import numpy as np
import os
import sunpy.map as smap
import sys

parser = argparse.ArgumentParser()
parser.add_argument("-getdata", action = "store_true")
args = parser.parse_args()

MAIN_DIR = "/Users/%s/Desktop/lmsal" % getpass.getuser()
os.system("rm resources/region-data/raw-images/*.npy")
os.system("rm resources/region-data/binary-images/*.npy")
os.system("rm resources/region-data/threshold-images/*.npy")

FIRST_DAY = "2010-05-15"
LAST_DAY = "2018-05-15"
DAY_CADENCE = 12
LOOP_ID = 0

if args.getdata:
	print Color.YELLOW + "Calling data-get.py"
	os.system("python data-get.py -sday %s -stime 00:00:00 -eday %s -etime 00:00:00 -cadence %d" % (FIRST_DAY, LAST_DAY, DAY_CADENCE))

print Color.YELLOW + "Importing AIA94 data" + Color.RESET
MAPCUBE_AIA_94 = smap.Map("%s/resources/aia-fits-files/*.94.image_lev1.fits" % MAIN_DIR, cube = True)
print Color.YELLOW + "Importing AIA131 data" + Color.RESET
MAPCUBE_AIA_131 = smap.Map("%s/resources/aia-fits-files/*.131.image_lev1.fits" % MAIN_DIR, cube = True)
print Color.YELLOW + "Importing AIA171 data" + Color.RESET
MAPCUBE_AIA_171 = smap.Map("%s/resources/aia-fits-files/*.171.image_lev1.fits" % MAIN_DIR, cube = True)
print Color.YELLOW + "Importing AIA193 data" + Color.RESET
MAPCUBE_AIA_193 = smap.Map("%s/resources/aia-fits-files/*.193.image_lev1.fits" % MAIN_DIR, cube = True)
print Color.YELLOW + "Importing AIA211 data" + Color.RESET
MAPCUBE_AIA_211 = smap.Map("%s/resources/aia-fits-files/*.211.image_lev1.fits" % MAIN_DIR, cube = True)
print Color.YELLOW + "Importing AIA304 data" + Color.RESET
MAPCUBE_AIA_304 = smap.Map("%s/resources/aia-fits-files/*.304.image_lev1.fits" % MAIN_DIR, cube = True)
print Color.YELLOW + "Importing AIA335 data" + Color.RESET
MAPCUBE_AIA_335 = smap.Map("%s/resources/aia-fits-files/*.335.image_lev1.fits" % MAIN_DIR, cube = True)
print Color.YELLOW + "Importing HMI magnetogram data" + Color.RESET
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

RECORDER = Recorder("database.csv")

for i in range(len(MAPCUBE["AIA193"])):

	for MEAS in MEASUREMENTS:

		raw_data = MAPCUBE["AIA193"][i].data

		xy_maxima = plm(raw_data,
						min_distance = 125,
						threshold_rel = 0.5)

		if xy_maxima.shape[0] == 0:
			hp_maxima = []

		else:
			hp_maxima = MAPCUBE["AIA193"][i].pixel_to_world(xy_maxima[:, 1] * u.pixel,
															xy_maxima[:, 0] * u.pixel)

		# edge_data = edge_detected_map.data
		# binary_data = feature.canny(edge_data, sigma = 3)
		# plt.imshow(binary_data, cmap = "gray")
		# plt.show()

		for j in range(len(hp_maxima)):
			RECORDER.write_ID(LOOP_ID)
			RECORDER.write_gen_info(MEAS, MAPCUBE[MEAS][i].wavelength)

			when = MAPCUBE[MEAS][i].date
			RECORDER.write_datetime(when)

			where_xy = xy_maxima[j]
			RECORDER.write_xywhere(where_xy)

			center = np.array([2048.0, 2048.0])

			if distance.euclidean(center, where_xy) > 1600.0:
				RECORDER.error_line()
				LOOP_ID += 1
				continue

			where_hpc = hp_maxima[j]
			RECORDER.write_hpcwhere(where_hpc)

			HALF_DIM_PXL = 1
			MIN_AVERAGE = 1600.0

			while np.average(raw_data[xy_maxima[j][0] - HALF_DIM_PXL : xy_maxima[j][0] + HALF_DIM_PXL,
							 xy_maxima[j][1] - HALF_DIM_PXL: xy_maxima[j][1] + HALF_DIM_PXL]) > MIN_AVERAGE:
				HALF_DIM_PXL += 5

			RECORDER.write_xysize(HALF_DIM_PXL * 2)

			HALF_DIM_HPC = MAPCUBE[MEAS][i].scale[0].value * HALF_DIM_PXL

			BOTTOM_LEFT = SkyCoord(where_hpc.Tx - HALF_DIM_HPC * u.arcsec,
								   where_hpc.Ty - HALF_DIM_HPC * u.arcsec,
								   frame = MAPCUBE[MEAS][i].coordinate_frame)

			TOP_RIGHT = SkyCoord(where_hpc.Tx + HALF_DIM_HPC * u.arcsec,
								 where_hpc.Ty + HALF_DIM_HPC * u.arcsec,
								 frame = MAPCUBE[MEAS][i].coordinate_frame)

			RECORDER.write_hpcsize(BOTTOM_LEFT, TOP_RIGHT)

			cut_disk = MAPCUBE[MEAS][i].submap(BOTTOM_LEFT, TOP_RIGHT)
			cd_data = cut_disk.data

			LOW_THRESHOLD_193 = 3000

			cd_data_193 = MAPCUBE["AIA193"][i].submap(BOTTOM_LEFT, TOP_RIGHT).data
			LOW_THRESHOLD = 0
			previous_low = 0
			new_low = 0
			target = len(cd_data_193[np.where(cd_data_193 > LOW_THRESHOLD_193)])

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
								 HIGH_THRESHOLD,
								 average_intensity,
								 median_intensity,
								 maximum_intensity)

			binary_image_data = np.logical_and(cd_data > LOW_THRESHOLD,
											   cd_data < HIGH_THRESHOLD)

			threshold_image_data = cd_data * binary_image_data

			# edge_x = ndimage.sobel(cd_data, 
			# 					   axis = 0,
			# 					   mode = "constant")

			# edge_y = ndimage.sobel(cd_data,
			# 					   axis = 1,
			# 					   mode = "constant")

			# loop_enhanced_data = np.hypot(edge_x, edge_y)
			# loop_enhanced_map = smap.Map(loop_enhanced_data, cut_disk.meta)

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
								 np.flip(threshold_image_data),
								 MAPCUBE[MEAS][i].detector,
								 MAPCUBE[MEAS][i].wavelength)
			
			hmi_raw_data = MAPCUBE["HMI"][i].data

			dim, rad, center_x, center_y = 4096.0, 1878.0, 2048.0, 2048.0
			y, x = np.ogrid[-center_x : dim - center_x, -center_y : dim - center_y]
			mask = x * x + y * y >= rad * rad
			hmi_raw_data[mask] = 10000.0

			hmi_loc = MAPCUBE["HMI"][i].world_to_pixel(where_hpc)

			if int(hmi_loc[0].value - HALF_DIM_PXL) < 0:
				y1 = 0
			else:
				y1 = int(hmi_loc[0].value - HALF_DIM_PXL)

			if int(hmi_loc[0].value + HALF_DIM_PXL) > MAPCUBE["HMI"][i].data.shape[0]:
				y2 = MAPCUBE["HMI"][i].data.shape[0]
			else:
				y2 = int(hmi_loc[0].value + HALF_DIM_PXL)

			if int(hmi_loc[1].value - HALF_DIM_PXL) < 0:
				x1 = 0
			else:
				x1 = int(hmi_loc[1].value - HALF_DIM_PXL)

			if int(hmi_loc[1].value + HALF_DIM_PXL) > MAPCUBE["HMI"][i].data.shape[1]:
				x2 = MAPCUBE["HMI"][i].data.shape[1]
			else:
				x2 = int(hmi_loc[1].value + HALF_DIM_PXL)

			hmi_cd_data = hmi_raw_data[x1 : x2,
									   y1 : y2]

			LOW_THRESHOLD_HMI = -500.0
			HIGH_THRESHOLD_HMI = 500.0

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
			LOOP_ID += 1

# extract the xy and hp coordinates of the loops and log them as arrays for later plotting

print Color.YELLOW + "DONE" + Color.RESET
