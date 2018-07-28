import warnings
warnings.filterwarnings("ignore", message="numpy.dtype size changed")

import sunpy.map as smap
import matplotlib.pyplot as plt
import numpy as np
from colortext import Color
from skimage.feature import peak_local_max as plm
import astropy.units as u

print Color.YELLOW + "\nIMPORTING DATA..." + Color.RESET
mapcube = smap.Map("%s/resources/hmi-fits-files/*.fits" % main_dir, cube = True)

for i in range(len(mapcube)):
	raw = mapcube[i].data
	# xy = plm(raw, min_distance = 60, threshold_rel = 0.7)
	xy = plm(raw,min_distance = 100, threshold_rel = 0.7)
	loc = mapcube[i].pixel_to_world(coord[0][1] * u.pixel, coord[0][0] * u.pixel)
	# returns 2D array of bright coordinates

	# raw = np.where(np.isnan(raw), 10., raw)
	# x, y = np.unravel_index(raw.argmin(), raw.shape)

	raw = plt.plot(mapcube[i].data)

	for j in range(4096):

		x, y = data[j].get_data

		plt.scatter(x,y)
