from IPython.core import debugger ; debug = debugger.Pdb().set_trace
from scipy.ndimage import zoom as interpolate
from scipy.ndimage.measurements import center_of_mass as com
from scipy.ndimage.morphology import binary_dilation as grow_mask
import matplotlib.pyplot as plt
import numpy as np
import sunpy.map as smap

hmi = smap.Map("resources/hmi-fits-files/hmi.M_720s.20170608_000000_TAI.3.magnetogram.fits")
aia = smap.Map("resources/aia-fits-files/aia.lev1_euv_12s.2017-06-08T000007Z.304.image_lev1.fits")

hmi_data = hmi.data
aia_data = aia.data

casted_hmi_data = np.zeros((4096, 4096))
casted_hmi_data[casted_hmi_data == 0] = 10000
scale = (hmi.scale[0]/aia.scale[0]).value
scale = float("%.3f" % scale)

interpolated_hmi_data = interpolate(hmi_data, scale, order = 1)
interpolated_hmi_data = np.flip(interpolated_hmi_data, (0,1))

x_size = interpolated_hmi_data.shape[0]
y_size = interpolated_hmi_data.shape[1]
x_center = int(aia.reference_pixel.x.value + 0.5) - 9
y_center = int(aia.reference_pixel.y.value + 0.5) + 4

casted_hmi_data[(y_center - 1 - y_size/2) : (y_center + y_size/2), (x_center - 1 - x_size/2) : (x_center + x_size/2)] = interpolated_hmi_data

cd_data = aia_data[1872:2544, 2008:2680]
binary_data = np.logical_and(cd_data < np.inf, cd_data > 40)
binary_data = grow_mask(binary_data, iterations = 1)
binary_data = binary_data.astype(int)

center = com(binary_data)
x_center = int(center[0] + 0.5)
y_center = int(center[1] + 0.5)
binary_data[x_center, y_center] = 2
dim = cd_data.shape[0]
threshold_percent = 0.98
total = float(len(np.where(binary_data == 1)[0]))
rad = 2.0
y, x = np.ogrid[-x_center:dim - x_center, -y_center:dim - y_center]
mask_in = None

while True:
	temp_in = x**2 + y**2 <= rad**2
	if len(np.where(binary_data * temp_in == 1)[0]) / total >= threshold_percent:
		mask_in = temp_in
		break
	rad += 1.0

a = b = rad
threshold_percent = 0.95

while True:
	temp_in = x**2/a**2 + y**2/b**2 <= 1
	if len(np.where(binary_data * temp_in == 1)[0]) / total < threshold_percent:
		mask_in = temp_in
		break
	a -= 1.0

threshold_percent = 0.92
mask_out = None

while True:
	temp_in = x**2/a**2 + y**2/b**2 <= 1
	temp_out = x**2/a**2 + y**2/b**2 > 1
	if len(np.where(binary_data * temp_in == 1)[0]) / total < threshold_percent:
		mask_in = temp_in
		mask_out = temp_out
		break
	b -= 1.0

masked_aia_cd_data = cd_data * mask_in
masked_aia_cd_data[mask_out] = 0

masked_binary_data = binary_data * mask_in
combined_aia = masked_aia_cd_data * masked_binary_data
combined_aia[mask_out] = 10000

hmi_cd_data = casted_hmi_data[1872:2544, 2008:2680]
masked_hmi_cd_data = hmi_cd_data * mask_in
combined_hmi = masked_hmi_cd_data * masked_binary_data
combined_hmi[mask_out] = -1

masked_binary_data[mask_out] = -1

plt.subplot(2,4,1)
plt.imshow(cd_data, cmap = "sdoaia304", origin = "lower")
plt.clim(0,350)

plt.subplot(2,4,2)
plt.imshow(masked_aia_cd_data, cmap = "sdoaia304", origin = "lower")
plt.clim(0,350)

plt.subplot(2,4,3)
plt.imshow(binary_data, cmap = "gray", origin = "lower")

plt.subplot(2,4,4)
plt.imshow(masked_binary_data, cmap = "gray", origin = "lower")

plt.subplot(2,4,5)
plt.imshow(hmi_cd_data, cmap = "gray", vmin = -120, vmax = 120, origin = "lower")

plt.subplot(2,4,6)
plt.imshow(masked_hmi_cd_data, cmap = "gray", vmin = -120, vmax = 120, origin = "lower")

plt.subplot(2,4,7)
plt.imshow(combined_hmi, cmap = "gray", vmin = -120, vmax = 120, origin = "lower")

plt.subplot(2,4,8)
plt.imshow(combined_aia, cmap = "sdoaia304", origin = "lower")
plt.clim(0,350)

plt.show()

# plt.subplot(1,3,3)
# plt.imshow(cd_data * binary_data, cmap = "sdoaia304", origin = "lower")
# plt.clim(0,400)
# plt.show()

# plt.imshow(aia_data, cmap = "sdoaia304", origin = "lower")
# plt.clim(0,350)
# plt.imshow(casted_hmi_data, cmap = "gray", vmin = -120, vmax = 120, origin = "lower", alpha = 0.25)
# plt.show()
