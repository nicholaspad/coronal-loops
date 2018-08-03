import warnings
warnings.filterwarnings("ignore", message = "numpy.dtype size changed")

from datetime import datetime
from recorder import Recorder
from sunpy.net import Fido, attrs as a
import astropy.units as u
import getpass
import os
import pprint

#########################

MAIN_DIR = "/Users/%s/Desktop/lmsal" % getpass.getuser()
EMAIL = "padman@lmsal.com"
PRINTER = Recorder()
PRINTER.display_start_time("data-get")
pp = pprint.PrettyPrinter()

#########################

WAVELENGTHS = {
				"aia" : [94, 131, 171, 193, 211,
							304, 335, 1600, 1700],
				"hmi" : {
						"1" : "hmi.M_720s - LoS MAGNETOGRAM",
						"2" : "hmi.B_720s - VECTOR MAGNETOGRAM",
						"3" : "hmi.sharp_720s - SHARP",
						"4" : "hmi.Ic_noLimbDark_720s - CONTINUUM"
						}
			  }

SEGMENTS = {
			"hmi.M_720s" : {"1" : "magnetogram"},

			"hmi.B_720s" : {"1" : "inclination",
							"2" : "azimuth",
							"3" : "disambig",
							"4" : "field",
							"5" : "vlos_mag",
							"6" : "dop_width",
							"7" : "eta_0",
							"8" : "damping",
							"9" : "src_continuum",
							"10" : "src_grad",
							"11" : "alpha_mag"},

			"hmi.sharp_720s" : {"1" : "magnetogram",
								"2" : "bitmap",
								"3" : "Dopplergram",
								"4" : "contunuum",
								"5" : "inclination",
								"6" : "azimuth",
								"7" : "field",
								"8" : "vlos_mag",
								"9" : "dop_width",
								"10" : "eta_0",
								"11" : "damping",
								"12" : "src_continuum",
								"13" : "src_grad",
								"14" : "alpha_mag"}
			}

#########################

PRINTER.info_text("Instruments: AIA, HMI")
INSTRUMENT = PRINTER.input_text("Enter instrument").lower()

#########################

temp_date = PRINTER.input_text("Enter start date (yyyy-mm-dd)")
temp_time = PRINTER.input_text("Enter start time (hh:mm:ss)")
hour = int(temp_time[0:2])
minute = int(temp_time[3:5])
second = int(temp_time[6:])
day = int(temp_date[8:])
month = int(temp_date[5:7])
year = int(temp_date[0:4])
START_TIME = datetime(year, month, day, hour, minute, second)

#########################

temp_date = PRINTER.input_text("Enter end date (yyyy-mm-dd)")
temp_time = PRINTER.input_text("Enter end time (hh:mm:ss)")
hour = int(temp_time[0:2])
minute = int(temp_time[3:5])
second = int(temp_time[6:])
day = int(temp_date[8:])
month = int(temp_date[5:7])
year = int(temp_date[0:4])
END_TIME = datetime(year, month, day, hour, minute, second)

#########################

CADENCE = int(PRINTER.input_text("Enter cadence (seconds)"))

#########################

if INSTRUMENT == "aia":
	PRINTER.info_text("Wavelengths: %s" % WAVELENGTHS["aia"])
	WAVELENGTH = int(PRINTER.input_text("Enter wavelength (angstroms)"))
	SERIES = "aia.lev1_euv_12s"

elif INSTRUMENT == "hmi":
	PRINTER.info_text("Data series:")
	pp.pprint(WAVELENGTHS["hmi"])
	seriesID = PRINTER.input_text("Enter series ID")
	SERIES = WAVELENGTHS["hmi"][seriesID].split(" ")[0]

	if SERIES == "hmi.M_720s":
		SEGMENT = "magnetogram"
		PRINTER.info_text("Data segment set to 'magnetogram'")

	elif SERIES == "hmi.B_720s":
		PRINTER.info_text("hmi.B_720s data segments:")
		pp.pprint(SEGMENTS["hmi.B_720s"])
		segmentID = PRINTER.input_text("Enter segment ID")
		SEGMENT = SEGMENTS["hmi.B_720s"][segmentID]

	elif SERIES == "hmi.sharp_720s":
		PRINTER.info_text("hmi.sharp_720s data segments:")
		pp.pprint(SEGMENTS["hmi.sharp_720s"])
		segmentID = PRINTER.input_text("Enter segment ID")
		SEGMENT = SEGMENTS["hmi.sharp_720s"][segmentID]

	elif SERIES == "hmi.Ic_noLimbDark_720s":
		SEGMENT = "continuum"
		PRINTER.info_text("Data segment set to 'continuum'")

#########################

PRINTER.line()
PRINTER.info_text("Searching JSOC database")

if INSTRUMENT == "aia":
	results = Fido.search(a.jsoc.Time("%s" % START_TIME.replace(microsecond = 0).isoformat(),
									  "%s" % END_TIME.replace(microsecond = 0).isoformat()),
						  a.jsoc.Notify(EMAIL),
						  a.jsoc.Series(SERIES),
						  a.jsoc.Wavelength(WAVELENGTH * u.angstrom),
						  a.Sample(CADENCE * u.second))

elif INSTRUMENT == "hmi":
	results = Fido.search(a.jsoc.Time("%s" % START_TIME.replace(microsecond = 0).isoformat(),
									  "%s" % END_TIME.replace(microsecond = 0).isoformat()),
						  a.jsoc.Notify(EMAIL),
						  a.jsoc.Series(SERIES),
						  a.jsoc.Segment(SEGMENT),
						  a.Sample(CADENCE * u.second))

PRINTER.info_text("Search complete. Displaying:")
print "\n" + results

#########################

PRINTER.line()
PRINTER.input_text("Press 'enter' to download")

PRINTER.info_text("Moved files in download directory to 'resources/discarded-files'")
if INSTRUMENT == "aia":
	os.system("mv %s/resources/aia-fits-files/*.fits %s/resources/discarded-files" % (MAIN_DIR, MAIN_DIR))
	PRINTER.info_text("Downloading to 'resources/aia-fits-files'\n")
	Fido.fetch(results, path = "%s/resources/aia-fits-files" % MAIN_DIR, progress = False)
	os.system("rm %s/resources/aia-fits-files/*.spikes.fits" % MAIN_DIR)

elif INSTRUMENT == "hmi":
	os.system("mv %s/resources/hmi-fits-files/*.fits %s/resources/discarded-files" % (MAIN_DIR, MAIN_DIR))
	PRINTER.info_text("Downloading to 'resources/hmi-fits-files'\n")
	Fido.fetch(results, path = "%s/resources/hmi-fits-files" % MAIN_DIR, progress = False)

#########################

PRINTER.info_text("Done: %d files downloaded" % len(results[0]))
PRINTER.line()
