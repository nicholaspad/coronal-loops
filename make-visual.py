from IPython.core import debugger ; debug = debugger.Pdb().set_trace
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

plt.figure(figsize = (16, 6))
gs = gridspec.GridSpec(8, 3)
gs.update(wspace = 0, hspace = 0)

plt.gcf().text(0.01, 0.94, "%s %s" % (DATE, TIME), fontsize = 12)
plt.gcf().text(0.01, 0.97, "ID %05d" % ID, fontsize = 12)
plt.gcf().text(0.01, 0.91, "HPC (%.1f, %.1f)" % (HPC_X, HPC_Y), fontsize = 12)

plt.subplot(3, 8, 1)
plt.title("AIA94")
plt.axis("off")
plt.imshow(np.load("resources/region-data/raw-images/%05dAIA94.npy" % ID),
		   cmap = "sdoaia94")

plt.subplot(3, 8, 2)
plt.title("AIA131")
plt.axis("off")
plt.imshow(np.load("resources/region-data/raw-images/%05dAIA131.npy" % ID),
		   cmap = "sdoaia131")

plt.subplot(3, 8, 3)
plt.title("AIA171")
plt.axis("off")
plt.imshow(np.load("resources/region-data/raw-images/%05dAIA171.npy" % ID),
		   cmap = "sdoaia171")

plt.subplot(3, 8, 4)
plt.title("AIA193")
plt.axis("off")
plt.imshow(np.load("resources/region-data/raw-images/%05dAIA193.npy" % ID),
		   cmap = "sdoaia193")

plt.subplot(3, 8, 5)
plt.title("AIA211")
plt.axis("off")
plt.imshow(np.load("resources/region-data/raw-images/%05dAIA211.npy" % ID),
		   cmap = "sdoaia211")

plt.subplot(3, 8, 6)
plt.title("AIA304")
plt.axis("off")
plt.imshow(np.load("resources/region-data/raw-images/%05dAIA304.npy" % ID),
		   cmap = "sdoaia304")

plt.subplot(3, 8, 7)
plt.title("AIA335")
plt.axis("off")
plt.imshow(np.load("resources/region-data/raw-images/%05dAIA335.npy" % ID),
		   cmap = "sdoaia335")

plt.subplot(3, 8, 8)
plt.title("HMI")
plt.axis("off")
plt.imshow(np.load("resources/region-data/magnetogram-images/%05dHMI6173.npy" % ID),
		   cmap = "gray",
		   vmin = -120,
		   vmax = 120)

plt.subplot(3, 8, 9)
plt.axis("off")
plt.imshow(np.load("resources/region-data/binary-images/%05dAIA94.npy" % ID),
		   cmap = "sdoaia94")

plt.subplot(3, 8, 10)
plt.axis("off")
plt.imshow(np.load("resources/region-data/binary-images/%05dAIA131.npy" % ID),
		   cmap = "sdoaia131")

plt.subplot(3, 8, 11)
plt.axis("off")
plt.imshow(np.load("resources/region-data/binary-images/%05dAIA171.npy" % ID),
		   cmap = "sdoaia171")

plt.subplot(3, 8, 12)
plt.axis("off")
plt.imshow(np.load("resources/region-data/binary-images/%05dAIA193.npy" % ID),
		   cmap = "sdoaia193")

plt.subplot(3, 8, 13)
plt.axis("off")
plt.imshow(np.load("resources/region-data/binary-images/%05dAIA211.npy" % ID),
		   cmap = "sdoaia211")

plt.subplot(3, 8, 14)
plt.axis("off")
plt.imshow(np.load("resources/region-data/binary-images/%05dAIA304.npy" % ID),
		   cmap = "sdoaia304")

plt.subplot(3, 8, 15)
plt.axis("off")
plt.imshow(np.load("resources/region-data/binary-images/%05dAIA335.npy" % ID),
		   cmap = "sdoaia335")

# plt.subplot(3, 8, 16)
# plt.axis("off")
# plt.imshow(np.load("resources/region-data/magnetogram-images/%05dHMI6173.npy" % ID),
#	 		 cmap = "gray")

plt.subplot(3, 8, 17)
plt.axis("off")
plt.imshow(np.load("resources/region-data/threshold-images/%05dAIA94.npy" % ID),
		   cmap = "sdoaia94")

plt.subplot(3, 8, 18)
plt.axis("off")
plt.imshow(np.load("resources/region-data/threshold-images/%05dAIA131.npy" % ID),
		   cmap = "sdoaia131")

plt.subplot(3, 8, 19)
plt.axis("off")
plt.imshow(np.load("resources/region-data/threshold-images/%05dAIA171.npy" % ID),
		   cmap = "sdoaia171")

plt.subplot(3, 8, 20)
plt.axis("off")
plt.imshow(np.load("resources/region-data/threshold-images/%05dAIA193.npy" % ID),
		   cmap = "sdoaia193")

plt.subplot(3, 8, 21)
plt.axis("off")
plt.imshow(np.load("resources/region-data/threshold-images/%05dAIA211.npy" % ID),
		   cmap = "sdoaia211")

plt.subplot(3, 8, 22)
plt.axis("off")
plt.imshow(np.load("resources/region-data/threshold-images/%05dAIA304.npy" % ID),
		   cmap = "sdoaia304")

plt.subplot(3, 8, 23)
plt.axis("off")
plt.imshow(np.load("resources/region-data/threshold-images/%05dAIA335.npy" % ID),
		   cmap = "sdoaia335")

# plt.subplot(3, 8, 24)
# plt.axis("off")
# plt.imshow(np.load("resources/region-data/magnetogram-images/%05dHMI6173.npy" % ID),
#	 		 cmap = "gray")

plt.subplots_adjust(wspace = 0.02, hspace = 0)
plt.show()
