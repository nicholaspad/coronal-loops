import warnings
warnings.filterwarnings("ignore", message="numpy.dtype size changed")

from astropy.coordinates import SkyCoord
from colortext import Color
from IPython.core import debugger ; debug = debugger.Pdb().set_trace
from recorder import Recorder
from scipy import ndimage
from skimage import feature
from skimage.feature import peak_local_max as plm
from tqdm import tqdm
import astropy.units as u
import getpass
import matplotlib.pyplot as plt
import numpy as np
import sunpy.map as smap
import sys

MAIN_DIR = "/Users/%s/Desktop/lmsal" % getpass.getuser()

print Color.YELLOW + "IMPORTING DATA..." + Color.RESET

MAPCUBE_AIA = smap.Map("%s/resources/aia-fits-files/*.fits" % MAIN_DIR)

MAPCUBE_HMI = smap.Map("%s/resources/hmi-fits-files/*.fits" % MAIN_DIR)

MAPCUBE = {
	"AIA" : MAPCUBE_AIA,
	"HMI" : MAPCUBE_HMI
}

FIRST_DAY = "2010-05-13"
DAY_INCREMENT = 1
LOOP_ID = 0

RECORDER = Recorder("database.csv")

for i in range(len(MAPCUBE["AIA"])):
	raw_data = MAPCUBE["AIA"][i].data

	xy_maxima = plm(raw_data,
					min_distance = 100,
					threshold_rel = 0.6)

	hp_maxima = MAPCUBE["AIA"][i].pixel_to_world(xy_maxima[:, 1] * u.pixel,
												 xy_maxima[:, 0] * u.pixel)

	# edge_data = edge_detected_map.data
	# binary_data = feature.canny(edge_data, sigma = 3)
	# plt.imshow(binary_data, cmap = "gray")
	# plt.show()

	for j in range(len(hp_maxima)):
		RECORDER.write_ID(LOOP_ID)

		when = MAPCUBE["AIA"][i].date
		RECORDER.write_datetime(when)

		where_xy = xy_maxima[j]
		RECORDER.write_xywhere(where_xy)

		where_hpc = hp_maxima[j]
		RECORDER.write_hpcwhere(where_hpc)

		HALF_DIM_PXL = 1
		MIN_AVERAGE = 500

		while np.average(raw_data[xy_maxima[j][0] - HALF_DIM_PXL : xy_maxima[j][0] + HALF_DIM_PXL,
						 xy_maxima[j][1] - HALF_DIM_PXL: xy_maxima[j][1] + HALF_DIM_PXL]) > MIN_AVERAGE:
			HALF_DIM_PXL += 5

		RECORDER.write_xysize(HALF_DIM_PXL * 2)

		HALF_DIM_HPC = MAPCUBE["AIA"][i].scale[0].value * HALF_DIM_PXL

		bottom_left = SkyCoord(hp_maxima[j].Tx - HALF_DIM_HPC * u.arcsec,
							   hp_maxima[j].Ty - HALF_DIM_HPC * u.arcsec,
							   frame = MAPCUBE["AIA"][i].coordinate_frame)

		top_right = SkyCoord(hp_maxima[j].Tx + HALF_DIM_HPC * u.arcsec,
							 hp_maxima[j].Ty + HALF_DIM_HPC * u.arcsec,
							 frame = MAPCUBE["AIA"][i].coordinate_frame)

		RECORDER.write_hpcsize(bottom_left, top_right)

		cut_disk = MAPCUBE["AIA"][i].submap(bottom_left, top_right)
		np.save("%s/resources/region-data/raw-images/%05d" % (MAIN_DIR, LOOP_ID), cut_disk.data)

		THRESHOLD = 800

		threshold_data = cut_disk.data[np.where(cut_disk.data > THRESHOLD)]

		average_intensity = np.average(threshold_data)
		median_intensity = np.median(threshold_data)
		maximum_intensity = np.max(threshold_data)

		RECORDER.write_inten(average_intensity, median_intensity, maximum_intensity)

		binary_image = np.logical_and(cut_disk.data > THRESHOLD, cut_disk.data < np.inf)
		np.save("%s/resources/region-data/binary-images/%05d" % (MAIN_DIR, LOOP_ID), binary_image)

		threshold_image = cut_disk.data * binary_image
		np.save("%s/resources/region-data/threshold-images/%05d" % (MAIN_DIR, LOOP_ID), threshold_image)

		# edge_x = ndimage.sobel(cut_disk.data, 
		# 					   axis = 0,
		# 					   mode = "constant")

		# edge_y = ndimage.sobel(cut_disk.data,
		# 					   axis = 1,
		# 					   mode = "constant")

		# loop_enhanced_data = np.hypot(edge_x, edge_y)
		# loop_enhanced_map = smap.Map(loop_enhanced_data, cut_disk.meta)

		# np.save("data", cut_disk.data)

		# look at corresponding hmi data with this bounding box and
		# record the total strength of the magnetic flux

		RECORDER.new_line()
		LOOP_ID += 1

# extract the xy and hp coordinates of the loops and log them as arrays for later plotting

print Color.YELLOW + "DONE" + Color.RESET
