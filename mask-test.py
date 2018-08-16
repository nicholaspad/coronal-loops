import warnings
warnings.filterwarnings("ignore", message = "numpy.dtype size changed")

import copy
import numpy as np

a = np.array([[False, False, False, False],
			  [False, True, False, False],
			  [False, False, False, False],
			  [False, False, True, True]])

temp = copy.copy(a)

for i in range(len(temp)):

	for j in range(len(temp[0])):

		if temp[i,j]:

			if i == j == 0: # top left corner

				a[i+1,j] = a[i,j+1] = True

			elif i == len(a)-1 and j == 0: # top right corner

				a[i-1,j] = a[i,j+1] = True

			elif i == 0 and j == len(a[0])-1: # bottom left corner:

				a[i+1,j] = a[i,j-1] = True

			elif i == len(a)-1 and j == len(a[0])-1: # bottom right corner

				a[i-1,j] = a[i,j-1] = True

			elif i == 0: # first row, not a corner

				a[i+1,j] = a[i,j-1] = a[i,j+1] = True

			elif j == 0: # first column, not a corner

				a[i+1,j] = a[i-1,j] = a[i,j+1] = True

			elif i == len(a)-1: # last row, not a corner

				a[i-1,j] = a[i,j-1] = a[i,j+1] = True

			elif j == len(a[0])-1: # last column, not a corner

				a[i-1,j] = a[i+1,j] = a[i,j-1] = True

			else: # anywhere else

				a[i-1,j] = a[i+1,j] = a[i,j+1] = a[i,j-1] = True
