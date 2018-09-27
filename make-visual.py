# -*- coding: utf-8 -*-

import warnings
warnings.filterwarnings("ignore", message = "numpy.dtype size changed")

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

N = DATA[0]
DATE = DATA[1]
TIME = DATA[2]
HPC_X = float(DATA[5])
HPC_Y = float(DATA[6])
SIZE_X = float(DATA[9])
SIZE_Y = float(DATA[10])
MED_INTEN = float(DATA[12])
AVG_GAUSS = float(DATA[16])

plt.figure(figsize = (8, 6))
gs = gridspec.GridSpec(4, 3)
gs.update(wspace = 0, hspace = 0)

font = "Inconsolata"

plt.gcf().text(0.75, 0.32, u"WHEN: %s %s" % (DATE, TIME), fontsize = 11, fontname = font)
plt.gcf().text(0.75, 0.28, u"ID: %05d" % ID, fontsize = 12, fontname = font)
plt.gcf().text(0.75, 0.24, u"LOCATION (%.1f arcsec, %.1f arcsec)" % (HPC_X, HPC_Y), fontsize = 11, fontname = font)
plt.gcf().text(0.75, 0.20, u"SIZE (%d arcsec, %d arcsec)" % (SIZE_X, SIZE_Y), fontsize = 11, fontname = font)
plt.gcf().text(0.75, 0.16, u"OTHER - MED INTENSITY: %.1f" % MED_INTEN, fontsize = 11, fontname = font)
plt.gcf().text(0.75, 0.12, u"OTHER - AVG GAUSS: %.3f" % AVG_GAUSS, fontsize = 11, fontname = font)

##### ROW 1
plt.subplot(3,4,1)
plt.title("Raw AIA171", fontname = font)
plt.axis("off")
plt.imshow(np.load("resources/region-data/raw-images/%05dAIA171.npy" % ID),
		   cmap = "sdoaia171",
		   origin = "lower")

plt.subplot(3,4,2)
plt.title("Raw AIA304", fontname = font)
plt.axis("off")
plt.imshow(np.load("resources/region-data/raw-images/%05dAIA304.npy" % ID),
		   cmap = "sdoaia304",
		   origin = "lower")

plt.subplot(3,4,3)
plt.title("Raw HMI", fontname = font)
plt.axis("off")
plt.imshow(np.load("resources/region-data/raw-images/%05dHMI6173.npy" % ID),
		   cmap = "gray",
		   vmin = -120,
		   vmax = 120,
		   origin = "lower")

plt.subplot(3,4,4)
plt.title("Elliptical mask", fontname = font)
plt.axis("off")
plt.imshow(np.load("resources/region-data/e-masks/%05d.npy" % ID),
		   cmap = "gray",
		   origin = "lower")

##### ROW 2
plt.subplot(3,4,5)
plt.title("Masked AIA304", fontname = font)
plt.axis("off")
plt.imshow(np.load("resources/region-data/masked-images/%05dAIA304.npy" % ID),
		   cmap = "sdoaia304",
		   origin = "lower")

plt.subplot(3,4,6)
plt.title("E-masked AIA304", fontname = font)
plt.axis("off")
plt.imshow(np.load("resources/region-data/e-masked-images/%05dAIA304.npy" % ID),
		   cmap = "sdoaia304",
		   origin = "lower")

plt.subplot(3,4,7)
plt.title("Masked HMI", fontname = font)
plt.axis("off")
plt.imshow(np.load("resources/region-data/masked-images/%05dHMI6173.npy" % ID),
		   cmap = "gray",
		   vmin = -120,
		   vmax = 120,
		   origin = "lower")

plt.subplot(3,4,8)
plt.title("E-masked HMI", fontname = font)
plt.axis("off")
plt.imshow(np.load("resources/region-data/e-masked-images/%05dHMI6173.npy" % ID),
		   cmap = "gray",
		   vmin = -120,
		   vmax = 120,
		   origin = "lower")

##### ROW 3
plt.subplot(3,4,9)
plt.title("Raw mask", fontname = font)
plt.axis("off")
plt.imshow(np.load("resources/region-data/raw-masks/%05d.npy" % ID),
		   cmap = "gray",
		   origin = "lower")

plt.subplot(3,4,10)
plt.title("Raw image overlay", fontname = font)
plt.axis("off")
plt.imshow(np.load("resources/region-data/raw-images/%05dAIA304.npy" % ID),
		   cmap = "sdoaia304",
		   origin = "lower")
plt.imshow(np.load("resources/region-data/raw-images/%05dHMI6173.npy" % ID),
		   cmap = "gray",
		   vmin = -120,
		   vmax = 120,
		   origin = "lower",
		   alpha = 0.5)

plt.subplot(3,4,11)
plt.title("E-mask overlay", fontname = font)
plt.axis("off")
plt.imshow(np.load("resources/region-data/raw-masks/%05d.npy" % ID),
		   cmap = "gray",
		   origin = "lower")
plt.imshow(np.load("resources/region-data/e-masks/%05d.npy" % ID),
		   cmap = "gray",
		   origin = "lower",
		   alpha = 0.5)

##### SLIDER MANAGER
def update(val):
	alpha = slider_alpha.val
	plt.subplot(3,4,10)
	plt.title("Raw image overlay", fontname = font)
	plt.axis("off")
	plt.imshow(np.load("resources/region-data/raw-images/%05dAIA304.npy" % ID),
			   cmap = "sdoaia304",
			   origin = "lower")
	plt.imshow(np.load("resources/region-data/raw-images/%05dHMI6173.npy" % ID),
			   cmap = "gray",
			   vmin = -120,
			   vmax = 120,
			   origin = "lower",
			   alpha = alpha)

	plt.subplot(3,4,11)
	plt.title("E-mask overlay", fontname = font)
	plt.axis("off")
	plt.imshow(np.load("resources/region-data/raw-masks/%05d.npy" % ID),
			   cmap = "gray",
			   origin = "lower")
	plt.imshow(np.load("resources/region-data/e-masks/%05d.npy" % ID),
			   cmap = "gray",
			   origin = "lower",
			   alpha = alpha)

ax_alpha = plt.axes([0.125, 0.06, 0.2, 0.03])
slider_alpha = Slider(ax_alpha, "Opacity", 0, 1, valstep = 0.05, valinit = 0.5)
slider_alpha.on_changed(update)

plt.show()
