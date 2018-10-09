from recorder import Recorder
import argparse
import matplotlib.pyplot as plt
import numpy as np
import sys

PRINTER = Recorder()
parser = argparse.ArgumentParser()
parser.add_argument("-file")
parser.add_argument("-type")
args = parser.parse_args()

if args.file == None or args.type == None:
	PRINTER.info_text("Specify filename and datatype with '-file <filename> -type <datatype>'")
	sys.exit()

FILE = args.file
TYPE = args.type.lower()

if TYPE == "aia171":
	plt.imshow(np.load(FILE), cmap = "sdoaia171", origin = "lower")
	plt.title("AIA171")
	plt.clim(0,3500)
	plt.show()
elif TYPE == "aia304":
	plt.imshow(np.load(FILE), cmap = "sdoaia304", origin = "lower")
	plt.title("AIA304")
	plt.clim(0,1500)
	plt.show()
elif TYPE == "hmi":
	plt.imshow(np.load(FILE), cmap = "gray", origin = "lower", vmin = -120, vmax = 120)
	plt.title("HMI-M")
	plt.show()
else:
	PRINTER.info_text("Datatype %s not recognized." % TYPE.upper())