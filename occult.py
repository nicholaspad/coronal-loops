import numpy as np
from astropy.convolution import convolve, Box2DKernel
from copy import copy

"""
Default values are for SDO-AIA images.
rmin, qthresh1, and qthresh2 default values are unknown.
"""
def trace(image1, nsm1=3.0, rmin=10.0, lmin=25.0, nstruc=1000, nloopw=100.0, ngap=3.0, qthresh1=1, qthresh2=1):
	# Control parameters
	nloop = nloopw
	reso = 1
	step = 1
	nloopmax = 10000
	npmax = 2000
	nsm2 = nsm1 + 1
	nlen = float(rmin)
	na = 180
	nb = 30
	s_loop = step * np.arange(nlen)
	s0_loop = step * (np.arange(nlen) - nlen/2)
	wid = (nsm2/2 - 1) > 1
	looplen = 0.0

	# Base level
	ind_pos = np.where(image1 > 0)
	zmed = np.median(image1[ind_pos])
	thresh = zmed * qthresh1
	image1[image1 < (thresh)] = thresh

	#Highpass filter
	if nsm1 <= 2:
		image2 = image1 - convolve(image1, Box2DKernel(nsm2))
	elif nsm1 >= 3:
		image2 = convolve(image1, Box2DKernel(nsm1)) - convolve(image1, Box2DKernel(nsm2))

	dim = image1.shape
	nx = dim[1]
	ny = dim[0]

	#Erase boundaries zones (smoothing effects)
	image2[nsm2:-nsm2, nsm2:-nsm2] = 0.0

	#Noise threshold
	ind_pos = np.where(image2 > 0)
	zmed = np.median(image2[ind_pos])
	thresh = zmed * qthresh2

	#Loop traching start at maximum flux position
	iloop = 0
	residual = copy(image2)
	residual[residual < 0] = 0.0
	iloop_nstruc = np.zeros((nstruc, nstruc))
	loop_len = np.zeros((nloopmax, nloopmax))

	for istruc in range(nstruc):
		zstart = [np.max(residual), int(str(np.unravel_index(np.argmax(residual, axis=None), residual.shape)[1]) + str(np.unravel_index(np.argmax(residual, axis=None), residual.shape)[0]))]
		if zstart[0] <= thresh:
			end_trace(image1, wid, nsm2, nlen, na, nb, loop_len, nloop)
		
		if istruc % 100 == 0:
			ipix = np.where(residual > 0)
			qpix = float(len(ipix)) / float(nx) * float(ny)
			flux_sigma = zstart[0] / zmed
			print "Struct#{} Loop#{} Signal/noise={}".format(istruc, iloop, flux_sigma)
		
		jstart = float(zstart[1] / nx)
		istart = float(zstart[1] % nx)

		#Tracing loop structure stepwise
		ip = 0
		ndir = 2
		for idir in range(ndir):
			xl = np.zeros((npmax+1, npmax+1))
			yl = np.zeros((npmax+1, npmax+1))
			zl = np.zeros((npmax+1, npmax+1))
			al = np.zeros((npmax+1, npmax+1))
			ir = np.zeros((npmax+1, npmax+1))

			if idir == 0:
				sign_dir = 1
			elif idir == 1:
				sign_dir = -1

			#Initial direction finding
			[...]

def end_trace(image1, wid, nsm2, nlen, na, nb, loop_len, nloop):
	fluxmin = np.min(image1)
	fluxmax = np.max(image1)
	output = np.array[wid, fluxmin, fluxmax, nsm2, nlen, na, nb]

	#Select longest loops

trace(np.load("image.npy"))
