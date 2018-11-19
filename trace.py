from IPython.core import debugger; debug = debugger.Pdb().set_trace
from skimage.morphology import binary_dilation as dilate
import matplotlib.pyplot as plt
import numpy as np

# x+ : down
# y+ : right

img = np.array([[1,1,0,0,0,0,0,0,0,0],
				[0,1,1,9,0,0,0,0,0,0],
				[0,3,4,4,0,0,0,0,0,0],
				[0,40,1,2,0,0,0,0,0,0],
				[0,0,0,0,1,0,0,0,0,0],
				[0,0,0,0,0,1,0,0,0,0],
				[0,0,0,0,0,0,1,0,0,0],
				[0,0,0,0,0,0,0,1,0,0],
				[0,0,0,0,0,0,0,0,1,0],
				[0,0,0,0,0,0,0,0,0,1]]).astype(float)

img = np.zeros((500,500)).astype(float)
img[247,252] = 1.

xi = 249
yi = 249
r = 3

mask = np.zeros(img.shape)
mask[xi,yi] = 1

def weightvector(fov):
	xcm = 0
	ycm = 0

	M = 0

	for y in range(len(fov)):
		for x in range(len(fov[0])):
			if (x-r) != 0 and (y-r) != 0:
				xcm += (x-r) * fov[y,x]
				ycm += (y-r) * fov[y,x]
				M += fov[y,x]

	xcm /= M
	ycm /= M

	xcm = np.round(xcm)
	ycm = np.round(ycm)

	return (xcm, ycm)

def vectorarray(vector, img):
	dim = max(np.abs(vector[0]), np.abs(vector[1])) * 3
	k, h = np.ogrid[-dim:dim, -dim:dim]
	m = vector[1]/vector[0]
	ar = (m*h == k)
	ar = dilate(ar, np.ones((3,3)))
	return ar

def move(vector, varray, img, mask):
	cast = np.zeros(img.shape)
	if vector[1]>0 and vector[0]>0:
		# attach upper-left corner of varray to the vector tail
		cast[xi:xi+varray.shape[0], yi:yi+varray.shape[1]] = varray
		plt.imshow(cast,cmap="gray");plt.show()
	elif vector[1]<0 and vector[0]>0:
		# attach lower-left corner of varray to the vector tail
		cast[xi-varray.shape[0]:xi, yi:yi+varray.shape[1]] = varray
		plt.imshow(cast,cmap="gray");plt.show()
	elif vector[1]<0 and vector[0]<0:
		# attach lower-right corner of varray to the vector tail
		pass
	elif vector[1]>0 and vector[0]<0:
		# attach upper-right corner of varray to the vector tail
		pass
	mask += cast
	mask[mask>1] = 1
	return mask

fov = img[xi-r : xi+r+1, yi-r : yi+r+1]
print fov

vector = weightvector(fov)

varray = vectorarray(vector, img)

mask = move(vector, varray, img, mask)
