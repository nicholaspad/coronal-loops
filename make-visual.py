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

HPC_X = float(DATA[7])
HPC_Y = float(DATA[8])

plt.figure(figsize = (16, 10))
gs = gridspec.GridSpec(8, 5)
gs.update(wspace = 0, hspace = 0)

plt.gcf().text(0.01, 0.94, "%s %s" % (DATE, TIME), fontsize = 12)
plt.gcf().text(0.01, 0.97, "ID %05d" % ID, fontsize = 12)
plt.gcf().text(0.01, 0.91, "HPC (%.1f, %.1f)" % (HPC_X, HPC_Y), fontsize = 12)

plt.subplot(4, 8, 1)
plt.title("AIA94")
plt.axis("off")
plt.imshow(np.load("resources/region-data/raw-images/%05dAIA94.npy" % ID),
		   cmap = "sdoaia94",
		   origin = "lower")

plt.subplot(4, 8, 2)
plt.title("AIA131")
plt.axis("off")
plt.imshow(np.load("resources/region-data/raw-images/%05dAIA131.npy" % ID),
		   cmap = "sdoaia131",
		   origin = "lower")

plt.subplot(4, 8, 3)
plt.title("AIA171")
plt.axis("off")
plt.imshow(np.load("resources/region-data/raw-images/%05dAIA171.npy" % ID),
		   cmap = "sdoaia171",
		   origin = "lower")

plt.subplot(4, 8, 4)
plt.title("AIA193")
plt.axis("off")
plt.imshow(np.load("resources/region-data/raw-images/%05dAIA193.npy" % ID),
		   cmap = "sdoaia193",
		   origin = "lower")

plt.subplot(4, 8, 5)
plt.title("AIA211")
plt.axis("off")
plt.imshow(np.load("resources/region-data/raw-images/%05dAIA211.npy" % ID),
		   cmap = "sdoaia211",
		   origin = "lower")

plt.subplot(4, 8, 6)
plt.title("AIA304")
plt.axis("off")
plt.imshow(np.load("resources/region-data/raw-images/%05dAIA304.npy" % ID),
		   cmap = "sdoaia304",
		   origin = "lower")

plt.subplot(4, 8, 7)
plt.title("AIA335")
plt.axis("off")
plt.imshow(np.load("resources/region-data/raw-images/%05dAIA335.npy" % ID),
		   cmap = "sdoaia335",
		   origin = "lower")

plt.subplot(4, 8, 8)
plt.title("HMI")
plt.axis("off")
plt.imshow(np.load("resources/region-data/magnetogram-images/%05dHMI6173.npy" % ID),
		   cmap = "gray",
		   vmin = -120,
		   vmax = 120,
		   origin = "lower")

plt.subplot(4, 8, 9)
plt.axis("off")
plt.imshow(np.load("resources/region-data/binary-images/%05dAIA94.npy" % ID),
		   cmap = "sdoaia94",
		   origin = "lower")

plt.subplot(4, 8, 10)
plt.axis("off")
plt.imshow(np.load("resources/region-data/binary-images/%05dAIA131.npy" % ID),
		   cmap = "sdoaia131",
		   origin = "lower")

plt.subplot(4, 8, 11)
plt.axis("off")
plt.imshow(np.load("resources/region-data/binary-images/%05dAIA171.npy" % ID),
		   cmap = "sdoaia171",
		   origin = "lower")

plt.subplot(4, 8, 12)
plt.axis("off")
plt.imshow(np.load("resources/region-data/binary-images/%05dAIA193.npy" % ID),
		   cmap = "sdoaia193",
		   origin = "lower")

plt.subplot(4, 8, 13)
plt.axis("off")
plt.imshow(np.load("resources/region-data/binary-images/%05dAIA211.npy" % ID),
		   cmap = "sdoaia211",
		   origin = "lower")

plt.subplot(4, 8, 14)
plt.axis("off")
plt.imshow(np.load("resources/region-data/binary-images/%05dAIA304.npy" % ID),
		   cmap = "sdoaia304",
		   origin = "lower")

plt.subplot(4, 8, 15)
plt.axis("off")
plt.imshow(np.load("resources/region-data/binary-images/%05dAIA335.npy" % ID),
		   cmap = "sdoaia335",
		   origin = "lower")

# plt.subplot(4, 8, 16)
# plt.axis("off")
# plt.imshow(np.load("resources/region-data/magnetogram-images/%05dHMI6173.npy" % ID),
#	 		 cmap = "gray",
#		     origin = "lower")

plt.subplot(4, 8, 17)
plt.axis("off")
plt.imshow(np.load("resources/region-data/threshold-images/%05dAIA94.npy" % ID),
		   cmap = "sdoaia94",
		   origin = "lower")

plt.subplot(4, 8, 18)
plt.axis("off")
plt.imshow(np.load("resources/region-data/threshold-images/%05dAIA131.npy" % ID),
		   cmap = "sdoaia131",
		   origin = "lower")

plt.subplot(4, 8, 19)
plt.axis("off")
plt.imshow(np.load("resources/region-data/threshold-images/%05dAIA171.npy" % ID),
		   cmap = "sdoaia171",
		   origin = "lower")

plt.subplot(4, 8, 20)
plt.axis("off")
plt.imshow(np.load("resources/region-data/threshold-images/%05dAIA193.npy" % ID),
		   cmap = "sdoaia193",
		   origin = "lower")

plt.subplot(4, 8, 21)
plt.axis("off")
plt.imshow(np.load("resources/region-data/threshold-images/%05dAIA211.npy" % ID),
		   cmap = "sdoaia211",
		   origin = "lower")

plt.subplot(4, 8, 22)
plt.axis("off")
plt.imshow(np.load("resources/region-data/threshold-images/%05dAIA304.npy" % ID),
		   cmap = "sdoaia304",
		   origin = "lower")

plt.subplot(4, 8, 23)
plt.axis("off")
plt.imshow(np.load("resources/region-data/threshold-images/%05dAIA335.npy" % ID),
		   cmap = "sdoaia335",
		   origin = "lower")

# plt.subplot(4, 8, 24)
# plt.axis("off")
# plt.imshow(np.load("resources/region-data/magnetogram-images/%05dHMI6173.npy" % ID),
#	 		 cmap = "gray",
#		     origin = "lower")

plt.subplot(4, 8, 25)
plt.axis("off")
plt.imshow(np.load("resources/region-data/raw-images/%05dAIA94.npy" % ID),
		   cmap = "sdoaia94",
		   origin = "lower")
plt.imshow(np.load("resources/region-data/magnetogram-images/%05dHMI6173.npy" % ID),
		   cmap = "gray",
		   alpha = 0.5,
		   origin = "lower")

plt.subplot(4, 8, 26)
plt.axis("off")
plt.imshow(np.load("resources/region-data/raw-images/%05dAIA131.npy" % ID),
		   cmap = "sdoaia131")
plt.imshow(np.load("resources/region-data/magnetogram-images/%05dHMI6173.npy" % ID),
		   cmap = "gray",
		   alpha = 0.5,
		   origin = "lower")

plt.subplot(4, 8, 27)
plt.axis("off")
plt.imshow(np.load("resources/region-data/raw-images/%05dAIA171.npy" % ID),
		   cmap = "sdoaia171")
plt.imshow(np.load("resources/region-data/magnetogram-images/%05dHMI6173.npy" % ID),
		   cmap = "gray",
		   alpha = 0.5,
		   origin = "lower")

plt.subplot(4, 8, 28)
plt.axis("off")
plt.imshow(np.load("resources/region-data/raw-images/%05dAIA193.npy" % ID),
		   cmap = "sdoaia193")
plt.imshow(np.load("resources/region-data/magnetogram-images/%05dHMI6173.npy" % ID),
		   cmap = "gray",
		   alpha = 0.5,
		   origin = "lower")

plt.subplot(4, 8, 29)
plt.axis("off")
plt.imshow(np.load("resources/region-data/raw-images/%05dAIA211.npy" % ID),
		   cmap = "sdoaia211")
plt.imshow(np.load("resources/region-data/magnetogram-images/%05dHMI6173.npy" % ID),
		   cmap = "gray",
		   alpha = 0.5,
		   origin = "lower")

plt.subplot(4, 8, 30)
plt.axis("off")
plt.imshow(np.load("resources/region-data/raw-images/%05dAIA304.npy" % ID),
		   cmap = "sdoaia304")
plt.imshow(np.load("resources/region-data/magnetogram-images/%05dHMI6173.npy" % ID),
		   cmap = "gray",
		   alpha = 0.5,
		   origin = "lower")

plt.subplot(4, 8, 31)
plt.axis("off")
plt.imshow(np.load("resources/region-data/raw-images/%05dAIA335.npy" % ID),
		   cmap = "sdoaia335")
plt.imshow(np.load("resources/region-data/magnetogram-images/%05dHMI6173.npy" % ID),
		   cmap = "gray",
		   alpha = 0.5,
		   origin = "lower")

# plt.subplot(4, 8, 32)
# plt.axis("off")
# plt.imshow(np.load("resources/region-data/magnetogram-images/%05dHMI6173.npy" % ID),
#	 		 cmap = "gray",
#		     origin = "lower")


def update(val):
	alpha = slider_alpha.val
	plt.subplot(4, 8, 25)
	plt.axis("off")
	plt.imshow(np.load("resources/region-data/raw-images/%05dAIA94.npy" % ID),
			   cmap = "sdoaia94")
	plt.imshow(np.load("resources/region-data/magnetogram-images/%05dHMI6173.npy" % ID),
			   cmap = "gray",
			   alpha = alpha,
			   origin = "lower")

	plt.subplot(4, 8, 26)
	plt.axis("off")
	plt.imshow(np.load("resources/region-data/raw-images/%05dAIA131.npy" % ID),
			   cmap = "sdoaia131")
	plt.imshow(np.load("resources/region-data/magnetogram-images/%05dHMI6173.npy" % ID),
			   cmap = "gray",
			   alpha = alpha,
			   origin = "lower")

	plt.subplot(4, 8, 27)
	plt.axis("off")
	plt.imshow(np.load("resources/region-data/raw-images/%05dAIA171.npy" % ID),
			   cmap = "sdoaia171")
	plt.imshow(np.load("resources/region-data/magnetogram-images/%05dHMI6173.npy" % ID),
			   cmap = "gray",
			   alpha = alpha,
			   origin = "lower")

	plt.subplot(4, 8, 28)
	plt.axis("off")
	plt.imshow(np.load("resources/region-data/raw-images/%05dAIA193.npy" % ID),
			   cmap = "sdoaia193")
	plt.imshow(np.load("resources/region-data/magnetogram-images/%05dHMI6173.npy" % ID),
			   cmap = "gray",
			   alpha = alpha,
			   origin = "lower")

	plt.subplot(4, 8, 29)
	plt.axis("off")
	plt.imshow(np.load("resources/region-data/raw-images/%05dAIA211.npy" % ID),
			   cmap = "sdoaia211")
	plt.imshow(np.load("resources/region-data/magnetogram-images/%05dHMI6173.npy" % ID),
			   cmap = "gray",
			   alpha = alpha,
			   origin = "lower")

	plt.subplot(4, 8, 30)
	plt.axis("off")
	plt.imshow(np.load("resources/region-data/raw-images/%05dAIA304.npy" % ID),
			   cmap = "sdoaia304")
	plt.imshow(np.load("resources/region-data/magnetogram-images/%05dHMI6173.npy" % ID),
			   cmap = "gray",
			   alpha = alpha,
			   origin = "lower")

	plt.subplot(4, 8, 31)
	plt.axis("off")
	plt.imshow(np.load("resources/region-data/raw-images/%05dAIA335.npy" % ID),
			   cmap = "sdoaia335")
	plt.imshow(np.load("resources/region-data/magnetogram-images/%05dHMI6173.npy" % ID),
			   cmap = "gray",
			   alpha = alpha,
			   origin = "lower")

ax_alpha = plt.axes([0.125, 0.06, 0.2, 0.03])
slider_alpha = Slider(ax_alpha, "Magnetogram Opacity", 0, 1, valstep = 0.05, valinit = 0.5)
slider_alpha.on_changed(update)

plt.subplots_adjust(wspace = 0.02, hspace = 0)
plt.show()
