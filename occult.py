import numpy as np
from astropy.convolution import convolve, Box2DKernel
from copy import copy

"""
Default values are for SDO-AIA images.
rmin, qthresh1, and qthresh2 default values are unknown.
"""
def trace(image1, nsm1=3, rmin=10, lmin=25, nstruc=1000, nloopw=100, ngap=3, qthresh1=1, qthresh2=1):
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
	s0_loop = step * (np.arange(nlen) - nlen / 2)
	wid = (nsm2 / 2 - 1) > 1
	looplen = 0.0

	# Base level
	ind_pos = np.where(image1 > 0)
	zmed = np.median(image1[ind_pos])
	thresh = zmed * qthresh1
	image1[image1 < (thresh)] = thresh

	# Highpass filter
	if nsm1 <= 2:
		image2 = image1 - convolve(image1, Box2DKernel(nsm2))
	elif nsm1 >= 3:
		image2 = convolve(image1, Box2DKernel(nsm1)) - convolve(image1, Box2DKernel(nsm2))

	dim = image1.shape
	nx = dim[1]
	ny = dim[0]

	# Erase boundaries zones (smoothing effects)
	image2[int(nsm2):-int(nsm2), int(nsm2):-int(nsm2)] = 0.0

	# Noise threshold
	ind_pos = np.where(image2 > 0)
	zmed = np.median(image2[ind_pos])
	thresh = zmed * qthresh2

	# Loop traching start at maximum flux position
	iloop = 0
	residual = copy(image2)
	residual[residual < 0] = 0.0
	iloop_nstruc = np.zeros(nstruc)
	loop_len = np.zeros(nloopmax)

	for istruc in range(nstruc):
		zstart = [np.max(residual), int(str(np.unravel_index(np.argmax(residual, axis=None), residual.shape)[1]) + str(np.unravel_index(np.argmax(residual, axis=None), residual.shape)[0]))]
		if zstart[0] <= thresh:
			end_trace(image1, wid, nsm2, nlen, na, nb, loop_len, nloop)
		
		if istruc % 100 == 0:
			ipix = np.where(residual > 0)
			qpix = float(len(ipix)) / float(nx) * float(ny)
			flux_sigma = zstart[0] / zmed
			print "Struct#%04d Loop#%04d Signal/noise=%.3f" % (istruc, iloop, flux_sigma)
		
		jstart = int(zstart[1] / nx)
		istart = int(zstart[1] % nx)

		# Tracing loop structure stepwise
		ip = 0
		ndir = 2
		for idir in range(ndir):
			xl = np.zeros(npmax+1)
			yl = np.zeros(npmax+1)
			zl = np.zeros(npmax+1)
			al = np.zeros(npmax+1)
			ir = np.zeros(npmax+1)

			if idir == 0:
				sign_dir = 1
			elif idir == 1:
				sign_dir = -1

			# Initial direction finding
			xl[0] = istart
			yl[0] = jstart
			zl[0] = zstart[0]
			alpha = np.pi * np.arange(na) / float(na)
			flux_max = 0.0

			for ia in range(na):
				x_ = xl[0] + s0_loop * np.cos(alpha[ia])
				y_ = yl[0] + s0_loop * np.sin(alpha[ia])
				ix = (x_ + 0.5).astype(int)
				iy = (y_ + 0.5).astype(int)
				flux_ = residual[(iy,ix)]
				flux = np.sum(flux_[np.where(flux_ > 0.0)]) / float(nlen)

				if flux > flux_max:
					flux_max = flux
					al[0] = alpha[ia]
					x_lin = x_
					y_lin = y_

	# Curvature radius
	xx_curv = np.zeros((nlen, nb, npmax))
	yy_curv = np.zeros((nlen, nb, npmax))

	for ip in range(npmax):
		if ip == 0:
			ib1 = 0
			ib2 = nb - 1

		if ip >= 1:
			ib1 = (ir[ip] - 1) > 0
			ib2 = (ir[ip] + 1) < (nb - 1)

		beta0 = al[ip] + np.pi / 2.0
		xcen = xl[ip] + rmin * np.cos(beta0)
		ycen = yl[ip] + rmin * np.sin(beta0)
		flux_max = 0.0

	for ib in range(ib1, ib2 + 1):
		pass [...] # continue here

def end_trace(image1, wid, nsm2, nlen, na, nb, loop_len, nloop):
	fluxmin = np.min(image1)
	fluxmax = np.max(image1)
	output = np.array[wid, fluxmin, fluxmax, nsm2, nlen, na, nb]

	#Select longest loops

# trace(np.load("image.npy"))
