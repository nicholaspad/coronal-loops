import warnings
warnings.filterwarnings("ignore", message="numpy.dtype size changed")

from astropy.coordinates import SkyCoord
from colortext import Color
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

main_dir = "/Users/%s/Desktop/lmsal" % getpass.getuser()

print Color.YELLOW + "IMPORTING DATA..." + Color.RESET

mapcube_aia = smap.Map("%s/resources/aia-fits-files/*.fits" % main_dir, 
						cube = True)

mapcube_hmi = smap.Map("%s/resources/hmi-fits-files/*.fits" % main_dir,
						cube = True)

mapcube = {
	"aia" : mapcube_aia,
	"hmi" : mapcube_hmi
}

CL_ID = 0

for i in range(len(mapcube["aia"])):
	when = mapcube["aia"][i].date.strftime("%Y-%m-%d %H.%M.%S")
	date = when.split(" ")[0]
	time = when.split(" ")[1]

	# record date and time

	raw_data = mapcube["aia"][i].data

	xy_maxima = plm(raw_data,
					min_distance = 100,
					threshold_rel = 0.55)

	hp_maxima = mapcube["aia"][i].pixel_to_world(xy_maxima[:, 1] * u.pixel,
												 xy_maxima[:, 0] * u.pixel)

	subtracted_data = (raw_data > 0) * raw_data
	subtracted_map = smap.Map(subtracted_data, mapcube["aia"][i].meta)

	# edge_data = edge_detected_map.data
	# binary_data = feature.canny(edge_data, sigma = 3)
	# plt.imshow(binary_data, cmap = "gray")
	# plt.show()

	for j in range(len(hp_maxima)):
		# algorithm to determine bounds by successively zooming out
		# record and utilize dimensions of bounding box

		bound_x = 150
		bound_y = 150

		bottom_left = SkyCoord(hp_maxima[j].Tx - bound_x * u.arcsec,
							   hp_maxima[j].Ty - bound_y * u.arcsec,
							   frame = mapcube["aia"][i].coordinate_frame)

		top_right = SkyCoord(hp_maxima[j].Tx + bound_x * u.arcsec,
							 hp_maxima[j].Ty + bound_y * u.arcsec,
							 frame = mapcube["aia"][i].coordinate_frame)

		cut_disk = subtracted_map.submap(bottom_left, top_right)

		edge_x = ndimage.sobel(cut_disk.data, 
							   axis = 0,
							   mode = "constant")

		edge_y = ndimage.sobel(cut_disk.data,
							   axis = 1,
							   mode = "constant")

		edge_detected_map_data = np.hypot(edge_x, edge_y)
		edge_detected_map = smap.Map(edge_detected_map_data, cut_disk.meta)

		# edge_detected_map.plot()
		# plt.show()

		# record cartesian pixel location
		# record helioprojective solar location
		loop_number = "%05d" % CL_ID
		CL_ID += 1

		# look at corresponding hmi data with this bounding box and
		# record the total strength of the magnetic flux

# extract the xy and hp coordinates of the loops and log them as arrays for later plotting
# anything else?
# use csv file format
