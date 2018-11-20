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
img[247,244] = 1.
img[249,246] = 1.

xi = 249
yi = 249
r = 3

EXP_MULT = 3

def weightvector(fov):
	xcm = 0
	ycm = 0

	M = 0

	for y in range(len(fov)):
		for x in range(len(fov[0])):
			if not ((x-r) == 0 and (y-r) == 0):
				xcm += (x-r) * fov[y,x]
				ycm += (y-r) * fov[y,x]
				M += fov[y,x]

	xcm /= M
	ycm /= M

	xcm = np.round(xcm)
	ycm = np.round(ycm)

	return (xcm, ycm)

def vectorarray(vector, img):
	dim = max(np.abs(vector[0]), np.abs(vector[1])) * EXP_MULT
	_y, _x = np.ogrid[-dim:dim+1, -dim:dim+1]

	if vector[0] != 0:
		m = vector[1]/vector[0]
		ar = (m*_x==_y)
	else:
		ar = (_x==vector[0])

	ar = dilate(ar, np.ones((3,3)))

	_x = vector[0]
	_y = vector[1]

	#align vector array
	border = np.argwhere(ar)
	tl = border.min(axis=0)
	br = border.max(axis=0)
	ar = ar[tl[0]:br[0]+1, tl[1]:br[1]+1]
	return ar

def move(vector, varray, img, mask):
	cast = np.zeros(img.shape)
	_x = vector[0]
	_y = vector[1]

	if _y>0 and _x>0: # down right
		cast[yi-1:yi+varray.shape[0]-1, xi-1:xi+varray.shape[1]-1] = varray

	elif _y<0 and _x>0: # up right
		cast[yi-varray.shape[0]+1:yi+1, xi-1:xi+varray.shape[1]-1] = varray

	elif _y<0 and _x<0: # up left
		cast[yi-varray.shape[0]+1:yi+1, xi-varray.shape[1]+1:xi+1] = varray

	elif _y>0 and _x<0: # down left
		cast[yi-1:yi+varray.shape[0]-1, xi-varray.shape[1]+1:xi+1] = varray

	elif _y<0 and _x==0: # up
		cast[int(yi-EXP_MULT*np.abs(_y)):yi+1, xi] = 1.
		cast = dilate(cast, np.ones((3,3)))

	elif _y>0 and _x==0: # down
		cast[yi:int(yi+EXP_MULT*np.abs(_y))+1, xi] = 1.
		cast = dilate(cast, np.ones((3,3)))

	elif _y==0 and _x>0: # right
		cast[yi, xi:int(xi+EXP_MULT*np.abs(_x)+1)] = 1.
		cast = dilate(cast, np.ones((3,3)))

	elif _y==0 and _x<0: # left
		cast[yi, int(xi-EXP_MULT*np.abs(_x)):xi+1] = 1.
		cast = dilate(cast, np.ones((3,3)))

	mask += cast
	mask[mask>1] = 1
	return mask

space = np.zeros(img.shape)
fov = img[yi-r:yi+r+1, xi-r:xi+r+1]

vector = weightvector(fov)
varray = vectorarray(vector, img)
space = move(vector, varray, img, space)

_x = vector[0]
_y = vector[1]

# make fov in the direction of the previous movement vector

debug()
