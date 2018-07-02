import astropy.units as u
from astropy.coordinates import SkyCoord
import getpass
import matplotlib.pyplot as plt
from matplotlib.widgets import RectangleSelector
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

"""
Starts an execution timer and clears the console.
"""
start_time = time.time()
os.system("clear")

"""
Class that allows for colored text.
"""
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

"""
Action listener method for the region selection.
"""
def line_select_callback(eclick, erelease):
	global x1, x2, y1, y2, plt
	x1, y1 = eclick.xdata * u.pixel, eclick.ydata * u.pixel
	x2, y2 = erelease.xdata * u.pixel, erelease.ydata * u.pixel
	plt.close()

"""
Clears source folders and imports all FITS files into a datacube.
"""
print Color.BOLD + Color.PURPLE + "\nClearing source folders..."
os.system("rm /Users/%s/Desktop/lmsal/ar-cut/src/*.jpg" % getpass.getuser())

print "\nImporting FITS files into datacube..." + Color.END
mapcube = smap.Map("../data-get/src/*.fits", cube = True)

if len(mapcube) == 0:
	print Color.BOLD + Color.RED + "\nNO DATA. EXITING..."
	os.exit(0)

print Color.RED + Color.BOLD + "\nMAPCUBE GENERATED\n==> %s" % mapcube + Color.END

"""
Identifies an Active Region, either automatically or specified by the user.
"""
if(raw_input(Color.BOLD + Color.RED + "\nAUTOMATICALLY IDENTIFY ACTIVE REGION? [y/n]\n==> ") == "y"):
	print Color.BOLD + Color.PURPLE + "\nIdentifying active region..." + Color.END
	px = np.argwhere(mapcube[0].data == mapcube[0].data.max()) * u.pixel

	init_coord = mapcube[0].pixel_to_world(px[:, 1], px[:, 0])

	auto_sel = True
	fig = plt.figure()
	plt.style.use('dark_background')
else:
	print Color.PURPLE + "\nOPENING PLOT..."
	fig = plt.figure()
	ax = plt.subplot(111, projection = smap.Map(mapcube[0]))
	mapcube[0].plot_settings["cmap"] = cm.get_cmap(name = "sdoaia%s" % str(int(mapcube[0].measurement.value)))
	mapcube[0].plot()
	ax.grid(False)
	plt.style.use('dark_background')
	plt.title("DRAG A SELECTION")
	plt.xlabel("Longitude [arcsec]")
	plt.ylabel("Latitude [arcsec]")
	selector = RectangleSelector(ax, line_select_callback, drawtype='box', useblit=True, button=[1, 3], minspanx=5, minspany=5, spancoords='pixels', interactive=True)
	plt.connect('key_press_event', selector)
	plt.show()

	init_coord = mapcube[0].pixel_to_world((y2 + y1)/2.0, (x2 + x1)/2.0)

	auto_sel = False
	os.system("open -a Terminal")

"""
Creates a SkyCoord (Helioprojective coordinate) based on the location of the Active Region.
"""
print Color.END + Color.PURPLE + "\nHELIOPROJECTIVE COORDINATE ==>\n(%s, %s)" % (init_coord.Tx, init_coord.Ty)
init_time = str(mapcube[0].date)
print "\nINITIAL TIME ==>\n%s" % str(init_time)
init_loc = SkyCoord(init_coord.Tx, init_coord.Ty, obstime = init_time, observer=get_earth(init_time), frame = frames.Helioprojective)
print "\nINITIAL LOCATION OBJECT ==>\n%s" % init_loc + Color.END

"""
Calculates coordinates of future cutouts, based on the date from FITS file metadata.
Essentially, this keeps the cutout centered on the Active Region.
"""
print Color.BOLD + Color.PURPLE + "\nCalculating future coordinates..." + Color.END
locs = [solar_rotate_coordinate(init_loc, mapcube[i].date) for i in range(len(mapcube))]

"""
Gathers some information to generate the cutouts.
"""
if(raw_input(Color.BOLD + Color.RED + "\nUSE DEFAULT SETTINGS? [y/n]\n==> ") == "y"):
	fps = 12
	low_scale = 0
	high_scale = 20000
else:
	fps = int(raw_input("\nENTER FPS VALUE:\n==> "))
	low_scale = int(raw_input("\nENTER LOW SCALE VALUE:\n==> "))
	high_scale = int(raw_input("\nENTER HIGH SCALE VALUE:\n==> "))

"""
Determines the region dimensions based on the user's selection.
If Active Region was automatically found, a square region is used.
"""
if auto_sel:
	xdim = 800 * u.arcsec
	ydim = 800 * u.arcsec
else:
	coord1 = mapcube[0].pixel_to_world(x1, y1)
	coord2 = mapcube[0].pixel_to_world(x2, y2)
	xdim = coord2.Tx - coord1.Tx
	ydim = coord2.Ty - coord1.Ty

dpi = 300
color = "sdoaia%s" % str(int(mapcube[0].measurement.value))

"""
Uses matplotlib and astropy SkyCoord to generate cutoutouts, based on the coordinates calculated previously.
"""
print Color.RED + Color.BOLD
for i in tqdm(range(len(mapcube)), desc = "GENERATING CUTOUTS..."):
	c1 = SkyCoord(locs[i].Tx - xdim/2.0, locs[i].Ty - ydim/2.0, frame = mapcube[i].coordinate_frame)
	c2 = SkyCoord(locs[i].Tx + xdim/2.0, locs[i].Ty + ydim/2.0, frame = mapcube[i].coordinate_frame)

	cutout = mapcube[i].submap(c1, c2)

	"""
	Set up skeleton matplotlib pyplot.
	"""
	fig = plt.figure()
	ax = plt.subplot(projection = cutout)
	cutout.plot_settings["cmap"] = cm.get_cmap(name = color)
	cutout.plot()

	"""
	Calculate and mark the center of intensity of the current cutout.
	"""
	data = cutout.data
	ci = list(ndimage.measurements.center_of_mass(data))
	ci = [int(ci[1] + 0.5) * u.pixel, int(ci[0] + 0.5) * u.pixel]
 	coord = cutout.pixel_to_world(ci[0], ci[1])
 	loc = SkyCoord(coord.Tx, coord.Ty, obstime = str(mapcube[i].date), observer = get_earth(mapcube[i].date), frame = frames.Helioprojective)
	ax.plot_coord(loc, "g3")
	
	"""
	More plot setup.
	"""
	ax.grid(False)
	plt.style.use('dark_background')
	plt.xlabel("Longitude [arcsec]")
	plt.ylabel("Latitude [arcsec]")
	plt.clim(low_scale, high_scale)
	plt.colorbar()

	"""
	Save the plot to a specified location.
	"""
	plt.savefig("/Users/%s/Desktop/lmsal/ar-cut/src/cutout_%03d.jpg" % (getpass.getuser(), i), dpi = dpi)
	plt.close()

"""
Uses ffmpeg to generate a video with the specified fps. Video is saved to the working directory.
"""
print Color.PURPLE + Color.BOLD + "\nGENERATING VIDEO...\n" + Color.END
os.system("ffmpeg -y -f image2 -start_number 000 -framerate %s -i /Users/%s/Desktop/lmsal/ar-cut/src/cutout_%%3d.jpg -pix_fmt yuv420p -s 1562x1498 /Users/%s/Desktop/lmsal/ar-cut/output.mp4" % (fps, getpass.getuser(), getpass.getuser()))

elapsed_time = time.time() - start_time
print Color.BOLD + Color.RED + "\nDONE - EXECUTION TIME: %s\n" % time.strftime("%H:%M:%S", time.gmtime(elapsed_time)) + Color.END
os.system("open output.mp4")

"""
Close the program and ask if user wants to clear the source folders.
"""
# clear = raw_input("\nClear source FITS folders? [y/n]\n==> ")
# if clear == "y":
# 	print "\nClearing source folders..."
# 	os.system("rm /Users/%s/Desktop/lmsal/data-imp/source-fits/*.fits" % getpass.getuser())
