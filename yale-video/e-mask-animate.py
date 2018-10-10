from copy import copy
from IPython.core import debugger; debug = debugger.Pdb().set_trace
from recorder import Recorder
from scipy.ndimage.measurements import center_of_mass as com
import matplotlib.pyplot as plt
import numpy as np

RECORDER = Recorder()
RECORDER.display_start_time("e-mask-animate")

IMG = np.load("R00010AIA304.npy")
r_mask = copy(IMG)
r_mask[r_mask <= 450] = 0
r_mask[r_mask > 450] = 1

##### initial setup for elliptical mask fit
RECORDER.info_text("Preparing for elliptical mask fit...")

center = com(r_mask)
x_center = int(center[0] + 0.5)
y_center = int(center[1] + 0.5)
dim = IMG.shape[0]
threshold_percent_1 = 1.0
threshold_percent_2 = 0.97
threshold_percent_3 = 0.94

total = float(len(np.where(r_mask == 1)[0]))
rad = 2.0
y, x = np.ogrid[-x_center:dim - x_center, -y_center:dim - y_center]
mask_in = None
mask_out = None

COUNT = 1

##### fits circle to 100% of the data
RECORDER.info_text("Fitting elliptical mask to binary AIA304 data...")

while True:
	temp_in = x**2 + y**2 <= rad**2
	temp_out = x**2 + y**2 > rad**2

	ar = (temp_in * IMG).astype(float)
	ar[temp_out] = np.nan

	# np.save("test/%05d" % COUNT, temp_in * IMG)
	plt.imshow(ar, cmap = "sdoaia304", origin = "lower")
	plt.savefig("test/%05d" % COUNT)
	plt.close()
	RECORDER.info_text("IMAGE %05d" % COUNT)
	COUNT += 1
	if len(np.where(r_mask * temp_in == 1)[0]) / total >= threshold_percent_1:
		mask_in = temp_in
		break
	rad += 1.0

##### adjusts horizontal axis of ellipse to fit 95% of the data
RECORDER.info_text("Adjusting horizontal axis...")

a = b = rad

while True:
	temp_in = x**2/a**2 + y**2/b**2 <= 1
	temp_out = x**2/a**2 + y**2/b**2 > 1

	ar = (temp_in * IMG).astype(float)
	ar[temp_out] = np.nan

	# np.save("test/%05d" % COUNT, temp_in * IMG)
	plt.imshow(ar, cmap = "sdoaia304", origin = "lower")
	plt.savefig("test/%05d" % COUNT)
	plt.close()
	RECORDER.info_text("IMAGE %05d" % COUNT)
	COUNT += 1
	if len(np.where(r_mask * temp_in == 1)[0]) / total < threshold_percent_2:
		mask_in = temp_in
		break
	a -= 1.0

##### adjusts vertical axis of ellipse to fit 90% of the data
RECORDER.info_text("Adjusting vertical axis...")

while True:
	temp_in = x**2/a**2 + y**2/b**2 <= 1
	temp_out = x**2/a**2 + y**2/b**2 > 1

	ar = (temp_in * IMG).astype(float)
	ar[temp_out] = np.nan

	# np.save("test/%05d" % COUNT, temp_in * IMG)
	plt.imshow(ar, cmap = "sdoaia304", origin = "lower")
	plt.savefig("test/%05d" % COUNT)
	plt.close()
	RECORDER.info_text("IMAGE %05d" % COUNT)
	COUNT += 1
	if len(np.where(r_mask * temp_in == 1)[0]) / total < threshold_percent_3:
		mask_in = temp_in
		mask_out = temp_out
		break
	b -= 1.0

RECORDER.display_end_time("e-mask-animate")
