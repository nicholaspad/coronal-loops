import warnings
warnings.filterwarnings("ignore", message = "numpy.dtype size changed")

from astropy.coordinates import SkyCoord
from datetime import datetime
from helper import clear_filesystem
from IPython.core import debugger; debug = debugger.Pdb().set_trace
from matplotlib.path import Path
from recorder import Recorder
from scipy.ndimage import zoom as interpolate
from scipy.ndimage.measurements import center_of_mass as com
from scipy.ndimage.morphology import binary_dilation as grow_mask
from scipy.spatial import distance
from skimage import measure
import astropy.units as u
import getpass
import matplotlib.pyplot as plt
import numpy as np
import os
import scipy.ndimage as ndimage
import scipy.ndimage.filters as filters
import sunpy.map as smap

##### initial setup

MAIN_DIR = "/Users/%s/Desktop/lmsal" % getpass.getuser()
RECORDER = Recorder("database.csv")
RECORDER.display_start_time("region-analysis")
clear_filesystem()

##### import data

RECORDER.info_text("Importing AIA171 data")
MAPCUBE_AIA_171 = smap.Map("%s/resources/aia-fits-files/*.171.image_lev1.fits" % MAIN_DIR, sequence = True)
RECORDER.info_text("Importing AIA304 data")
MAPCUBE_AIA_304 = smap.Map("%s/resources/aia-fits-files/*.304.image_lev1.fits" % MAIN_DIR, sequence = True)
RECORDER.info_text("Importing HMI magnetogram data\n")
MAPCUBE_HMI = smap.Map("%s/resources/hmi-fits-files/*.fits" % MAIN_DIR, sequence = True)

##### prepare mapcube

DATA = {
	"AIA171" : MAPCUBE_AIA_171,
	"AIA304" : MAPCUBE_AIA_304,
	"HMI" : MAPCUBE_HMI
}

N = len(DATA["AIA171"])

##### helper variables

LOOP_ID = 1
NUM_LOOPS = 0

ADD_OFFDISK = False
NUM_OFF_DISK = 0

ADD_SMALL = False
NUM_SMALL = 0

##### find and store bright regions

REGIONS = []
REGIONS_HPC = []

for i in range(N):

	RAW = DATA["AIA171"][i].data

	MIN_DISTANCE = 1000
	MIN_VALUE = 0.6 * RAW.max()

	max = filters.maximum_filter(RAW,
								 MIN_DISTANCE)
	temp = (RAW == max)
	min = filters.minimum_filter(RAW,
								 MIN_DISTANCE)
	diff = ((max - min) > MIN_VALUE)
	temp[diff == 0] = 0

	labeled, num_objects = ndimage.label(temp)
	xy_maxima = np.array(ndimage.center_of_mass(RAW,
												labeled,
												range(1, num_objects + 1)))

	xy_maxima = xy_maxima.astype(int)
	REGIONS.append(xy_maxima)

	if xy_maxima.shape[0] == 0:
		REGIONS_HPC.append(np.array([]))

	else:
		REGIONS_HPC.append(DATA["AIA171"][i].pixel_to_world(xy_maxima[:, 1] * u.pixel,
															xy_maxima[:, 0] * u.pixel))

##### analyze bright region

for i in range(N):

	RAW_AIA = DATA["AIA304"][i].data
	RAW_AIA_171 = DATA["AIA171"][i].data
	RAW_HMI = DATA["HMI"][i].data

	M = len(REGIONS[i])

	for j in range(M):

		##### basic information about data point

		PRODUCT = "AIA304"

		RECORDER.show_instr(PRODUCT)
		RECORDER.write_ID(LOOP_ID)

		when = DATA[PRODUCT][i].date
		RECORDER.write_datetime(when)

		xy = REGIONS[i][j]
		RECORDER.write_xywhere(xy)

		center = np.array([int(DATA[PRODUCT][i].reference_pixel[0].value),
						   int(DATA[PRODUCT][i].reference_pixel[1].value)])
		radius = (DATA[PRODUCT][i].rsun_obs / DATA[PRODUCT][i].scale[0]).value

		##### algorithm to eliminate regions far from solar center

		OFF_DISK_THRESHOLD = 50.0

		if distance.euclidean(center, xy) >= (radius - OFF_DISK_THRESHOLD):
			RECORDER.off_disk()
			NUM_OFF_DISK += 1
			continue

		hpc = REGIONS_HPC[i][j]
		RECORDER.write_hpcwhere(hpc)

		##### algorithm to determine bounds of region
		RECORDER.info_text("Finding optimal region bounds...")

		AVERAGE_BRIGHTNESS_THRESHOLD = 200.0
		HALF_DIM_PXL = 1

		while np.average(RAW_AIA[xy[0] - HALF_DIM_PXL : xy[0] + HALF_DIM_PXL,
								 xy[1] - HALF_DIM_PXL: xy[1] + HALF_DIM_PXL]) > AVERAGE_BRIGHTNESS_THRESHOLD:
			HALF_DIM_PXL += 1

		if HALF_DIM_PXL < 50.0:
			RECORDER.too_small()
			NUM_SMALL += 1
			continue

		RECORDER.write_xysize(HALF_DIM_PXL * 2.0)

		##### converts pixel coordinates to helioprojective coordinates

		HALF_DIM_HPC = DATA[PRODUCT][i].scale[0].value * HALF_DIM_PXL

		bl = SkyCoord(hpc.Tx - HALF_DIM_HPC * u.arcsec,
					  hpc.Ty - HALF_DIM_HPC * u.arcsec,
					  frame = DATA[PRODUCT][i].coordinate_frame)

		tr = SkyCoord(hpc.Tx + HALF_DIM_HPC * u.arcsec,
					  hpc.Ty + HALF_DIM_HPC * u.arcsec,
					  frame = DATA[PRODUCT][i].coordinate_frame)

		RECORDER.write_hpcsize(bl, tr)

		cut_aia = RAW_AIA[xy[0] - HALF_DIM_PXL : xy[0] + HALF_DIM_PXL,
						  xy[1] - HALF_DIM_PXL: xy[1] + HALF_DIM_PXL]

		cut_aia_171 = RAW_AIA_171[xy[0] - HALF_DIM_PXL : xy[0] + HALF_DIM_PXL,
								  xy[1] - HALF_DIM_PXL: xy[1] + HALF_DIM_PXL]

		RECORDER.write_image(0,
							 LOOP_ID,
							 cut_aia,
							 DATA[PRODUCT][i].detector,
							 DATA[PRODUCT][i].wavelength)

		RECORDER.write_image(0,
							 LOOP_ID,
							 cut_aia_171,
							 DATA["AIA171"][i].detector,
							 DATA["AIA171"][i].wavelength)

		##### grows a binary mask based on the threshold
		RECORDER.info_text("Growing binary mask...")

		LOW_BRIGHTNESS_THRESHOLD = 450

		r_mask = np.logical_and(cut_aia > LOW_BRIGHTNESS_THRESHOLD,
									 cut_aia < np.inf)
		r_mask = grow_mask(r_mask,
								iterations = 1,
								structure = np.ones((3,3)).astype(bool)).astype(int)

		RECORDER.write_image(1,
							 LOOP_ID,
							 r_mask,
							 DATA[PRODUCT][i].detector,
							 DATA[PRODUCT][i].wavelength)

		##### applies binary mask to AIA304 data
		RECORDER.info_text("Applying binary mask to AIA304 data...")

		masked_aia_data = cut_aia * r_mask

		RECORDER.write_image(2,
							 LOOP_ID,
							 masked_aia_data,
							 DATA[PRODUCT][i].detector,
							 DATA[PRODUCT][i].wavelength)

		##### initial setup for elliptical mask fit
		RECORDER.info_text("Preparing for elliptical mask fit...")

		center = com(r_mask)
		x_center = int(center[0] + 0.5)
		y_center = int(center[1] + 0.5)
		dim = cut_aia.shape[0]
		threshold_percent_1 = 1.0
		threshold_percent_2 = 0.97
		threshold_percent_3 = 0.94

		total = float(len(np.where(r_mask == 1)[0]))
		rad = 2.0
		y, x = np.ogrid[-x_center:dim - x_center, -y_center:dim - y_center]
		mask_in = None
		mask_out = None

		##### fits circle to 100% of the data
		RECORDER.info_text("Fitting elliptical mask to binary AIA304 data...")

		while True:
			temp_in = x**2 + y**2 <= rad**2
			if len(np.where(r_mask * temp_in == 1)[0]) / total >= threshold_percent_1:
				mask_in = temp_in
				break
			rad += 1.0

		##### adjusts horizontal axis of ellipse to fit 95% of the data
		RECORDER.info_text("Adjusting horizontal axis...")

		a = b = rad

		while True:
			temp_in = x**2/a**2 + y**2/b**2 <= 1
			if len(np.where(r_mask * temp_in == 1)[0]) / total < threshold_percent_2:
				mask_in = temp_in
				break
			a -= 1.0

		##### adjusts vertical axis of ellipse to fit 90% of the data
		RECORDER.info_text("Adjusting vertical axis...")

		while True:
			temp_in = x**2/a**2 + y**2/b**2 <= 1
			temp_out = x**2/a**2 + y**2/b**2 > 1
			if len(np.where(r_mask * temp_in == 1)[0]) / total < threshold_percent_3:
				mask_in = temp_in
				mask_out = temp_out
				break
			b -= 1.0

		##### creates elliptical binary mask
		RECORDER.info_text("Finalizing elliptical mask...")

		e_mask = r_mask * mask_in

		RECORDER.write_image(3,
							 LOOP_ID,
							 e_mask,
							 DATA[PRODUCT][i].detector,
							 DATA[PRODUCT][i].wavelength)

		##### applies elliptical binary mask to data
		RECORDER.info_text("Applying elliptical mask to AIA304 data...")

		e_masked_aia_data = (cut_aia * e_mask).astype(float)
		e_masked_aia_data[mask_out] = np.nan

		RECORDER.write_image(4,
							 LOOP_ID,
							 e_masked_aia_data,
							 DATA[PRODUCT][i].detector,
							 DATA[PRODUCT][i].wavelength)

		##### calculates contour-fit binary mask from elliptical mask
		RECORDER.info_text("Fitting contour mask to elliptical mask...")

		contours = np.array(measure.find_contours(e_masked_aia_data, 0.5))

		L = len(contours)
		max_area = 0.0
		max_index = 0.0

		for i in range(L):
			n = len(contours[i])
			area = 0.0
			for j in range(n):
				k = (j + 1) % n
				area += contours[i][j][0] * contours[i][k][1]
				area -= contours[i][k][0] * contours[i][j][1]
			area = abs(area) / 2.0
			if area > max_area:
				max_area = area
				max_index = i

		contour = np.array([contours[max_index]])

		contour = np.array([contours[max_index]])

		x_dim = e_masked_aia_data.shape[0]
		y_dim = e_masked_aia_data.shape[1]

		x, y = np.meshgrid(np.arange(x_dim), np.arange(y_dim))
		x, y = x.flatten(), y.flatten()

		points = np.vstack((x,y)).T

		vertices = contour[0]
		path = Path(vertices)
		c_mask = path.contains_points(points)
		c_mask = np.rot90(np.flip(c_mask.reshape((y_dim,x_dim)), 1))

		RECORDER.write_image(5,
							 LOOP_ID,
							 c_mask,
							 DATA[PRODUCT][i].detector,
							 DATA[PRODUCT][i].wavelength)

		##### show mask outline
		# for n, c in enumerate(contour):
		# 	plt.plot(c[:, 1], c[:, 0], linewidth = 1, color = "white")

		##### applies contour mask to data
		RECORDER.info_text("Applying contour mask to AIA304 data...")

		c_masked_aia_data = (e_masked_aia_data * c_mask).astype(float)

		RECORDER.write_image(6,
							 LOOP_ID,
							 c_masked_aia_data,
							 DATA[PRODUCT][i].detector,
							 DATA[PRODUCT][i].wavelength)

		##### takes statistics for c-masked AIA304 data
		RECORDER.info_text("Recording statistics for contour-masked AIA304 data...")

		temp_threshold_data = c_masked_aia_data[np.where(c_masked_aia_data > LOW_BRIGHTNESS_THRESHOLD)]
		average_intensity = np.average(temp_threshold_data)
		median_intensity = np.median(temp_threshold_data)
		maximum_intensity = np.max(temp_threshold_data)

		RECORDER.write_inten(LOW_BRIGHTNESS_THRESHOLD,
							 average_intensity,
							 median_intensity,
							 maximum_intensity)


		""""""

		# TODO: processing on c_masked_aia_data

		""""""


		##### aligns HMI data to AIA304 data with interpolation and casting
		RECORDER.info_text("Aligning HMI data to AIA304 data...")

		PRODUCT = "HMI"

		ALIGNED_RAW_HMI = np.zeros((4096, 4096)).astype(float)
		ALIGNED_RAW_HMI[ALIGNED_RAW_HMI == 0] = np.nan
		scale = (DATA[PRODUCT][i].scale[0] / DATA["AIA304"][i].scale[0]).value
		scale = float("%.3f" % scale)

		RECORDER.info_text("Interpolating HMI data with %.6f scale factor..." % scale)
		interpolated_hmi_data = interpolate(RAW_HMI,
											scale,
											order = 1)
		interpolated_hmi_data = np.flip(interpolated_hmi_data,
										(0,1))

		x_size = interpolated_hmi_data.shape[1]
		y_size = interpolated_hmi_data.shape[0]
		x_center = int(DATA["AIA304"][i].reference_pixel.y.value + 0.5)
		y_center = int(DATA["AIA304"][i].reference_pixel.x.value + 0.5)

		RECORDER.info_text("Casting interpolated HMI data to 4k by 4k empty image...")
		ALIGNED_RAW_HMI[(y_center - 1 - y_size / 2) : (y_center + y_size / 2),
						(x_center - 1 - x_size / 2) : (x_center + x_size / 2)] = interpolated_hmi_data

		cut_hmi = ALIGNED_RAW_HMI[xy[0] - HALF_DIM_PXL : xy[0] + HALF_DIM_PXL,
								  xy[1] - HALF_DIM_PXL: xy[1] + HALF_DIM_PXL]

		RECORDER.write_image(0,
							 LOOP_ID,
							 cut_hmi,
							 DATA[PRODUCT][i].detector,
							 DATA[PRODUCT][i].wavelength)

		##### applies binary mask to HMI data
		RECORDER.info_text("Applying binary mask to HMI data...")

		masked_hmi_data = cut_hmi * r_mask

		RECORDER.write_image(2,
							 LOOP_ID,
							 masked_hmi_data,
							 DATA[PRODUCT][i].detector,
							 DATA[PRODUCT][i].wavelength)

		##### applies elliptical binary mask to the data
		RECORDER.info_text("Applying elliptical mask to HMI data...")

		e_masked_hmi_data = cut_hmi * e_mask
		e_masked_hmi_data[mask_out] = np.nan

		RECORDER.write_image(4,
							 LOOP_ID,
							 e_masked_hmi_data,
							 DATA[PRODUCT][i].detector,
							 DATA[PRODUCT][i].wavelength)

		##### takes a few statistics for masked HMI data
		RECORDER.info_text("Recording statistics for masked HMI data...")

		temp_threshold_data = np.ma.array(e_masked_hmi_data,
										  mask = np.isnan(e_masked_hmi_data))

		unsig_gauss = np.sum(np.abs(temp_threshold_data))
		average_gauss = np.average(temp_threshold_data)
		median_gauss = np.median(temp_threshold_data)

		RECORDER.write_gauss(unsig_gauss,
							 average_gauss,
							 median_gauss)

		RECORDER.new_line()

		NUM_LOOPS += 1
		LOOP_ID += 1

RECORDER.remove_duplicates()

RECORDER.info_text("Compressing database\n")
os.chdir("resources/")
os.system("zip -r -X data_%s.zip region-data" % str(datetime.now().strftime("%Y-%m-%d_%H.%M.%S")))
os.chdir("../")
RECORDER.info_text("Done:\t%s regions analyzed\n\t\t%s regions off-disk\n\t\t%s regions too small" % (NUM_LOOPS, NUM_OFF_DISK, NUM_SMALL))
RECORDER.line()
RECORDER.display_end_time("loop-analysis")
