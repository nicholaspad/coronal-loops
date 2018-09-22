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

DATA = []
with open("resources/region-data/database.csv") as f:
	for line in f:
		if line.split(",")[0] == "%05d" % ID:
			DATA = line.split(",")

DATE = DATA[3]
TIME = DATA[4]