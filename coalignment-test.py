from IPython.core import debugger ; debug = debugger.Pdb().set_trace
from scipy.ndimage import zoom as interpolate
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
x_center = int(aia.reference_pixel.x.value + 0.5) - 12
y_center = int(aia.reference_pixel.y.value + 0.5) + 4

casted_hmi_data[(y_center - 1 - y_size/2) : (y_center + y_size/2), (x_center - 1 - x_size/2) : (x_center + x_size/2)] = interpolated_hmi_data

cd_data = aia_data[1937:2479, 2008:2680]
binary_data = np.logical_and(cd_data < np.inf, cd_data > 50)
binary_data = grow_mask(binary_data, iterations = 2)

plt.subplot(1,3,1)
plt.imshow(cd_data, cmap = "sdoaia304", origin = "lower")
plt.clim(0,400)

plt.subplot(1,3,2)
plt.imshow(binary_data, cmap = "gray", origin = "lower")

plt.subplot(1,3,3)
plt.imshow(cd_data * binary_data, cmap = "sdoaia304", origin = "lower")
plt.clim(0,400)
plt.show()

# plt.imshow(aia_data, cmap = "sdoaia304", origin = "lower")
# plt.clim(0,750)
# plt.imshow(casted_hmi_data, cmap = "gray", vmin = -120, vmax = 120, origin = "lower", alpha = 0.25)
# plt.show()
