import astropy.units as u
from astropy.coordinates import SkyCoord
import getpass
import matplotlib.pyplot as plt
from matplotlib.widgets import RectangleSelector
import numpy as np
import os
from regions import PixCoord, CirclePixelRegion
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
Method that prompts user to select a region of the sun.
"""
def cutout_selection(mapcube):
	print Color.DARKCYAN + "\nOPENING PLOT..."
	fig = plt.figure()
	ax = plt.subplot(111, projection = smap.Map(mapcube[0]))
	mapcube[0].plot_settings["cmap"] = cm.get_cmap(name = "sdoaia%s" % str(int(mapcube[0].measurement.value)))
	mapcube[0].plot()
	ax.grid(False)
	plt.title("DRAG A SELECTION CENTERED SOMEWHERE ON THE SUN")
	plt.xlabel("Longitude [arcsec]")
	plt.ylabel("Latitude [arcsec]")
	selector = RectangleSelector(ax, line_select_callback, drawtype = 'box', useblit = True, button = [1, 3], minspanx = 5, minspany = 5, spancoords = 'pixels', interactive = True)
	plt.connect('key_press_event', selector)
	plt.clim(0, 40000)
	plt.style.use('dark_background')
	plt.show()
	os.system("open -a Terminal")
	return mapcube[0].pixel_to_world((x2 + x1)/2.0, (y2 + y1)/2.0)

"""
Method that calculates the location of the center of intensity of the first cutout.
"""
def calc_ci(mapcube, xdim, ydim, locs, id):
	c1 = SkyCoord(locs[id].Tx - xdim/2.0, locs[id].Ty - ydim/2.0, frame = mapcube[id].coordinate_frame)
	c2 = SkyCoord(locs[id].Tx + xdim/2.0, locs[id].Ty + ydim/2.0, frame = mapcube[id].coordinate_frame)

	cutout = mapcube[id].submap(c1, c2)
	data = cutout.data
	threshold = np.amax(data) - 500

	for i in range(len(data)):
		for j in range(len(data[0])):
			if data[i][j] < threshold:
				data[i][j] = 0

	ci = list(ndimage.measurements.center_of_mass(data))
	ci = [int(ci[1] + 0.5) * u.pixel, int(ci[0] + 0.5) * u.pixel]

 	coord = cutout.pixel_to_world(ci[0], ci[1])

 	return SkyCoord(coord.Tx, coord.Ty, obstime = str(mapcube[id].date), observer = get_earth(mapcube[id].date), frame = frames.Helioprojective)

def calc_num_wav(mapcube):
	count = 0
	wav = []
	for i in range(len(mapcube)):
		if mapcube[i].wavelength.value not in wav:
			wav.append(mapcube[i].wavelength.value)
			count += 1
	return count

def sort_mapcube(mapcube, num_wav):
	sorted = []
	wavelengths = []

	for i in range(num_wav):
		sorted.append([])
		wavelengths.append(mapcube[i].wavelength.value)

	for i in range(len(mapcube)):
		for j in range(len(wavelengths)):
			if mapcube[i].wavelength.value == wavelengths[j]:
				sorted[j].append(mapcube[i])

	return sorted

###################################################################################################

"""
Clears source folders and imports all FITS files into a datacube.
"""
print Color.BOLD + Color.DARKCYAN + "CLEARING SOURCE FOLDERS..." + Color.END
os.system("rm /Users/%s/Desktop/lmsal/ar-cut/src/*.jpg" % getpass.getuser())

print Color.BOLD + Color.DARKCYAN + "\nIMPORTING DATA..." + Color.END
mapcube = smap.Map("/Users/%s/Desktop/lmsal/data-get/src/*.fits" % getpass.getuser(), cube = True)
num_wav = calc_num_wav(mapcube)
print Color.BOLD + Color.DARKCYAN + "\nSORTING DATACUBE..." + Color.END
mapcube_sorted = sort_mapcube(mapcube, num_wav)

if len(mapcube) == 0:
	print Color.BOLD + Color.RED + "\nNO DATA. EXITING..." + Color.END
	os.exit(0)

print Color.DARKCYAN + Color.UNDERLINE + "\nMAPCUBE GENERATED" + Color.END + Color.DARKCYAN + "\n%s" % mapcube + Color.END

"""
Identifies an Active Region, either automatically or specified by the user.
"""
if(raw_input(Color.BOLD + Color.RED + "\nAUTOMATICALLY FIND BRIGHTEST REGION? [y/n]\n==> ") == "y"):
	print Color.BOLD + Color.DARKCYAN + "\nIDENTIFYING ACTIVE REGION..." + Color.END
	px = np.argwhere(mapcube[0].data == mapcube[0].data.max()) * u.pixel

	if len(px) > 1:
		temp = ndimage.measurements.center_of_mass(np.array(px))
		px = [px[int(temp[0] + 0.5)]]

	"""
	If the brightest location returns NaN value (due to being outside the solar limb), default to user input.
	"""
	center = PixCoord(x = 2043, y = 2025)
	radius = 1610
	region = CirclePixelRegion(center, radius)
	point = PixCoord(px[0][1], px[0][0])
	if not region.contains(point):
		print Color.BOLD + Color.YELLOW + "\nBRIGHTEST LOCATION IS OUTSIDE SOLAR LIMB. DEFAULTING TO USER SELECTION..."
		init_coord = cutout_selection(mapcube)
	else:
		init_coord = mapcube[0].pixel_to_world(px[0][1], px[0][0])

	auto_sel = True
	fig = plt.figure()
	plt.style.use('dark_background')
else:
	init_coord = cutout_selection(mapcube)
	auto_sel = False

"""
Creates a SkyCoord (Helioprojective coordinate) based on the location of the Active Region.
"""
print Color.END + Color.DARKCYAN + Color.UNDERLINE + "\nHELIOPROJECTIVE COORDINATE" + Color.END + Color.DARKCYAN + "\n(%s, %s)" % (init_coord.Tx, init_coord.Ty)
init_time = str(mapcube[0].date)
print Color.UNDERLINE + "\nINITIAL TIME" + Color.END + Color.DARKCYAN + "\n%s" % str(init_time)
init_loc = SkyCoord(init_coord.Tx, init_coord.Ty, obstime = init_time, observer=get_earth(init_time), frame = frames.Helioprojective)
print Color.UNDERLINE + "\nINITIAL LOCATION" + Color.END + Color.DARKCYAN + "\n%s" % init_loc + Color.END

"""
Calculates coordinates of future cutouts, based on the date from FITS file metadata.
"""
print Color.BOLD + Color.DARKCYAN + "\nCALCULATING FUTURE ROTATIONAL COORDINATES..." + Color.END
locs = [solar_rotate_coordinate(init_loc, mapcube[i].date) for i in range(len(mapcube))]

"""
Gathers some information to generate the cutouts.
"""
if(raw_input(Color.BOLD + Color.RED + "\nUSE DEFAULT SETTINGS (12 FPS, LOW SCALE 0, HIGH SCALE 50000)? [y/n]\n==> ") == "y"):
	fps = 12
	low_scale = 0
	high_scale = 40000
else:
	fps = int(raw_input("\nENTER FPS VALUE:\n==> "))
	low_scale = int(raw_input("\nENTER LOW SCALE VALUE:\n==> "))
	high_scale = int(raw_input("\nENTER HIGH SCALE VALUE:\n==> "))

"""
Determines the region dimensions based on the user's selection.
If Active Region was automatically found, a square region is used.
"""
if auto_sel:
	xdim = 600 * u.arcsec
	ydim = 600 * u.arcsec
else:
	coord1 = mapcube[0].pixel_to_world(x1, y1)
	coord2 = mapcube[0].pixel_to_world(x2, y2)
	xdim = coord2.Tx - coord1.Tx
	ydim = coord2.Ty - coord1.Ty
dpi = 600

"""
Instantiates a SkyCoord containing the initial center of intensity location.
"""
print Color.DARKCYAN + Color.BOLD + "\nCALCULATING INITIAL CENTER OF INTENSITY...\n"
init_ci = calc_ci(mapcube, xdim, ydim, locs, 0)

"""
Uses matplotlib and astropy SkyCoord to generate cutoutouts, based on the coordinates calculated previously.
"""
id = 0

for i in tqdm(range(len(mapcube_sorted[0])), desc = "GENERATING CUTOUTS", bar_format = '{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{remaining} remaining, ' '{rate_fmt}{postfix}]'):
	c1 = SkyCoord(locs[i].Tx - xdim/2.0, locs[i].Ty - ydim/2.0, frame = mapcube[i].coordinate_frame)
	c2 = SkyCoord(locs[i].Tx + xdim/2.0, locs[i].Ty + ydim/2.0, frame = mapcube[i].coordinate_frame)

	"""
	Set up skeleton matplotlib pyplot.
	"""
	fig = plt.figure()

	for j in range(num_wav):
		mapcube_sorted[j][i].plot_settings["cmap"] = cm.get_cmap(name = "sdoaia%s" % str(int(mapcube_sorted[j][i].measurement.value)))
		ax = plt.subplot(111, projection = mapcube_sorted[j][i])
		mapcube_sorted[j][i].plot()
		ax.grid(False)
		# cutout = mapcube_sorted[j][i].submap(c1, c2)
		# ax = plt.subplot(1, num_wav, j + 1, projection = cutout)
		# cutout.plot_settings["cmap"] = cm.get_cmap(name = "sdoaia%s" % str(int(mapcube_sorted[j][i].measurement.value)))
		# cutout.plot()

		# loc = solar_rotate_coordinate(init_ci, mapcube_sorted[j][i].date)
		# ax.plot_coord(loc, "w3")

		# ax.grid(False)
		# plt.style.use('dark_background')
		# plt.xlabel("Longitude [arcsec]")
		# plt.ylabel("Latitude [arcsec]")
		# plt.clim(low_scale, high_scale)

		# if j != 0:
		# 	plt.ylabel("")

	"""
	Save the cutout to a specified location.
	"""
	# plt.tight_layout(w_pad = 3.25)
	# plt.margins(x = 4, y = 4)
	plt.savefig("/Users/%s/Desktop/lmsal/ar-cut/src/cutout_%03d.jpg" % (getpass.getuser(), id), dpi = dpi)
	plt.close()

	id += 1

"""
Uses ffmpeg to generate a video called output.mp4. Video is saved to the working directory.
"""
# print Color.DARKCYAN + Color.BOLD + "\nGENERATING VIDEO...\n" + Color.END
# os.system("ffmpeg -y -f image2 -start_number 000 -framerate %s -i /Users/%s/Desktop/lmsal/ar-cut/src/cutout_%%3d.jpg -q:v 2 -vcodec mpeg4 -b:v 800k /Users/%s/Desktop/lmsal/ar-cut/output.mp4" % (fps, getpass.getuser(), getpass.getuser()))

elapsed_time = time.time() - start_time
print Color.BOLD + Color.CYAN + "\nDONE: VIDEO SAVED TO /Users/%s/Desktop/lmsal/ar-cut/output.mp4" % getpass.getuser()
print "MOVE VIDEO TO PREVENT AN OVERWRITE!"
print "EXECUTION TIME: %s" % time.strftime("%H:%M:%S", time.gmtime(elapsed_time)) + Color.END
# print Color.BOLD + Color.DARKCYAN + "CLEARING SOURCE FOLDERS...\n" + Color.END
# os.system("rm /Users/%s/Desktop/lmsal/ar-cut/src/*.jpg" % getpass.getuser())
os.system("open /Users/%s/Desktop/lmsal/ar-cut/output.mp4" % getpass.getuser())
