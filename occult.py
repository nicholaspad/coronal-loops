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
	image1[image1 < thresh] = thresh

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
			quit()
		
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
					rad_i = rmin / (-1.0 + 2.0 * float(ib) / float(nb - 1))
					xcen_i = xl[ip] + (xcen - xl[ip]) * (rad_i / rmin)
					ycen_i = yl[ip] + (ycen - yl[ip]) * (rad_i / rmin)
					beta_i = beta0 + sign_dir * s_loop / rad_i
					x_ = xcen_i - rad_i * np.cos(beta_i)
					y_ = ycen_i - rad_i * np.sin(beta_i)
					ix = (x_ + 0.5).astype(int)
					iy = (y_ + 0.5).astype(int)
					flux_ = copy(residual)
					flux_[flux_ < 0] = 0.0
					flux = np.sum(flux_) / float(nlen)

					if idir == 1:
						xx_curv[ib, :, ip] = x_
						yy_curv[ib, :, ip] = y_

					if flux > flux_max:
						flux_max = flux
						al[ip + 1] = al[ip] + sign_dir * (step / rad_i)
						ir[ip + 1] = ib
						al_mid = (al[ip] + al[ip + 1]) / 2.0
						xl[ip + 1] = xl[ip] + step * np.cos(al_mid + np.pi * idir)
						yl[ip + 1] = yl[ip] + step * np.cos(al_mid + np.pi * idir)
						ix_ip = (int(xl[ip + 1] + 0.5) > 0) < (nx - 1)
						iy_ip = (int(yl[ip + 1] + 0.5) > 0) < (ny - 1)
						zl[ip + 1] = residual[iy_ip][ix_ip]

						if ip == 0:
							x_curv = x_
							y_curv = y_

				iz1 = (np + 1 - ngap) > 0

				if np.max(zl[iz1:ip+2]) <= 0:
					ip = (izl - 1) > 0
					break

			# Re-ordering loop coordinates
			if idir == 0:
				xloop = np.flip(xl[0:ip+1])
				yloop = np.flip(yl[0:ip+1])
				zloop = np.flip(zl[0:ip+1])

			if idir == 1 and ip >= 1:
				xloop = np.array([xloop, xl[1:ip+1]])
				yloop = np.array([yloop, yl[1:ip+1]])
				zloop = np.array([zloop, zl[1:ip+1]])

		ind = np.where(np.logical_and(xloop != 0, yloop != 0))
		nind = len(ind)
		looplen = 0

		if nind <= 1:
			# SKIP_STRUCT
			# Store loop coordinates
			if looplen >= lmin:
				nn = int(ns / reso + 0.5)
				ii = np.arange(nn) * reso
				## interpol
		else:
			xloop = xloop[ind]
			yloop = yloop[ind]
			zloop = zloop[ind]

			if iloop >= nloopmax:
				end_trace(image1, wid, nsm2, nlen, na, nb, loop_len, nloop)
				quit()

			# Loop completed - loop length
			np = len(xloop)
			s = np.zeros(np)
			looplen = 0

			if np >= 2:
				for ip in range(1, np):
					s[ip] = s[ip-1] + np.sqrt(np.power(xloop[ip] - xloop[ip-1], 2) + np.power(yloop[ip] - yloop[ip-1], 2))

			looplen = s[np-1]
			ns = int(looplen) > 3
			ss = np.arange(ns)

# END_TRACE
def end_trace(image1, wid, nsm2, nlen, na, nb, loop_len, nloop):
	fluxmin = np.min(image1)
	fluxmax = np.max(image1)
	output = np.array[wid, fluxmin, fluxmax, nsm2, nlen, na, nb]

	#Select longest loops

# trace(np.load("image.npy"))
