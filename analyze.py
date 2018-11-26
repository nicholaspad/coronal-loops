import warnings
warnings.filterwarnings("ignore", message = "From scipy 0.13.0, the output shape of")
warnings.filterwarnings("ignore", message = "invalid value encountered in greater")
warnings.filterwarnings("ignore", message = "invalid value encountered in less")
warnings.filterwarnings("ignore", message = "numpy.dtype size changed")

from IPython.core import debugger; debug = debugger.Pdb().set_trace
from matplotlib.path import Path
from os import listdir
from os.path import isfile, join
from recorder import Recorder
from scipy import ndimage
from scipy.ndimage import zoom as interpolate
from scipy.ndimage.measurements import center_of_mass as com
from skimage import measure
from skimage.filters import laplace
from sunpy.physics.differential_rotation import solar_rotate_coordinate as rot
from tqdm import tqdm
import astropy.units as u
import cv2 as cv
import matplotlib.pyplot as plt
import numpy as np
import sunpy.map as smap

#*************************************#

RECORDER = Recorder()
RECORDER.display_start_time("analyze")

RECORDER.sys_text("Importing data")

## LOCKHEED ##
IMAGE_SAVEPATH = "/Users/padman/Desktop/lmsal/resources/analyze-data/"
PATH171 = "/Volumes/Nicholas-Data/AIA171/"
PATH304 = "/Volumes/Nicholas-Data/AIA304/"
PATHHMI = "/Volumes/Nicholas-Data/HMI/"

## PERSONAL MAC ##
# IMAGE_SAVEPATH = "/Users/Lockheed Martin/Desktop/lmsal/resources/analyze-data/"
# PATH171 = "/Volumes/Nicholas-Data/AIA171/"
# PATH304 = "/Volumes/Nicholas-Data/AIA304/"
# PATHHMI = "/Volumes/Nicholas-Data/HMI/"

## PERSONAL PC ##
# IMAGE_SAVEPATH = "/Users/Lockheed Martin/Desktop/lmsal/resources/analyze-data/"
# PATH171 = "/Volumes/Nicholas-Data/AIA171/"
# PATH304 = "/Volumes/Nicholas-Data/AIA304/"
# PATHHMI = "/Volumes/Nicholas-Data/HMI/"

AIA171_DIR = [f for f in listdir(PATH171) if isfile(join(PATH171, f))]
AIA304_DIR = [f for f in listdir(PATH304) if isfile(join(PATH304, f))]
HMI_DIR = [f for f in listdir(PATHHMI) if isfile(join(PATHHMI, f))]

#*************************************#

def hmialign(data, scale):
	ar = np.zeros((4096, 4096)).astype(float)

	interpolated_hmi_data = interpolate(data, scale, order = 1)
	interpolated_hmi_data = np.flip(interpolated_hmi_data, (0,1))

	x_size = interpolated_hmi_data.shape[1]
	y_size = interpolated_hmi_data.shape[0]
	x_center = int(AIA304.reference_pixel.y.value + 0.5)
	y_center = int(AIA304.reference_pixel.x.value + 0.5)

	ar[(y_center - 1 - y_size / 2) : (y_center + y_size / 2),
	   (x_center - 1 - x_size / 2) : (x_center + x_size / 2)] = interpolated_hmi_data

	return ar

#*************************************#

RECORDER.info_text("Analyzing region")

x_center_o = 1012
y_center_o = 1630
DIM = 300

for id in tqdm(range(0, len(AIA171_DIR), 1920), desc = "Analyzing"):
	AIA171 = smap.Map(PATH171 + AIA171_DIR[id])
	AIA304 = smap.Map(PATH304 + AIA304_DIR[id])
	HMI = smap.Map(PATHHMI + HMI_DIR[id])

	RECORDER.info_text("Current timestamp: %s" % AIA171.date)

	if id == 0:
		init_loc = AIA171.pixel_to_world(x_center_o * u.pixel, y_center_o * u.pixel)

	new_loc = rot(init_loc, AIA171.date)
	new_xy = AIA171.world_to_pixel(new_loc)

	cx = int(new_xy[1].value)
	cy = int(new_xy[0].value)

	scale = (HMI.scale[0] / AIA304.scale[0]).value
	scale = float("%.3f" % scale)
	ALIGNED_RAW_HMI = hmialign(HMI.data, scale)

	img171 = AIA171.data[cx-DIM : cx+DIM, cy-DIM : cy+DIM]
	img304 = AIA304.data[cx-DIM : cx+DIM, cy-DIM : cy+DIM]
	imghmi = ALIGNED_RAW_HMI[cx-DIM+25 : cx+DIM+25, cy-DIM-20 : cy+DIM-20]

	#*************************************#
	
	RECORDER.sys_text("Producing AIA171 binary mask [r-mask]")

	LOW_BRIGHTNESS_THRESHOLD = 1500./AIA171.exposure_time.value
	r_mask = np.logical_and(img171 > LOW_BRIGHTNESS_THRESHOLD, img171 < np.inf)
	r_mask = r_mask.astype(np.uint8)
	r_mask = cv.dilate(r_mask, np.ones((3,3)).astype(bool).astype(int), iterations = 1)

	img171 *= r_mask

	#*************************************#

	RECORDER.sys_text("Generating AIA304 binary mask [r-mask]")

	LOW_BRIGHTNESS_THRESHOLD = 400
	r_mask = np.logical_and(img304 > LOW_BRIGHTNESS_THRESHOLD, img304 < np.inf)
	r_mask = r_mask.astype(np.uint8)
	r_mask = cv.dilate(r_mask, np.ones((3,3)).astype(bool).astype(int), iterations = 1)

	img304 *= r_mask

	#*************************************#

	RECORDER.sys_text("Generating AIA304 elliptical mask [e-mask]")

	center = com(r_mask)
	x_center = int(center[0] + 0.5)
	y_center = int(center[1] + 0.5)
	dim = img304.shape[0]
	threshold_percent_1 = 0.98
	threshold_percent_2 = 0.96
	threshold_percent_3 = 0.94

	total = float(len(np.where(r_mask == 1)[0]))
	rad = 2.0
	y, x = np.ogrid[-x_center:dim - x_center, -y_center:dim - y_center]
	e_mask = None
	mask_out = None

	while True:
		temp_in = x**2 + y**2 <= rad**2
		if len(np.where(r_mask * temp_in == 1)[0]) / total >= threshold_percent_1:
			e_mask = temp_in
			break
		rad += 1.0

	a = b = rad

	while True:
		temp_in = x**2/a**2 + y**2/b**2 <= 1
		if len(np.where(r_mask * temp_in == 1)[0]) / total < threshold_percent_2:
			e_mask = temp_in
			break
		a -= 1.0

	while True:
		temp_in = x**2/a**2 + y**2/b**2 <= 1
		temp_out = x**2/a**2 + y**2/b**2 > 1
		if len(np.where(r_mask * temp_in == 1)[0]) / total < threshold_percent_3:
			e_mask = temp_in
			mask_out = temp_out
			break
		b -= 1.0

	img304 *= e_mask

	#*************************************#

	RECORDER.sys_text("Generating AIA304 contour mask [c-mask]")

	contours = np.array(measure.find_contours(r_mask, 0.5))
	max_area = 0.0
	max_index = 0

	for i in range(len(contours)):
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

	x_dim = r_mask.shape[0]
	y_dim = r_mask.shape[1]

	x, y = np.meshgrid(np.arange(x_dim), np.arange(y_dim))
	x, y = x.flatten(), y.flatten()

	points = np.vstack((x,y)).T

	vertices = contour[0]
	path = Path(vertices)
	c_mask = path.contains_points(points)
	c_mask = np.rot90(np.flip(c_mask.reshape((y_dim,x_dim)), 1))

	c_mask = c_mask.astype(np.uint8)
	c_mask = cv.morphologyEx(c_mask, cv.MORPH_CLOSE, np.ones((3,3)).astype(bool).astype(int))

	img304 *= c_mask
	img304 = img304.astype(float)
	img304[img304 == 0] = np.nan

	#*************************************#

	RECORDER.sys_text("Generating HMI binary mask [r-mask]")

	POS_GAUSS_THRESHOLD = 120
	NEG_GAUSS_THRESHOLD = -1 * POS_GAUSS_THRESHOLD

	r_mask_1 = np.logical_and(imghmi < -125, imghmi > -10000000)
	r_mask_2 = np.logical_and(imghmi > 125, imghmi < 10000000)
	r_mask = r_mask_1.astype(float) + r_mask_2.astype(float)
	r_mask[r_mask == 2.] = 1.

	r_mask = r_mask.astype(np.uint8)
	r_mask = cv.dilate(r_mask, np.ones((3,3)).astype(bool).astype(int), iterations = 1)
	r_mask = cv.morphologyEx(r_mask, cv.MORPH_CLOSE, np.ones((3,3)).astype(bool).astype(int))
	r_mask = cv.dilate(r_mask, np.ones((3,3)).astype(bool).astype(int), iterations = 1)

	imghmi *= r_mask

	#*************************************#

	RECORDER.sys_text("Generating HMI elliptical mask [e-mask]")

	center = com(r_mask)
	x_center = int(center[0] + 0.5)
	y_center = int(center[1] + 0.5)
	dim = imghmi.shape[0]
	threshold_percent_1 = 0.98
	threshold_percent_2 = 0.96
	threshold_percent_3 = 0.94

	total = float(len(np.where(r_mask == 1)[0]))
	rad = 2.0
	y, x = np.ogrid[-x_center:dim - x_center, -y_center:dim - y_center]
	e_mask = None
	mask_out = None

	while True:
		temp_in = x**2 + y**2 <= rad**2
		if len(np.where(r_mask * temp_in == 1)[0]) / total >= threshold_percent_1:
			e_mask = temp_in
			break
		rad += 1.0

	a = b = rad

	while True:
		temp_in = x**2/a**2 + y**2/b**2 <= 1
		if len(np.where(r_mask * temp_in == 1)[0]) / total < threshold_percent_2:
			e_mask = temp_in
			break
		a -= 1.0

	while True:
		temp_in = x**2/a**2 + y**2/b**2 <= 1
		temp_out = x**2/a**2 + y**2/b**2 > 1
		if len(np.where(r_mask * temp_in == 1)[0]) / total < threshold_percent_3:
			e_mask = temp_in
			mask_out = temp_out
			break
		b -= 1.0

	imghmi *= e_mask

	#*************************************#

	RECORDER.sys_text("Generating HMI contour mask [c-mask]")

	contours = np.array(measure.find_contours(r_mask, 0.5))
	L = len(contours)
	max_area = 0.0
	max_index = 0

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

	second_max_area = 0.0
	second_max_index = 0

	for i in range(L):
		n = len(contours[i])
		area = 0.0
		for j in range(n):
			k = (j + 1) % n
			area += contours[i][j][0] * contours[i][k][1]
			area -= contours[i][k][0] * contours[i][j][1]
		area = abs(area) / 2.0
		if area > second_max_area and area < max_area:
			second_max_area = area
			second_max_index = i

	third_max_area = 0.0
	third_max_index = 0

	for i in range(L):
		n = len(contours[i])
		area = 0.0
		for j in range(n):
			k = (j + 1) % n
			area += contours[i][j][0] * contours[i][k][1]
			area -= contours[i][k][0] * contours[i][j][1]
		area = abs(area) / 2.0
		if area > third_max_area and area < second_max_area:
			third_max_area = area
			third_max_index = i

	fourth_max_area = 0.0
	fourth_max_index = 0

	for i in range(L):
		n = len(contours[i])
		area = 0.0
		for j in range(n):
			k = (j + 1) % n
			area += contours[i][j][0] * contours[i][k][1]
			area -= contours[i][k][0] * contours[i][j][1]
		area = abs(area) / 2.0
		if area > fourth_max_area and area < third_max_area:
			fourth_max_area = area
			fourth_max_index = i

	contour1 = np.array([contours[max_index]])
	contour2 = np.array([contours[second_max_index]])
	contour3 = np.array([contours[third_max_index]])
	contour4 = np.array([contours[fourth_max_index]])

	x_dim = imghmi.shape[0]
	y_dim = imghmi.shape[1]

	x, y = np.meshgrid(np.arange(x_dim), np.arange(y_dim))
	x, y = x.flatten(), y.flatten()

	points = np.vstack((x,y)).T

	vertices1 = contour1[0]
	vertices2 = contour2[0]
	vertices3 = contour3[0]
	vertices4 = contour4[0]

	path1 = Path(vertices1)
	path2 = Path(vertices2)
	path3 = Path(vertices3)
	path4 = Path(vertices4)

	c_mask1 = path1.contains_points(points)
	c_mask1 = np.rot90(np.flip(c_mask1.reshape((y_dim,x_dim)), 1))

	c_mask2 = path2.contains_points(points)
	c_mask2 = np.rot90(np.flip(c_mask2.reshape((y_dim,x_dim)), 1))

	c_mask3 = path3.contains_points(points)
	c_mask3 = np.rot90(np.flip(c_mask3.reshape((y_dim,x_dim)), 1))

	c_mask4 = path4.contains_points(points)
	c_mask4 = np.rot90(np.flip(c_mask4.reshape((y_dim,x_dim)), 1))

	c_mask = c_mask1.astype(float) + c_mask2.astype(float) + c_mask3.astype(float) + c_mask4.astype(float)
	c_mask[c_mask == 2.] = 1.
	c_mask[c_mask == 3.] = 1.
	c_mask[c_mask == 4.] = 1.

	c_mask = c_mask.astype(np.uint8)
	c_mask = cv.morphologyEx(c_mask, cv.MORPH_CLOSE, np.ones((3,3)).astype(bool).astype(int))

	imghmi *= c_mask
	imghmi[imghmi == 0] = np.nan

	#*************************************#

	# statistical analysis

	""" AIA171 """

	img171

	""" AIA304 """

	img304

	""" HMI """

	imghmi

	#*************************************#

	RECORDER.sys_text("Doing final processing")

	img304[img304 < 1] = 1
	img304 = np.log(img304)/AIA304.exposure_time.value

	# img171[img171 < 1] = 1
	# img171 = np.sqrt(img171)/AIA171.exposure_time.value

	img171 = laplace(img171) * 100

	#*************************************#

	RECORDER.info_text("Saving image ID %05d" % id)
	#plt.imsave(IMAGE_SAVEPATH + "aia304/%05d" % id, img304, cmap = "sdoaia304", origin = "lower", vmin = 0, vmax = 3)
	plt.imsave(IMAGE_SAVEPATH + "aia171/%05d" % id, img171, cmap = "sdoaia171", origin = "lower", vmin = 0, vmax = 4)
	#plt.imsave(IMAGE_SAVEPATH + "hmi/%05d" % id, imghmi, cmap = "gray", origin = "lower", vmin = -120, vmax = 120)

