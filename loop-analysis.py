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

RECORDER = Recorder("database.csv")

for i in range(len(MAPCUBE["AIA193"])):
	raw_data = MAPCUBE["AIA193"][i].data

	xy_maxima = plm(raw_data,
					min_distance = 120,
					threshold_rel = 0.7)

	hp_maxima = MAPCUBE["AIA193"][i].pixel_to_world(xy_maxima[:, 1] * u.pixel,
												 xy_maxima[:, 0] * u.pixel)

	# edge_data = edge_detected_map.data
	# binary_data = feature.canny(edge_data, sigma = 3)
	# plt.imshow(binary_data, cmap = "gray")
	# plt.show()

	for j in range(len(hp_maxima)):
		RECORDER.write_ID(LOOP_ID)
		RECORDER.write_gen_info("AIA193", mapcube["AIA193"][i].wavelength)

		when = MAPCUBE["AIA193"][i].date
		RECORDER.write_datetime(when)

		where_xy = xy_maxima[j]
		RECORDER.write_xywhere(where_xy)

		center =  np.array([MAPCUBE["AIA193"][i].reference_pixel[0].value,
							MAPCUBE["AIA193"][i].reference_pixel[1].value])

		if distance.euclidean(center, where_xy) > 1600.0:
			RECORDER.error_line()
			LOOP_ID += 1
			continue

		where_hpc = hp_maxima[j]
		RECORDER.write_hpcwhere(where_hpc)

		HALF_DIM_PXL = 1
		MIN_AVERAGE = 500

		while np.average(raw_data[xy_maxima[j][0] - HALF_DIM_PXL : xy_maxima[j][0] + HALF_DIM_PXL,
						 xy_maxima[j][1] - HALF_DIM_PXL: xy_maxima[j][1] + HALF_DIM_PXL]) > MIN_AVERAGE:
			HALF_DIM_PXL += 5

		RECORDER.write_xysize(HALF_DIM_PXL * 2)

		HALF_DIM_HPC = MAPCUBE["AIA193"][i].scale[0].value * HALF_DIM_PXL

		bottom_left = SkyCoord(hp_maxima[j].Tx - HALF_DIM_HPC * u.arcsec,
							   hp_maxima[j].Ty - HALF_DIM_HPC * u.arcsec,
							   frame = MAPCUBE["AIA193"][i].coordinate_frame)

		top_right = SkyCoord(hp_maxima[j].Tx + HALF_DIM_HPC * u.arcsec,
							 hp_maxima[j].Ty + HALF_DIM_HPC * u.arcsec,
							 frame = MAPCUBE["AIA193"][i].coordinate_frame)

		RECORDER.write_hpcsize(bottom_left, top_right)

		cut_disk = MAPCUBE["AIA193"][i].submap(bottom_left, top_right)
		cd_data = cut_disk.data

		LOW_THRESHOLD = 800
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

		# np.save("data", cd_data)

		# look at corresponding hmi data with this bounding box and
		# record the total strength of the magnetic flux

		RECORDER.write_image(0,
							 LOOP_ID,
							 cd_data,
							 mapcube["AIA193"].instrument,
							 mapcube["AIA193"][i].wavelength)
		RECORDER.write_image(1,
							 LOOP_ID,
							 binary_image_data,
							 mapcube["AIA193"].instrument,
							 mapcube["AIA193"][i].wavelength)
		RECORDER.write_image(2,
							 LOOP_ID,
							 threshold_image_data,
							 mapcube["AIA193"].instrument,
							 mapcube["AIA193"][i].wavelength)
		
		RECORDER.new_line()
		LOOP_ID += 1

# extract the xy and hp coordinates of the loops and log them as arrays for later plotting

print Color.YELLOW + "DONE" + Color.RESET
