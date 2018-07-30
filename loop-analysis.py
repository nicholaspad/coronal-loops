import warnings
warnings.filterwarnings("ignore", message="numpy.dtype size changed")

from astropy.coordinates import SkyCoord
from colortext import Color
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

	subtracted_data = (raw_data > 0) * raw_data
	subtracted_map = smap.Map(subtracted_data, MAPCUBE["AIA"][i].meta)

	# edge_data = edge_detected_map.data
	# binary_data = feature.canny(edge_data, sigma = 3)
	# plt.imshow(binary_data, cmap = "gray")
	# plt.show()

	for j in range(len(hp_maxima)):
		RECORDER.write_ID(LOOP_ID)
		LOOP_ID += 1

		when = MAPCUBE["AIA"][i].date
		RECORDER.write_datetime(when)

		where_xy = xy_maxima[j]
		RECORDER.write_xywhere(where_xy)

		where_hpc = hp_maxima[j]
		RECORDER.write_hpcwhere(where_hpc)

		# algorithm to determine bounds by successively zooming out
		# record and utilize dimensions of bounding box

		HALF_DIM = 1

		while np.average(raw_data[xy_maxima[j][0] - HALF_DIM : xy_maxima[j][0] + HALF_DIM,
						 xy_maxima[j][1] - HALF_DIM: xy_maxima[j][1] + HALF_DIM]) > 540.0:
			HALF_DIM += 5

		RECORDER.write_xysize(HALF_DIM * 2)

		bottom_left = SkyCoord(hp_maxima[j].Tx - HALF_DIM * u.arcsec,
							   hp_maxima[j].Ty - HALF_DIM * u.arcsec,
							   frame = MAPCUBE["AIA"][i].coordinate_frame)

		top_right = SkyCoord(hp_maxima[j].Tx + HALF_DIM * u.arcsec,
							 hp_maxima[j].Ty + HALF_DIM * u.arcsec,
							 frame = MAPCUBE["AIA"][i].coordinate_frame)

		RECORDER.write_hpcsize(bottom_left, top_right)

		cut_disk = subtracted_map.submap(bottom_left, top_right)

		edge_x = ndimage.sobel(cut_disk.data, 
							   axis = 0,
							   mode = "constant")

		edge_y = ndimage.sobel(cut_disk.data,
							   axis = 1,
							   mode = "constant")

		loop_enhanced_data = np.hypot(edge_x, edge_y)
		loop_enhanced_map = smap.Map(loop_enhanced_data, cut_disk.meta)

		

		# look at corresponding hmi data with this bounding box and
		# record the total strength of the magnetic flux

		RECORDER.new_line()

# extract the xy and hp coordinates of the loops and log them as arrays for later plotting

print Color.YELLOW + "DONE" + Color.RESET
