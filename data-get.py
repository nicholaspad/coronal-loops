from colortext import Color
from datetime import datetime
from sunpy.net import Fido, attrs as a
import astropy.units as u
import getpass
import itertools
import os
import time





# # # # # # # # # # # OPTIONS # # # # # # # # # # #
# ----------------------------------------------- #
make_active_region_cutouts = False
# ----------------------------------------------- #
# # # # # # # # # # # # # # # # # # # # # # # # # #





os.system("clear")
main_dir = "/Users/%s/Desktop/lmsal" % getpass.getuser()

###

username = getpass.getuser()
possible_instruments = ["aia", "hmi"]
wavelengths = {
	"aia" : [94, 131, 171, 193, 211, 304, 335, 1600, 1700],
	"hmi" : [6173]
}

###

print Color.BOLD_YELLOW + "\nAvailable instruments: %s" % possible_instruments + Color.RESET

instrument = raw_input(Color.BOLD_RED + "\nEnter instrument:\n==> ").lower()

###

temp_date = raw_input(Color.BOLD_RED + "\nEnter start date: (format yyyy/mm/dd)\n==> ")
temp_time = raw_input(Color.BOLD_RED + "\nEnter start time: (format hh:mm:ss)\n==> ")

hour = int(temp_time[0:2])
minute = int(temp_time[3:5])
second = int(temp_time[6:])
day = int(temp_date[8:])
month = int(temp_date[5:7])
year = int(temp_date[0:4])

start_time = datetime(year, month, day, hour, minute, second)

###

temp_date = raw_input(Color.BOLD_RED + "\nEnter end date: (format yyyy/mm/dd)\n==> ")
temp_time = raw_input(Color.BOLD_RED + "\nEnter end time: (format hh:mm:ss)\n==> ")

hour = int(temp_time[0:2])
minute = int(temp_time[3:5])
second = int(temp_time[6:])
day = int(temp_date[8:])
month = int(temp_date[5:7])
year = int(temp_date[0:4])

end_time = datetime(year, month, day, hour, minute, second)

###

cadence = int(raw_input(Color.BOLD_RED + "\nEnter cadence in seconds:\n==> "))

###

if instrument == "aia":
	print Color.BOLD_YELLOW + "\nWavelengths for %s: %s" % (instrument, wavelengths["aia"]) + Color.RESET
	wavelength = int(raw_input(Color.BOLD_RED + "\nEnter wavelength:\n==> "))

elif instrument == "hmi":
	wavelength = 6173

###
print Color.BOLD_YELLOW + "\nSearching..." + Color.RESET

if instrument == "aia" and wavelength != 1600 and wavelength != 1700:
	results = Fido.search(
		a.jsoc.Time("%s" % start_time.replace(microsecond = 0).isoformat(),
				"%s" % end_time.replace(microsecond = 0).isoformat()),
		a.jsoc.Notify("padman@lmsal.com"),
		a.jsoc.Series("aia.lev1_euv_12s"),
		a.jsoc.Wavelength(wavelength * u.angstrom),
		a.Sample(cadence * u.second))

elif instrument == "aia" and (wavelength == 1600 or wavelength == 1700):
	results = Fido.search(
		a.jsoc.Time("%s" % start_time.replace(microsecond = 0).isoformat(),
				"%s" % end_time.replace(microsecond = 0).isoformat()),
		a.jsoc.Notify("padman@lmsal.com"),
		a.jsoc.Series("aia.lev1_uv_24s"),
		a.jsoc.Wavelength(wavelength * u.angstrom),
		a.Sample(cadence * u.second))

print Color.BOLD_YELLOW + "\nData search complete. Displaying...\n" + Color.RESET
print results

###

if raw_input(Color.BOLD_RED + "Clear source folders? [y/n]\n==> ") == "y":
	print Color.BOLD_YELLOW + "\nClearing source folders..." + Color.RESET
	os.system("rm %s/resources/fits-files/*.fits" % main_dir)

###

raw_input(Color.BOLD_RED + "\nPress ENTER to begin download:\n==> ")
print Color.BOLD_YELLOW + "\nDownloading to resources/fits-files...\n" + Color.RESET

Fido.fetch(results, path = "%s/resources/fits-files" % main_dir, progress = False)
os.system("rm %s/resources/fits-files/*.spikes.fits" % main_dir)

print Color.BOLD_YELLOW + "\nDONE: Files saved to resources/fits-files" + Color.RESET

###

if make_active_region_cutouts:
	os.system("python %s/active-region-cutouts.py" % main_dir)
