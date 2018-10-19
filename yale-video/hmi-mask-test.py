from IPython.core import debugger; debug = debugger.Pdb().set_trace
from scipy.ndimage.measurements import center_of_mass as com
from skimage import measure
from matplotlib.path import Path
import cv2 as cv
import matplotlib.pyplot as plt
import numpy as np
import sunpy.map as smap

f = smap.Map("sample-data/hmi.M_45s.20110211_000000_TAI.2.magnetogram.fits")
raw = f.data

crop = raw[2280:2780,2102:2602]

POS_GAUSS_THRESHOLD = 125
NEG_GAUSS_THRESHOLD = POS_GAUSS_THRESHOLD * -1

r_mask_1 = np.logical_and(crop < NEG_GAUSS_THRESHOLD, crop > -10000000)
r_mask_2 = np.logical_and(crop > POS_GAUSS_THRESHOLD, crop < 10000000)
r_mask = r_mask_1.astype(float) + r_mask_2.astype(float)
r_mask[r_mask == 2.] = 1.
r_mask = cv.dilate(r_mask, np.ones((3,3)).astype(bool).astype(int), iterations = 1)
r_mask = cv.morphologyEx(r_mask, cv.MORPH_CLOSE, np.ones((3,3)).astype(bool).astype(int))
r_mask = cv.dilate(r_mask, np.ones((3,3)).astype(bool).astype(int), iterations = 1)

debug()

center = com(r_mask)
x_center = int(center[0] + 0.5)
y_center = int(center[1] + 0.5)
dim = crop.shape[0]
threshold_percent_1 = 1.0
threshold_percent_2 = 0.94
threshold_percent_3 = 0.88

total = float(len(np.where(r_mask == 1)[0]))
rad = 2.0
y, x = np.ogrid[-x_center:dim - x_center, -y_center:dim - y_center]
mask_in = None
mask_out = None

while True:
	temp_in = x**2 + y**2 <= rad**2
	if len(np.where(r_mask * temp_in == 1)[0]) / total >= threshold_percent_1:
		mask_in = temp_in
		break
	rad += 1.0

##### adjusts horizontal axis of ellipse
a = b = rad

while True:
	temp_in = x**2/a**2 + y**2/b**2 <= 1
	if len(np.where(r_mask * temp_in == 1)[0]) / total < threshold_percent_2:
		mask_in = temp_in
		break
	a -= 1.0

##### adjusts vertical axis of ellipse
while True:
	temp_in = x**2/a**2 + y**2/b**2 <= 1
	temp_out = x**2/a**2 + y**2/b**2 > 1
	if len(np.where(r_mask * temp_in == 1)[0]) / total < threshold_percent_3:
		mask_in = temp_in
		mask_out = temp_out
		break
	b -= 1.0

##### creates elliptical binary mask
e_mask = r_mask * mask_in

masked = crop * e_mask
masked[mask_out] = -10000000

##### contour mask

contours = np.array(measure.find_contours(e_mask, 0.5))

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

second_max_area = 0.0
second_max_index = 0.0

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

contour1 = np.array([contours[max_index]])
contour2 = np.array([contours[second_max_index]])

x_dim = e_mask.shape[0]
y_dim = e_mask.shape[1]

x, y = np.meshgrid(np.arange(x_dim), np.arange(y_dim))
x, y = x.flatten(), y.flatten()

points = np.vstack((x,y)).T

vertices1 = contour1[0]
vertices2 = contour2[0]

path1 = Path(vertices1)
path2 = Path(vertices2)

c_mask1 = path1.contains_points(points)
c_mask1 = np.rot90(np.flip(c_mask1.reshape((y_dim,x_dim)), 1))

c_mask2 = path2.contains_points(points)
c_mask2 = np.rot90(np.flip(c_mask2.reshape((y_dim,x_dim)), 1))

c_mask = c_mask1.astype(float) + c_mask2.astype(float)
c_mask[c_mask == 2.] = 1.

c_mask = cv.morphologyEx(c_mask, cv.MORPH_CLOSE, np.ones((3,3)).astype(bool).astype(int))

debug()
