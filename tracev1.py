from copy import copy
from IPython.core import debugger; debug = debugger.Pdb().set_trace
from skimage.morphology import binary_dilation as dilate
import matplotlib.pyplot as plt
import numpy as np

# x+ : right
# y+ : down

img = np.zeros((500,500)).astype(float)
img[249,249] = 1.
img[246,251] = 1.
img[244,254] = 1.
img[241,256] = 1.
img[241,259] = 1.
img[243,262] = 1.
img[245,263] = 1.
img[247,263] = 1.
img[249,261] = 1.

xi = 249
yi = 249

ticker = 0
h = 249
k = 249

# for i in range(60):
# 	h += np.random.randint(2,5)
# 	k += np.random.randint(2,4)
# 	img[h,k] = 1.
# 	ticker += 1

plt.imsave("/Users/lockheedmartin/Desktop/img", img, cmap = "gray")

EXP_MULT = 1
fov_rad = 3

def weightvector(fov,dir=None):
	xcm = 0
	ycm = 0
	M = 0

	# FIX DIRECTIONS
	# IF NOT STATEMENTS WRONG???
	# FILL IN OTHER FOUR DIRECTIONS

	if dir is None:
		for y in range(len(fov)):
			for x in range(len(fov[0])):
				if not ((x-fov_rad)==0 and (y-fov_rad)==0):
					xcm += (x-fov_rad)*fov[y, x]
					ycm += (y-fov_rad)*fov[y, x]
					M += fov[y, x]

	elif dir=="up":
		for y in range(len(fov)):
			for x in range(len(fov[0])):
				if not ((x-fov_rad)==0 and (y-fov_rad)==0):
					xcm += (x-fov_rad)*fov[y, x]
					ycm += (y-fov_rad)*fov[y, x]
					M += fov[y, x]

	elif dir=="down":
		for y in range(len(fov)):
			for x in range(len(fov[0])):
				if not ((x-fov_rad)==0 and y==0):
					xcm += (x-fov_rad)*fov[y, x]
					ycm += y*fov[y, x]
					M += fov[y, x]

	elif dir=="left":
		for y in range(len(fov)):
			for x in range(len(fov[0])):
				if not ((x-fov_rad)==0 and (y-fov_rad)==0):
					xcm += (x-fov_rad)*fov[y, x]
					ycm += (y-fov_rad)*fov[y, x]
					M += fov[y, x]

	elif dir=="right":
		for y in range(len(fov)):
			for x in range(len(fov[0])):
				if not (x==0 and (y-fov_rad)==0):
					xcm += x*fov[y, x]
					ycm += (y-fov_rad)*fov[y, x]
					M += fov[y, x]

	xcm /= M
	ycm /= M

	if np.isnan(xcm) or np.isnan(ycm):
		return "continue"

	# div = min(np.abs(xcm), np.abs(ycm))
	# xcm /= div
	# ycm /= div

	xcm = np.round(xcm)
	ycm = np.round(ycm)

	return (xcm, ycm)

def vectorarray(vector, img):
	dim = max(np.abs(vector[0]), np.abs(vector[1]))*EXP_MULT
	_y, _x = np.ogrid[-dim:dim+1, -dim:dim+1]

	if vector[0] != 0:
		m = vector[1]/vector[0]
		ar = (m*_x==_y)
	else:
		ar = (_x==vector[0])

	ar = dilate(ar, np.ones((3,3)))

	_x = vector[0]
	_y = vector[1]

	# align vector array
	border = np.argwhere(ar)
	tl = border.min(axis=0)
	br = border.max(axis=0)
	ar = ar[tl[0]:br[0]+1, tl[1]:br[1]+1]

	return ar

def move(vector, varray, img, mask, xi, yi):
	cast = np.zeros(img.shape)
	_mask = copy(mask)
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

	_mask += cast
	_mask[_mask>1] = 1

	return _mask

def getnewdir(_x, _y):
	if _x != 0:
		m = _y/_x

		if _x<0:
			if m<=-1:
				_dir = "left"
			elif m>-1 and m<1:
				_dir = "left"
			elif m>=1:
				_dir = "left"

		elif _x>0:
			if m<=-1:
				_dir = "right"
			elif m>-1 and m<1:
				_dir = "right"
			elif m>=1:
				_dir = "right"
	else:
		if _y>0:
			_dir = "down"

		elif _y<0:
			_dir = "up"

	return _dir

def getnewfov(img, dir, xi, yi):
	if dir=="up":
		_fov = img[yi-fov_rad:yi+1, xi-fov_rad:xi+fov_rad+1]

	elif dir=="down":
		_fov = img[yi:yi+fov_rad+1, xi-fov_rad:xi+fov_rad+1]

	elif dir=="left":
		_fov = img[yi-fov_rad:yi+fov_rad+1, xi-fov_rad:xi+1]

	elif dir=="right":
		_fov = img[yi-fov_rad:yi+fov_rad+1, xi:xi+fov_rad+1]

	return _fov

# initial step
space = np.zeros(img.shape)
fov = img[yi-fov_rad:yi+fov_rad+1, xi-fov_rad:xi+fov_rad+1]

vector = weightvector(fov)
varray = vectorarray(vector, img)
space = move(vector, varray, img, space, xi, yi)

for i in range(7):
	_x = vector[0]
	_y = vector[1]
	print i, _x, _y
	dir = getnewdir(_x, _y)

	xi = int(xi + _x*EXP_MULT + 0.5)
	yi = int(yi + _y*EXP_MULT + 0.5)
	fov = getnewfov(img, dir, xi, yi)

	vector = weightvector(fov, dir)
	# if isinstance(vector, str):
	# 	print fov
	# 	vector = (_x, _y)

	varray = vectorarray(vector, img)
	space = move(vector, varray, img, space, xi, yi)	

plt.imsave("/Users/lockheedmartin/Desktop/space", space, cmap = "gray")
