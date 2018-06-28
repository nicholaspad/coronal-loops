import astropy.units as u
from astropy.coordinates import SkyCoord
import getpass
import matplotlib.pyplot as plt
import numpy as np
import os
from scipy import ndimage
import sunpy.cm as cm
from sunpy.coordinates.ephemeris import get_earth
from sunpy.coordinates import frames
import sunpy.map as smap
from sunpy.physics.differential_rotation import solar_rotate_coordinate
import time
from tqdm import tqdm

start_time = time.time()

class Color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

print Color.BOLD + Color.PURPLE + "\nClearing source folders..." + Color.END
os.system("rm /Users/%s/Desktop/lmsal/ar-find/source-cutouts/*.jpg" % getpass.getuser())

print Color.BOLD + Color.PURPLE + "\nImporting FITS files into datacube..." + Color.END
mapcube = smap.Map("../data-imp/source-fits/*.fits", cube = True)

print Color.RED + Color.BOLD + "\nMAPCUBE GENERATED ==>\n%s" % mapcube + Color.END

print Color.BOLD + Color.PURPLE + "\nIdentifying active region..." + Color.END
px = np.argwhere(mapcube[0].data == mapcube[0].data.max()) * u.pixel
print Color.PURPLE + "\nACTIVE REGION ==>\n%s" % px
init_coord = mapcube[0].pixel_to_world(px[:, 1], px[:, 0])
print "\nHELIOPROJECTIVE COORDINATE ==>\n(%s, %s)" % (init_coord.Tx, init_coord.Ty)
init_time = str(mapcube[0].date)
print "\nINITIAL TIME ==>\n%s" % str(init_time)
init_loc = SkyCoord(init_coord.Tx, init_coord.Ty, obstime = init_time, observer=get_earth(init_time), frame = frames.Helioprojective)
print "\nINITIAL LOCATION OBJECT ==>\n%s" % init_loc + Color.END

print Color.BOLD + Color.PURPLE + "\nCalculating future coordinates..." + Color.END
locs = []
for i in range(len(mapcube)):
	locs.append(solar_rotate_coordinate(init_loc, mapcube[i].date))

dim = 500 * u.arcsec
fps = 10
dpi = 300
color = "sdoaia%s" % str(int(mapcube[0].measurement.value))
low_scale = 0
high_scale = 100000

print Color.RED + Color.BOLD
for i in tqdm(range(len(mapcube)), desc = "GENERATING CUTOUTS"):
	bl = SkyCoord(locs[i].Tx - dim/2, locs[i].Ty - dim/2, frame = mapcube[i].coordinate_frame)
	tr = SkyCoord(locs[i].Tx + dim/2, locs[i].Ty + dim/2, frame = mapcube[i].coordinate_frame)

	cutout = mapcube[i].submap(bl, tr)

	fig = plt.figure()
	ax = plt.subplot(projection = cutout)
	cutout.plot_settings["cmap"] = cm.get_cmap(name = color)
	cutout.plot()

	data = cutout.data
	ci = list(ndimage.measurements.center_of_mass(data))
	ci = [int(ci[0] + 0.5) * u.pixel, int(ci[1] + 0.5) * u.pixel]
 	coord = cutout.pixel_to_world(ci[0], ci[1])
 	loc = SkyCoord(coord.Tx, coord.Ty, obstime = str(mapcube[i].date), observer = get_earth(str(mapcube[i].date)), frame = frames.Helioprojective)
	ax.plot_coord(loc, "rx")
	
	ax.grid(False)
	plt.style.use('dark_background')
	plt.xlabel("Longitude [arcsec]")
	plt.ylabel("Latitude [arcsec]")
	plt.clim(low_scale, high_scale)
	plt.colorbar()

	plt.savefig("/Users/%s/Desktop/lmsal/ar-find/source-cutouts/cutout_%03d.jpg" % (getpass.getuser(), i), dpi = dpi)

	plt.close()

print Color.PURPLE + Color.BOLD + "\nGENERATING VIDEO...\n" + Color.END
os.system("ffmpeg -f image2 -start_number 000 -framerate %s -i /Users/%s/Desktop/lmsal/ar-find/source-cutouts/cutout_%%3d.jpg -pix_fmt yuv420p -s 1562x1498 /Users/%s/Desktop/lmsal/ar-find/output.mp4" % (fps, getpass.getuser(), getpass.getuser()))

print Color.BOLD + Color.GREEN + "\nDONE" + Color.END

# clear = raw_input("\nClear source FITS folders? [y/n]\n==> ")
# if clear == "y":
# 	print "\nClearing source folders..."
# 	os.system("rm /Users/%s/Desktop/lmsal/data-imp/source-fits/*.fits" % getpass.getuser())

elapsed_time = time.time() - start_time
print "\nEXECUTION TIME: %s\n" % time.strftime("%H:%M:%S", time.gmtime(elapsed_time)) + Color.END
