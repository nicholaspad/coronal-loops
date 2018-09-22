from IPython.core import debugger ; debug = debugger.Pdb().set_trace
from matplotlib.widgets import Slider
from recorder import Recorder
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np
import argparse
import sys

PRINTER = Recorder()

parser = argparse.ArgumentParser()
parser.add_argument("--id")
args = parser.parse_args()

if args.id == None:
	PRINTER.info_text("Specify region ID with '--id <number>'")
	PRINTER.line()
	sys.exit()

ID = int(args.id)

DATA = []
with open("resources/region-data/database.csv") as f:
	for line in f:
		if line.split(",")[0] == "%05d" % ID:
			DATA = line.split(",")

DATE = DATA[3]
TIME = DATA[4]

HPC_X = float(DATA[5])
HPC_Y = float(DATA[6])

PX_X = int(DATA[7])
PX_Y = int(DATA[8])

plt.figure(figsize = (16, 10))
gs = gridspec.GridSpec(8, 5)
gs.update(wspace = 0, hspace = 0)

plt.gcf().text(0.01, 0.94, "%s %s" % (DATE, TIME), fontsize = 12)
plt.gcf().text(0.01, 0.97, "Region ID %05d" % ID, fontsize = 12)
plt.gcf().text(0.01, 0.91, "Location (%.1f arcsec, %.1f arcsec)" % (HPC_X, HPC_Y), fontsize = 12)
plt.gcf().text(0.01, 0.88, "Size (%d px, %d px)" % (PX_X, PX_Y), fontsize = 12)

# ROW 1

plt.subplot(5, 8, 1)
plt.title("AIA94")
plt.axis("off")
plt.imshow(np.load("resources/region-data/raw-images/%05dAIA94.npy" % ID),
		   cmap = "sdoaia94",
		   origin = "lower")

plt.subplot(5, 8, 2)
plt.title("AIA131")
plt.axis("off")
plt.imshow(np.load("resources/region-data/raw-images/%05dAIA131.npy" % ID),
		   cmap = "sdoaia131",
		   origin = "lower")

plt.subplot(5, 8, 3)
plt.title("AIA171")
plt.axis("off")
plt.imshow(np.load("resources/region-data/raw-images/%05dAIA171.npy" % ID),
		   cmap = "sdoaia171",
		   origin = "lower")

plt.subplot(5, 8, 4)
plt.title("AIA193")
plt.axis("off")
plt.imshow(np.load("resources/region-data/raw-images/%05dAIA193.npy" % ID),
		   cmap = "sdoaia193",
		   origin = "lower")

plt.subplot(5, 8, 5)
plt.title("AIA211")
plt.axis("off")
plt.imshow(np.load("resources/region-data/raw-images/%05dAIA211.npy" % ID),
		   cmap = "sdoaia211",
		   origin = "lower")

plt.subplot(5, 8, 6)
plt.title("AIA304")
plt.axis("off")
plt.imshow(np.load("resources/region-data/raw-images/%05dAIA304.npy" % ID),
		   cmap = "sdoaia304",
		   origin = "lower")

plt.subplot(5, 8, 7)
plt.title("AIA335")
plt.axis("off")
plt.imshow(np.load("resources/region-data/raw-images/%05dAIA335.npy" % ID),
		   cmap = "sdoaia335",
		   origin = "lower")

plt.subplot(5, 8, 8)
plt.title("HMI")
plt.axis("off")
plt.imshow(np.load("resources/region-data/magnetogram-images/%05dHMI6173.npy" % ID),
		   cmap = "gray",
		   vmin = -120,
		   vmax = 120,
		   origin = "lower")

# ROW 2

plt.subplot(5, 8, 9)
plt.axis("off")
plt.imshow(np.load("resources/region-data/raw-images/%05dAIA94.npy" % ID),
		   cmap = "sdoaia94",
		   origin = "lower")
plt.imshow(np.load("resources/region-data/magnetogram-images/%05dHMI6173.npy" % ID),
		   cmap = "gray",
		   alpha = 0.5,
		   vmin = -120,
		   vmax = 120,
		   origin = "lower")

plt.subplot(5, 8, 10)
plt.axis("off")
plt.imshow(np.load("resources/region-data/raw-images/%05dAIA131.npy" % ID),
		   cmap = "sdoaia131",
		   origin = "lower")
plt.imshow(np.load("resources/region-data/magnetogram-images/%05dHMI6173.npy" % ID),
		   cmap = "gray",
		   alpha = 0.5,
		   vmin = -120,
		   vmax = 120,
		   origin = "lower")

plt.subplot(5, 8, 11)
plt.axis("off")
plt.imshow(np.load("resources/region-data/raw-images/%05dAIA171.npy" % ID),
		   cmap = "sdoaia171",
		   origin = "lower")
plt.imshow(np.load("resources/region-data/magnetogram-images/%05dHMI6173.npy" % ID),
		   cmap = "gray",
		   alpha = 0.5,
		   vmin = -120,
		   vmax = 120,
		   origin = "lower")

plt.subplot(5, 8, 12)
plt.axis("off")
plt.imshow(np.load("resources/region-data/raw-images/%05dAIA193.npy" % ID),
		   cmap = "sdoaia193",
		   origin = "lower")
plt.imshow(np.load("resources/region-data/magnetogram-images/%05dHMI6173.npy" % ID),
		   cmap = "gray",
		   alpha = 0.5,
		   vmin = -120,
		   vmax = 120,
		   origin = "lower")

plt.subplot(5, 8, 13)
plt.axis("off")
plt.imshow(np.load("resources/region-data/raw-images/%05dAIA211.npy" % ID),
		   cmap = "sdoaia211",
		   origin = "lower")
plt.imshow(np.load("resources/region-data/magnetogram-images/%05dHMI6173.npy" % ID),
		   cmap = "gray",
		   alpha = 0.5,
		   vmin = -120,
		   vmax = 120,
		   origin = "lower")

plt.subplot(5, 8, 14)
plt.axis("off")
plt.imshow(np.load("resources/region-data/raw-images/%05dAIA304.npy" % ID),
		   cmap = "sdoaia304",
		   origin = "lower")
plt.imshow(np.load("resources/region-data/magnetogram-images/%05dHMI6173.npy" % ID),
		   cmap = "gray",
		   alpha = 0.5,
		   vmin = -120,
		   vmax = 120,
		   origin = "lower")

plt.subplot(5, 8, 15)
plt.axis("off")
plt.imshow(np.load("resources/region-data/raw-images/%05dAIA335.npy" % ID),
		   cmap = "sdoaia335",
		   origin = "lower")
plt.imshow(np.load("resources/region-data/magnetogram-images/%05dHMI6173.npy" % ID),
		   cmap = "gray",
		   alpha = 0.5,
		   vmin = -120,
		   vmax = 120,
		   origin = "lower")

# plt.subplot(5, 8, 16)
# plt.axis("off")
# plt.imshow()

# ROW 3

plt.subplot(5, 8, 17)
plt.axis("off")
plt.imshow(np.load("resources/region-data/binary-images/%05dAIA94.npy" % ID),
		   cmap = "sdoaia94",
		   origin = "lower")

plt.subplot(5, 8, 18)
plt.axis("off")
plt.imshow(np.load("resources/region-data/binary-images/%05dAIA131.npy" % ID),
		   cmap = "sdoaia131",
		   origin = "lower")

plt.subplot(5, 8, 19)
plt.axis("off")
plt.imshow(np.load("resources/region-data/binary-images/%05dAIA171.npy" % ID),
		   cmap = "sdoaia171",
		   origin = "lower")

plt.subplot(5, 8, 20)
plt.axis("off")
plt.imshow(np.load("resources/region-data/binary-images/%05dAIA193.npy" % ID),
		   cmap = "sdoaia193",
		   origin = "lower")

plt.subplot(5, 8, 21)
plt.axis("off")
plt.imshow(np.load("resources/region-data/binary-images/%05dAIA211.npy" % ID),
		   cmap = "sdoaia211",
		   origin = "lower")

plt.subplot(5, 8, 22)
plt.axis("off")
plt.imshow(np.load("resources/region-data/binary-images/%05dAIA304.npy" % ID),
		   cmap = "sdoaia304",
		   origin = "lower")

plt.subplot(5, 8, 23)
plt.axis("off")
plt.imshow(np.load("resources/region-data/binary-images/%05dAIA335.npy" % ID),
		   cmap = "sdoaia335",
		   origin = "lower")

# plt.subplot(5, 8, 24)
# plt.axis("off")
# plt.imshow()

# ROW 4

plt.subplot(5, 8, 25)
plt.axis("off")
plt.imshow(np.load("resources/region-data/threshold-images/%05dAIA94.npy" % ID),
		   cmap = "sdoaia94",
		   origin = "lower")

plt.subplot(5, 8, 26)
plt.axis("off")
plt.imshow(np.load("resources/region-data/threshold-images/%05dAIA131.npy" % ID),
		   cmap = "sdoaia131",
		   origin = "lower")

plt.subplot(5, 8, 27)
plt.axis("off")
plt.imshow(np.load("resources/region-data/threshold-images/%05dAIA171.npy" % ID),
		   cmap = "sdoaia171",
		   origin = "lower")

plt.subplot(5, 8, 28)
plt.axis("off")
plt.imshow(np.load("resources/region-data/threshold-images/%05dAIA193.npy" % ID),
		   cmap = "sdoaia193",
		   origin = "lower")

plt.subplot(5, 8, 29)
plt.axis("off")
plt.imshow(np.load("resources/region-data/threshold-images/%05dAIA211.npy" % ID),
		   cmap = "sdoaia211",
		   origin = "lower")

plt.subplot(5, 8, 30)
plt.axis("off")
plt.imshow(np.load("resources/region-data/threshold-images/%05dAIA304.npy" % ID),
		   cmap = "sdoaia304",
		   origin = "lower")

plt.subplot(5, 8, 31)
plt.axis("off")
plt.imshow(np.load("resources/region-data/threshold-images/%05dAIA335.npy" % ID),
		   cmap = "sdoaia335",
		   origin = "lower")

# plt.subplot(5, 8, 32)
# plt.axis("off")
# plt.imshow()

# ROW 5

plt.subplot(5, 8, 33)
plt.axis("off")
plt.imshow(np.load("resources/region-data/masked-magnetogram-images/%05dAIA94.npy" % ID),
		   cmap = "gray",
		   vmin = -120,
		   vmax = 120,
		   origin = "lower")

plt.subplot(5, 8, 34)
plt.axis("off")
plt.imshow(np.load("resources/region-data/masked-magnetogram-images/%05dAIA131.npy" % ID),
		   cmap = "gray",
		   vmin = -120,
		   vmax = 120,
		   origin = "lower")

plt.subplot(5, 8, 35)
plt.axis("off")
plt.imshow(np.load("resources/region-data/masked-magnetogram-images/%05dAIA171.npy" % ID),
		   cmap = "gray",
		   vmin = -120,
		   vmax = 120,
		   origin = "lower")

plt.subplot(5, 8, 36)
plt.axis("off")
plt.imshow(np.load("resources/region-data/masked-magnetogram-images/%05dAIA193.npy" % ID),
		   cmap = "gray",
		   vmin = -120,
		   vmax = 120,
		   origin = "lower")

plt.subplot(5, 8, 37)
plt.axis("off")
plt.imshow(np.load("resources/region-data/masked-magnetogram-images/%05dAIA211.npy" % ID),
		   cmap = "gray",
		   vmin = -120,
		   vmax = 120,
		   origin = "lower")

plt.subplot(5, 8, 38)
plt.axis("off")
plt.imshow(np.load("resources/region-data/masked-magnetogram-images/%05dAIA304.npy" % ID),
		   cmap = "gray",
		   vmin = -120,
		   vmax = 120,
		   origin = "lower")

plt.subplot(5, 8, 39)
plt.axis("off")
plt.imshow(np.load("resources/region-data/masked-magnetogram-images/%05dAIA335.npy" % ID),
		   cmap = "gray",
		   vmin = -120,
		   vmax = 120,
		   origin = "lower")

# plt.subplot(5, 8, 40)
# plt.axis("off")
# plt.imshow()

def update(val):
	alpha = slider_alpha.val
	plt.subplot(5, 8, 9)
	plt.axis("off")
	plt.imshow(np.load("resources/region-data/raw-images/%05dAIA94.npy" % ID),
			   cmap = "sdoaia94",
			   origin = "lower")
	plt.imshow(np.load("resources/region-data/magnetogram-images/%05dHMI6173.npy" % ID),
			   cmap = "gray",
			   vmin = -120,
			   vmax = 120,
			   alpha = alpha,
			   origin = "lower")

	plt.subplot(5, 8, 10)
	plt.axis("off")
	plt.imshow(np.load("resources/region-data/raw-images/%05dAIA131.npy" % ID),
			   cmap = "sdoaia131",
			   origin = "lower")
	plt.imshow(np.load("resources/region-data/magnetogram-images/%05dHMI6173.npy" % ID),
			   cmap = "gray",
			   vmin = -120,
			   vmax = 120,
			   alpha = alpha,
			   origin = "lower")

	plt.subplot(5, 8, 11)
	plt.axis("off")
	plt.imshow(np.load("resources/region-data/raw-images/%05dAIA171.npy" % ID),
			   cmap = "sdoaia171",
			   origin = "lower")
	plt.imshow(np.load("resources/region-data/magnetogram-images/%05dHMI6173.npy" % ID),
			   cmap = "gray",
			   vmin = -120,
			   vmax = 120,
			   alpha = alpha,
			   origin = "lower")

	plt.subplot(5, 8, 12)
	plt.axis("off")
	plt.imshow(np.load("resources/region-data/raw-images/%05dAIA193.npy" % ID),
			   cmap = "sdoaia193",
			   origin = "lower")
	plt.imshow(np.load("resources/region-data/magnetogram-images/%05dHMI6173.npy" % ID),
			   cmap = "gray",
			   vmin = -120,
			   vmax = 120,
			   alpha = alpha,
			   origin = "lower")

	plt.subplot(5, 8, 13)
	plt.axis("off")
	plt.imshow(np.load("resources/region-data/raw-images/%05dAIA211.npy" % ID),
			   cmap = "sdoaia211",
			   origin = "lower")
	plt.imshow(np.load("resources/region-data/magnetogram-images/%05dHMI6173.npy" % ID),
			   cmap = "gray",
			   vmin = -120,
			   vmax = 120,
			   alpha = alpha,
			   origin = "lower")

	plt.subplot(5, 8, 14)
	plt.axis("off")
	plt.imshow(np.load("resources/region-data/raw-images/%05dAIA304.npy" % ID),
			   cmap = "sdoaia304",
			   origin = "lower")
	plt.imshow(np.load("resources/region-data/magnetogram-images/%05dHMI6173.npy" % ID),
			   cmap = "gray",
			   vmin = -120,
			   vmax = 120,
			   alpha = alpha,
			   origin = "lower")

	plt.subplot(5, 8, 15)
	plt.axis("off")
	plt.imshow(np.load("resources/region-data/raw-images/%05dAIA335.npy" % ID),
			   cmap = "sdoaia335",
			   origin = "lower")
	plt.imshow(np.load("resources/region-data/magnetogram-images/%05dHMI6173.npy" % ID),
			   cmap = "gray",
			   vmin = -120,
			   vmax = 120,
			   alpha = alpha,
			   origin = "lower")

	# plt.subplot(5, 8, 16)
	# plt.axis("off")
	# plt.imshow()

ax_alpha = plt.axes([0.125, 0.06, 0.2, 0.03])
slider_alpha = Slider(ax_alpha, "Magnetogram Opacity", 0, 1, valstep = 0.05, valinit = 0.5)
slider_alpha.on_changed(update)

plt.subplots_adjust(wspace = 0.02, hspace = 0)
plt.show()
