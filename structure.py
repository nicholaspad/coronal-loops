from IPython.core import debugger; debug = debugger.Pdb().set_trace
from os import listdir
from os.path import isfile, join
from recorder import Recorder
from sunpy.map import Map
import astropy.units as u
import numpy as np

RECORDER = Recorder()
RECORDER.display_start_time("structure")

RECORDER.sys_text("Importing data directories")
IMAGE_PATH = "/Volumes/Nicholas-Data/output/"
PATH94 = "/Volumes/Nicholas-Data/AIA94/"
PATH131 = "/Volumes/Nicholas-Data/AIA131/"
PATH171 = "/Volumes/Nicholas-Data/AIA171/"
PATH193 = "/Volumes/Nicholas-Data/AIA193/"
PATH211 = "/Volumes/Nicholas-Data/AIA211/"
PATH304 = "/Volumes/Nicholas-Data/AIA304/"
PATH335 = "/Volumes/Nicholas-Data/AIA335/"

DIR94 = [f for f in listdir(PATH94) if isfile(join(PATH94, f))]
DIR131 = [f for f in listdir(PATH131) if isfile(join(PATH131, f))]
DIR171 = [f for f in listdir(PATH171) if isfile(join(PATH171, f))]
DIR193 = [f for f in listdir(PATH193) if isfile(join(PATH193, f))]
DIR211 = [f for f in listdir(PATH211) if isfile(join(PATH211, f))]
DIR304 = [f for f in listdir(PATH304) if isfile(join(PATH304, f))]
DIR335 = [f for f in listdir(PATH335) if isfile(join(PATH335, f))]

N = len(DIR94)

for K in tqdm(range(N), desc = "Working"):
	RECORDER.sys_text("Importing AIA94")
	K94 = Map(PATH94 + DIR94[K])
	RECORDER.sys_text("Importing AIA131")
	K131 = Map(PATH131 + DIR131[K])
	RECORDER.sys_text("Importing AIA171")
	K171 = Map(PATH171 + DIR171[K])
	RECORDER.sys_text("Importing AIA193")
	K193 = Map(PATH193 + DIR193[K])
	RECORDER.sys_text("Importing AIA211")
	K211 = Map(PATH211 + DIR211[K])
	RECORDER.sys_text("Importing AIA304")
	K304 = Map(PATH304 + DIR304[K])
	RECORDER.sys_text("Importing AIA335")
	K335 = Map(PATH335 + DIR335[K])

	RECORDER.info_text("Current datetime: %s" % K94.date)
	
	RECORDER.sys_text("Reading data")
	I94 = K94.data
	I131 = K131.data
	I171 = K171.data
	I193 = K193.data
	I211 = K211.data
	I304 = K304.data
	I335 = K335.data

	"""
	1. Corrected raw images
	2. Binary masked images
	3. Contour masked images
	4. Structural images
	"""

