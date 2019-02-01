from IPython.core import debugger; debug = debugger.Pdb().set_trace
from os import listdir
from os.path import isfile, join
from recorder import Recorder
from sunpy.map import Map
from tqdm import tqdm
import astropy.units as u
import matplotlib.pyplot as plt
import numpy as np

RECORDER = Recorder()
RECORDER.display_start_time("structure")

RECORDER.sys_text("Importing data directories")
SAVEPATH = "data/outputs/"
PATH94 = "data/AIA94/"
PATH131 = "data/AIA131/"
PATH171 = "data/AIA171/"
PATH193 = "data/AIA193/"
PATH211 = "data/AIA211/"
PATH304 = "data/AIA304/"
PATH335 = "data/AIA335/"

DIR94 = [f for f in listdir(PATH94) if isfile(join(PATH94, f))]
DIR131 = [f for f in listdir(PATH131) if isfile(join(PATH131, f))]
DIR171 = [f for f in listdir(PATH171) if isfile(join(PATH171, f))]
DIR193 = [f for f in listdir(PATH193) if isfile(join(PATH193, f))]
DIR211 = [f for f in listdir(PATH211) if isfile(join(PATH211, f))]
DIR304 = [f for f in listdir(PATH304) if isfile(join(PATH304, f))]
DIR335 = [f for f in listdir(PATH335) if isfile(join(PATH335, f))]

N = len(DIR94)

for K in tqdm(range(N), desc = "Working"):
	RECORDER.sys_text("Importing FITS data")
	K94 = Map(PATH94 + DIR94[K])
	K131 = Map(PATH131 + DIR131[K])
	K171 = Map(PATH171 + DIR171[K])
	K193 = Map(PATH193 + DIR193[K])
	K211 = Map(PATH211 + DIR211[K])
	K304 = Map(PATH304 + DIR304[K])
	K335 = Map(PATH335 + DIR335[K])

	RECORDER.info_text("Current datetime - %s" % K94.date)
	
	RECORDER.info_text("Reading raw image data")
	I94 = K94.data
	I131 = K131.data
	I171 = K171.data
	I193 = K193.data
	I211 = K211.data
	I304 = K304.data
	I335 = K335.data

	RECORDER.sys_text("Exporting corrected raw images")
	plt.imsave(SAVEPATH + "AIA94/%04d" % K, )

	"""
	1. Corrected raw images
	2. Binary masked images
	3. Contour masked images
	4. Structural images
	"""

