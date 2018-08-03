import warnings
warnings.filterwarnings("ignore", message = "numpy.dtype size changed")

from astropy.coordinates import SkyCoord
from colortext import Color
from matplotlib.widgets import RectangleSelector
from recorder import Recorder
from regions import PixCoord, CirclePixelRegion
from scipy import ndimage
from sunpy.coordinates import frames
from sunpy.coordinates.ephemeris import get_earth
from sunpy.physics.differential_rotation import solar_rotate_coordinate
from tqdm import tqdm
import argparse
import astropy.units as u
import cv2
import getpass
import matplotlib.pyplot as plt
import numpy as np
import os
import sunpy.cm as cm
import sunpy.map as smap
import sys





# # # # # # # # # # # OPTIONS # # # # # # # # # # #
# ----------------------------------------------- #
ask_to_change_default_settings = False
# ----------------------------------------------- #
# applicable if only_fulldisk_images is False
WIDTH = 600 * u.arcsec
HEIGHT = 600 * u.arcsec
# ----------------------------------------------- #
default_quality = 600 #dpi
# ----------------------------------------------- #
only_fulldisk_images = True
plot_center_of_intensity = False
crop_cut_to_only_sun = True
# ----------------------------------------------- #
# # # # # # # # # # # # # # # # # # # # # # # # # #





MAIN_DIR = "/Users/%s/Desktop/lmsal" % getpass.getuser()
PRINTER = Recorder()
PRINTER.display_start_time("active-region-cutouts")
parser = argparse.ArgumentParser()
parser.add_argument("--instr")
args = parser.parse_args()

#########################

if args.instr == None:
	PRINTER.info_text("Specify instrument with '--instr <name>'")
	PRINTER.line()
	sys.exit()

INSTRUMENT = args.instr.lower()

#########################

def box_selection(eclick, erelease):
	global x1, x2, y1, y2, plt
	x1, y1 = eclick.xdata * u.pixel, eclick.ydata * u.pixel
	x2, y2 = erelease.xdata * u.pixel, erelease.ydata * u.pixel
	plt.close()

def cutout_selection(MAPCUBE):
	PRINTER.info_text("Opening plot")

	ax = plt.subplot(111, projection = smap.Map(MAPCUBE[0]))
	MAPCUBE[0].plot_settings["cmap"] = cm.get_cmap(name = "sdoaia%s" % str(int(MAPCUBE[0].measurement.value)))
	MAPCUBE[0].plot()
	ax.grid(False)

	plt.title("Drag a selection")
	plt.xlabel("Longitude [arcsec]")
	plt.ylabel("Latitude [arcsec]")

	selector = RectangleSelector(ax,
								 box_selection,
								 drawtype = "box",
								 useblit = True,
								 button = [1, 3],
								 minspanx = 5,
								 minspany = 5,
								 spancoords = "pixels",
								 interactive = True)

	plt.connect("key_press_event", selector)
	plt.clim(0, 40000)
	plt.style.use("dark_background")
	plt.show()

	os.system("open -a Terminal")

	return MAPCUBE[0].pixel_to_world((x2 + x1)/2.0,
									 (y2 + y1)/2.0)

def calc_ci(MAPCUBE, xdim, ydim, LOCS, id):
	c1 = SkyCoord(LOCS[id].Tx - xdim/2.0,
				  LOCS[id].Ty - ydim/2.0,
				  frame = MAPCUBE[id].coordinate_frame)

	c2 = SkyCoord(LOCS[id].Tx + xdim/2.0,
				  LOCS[id].Ty + ydim/2.0,
				  frame = MAPCUBE[id].coordinate_frame)

	CUTOUT = MAPCUBE[id].submap(c1, c2)
	DATA = CUTOUT.data
	THRESHOLD = np.amax(DATA) - 500

	for i in range(len(DATA)):

		for j in range(len(DATA[0])):

			if DATA[i][j] < THRESHOLD:
				DATA[i][j] = 0

	ci = list(ndimage.measurements.center_of_mass(DATA))
	ci = [int(ci[1] + 0.5) * u.pixel, int(ci[0] + 0.5) * u.pixel]

 	COORD = CUTOUT.pixel_to_world(ci[0], ci[1])

 	return SkyCoord(COORD.Tx,
 					COORD.Ty,
 					obstime = str(MAPCUBE[id].date),
 					observer = get_earth(MAPCUBE[id].date),
 					frame = frames.Helioprojective)

#########################

PRINTER.info_text("Moved files in download directory to 'resources/discarded-files'")
if INSTRUMENT == "hmi":
	os.system("mv %s/resources/hmi-images/*.jpg %s/resources/discarded-files" % (MAIN_DIR, MAIN_DIR))

	PRINTER.info_text("Importing data")
	MAPCUBE = smap.Map("%s/resources/hmi-fits-files/*.fits" % MAIN_DIR, cube = True)

elif INSTRUMENT == "aia":
	os.system("mv %s/resources/aia-images/*.jpg %s/resources/discarded-files" % (MAIN_DIR, MAIN_DIR))

	PRINTER.info_text("Importing data")
	MAPCUBE = smap.Map("%s/resources/aia-fits-files/*.fits" % MAIN_DIR, cube = True)

#########################

if len(MAPCUBE) == 0:
	PRINTER.info_text("No data; exiting")
	sys.exit()

#########################

if not only_fulldisk_images:

	if(PRINTER.input_text("Automatically find most-intense region? [y/n]") == "y"):
		PRINTER.info_text("Identifying region")
		px = np.argwhere(MAPCUBE[0].data == MAPCUBE[0].data.max()) * u.pixel

		if len(px) > 1:
			temp = ndimage.measurements.center_of_mass(np.array(px))
			px = [px[int(temp[0] + 0.5)]]

		#########################

		center = PixCoord(x = 2048, y = 2048)
		radius = 1600
		region = CirclePixelRegion(center, radius)
		point = PixCoord(px[0][1], px[0][0])

		if not region.contains(point):
			PRINTER.info_text("Identified region is outside the solar disk")
			PRINTER.info_text("Defaulting to user selection...")
			INIT_COORD = cutout_selection(MAPCUBE)
		else:
			INIT_COORD = MAPCUBE[0].pixel_to_world(px[0][1], px[0][0])

		auto_sel = True
	
	else:
		INIT_COORD = cutout_selection(MAPCUBE)
		auto_sel = False

	#########################

	PRINTER.line()
	INIT_TIME = str(MAPCUBE[0].date)
	PRINTER.display_item("Initial time", INIT_TIME)

	#########################

	INIT_LOC = SkyCoord(INIT_COORD.Tx,
						INIT_COORD.Ty,
						obstime = INIT_TIME,
						observer = get_earth(INIT_TIME),
						frame = frames.Helioprojective)

	PRINTER.display_item("Initial location", "(%s arcsec, %s arcsec)" % (INIT_LOC.Tx, INIT_LOC.Ty))

	#########################

	PRINTER.info_text("Calculating future coordinates")
	LOCS = [solar_rotate_coordinate(INIT_LOC, MAPCUBE[i].date) for i in range(len(MAPCUBE))]

#########################

if ask_to_change_default_settings:

	if(PRINTER.input_text("Use default settings (low scale 0, high scale 40000)? [y/n]") == "n"):
		default_low_scale = int(PRINTER.input_text("Enter low scale"))
		default_high_scale = int(PRINTER.input_text("Enter high scale"))

#########################

if not only_fulldisk_images:

	if not auto_sel:
		coord1 = MAPCUBE[0].pixel_to_world(x1, y1)
		coord2 = MAPCUBE[0].pixel_to_world(x2, y2)
		WIDTH = coord2.Tx - coord1.Tx
		HEIGHT = coord2.Ty - coord1.Ty

#########################

if not only_fulldisk_images:
	PRINTER.info_text("Calculating initial center of intensity")
	init_ci = calc_ci(MAPCUBE,
					  WIDTH,
					  HEIGHT,
					  LOCS,
					  0)

#########################

PRINTER.line()

if only_fulldisk_images:
	PRINTER.info_text("Generating full-disk images\n")
else:
	print ""

ID = 0

for i in tqdm(
			range(len(MAPCUBE)),
			desc = Color.YELLOW + "Generating",
			bar_format = "{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [eta {remaining}, " "{rate_fmt}]"):
	
	if not only_fulldisk_images:
		c1 = SkyCoord(
					LOCS[i].Tx - WIDTH / 2.0,
					LOCS[i].Ty - HEIGHT / 2.0,
					frame = MAPCUBE[i].coordinate_frame)
		
		c2 = SkyCoord(
					LOCS[i].Tx + WIDTH / 2.0,
					LOCS[i].Ty + HEIGHT / 2.0,
					frame = MAPCUBE[i].coordinate_frame)

	#########################

	ax = plt.subplot(111, projection = MAPCUBE[i])

	#########################

	if only_fulldisk_images:

		if INSTRUMENT == "hmi":
			MAPCUBE[i].plot(vmin = -120, vmax = 120)
		elif INSTRUMENT == "aia":
			MAPCUBE[i].plot()
			plt.clim(0, 40000)
			
	else:
		cutout = MAPCUBE[i].submap(c1, c2)
		ax = plt.subplot(111, projection = cutout)
		cutout.plot()

	#########################

	if plot_center_of_intensity and not only_fulldisk_images:
		loc = solar_rotate_coordinate(init_ci, MAPCUBE[i].date)
		ax.plot_coord(loc, "w3")

	#########################

	ax.grid(False)
	plt.style.use("dark_background")
	plt.xlabel("Longitude [arcsec]")
	plt.ylabel("Latitude [arcsec]")

	#########################

	if INSTRUMENT == "hmi":
		plt.savefig("%s/resources/hmi-images/cut-%03d.jpg" % (MAIN_DIR, ID), dpi = default_quality)

		if crop_cut_to_only_sun:
			CUT = cv2.imread("%s/resources/hmi-images/cut-%03d.jpg" % (MAIN_DIR, ID))
			SCALE = default_quality/300.0
			CROP_DATA = CUT[int(176 * SCALE) : int(1278 * SCALE), int(432 * SCALE) : int(1534 * SCALE)]
			CROP_DATA = np.flip(CROP_DATA, 0)
			CROP_DATA = np.flip(CROP_DATA, 1)
			cv2.imwrite("%s/resources/hmi-images/cut-%03d.jpg" % (MAIN_DIR, ID), CROP_DATA)
	
	elif INSTRUMENT == "aia":
		plt.savefig("%s/resources/aia-images/cut-%03d.jpg" % (MAIN_DIR, ID), dpi = default_quality)

		if crop_cut_to_only_sun:
			CUT = cv2.imread("%s/resources/aia-images/cut-%03d.jpg" % (MAIN_DIR, ID))
			SCALE = default_quality/300.0
			CROP_DATA = CUT[int(176 * SCALE) : int(1278 * SCALE), int(432 * SCALE) : int(1534 * SCALE)]
			cv2.imwrite("%s/resources/aia-images/cut-%03d.jpg" % (MAIN_DIR, ID), CROP_DATA)

	#########################

	ID += 1
	plt.close()

#########################

PRINTER.info_text("Done")
PRINTER.line()
