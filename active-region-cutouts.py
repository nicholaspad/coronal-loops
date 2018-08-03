import warnings
warnings.filterwarnings("ignore", message="numpy.dtype size changed")

import argparse
from astropy.coordinates import SkyCoord
from colortext import Color
import cv2
from matplotlib.widgets import RectangleSelector
from regions import PixCoord, CirclePixelRegion
from scipy import ndimage
from sunpy.coordinates import frames
from sunpy.coordinates.ephemeris import get_earth
from sunpy.physics.differential_rotation import solar_rotate_coordinate
from tqdm import tqdm
import astropy.units as u
import getpass
import matplotlib.pyplot as plt
import numpy as np
import os
import sys
import sunpy.cm as cm
import sunpy.map as smap





# # # # # # # # # # # OPTIONS # # # # # # # # # # #
# ----------------------------------------------- #
ask_to_change_default_settings = False
# ----------------------------------------------- #
# applicable if only_fulldisk_images is False
default_cutout_width = 600 * u.arcsec
default_cutout_height = 600 * u.arcsec
# ----------------------------------------------- #
default_quality = 600 #dpi
# ----------------------------------------------- #
only_fulldisk_images = True
plot_center_of_intensity = False
crop_cut_to_only_sun = True
# ----------------------------------------------- #
# # # # # # # # # # # # # # # # # # # # # # # # # #





parser = argparse.ArgumentParser()
parser.add_argument("--instr")
args = parser.parse_args()

if args.instr == None:
	print Color.YELLOW + "SPECIFY INSTRUMENT WITH --instr <name>" + Color.RESET
	sys.exit()

args.instr = args.instr.lower()

def line_select_callback(eclick, erelease):
	global x1, x2, y1, y2, plt
	x1, y1 = eclick.xdata * u.pixel, eclick.ydata * u.pixel
	x2, y2 = erelease.xdata * u.pixel, erelease.ydata * u.pixel
	plt.close()

def cutout_selection(mapcube):
	print Color.YELLOW + "\nOPENING PLOT..."

	ax = plt.subplot(111, projection = smap.Map(mapcube[0]))
	mapcube[0].plot_settings["cmap"] = cm.get_cmap(name = "sdoaia%s" % str(int(mapcube[0].measurement.value)))
	mapcube[0].plot()
	ax.grid(False)

	plt.title("DRAG A SELECTION CENTERED SOMEWHERE ON THE SUN")
	plt.xlabel("Longitude [arcsec]")
	plt.ylabel("Latitude [arcsec]")

	selector = RectangleSelector(
								ax,
								line_select_callback,
								drawtype = 'box',
								useblit = True,
								button = [1, 3],
								minspanx = 5,
								minspany = 5,
								spancoords = 'pixels',
								interactive = True)

	plt.connect('key_press_event', selector)
	plt.clim(0, 40000)
	plt.style.use('dark_background')
	plt.show()
	os.system("open -a Terminal")

	return mapcube[0].pixel_to_world(
									(x2 + x1)/2.0,
									(y2 + y1)/2.0)

def calc_ci(mapcube, xdim, ydim, locs, id):
	c1 = SkyCoord(
				locs[id].Tx - xdim/2.0,
				locs[id].Ty - ydim/2.0,
				frame = mapcube[id].coordinate_frame)

	c2 = SkyCoord(
				locs[id].Tx + xdim/2.0,
				locs[id].Ty + ydim/2.0,
				frame = mapcube[id].coordinate_frame)

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

 	return SkyCoord(coord.Tx,
 					coord.Ty,
 					obstime = str(mapcube[id].date),
 					observer = get_earth(mapcube[id].date),
 					frame = frames.Helioprojective)

###################################################################################################

os.system("clear")
main_dir = "/Users/%s/Desktop/lmsal" % getpass.getuser()

if args.instr == "hmi":
	print Color.YELLOW + "MOVING FILES IN DOWNLOAD DIRECTORY TO resources/discarded-files..." + Color.RESET
	os.system("mv %s/resources/hmi-images/*.jpg %s/resources/discarded-files" % (main_dir, main_dir))

	print Color.YELLOW + "\nIMPORTING DATA..." + Color.RESET
	mapcube = smap.Map("%s/resources/hmi-fits-files/*.fits" % main_dir, cube = True)

elif args.instr == "aia":
	print Color.YELLOW + "MOVING FILES IN DOWNLOAD DIRECTORY TO resources/discarded-files..." + Color.RESET
	os.system("mv %s/resources/aia-images/*.jpg %s/resources/discarded-files" % (main_dir, main_dir))

	print Color.YELLOW + "\nIMPORTING DATA..." + Color.RESET
	mapcube = smap.Map("%s/resources/aia-fits-files/*.fits" % main_dir, cube = True)

if len(mapcube) == 0:
	print Color.RED + "\nNO DATA. EXITING..." + Color.RESET
	sys.exit()

if not only_fulldisk_images:
	if(raw_input(Color.RED + "\nAUTOMATICALLY FIND MOST INTENSE REGION? [y/n]\n==> ") == "y"):
		print Color.YELLOW + "\nIDENTIFYING..." + Color.RESET
		px = np.argwhere(mapcube[0].data == mapcube[0].data.max()) * u.pixel

		if len(px) > 1:
			temp = ndimage.measurements.center_of_mass(np.array(px))
			px = [px[int(temp[0] + 0.5)]]

		center = PixCoord(x = 2043, y = 2025)
		radius = 1610
		region = CirclePixelRegion(center, radius)
		point = PixCoord(px[0][1], px[0][0])

		if not region.contains(point):
			print Color.YELLOW + "\nMOST INTENSE REGION IS OUTSIDE SOLAR LIMB.\nDEFAULTING TO USER SELECTION..."
			init_coord = cutout_selection(mapcube)
		else:
			init_coord = mapcube[0].pixel_to_world(px[0][1], px[0][0])

		auto_sel = True
		plt.style.use("dark_background")
	else:
		init_coord = cutout_selection(mapcube)
		auto_sel = False
		plt.style.use("dark_background")

	init_time = str(mapcube[0].date)
	print Color.UNDERLINE_YELLOW + "\nINITIAL TIME" + Color.RESET + Color.YELLOW + "\n%s" % str(init_time)

	init_loc = SkyCoord(init_coord.Tx,
						init_coord.Ty,
						obstime = init_time,
						observer = get_earth(init_time),
						frame = frames.Helioprojective)

	print Color.UNDERLINE_YELLOW + "\nINITIAL LOCATION" + Color.RESET
	print Color.YELLOW + "x: %s arcsec\ny: %s arcsec" % (init_loc.Tx, init_loc.Ty) + Color.RESET

	print Color.YELLOW + "\nCALCULATING FUTURE ROTATIONAL COORDINATES..." + Color.RESET
	locs = [solar_rotate_coordinate(init_loc, mapcube[i].date) for i in range(len(mapcube))]

if ask_to_change_default_settings:
	if(raw_input(Color.RED + "\nUSE DEFAULT SETTINGS (LOW SCALE 0, HIGH SCALE 40000)? [y/n]\n==> ") == "n"):
		default_low_scale = int(raw_input("\nENTER LOW SCALE VALUE:\n==> "))
		default_high_scale = int(raw_input("\nENTER HIGH SCALE VALUE:\n==> "))

if not only_fulldisk_images:
	if not auto_sel:
		coord1 = mapcube[0].pixel_to_world(x1, y1)
		coord2 = mapcube[0].pixel_to_world(x2, y2)
		default_cutout_width = coord2.Tx - coord1.Tx
		default_cutout_height = coord2.Ty - coord1.Ty

if not only_fulldisk_images:
	print Color.YELLOW + "\nCALCULATING INITIAL CENTER OF INTENSITY..."
	init_ci = calc_ci(
					mapcube,
					default_cutout_width,
					default_cutout_height,
					locs, 0)

print ""
id = 0
for i in tqdm(
			range(len(mapcube)),
			desc = Color.YELLOW + "GENERATING CUTOUTS",
			bar_format = '{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [eta {remaining}, ' '{rate_fmt}]'):
	
	if not only_fulldisk_images:
		c1 = SkyCoord(
					locs[i].Tx - default_cutout_width/2.0,
					locs[i].Ty - default_cutout_height/2.0,
					frame = mapcube[i].coordinate_frame)
		
		c2 = SkyCoord(
					locs[i].Tx + default_cutout_width/2.0,
					locs[i].Ty + default_cutout_height/2.0,
					frame = mapcube[i].coordinate_frame)

	ax = plt.subplot(111, projection = mapcube[i])
	mapcube[i].plot()
	ax.grid(False)

	if only_fulldisk_images:
		if args.instr == "hmi":
			mapcube[i].plot(vmin = -120, vmax = 120)
		elif args.instr == "aia":
			mapcube[i].plot()
			plt.clim(0, 40000)
			
	else:
		cutout = mapcube[i].submap(c1, c2)
		ax = plt.subplot(111, projection = cutout)
		cutout.plot()

	if plot_center_of_intensity and not only_fulldisk_images:
		loc = solar_rotate_coordinate(init_ci, mapcube[i].date)
		ax.plot_coord(loc, "w3")

	ax.grid(False)
	plt.style.use("dark_background")
	plt.xlabel("Longitude [arcsec]")
	plt.ylabel("Latitude [arcsec]")

	if args.instr == "hmi":
		plt.savefig("%s/resources/hmi-images/cut-%03d.jpg" % (main_dir, id), dpi = default_quality)

		if crop_cut_to_only_sun:
			cut = cv2.imread("%s/resources/hmi-images/cut-%03d.jpg" % (main_dir, id))
			scale = default_quality/300.0
			crop_data = cut[int(176 * scale) : int(1278 * scale), int(432 * scale) : int(1534 * scale)]
			crop_data = np.flip(crop_data, 0)
			crop_data = np.flip(crop_data, 1)
			# crop_data[np.where((crop_data == [255, 255, 255]).all(axis = 2))] = [0, 0, 0]
			# cv2.putText(crop_data, mapcube[i].date.strftime("%Y-%m-%d %H:%M:%S"), (10, 40), 0, 1.2, (255, 255, 255), 2, cv2.LINE_AA)
			cv2.imwrite("%s/resources/hmi-images/cut-%03d.jpg" % (main_dir, id), crop_data)
	
	elif args.instr == "aia":
		plt.savefig("%s/resources/aia-images/cut-%03d.jpg" % (main_dir, id), dpi = default_quality)

		if crop_cut_to_only_sun:
			cut = cv2.imread("%s/resources/aia-images/cut-%03d.jpg" % (main_dir, id))
			scale = default_quality/300.0
			crop_data = cut[int(176 * scale) : int(1278 * scale), int(432 * scale) : int(1534 * scale)]
			# cv2.putText(crop_data, mapcube[i].date.strftime("%Y-%m-%d %H:%M:%S"), (10,40), 0, 1.2, (255,255,255), 2, cv2.LINE_AA)
			cv2.imwrite("%s/resources/aia-images/cut-%03d.jpg" % (main_dir, id), crop_data)

	id += 1
	
	plt.close()

print "\nDONE\n" + Color.RESET
