from IPython.core import debugger ; debug = debugger.Pdb().set_trace
from matplotlib.path import Path
from skimage import measure
import matplotlib.pyplot as plt
import numpy as np

e = np.load("E00010AIA304.npy")
r = np.load("R00010AIA304.npy")
test = np.load("test.npy")

img = r

contours = np.array(measure.find_contours(img, 0.5))

L = len(contours)
max_area = 0.0
max_index = None

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

x_dim = img.shape[0]
y_dim = img.shape[1]

x, y = np.meshgrid(np.arange(x_dim), np.arange(y_dim))
x, y = x.flatten(), y.flatten()

points = np.vstack((x,y)).T

vertices = contour[0]
path = Path(vertices)
mask = path.contains_points(points)
mask = np.rot90(np.flip(mask.reshape((y_dim,x_dim)), 1))

##### show mask outline
# for n, c in enumerate(contour):
# 	plt.plot(c[:, 1], c[:, 0], linewidth = 1, color = "white")

plt.imshow(img * mask, cmap = "sdoaia304", origin = "lower")
plt.clim(0,1500)

plt.title("Contour Test")
plt.show()