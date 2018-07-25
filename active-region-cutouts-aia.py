from astropy.coordinates import SkyCoord
from colortext import Color
from matplotlib.widgets import RectangleSelector
from regions import PixCoord, CirclePixelRegion
from scipy import ndimage
from sunpy.coordinates import frames
from sunpy.coordinates.ephemeris import get_earth
from sunpy.physics.differential_rotation import solar_rotate_coordinate
from tqdm import tqdm
import astropy.units as u
import getpass
import lycon
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
default_low_scale = 0
default_high_scale = 40000
default_quality = 600 #dpi
# ----------------------------------------------- #
only_fulldisk_images = True
plot_center_of_intensity = False
crop_cut_to_only_sun = True
# ----------------------------------------------- #
# # # # # # # # # # # # # # # # # # # # # # # # # #





"""
Action listener for region selection.
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
	print Color.BOLD_YELLOW + "\nOPENING PLOT..."

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

"""
Method that calculates the location of the center of intensity of the first cutout.
"""
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

"""
Clears source folders and imports all FITS files into a datacube.
"""
os.system("clear")
main_dir = "/Users/%s/Desktop/lmsal" % getpass.getuser()

print Color.BOLD_YELLOW + "MOVING FILES IN DOWNLOAD DIRECTORY TO resources/discarded-files..." + Color.RESET
os.system("mv %s/resources/cutout-images/*.jpg %s/resources/discarded-files" % (main_dir, main_dir))

print Color.BOLD_YELLOW + "\nIMPORTING DATA..." + Color.RESET
mapcube = smap.Map("%s/resources/fits-files/*.fits" % main_dir, cube = True)

num_wav = calc_num_wav(mapcube)

print Color.BOLD_YELLOW + "\nSORTING DATA..." + Color.RESET
mapcube_sorted = sort_mapcube(mapcube, num_wav)

if len(mapcube) == 0:
	print Color.BOLD_RED + "\nNO DATA. EXITING..." + Color.RESET
	sys.exit()

"""
Identifies an Active Region, either automatically or specified by the user.
"""
if not only_fulldisk_images:
	if(raw_input(Color.BOLD_RED + "\nAUTOMATICALLY FIND BRIGHTEST REGION? [y/n]\n==> ") == "y"):
		print Color.BOLD_YELLOW + "\nIDENTIFYING..." + Color.RESET
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
			print Color.BOLD_YELLOW + "\nBRIGHTEST LOCATION IS OUTSIDE SOLAR LIMB.\nDEFAULTING TO USER SELECTION..."
			init_coord = cutout_selection(mapcube)
		else:
			init_coord = mapcube[0].pixel_to_world(px[0][1], px[0][0])

		auto_sel = True
		plt.style.use("dark_background")
	else:
		init_coord = cutout_selection(mapcube)
		auto_sel = False
		plt.style.use("dark_background")

	"""
	Creates a SkyCoord (Helioprojective coordinate) based on the location of the Active Region.
	"""
	init_time = str(mapcube[0].date)
	print Color.UNDERLINE_YELLOW + "\nINITIAL TIME" + Color.RESET + Color.YELLOW + "\n%s" % str(init_time)

	init_loc = SkyCoord(init_coord.Tx,
						init_coord.Ty,
						obstime = init_time,
						observer = get_earth(init_time),
						frame = frames.Helioprojective)

	print Color.BOLD_YELLOW + Color.UNDERLINE_YELLOW + "\nINITIAL LOCATION" + Color.RESET
	print Color.YELLOW + "x: %s arcsec\ny: %s arcsec" % (init_loc.Tx, init_loc.Ty) + Color.RESET

	"""
	Calculates coordinates of future cutouts, based on the date from FITS file metadata.
	"""
	print Color.BOLD_YELLOW + "\nCALCULATING FUTURE ROTATIONAL COORDINATES..." + Color.RESET
	locs = [solar_rotate_coordinate(init_loc, mapcube[i].date) for i in range(len(mapcube))]

"""
Gathers some information to generate the cutouts.
"""
if ask_to_change_default_settings:
	if(raw_input(Color.BOLD_RED + "\nUSE DEFAULT SETTINGS (LOW SCALE 0, HIGH SCALE 40000)? [y/n]\n==> ") == "n"):
		default_low_scale = int(raw_input("\nENTER LOW SCALE VALUE:\n==> "))
		default_high_scale = int(raw_input("\nENTER HIGH SCALE VALUE:\n==> "))

"""
Determines the region dimensions based on the user's selection.
If Active Region was automatically found, a square region is used.
"""
if not only_fulldisk_images:
	if not auto_sel:
		coord1 = mapcube[0].pixel_to_world(x1, y1)
		coord2 = mapcube[0].pixel_to_world(x2, y2)
		default_cutout_width = coord2.Tx - coord1.Tx
		default_cutout_height = coord2.Ty - coord1.Ty

"""
Instantiates a SkyCoord containing the initial center of intensity location.
"""
if not only_fulldisk_images:
	print Color.BOLD_YELLOW + "\nCALCULATING INITIAL CENTER OF INTENSITY..."
	init_ci = calc_ci(
					mapcube,
					default_cutout_width,
					default_cutout_height,
					locs, 0)

"""
Uses matplotlib and astropy SkyCoord to generate cutoutouts, based on the coordinates calculated previously.
"""
print ""
id = 0
for i in tqdm(
			range(len(mapcube_sorted[0])),
			desc = Color.BOLD_YELLOW + "GENERATING CUTOUTS",
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

	"""
	Set up skeleton matplotlib pyplot.
	"""
	for j in range(num_wav):
		wavelength_for_cmap = "sdoaia%s" % str(int(mapcube_sorted[j][i].measurement.value))
		mapcube_sorted[j][i].plot_settings["cmap"] = cm.get_cmap(name = wavelength_for_cmap)
		ax = plt.subplot(111, projection = mapcube_sorted[j][i])
		mapcube_sorted[j][i].plot()
		ax.grid(False)

		if only_fulldisk_images:
			mapcube_sorted[j][i].plot()
			plt.style.use("dark_background")
			plt.xlabel("Longitude [arcsec]")
			plt.ylabel("Latitude [arcsec]")
			plt.clim(default_low_scale, default_high_scale)
		else:
			cutout = mapcube_sorted[j][i].submap(c1, c2)
			ax = plt.subplot(
							1,
							num_wav,
							j + 1,
							projection = cutout)
			cutout.plot_settings["cmap"] = cm.get_cmap(name = wavelength_for_cmap)
			cutout.plot()

		if plot_center_of_intensity and not only_fulldisk_images:
			loc = solar_rotate_coordinate(init_ci, mapcube_sorted[j][i].date)
			ax.plot_coord(loc, "w3")

		ax.grid(False)
		plt.style.use("dark_background")
		plt.xlabel("Longitude [arcsec]")
		plt.ylabel("Latitude [arcsec]")
		plt.clim(default_low_scale, default_high_scale)

		if j != 0:
			plt.ylabel("")
			
	if mapcube_sorted[j][i].exposure_time != 0:
		plt.savefig("%s/resources/cutout-images/cut-%03d.jpg" % (main_dir, id), dpi = default_quality)

		if crop_cut_to_only_sun:
			cut = lycon.load("%s/resources/cutout-images/cut-%03d.jpg" % (main_dir, id))
			scale = default_quality/300.0
			crop_data = cut[int(176 * scale) : int(1278 * scale), int(432 * scale) : int(1534 * scale)]
			lycon.save("%s/resources/cutout-images/cut-%03d.jpg" % (main_dir, id), crop_data)

		id += 1
	
	plt.close()

print "\nDONE: IMAGES SAVED TO resources/cutout-images\n" + Color.RESET
