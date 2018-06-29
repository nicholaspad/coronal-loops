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
Action listener method for the initial coordinate selection.
"""
def onclick(event):
	global x, y
	x = float(event.xdata) * u.pixel
	y = float(event.ydata) * u.pixel
	global plt
	plt.close()

"""
Clears source folders and imports all FITS files into a datacube.
"""
print Color.BOLD + Color.PURPLE + "\nClearing source folders..."
os.system("rm /Users/%s/Desktop/lmsal/ar-cut/src/*.jpg" % getpass.getuser())

print "\nImporting FITS files into datacube..." + Color.END
mapcube = smap.Map("../data-get/src/*.fits", cube = True)

print Color.RED + Color.BOLD + "\nMAPCUBE GENERATED\n==> %s" % mapcube + Color.END

"""
Identifies an Active Region, either automatically or specified by the user.
"""
if(raw_input(Color.BOLD + Color.YELLOW + "\nAUTOMATICALLY IDENTIFY ACTIVE REGION? [y/n]\n==> ") == "y"):
	print Color.BOLD + Color.PURPLE + "\nIdentifying active region..." + Color.END
	px = np.argwhere(mapcube[0].data == mapcube[0].data.max()) * u.pixel
	init_coord = mapcube[0].pixel_to_world(px[:, 1], px[:, 0])
else:
	print Color.PURPLE + "\nOPENING PLOT..."
	fig = plt.figure()
	ax = plt.subplot(111, projection = smap.Map(mapcube[0]))
	mapcube[0].plot()
	cid = fig.canvas.mpl_connect('button_press_event', onclick)
	plt.style.use('dark_background')
	plt.title("CLICK ON A COORDINATE")
	plt.xlabel("Longitude [arcsec]")
	plt.ylabel("Latitude [arcsec]")
	plt.show()
	init_coord = mapcube[0].pixel_to_world(y, x)
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
locs = []
for i in range(len(mapcube)):
	locs.append(solar_rotate_coordinate(init_loc, mapcube[i].date))

"""
Gathers some information to generate the cutouts, including dimensions and scale factor.
"""
if(raw_input(Color.BOLD + Color.YELLOW + "\nUSE DEFAULT SETTINGS? [y/n]\n==> ") == "y"):
	dim = 800 * u.arcsec
	fps = 12
else:
	dim = int(raw_input(Color.BOLD + Color.YELLOW + "\nENTER CUTOUT DIMENSION IN ARCSECONDS:\n==> ")) * u.arcsec
	fps = int(raw_input("\nENTER FPS VALUE:\n==> "))
low_scale = 0
high_scale = 60000
dpi = 300
color = "sdoaia%s" % str(int(mapcube[0].measurement.value))

"""
Uses matplotlib and SkyCoord to generate cutoutouts, based on the coordinates calculated previously.
"""
print Color.RED + Color.BOLD
for i in tqdm(range(len(mapcube)), desc = "GENERATING CUTOUTS..."):
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
	ax.plot_coord(loc, "b3")
	
	ax.grid(False)
	plt.style.use('dark_background')
	plt.xlabel("Longitude [arcsec]")
	plt.ylabel("Latitude [arcsec]")
	plt.clim(low_scale, high_scale)
	plt.colorbar()

	plt.savefig("/Users/%s/Desktop/lmsal/ar-cut/src/cutout_%03d.jpg" % (getpass.getuser(), i), dpi = dpi)
	plt.close()

"""
Uses ffmpeg to generate a video with the specified fps. Video is saved to the working directory.
"""
print Color.PURPLE + Color.BOLD + "\nGENERATING VIDEO...\n" + Color.END
os.system("ffmpeg -f image2 -start_number 000 -framerate %s -i /Users/%s/Desktop/lmsal/ar-cut/src/cutout_%%3d.jpg -pix_fmt yuv420p -s 1562x1498 /Users/%s/Desktop/lmsal/ar-cut/output.mp4" % (fps, getpass.getuser(), getpass.getuser()))

print Color.BOLD + Color.RED + "\nDONE"

"""
Closing the program and asking if user wants to clear the source folders.
"""
# clear = raw_input("\nClear source FITS folders? [y/n]\n==> ")
# if clear == "y":
# 	print "\nClearing source folders..."
# 	os.system("rm /Users/%s/Desktop/lmsal/data-imp/source-fits/*.fits" % getpass.getuser())

elapsed_time = time.time() - start_time
print "\nEXECUTION TIME: %s\n" % time.strftime("%H:%M:%S", time.gmtime(elapsed_time)) + Color.END
os.system("open output.mp4")
