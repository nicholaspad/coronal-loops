import warnings
warnings.filterwarnings("ignore", message="numpy.dtype size changed")

from colortext import Color
from datetime import datetime
from sunpy.net import Fido, attrs as a
import astropy.units as u
import getpass
import os
import pprint

main_dir = "/Users/%s/Desktop/lmsal" % getpass.getuser()
pp = pprint.PrettyPrinter()

###

possible_instruments = ["AIA", "HMI"]

wavelengths = {
	"aia" : [94, 131, 171, 193, 211,
				304, 335, 1600, 1700],
	"hmi" : {
			"1" : "hmi.M_720s - LoS MAGNETOGRAM",
			"2" : "hmi.B_720s - VECTOR MAGNETOGRAM",
			"3" : "hmi.sharp_720s - SHARP",
			"4" : "hmi.Ic_noLimbDark_720s - CONTINUUM"
			}
	}

segments = {
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

###

os.system("clear")

print Color.YELLOW + "INSTRUMENTS:"
pp.pprint(possible_instruments)

instrument = raw_input(Color.BOLD_RED + "\nINSTRUMENT:\n==> ").lower()

###

temp_date = raw_input(Color.BOLD_RED + "\nSTART DATE: (FORMAT YYYY/MM/DD)\n==> ")
temp_time = raw_input(Color.BOLD_RED + "\nSTART TIME: (FORMAT HH:MM:SS)\n==> ")

hour = int(temp_time[0:2])
minute = int(temp_time[3:5])
second = int(temp_time[6:])
day = int(temp_date[8:])
month = int(temp_date[5:7])
year = int(temp_date[0:4])

start_time = datetime(year, month, day, hour, minute, second)

###

temp_date = raw_input(Color.BOLD_RED + "\nEND DATE: (FORMAT YYYY/MM/DD)\n==> ")
temp_time = raw_input(Color.BOLD_RED + "\nEND TIME: (FORMAT HH:MM:SS)\n==> ")

hour = int(temp_time[0:2])
minute = int(temp_time[3:5])
second = int(temp_time[6:])
day = int(temp_date[8:])
month = int(temp_date[5:7])
year = int(temp_date[0:4])

end_time = datetime(year, month, day, hour, minute, second)

###

cadence = int(raw_input(Color.BOLD_RED + "\nCADENCE (SECONDS):\n==> "))

###

if instrument == "aia":
	print Color.YELLOW + "\nAIA WAVELENGTHS (ANGSTROMS):"
	pp.pprint(wavelengths["aia"])
	wavelength = int(raw_input(Color.BOLD_RED + "\nWAVELENGTH:\n==> "))

elif instrument == "hmi":
	print Color.YELLOW + "\nDATA SERIES:"
	pp.pprint(wavelengths["hmi"])
	seriesId = raw_input(Color.BOLD_RED + "\nSERIES ID: (ENTER NUMBER)\n==> ")
	series = wavelengths["hmi"][seriesId].split(" ")[0]

	if series == "hmi.M_720s":
		print Color.YELLOW + "\nDATA SEGMENT SET TO MAGNETOGRAM"
		segment = "magnetogram"

	elif series == "hmi.B_720s":
		print Color.YELLOW + "\nHMI.B_720s DATA SEGMENTS:"
		pp.pprint(segments["hmi.B_720s"])
		segmentId = raw_input(Color.BOLD_RED + "\nSEGMENT ID: (ENTER NUMBER)\n==> ")
		segment = segments["hmi.B_720s"][segmentId]

	elif series == "hmi.sharp_720s":
		print Color.YELLOW + "\nHMI.SHARP_720s DATA SEGMENTS:"
		pp.pprint(segments["hmi.sharp_720s"])
		segmentId = raw_input(Color.BOLD_RED + "\nSEGMENT ID: (ENTER NUMBER)\n==> ")
		segment = segments["hmi.sharp_720s"][segmentId]

	elif series == "hmi.Ic_noLimbDark_720s":
		print Color.YELLOW + "\nDATA SEGMENT SET TO CONTINUUM"
		segment = "continuum"

###

print Color.YELLOW + "\nSEARCHING..." + Color.RESET

if instrument == "aia":
	if wavelength != 1600 and wavelength != 1700:
		results = Fido.search(
			a.jsoc.Time("%s" % start_time.replace(microsecond = 0).isoformat(),
					"%s" % end_time.replace(microsecond = 0).isoformat()),
			a.jsoc.Notify("padman@lmsal.com"),
			a.jsoc.Series("aia.lev1_euv_12s"),
			a.jsoc.Wavelength(wavelength * u.angstrom),
			a.Sample(cadence * u.second))

	else:
		results = Fido.search(
			a.jsoc.Time("%s" % start_time.replace(microsecond = 0).isoformat(),
					"%s" % end_time.replace(microsecond = 0).isoformat()),
			a.jsoc.Notify("padman@lmsal.com"),
			a.jsoc.Series("aia.lev1_uv_24s"),
			a.jsoc.Wavelength(wavelength * u.angstrom),
			a.Sample(cadence * u.second))

elif instrument == "hmi":
	results = Fido.search(
			a.jsoc.Time("%s" % start_time.replace(microsecond = 0).isoformat(),
					"%s" % end_time.replace(microsecond = 0).isoformat()),
			a.jsoc.Notify("padman@lmsal.com"),
			a.jsoc.Series(series),
			a.jsoc.Segment(segment),
			a.Sample(cadence * u.second))

print Color.YELLOW + "\nSEARCH COMPLETE. DISPLAYING...\n" + Color.RESET
print results

###

raw_input(Color.BOLD_RED + "PRESS ENTER TO DOWNLOAD\n==> ")

print Color.YELLOW + "\nMOVING FILES IN DOWNLOAD DIRECTORY TO resources/discarded-files..." + Color.RESET
if instrument == "aia":
	os.system("mv %s/resources/aia-fits-files/*.fits %s/resources/discarded-files" % (main_dir, main_dir))
	print Color.YELLOW + "\nDOWNLOADING TO resources/aia-fits-files...\n"
	Fido.fetch(results, path = "%s/resources/aia-fits-files" % main_dir, progress = False)
	os.system("rm %s/resources/aia-fits-files/*.spikes.fits" % main_dir)

elif instrument == "hmi":
	os.system("mv %s/resources/hmi-fits-files/*.fits %s/resources/discarded-files" % (main_dir, main_dir))
	print Color.YELLOW + "\nDOWNLOADING TO resources/hmi-fits-files...\n"
	Fido.fetch(results, path = "%s/resources/hmi-fits-files" % main_dir, progress = False)
	
print "\nDONE" + Color.RESET
