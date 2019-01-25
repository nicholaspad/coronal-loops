import numpy as np
import scipy
import scipy.ndimage as ndimage
import scipy.ndimage.filters as filters
import matplotlib.pyplot as plt
import sunpy.cm as cm
from IPython.core import debugger; debug = debugger.Pdb().set_trace

neighborhood_size = 45
threshold = 4.5

data = np.load("t.npy")

data_max = filters.maximum_filter(data, neighborhood_size)
maxima = (data == data_max)
data_min = filters.minimum_filter(data, neighborhood_size)
diff = ((data_max - data_min) > threshold)
maxima[diff == 0] = 0

labeled, num_objects = ndimage.label(maxima)
slices = ndimage.find_objects(labeled)
x, y = [], []
for dy,dx in slices:
    x_center = (dx.start + dx.stop - 1)/2
    x.append(x_center)
    y_center = (dy.start + dy.stop - 1)/2    
    y.append(y_center)

data[np.isnan(data)] = 0

plt.imshow(data, cmap = "sdoaia304", origin = "lower", vmin = 0, vmax = 7.4)
# plt.savefig('data.png', cmap = "gist_ncar", bbox_inches = 'tight')

plt.autoscale(False)
plt.plot(x,y, 'g+')
plt.savefig('resultaia1.png', bbox_inches = 'tight', dpi = 300)