import astropy.units as u
from datetime import datetime
import getpass
import itertools
import os
from sunpy.net import Fido, attrs as a
import sunpy.net.vso as vso
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

print "\nAvailable instruments: %s" % possible_instruments

instrument = raw_input("\nEnter instrument:\n==> ").lower()

###

temp_date = raw_input("\nEnter start date: (format yyyy/mm/dd)\n==> ")
temp_time = raw_input("\nEnter start time: (format hh:mm:ss)\n==> ")

hour = int(temp_time[0:2])
minute = int(temp_time[3:5])
second = int(temp_time[6:])
day = int(temp_date[8:])
month = int(temp_date[5:7])
year = int(temp_date[0:4])

start_time = datetime(year, month, day, hour, minute, second)

###

temp_date = raw_input("\nEnter end date: (format yyyy/mm/dd)\n==> ")
temp_time = raw_input("\nEnter end time: (format hh:mm:ss)\n==> ")

hour = int(temp_time[0:2])
minute = int(temp_time[3:5])
second = int(temp_time[6:])
day = int(temp_date[8:])
month = int(temp_date[5:7])
year = int(temp_date[0:4])

end_time = datetime(year, month, day, hour, minute, second)

###

cadence = int(raw_input("\nEnter cadence in seconds:\n==> "))

###

number_of_wavelengths = int(raw_input("\nEnter NUMBER of wavelengths: (up to 4)\n==> "))

print "\nWavelengths for %s: %s" % (instrument, wavelengths[instrument])
inputted_wavelengths = []

for i in range(number_of_wavelengths):
	inputted_wavelengths.append(int(raw_input("\nEnter wavelength %d:\n==> " % (i + 1))))

###
print "\nSearching..."

if number_of_wavelengths == 1:
	results = Fido.search(a.Time("%s" % start_time.replace(microsecond = 0).isoformat(), "%s" % end_time.replace(microsecond = 0).isoformat()), a.Instrument(instrument), a.Wavelength(float(inputted_wavelengths[0]) * u.angstrom), a.vso.Sample(cadence * u.second))
elif number_of_wavelengths == 2:
	results = Fido.search(a.Time("%s" % start_time.replace(microsecond = 0).isoformat(), "%s" % end_time.replace(microsecond = 0).isoformat()), a.Instrument(instrument), a.Wavelength(float(inputted_wavelengths[0]) * u.angstrom) | a.Wavelength(float(inputted_wavelengths[1]) * u.angstrom), a.vso.Sample(cadence * u.second))
elif number_of_wavelengths == 3:
	results = Fido.search(a.Time("%s" % start_time.replace(microsecond = 0).isoformat(), "%s" % end_time.replace(microsecond = 0).isoformat()), a.Instrument(instrument), a.Wavelength(float(inputted_wavelengths[0]) * u.angstrom) | a.Wavelength(float(inputted_wavelengths[1]) * u.angstrom) | a.Wavelength(float(inputted_wavelengths[2]) * u.angstrom), a.vso.Sample(cadence * u.second))
elif number_of_wavelengths == 4:
	results = Fido.search(a.Time("%s" % start_time.replace(microsecond = 0).isoformat(), "%s" % end_time.replace(microsecond = 0).isoformat()), a.Instrument(instrument), a.Wavelength(float(inputted_wavelengths[0]) * u.angstrom) | a.Wavelength(float(inputted_wavelengths[1]) * u.angstrom) | a.Wavelength(float(inputted_wavelengths[2]) * u.angstrom) | a.Wavelength(float(inputted_wavelengths[3]) * u.angstrom), a.vso.Sample(cadence * u.second))

print "\nData search complete. Displaying...\n"
print results

###

if raw_input("Clear source folders? [y/n]\n==> ") == "y":
	print "\nClearing source folders..."
	os.system("rm %s/resources/fits-files/*.fits" % main_dir)

###

raw_input("\nPress ENTER to begin download:\n==> ")
print "\nDownloading..."

Fido.fetch(results, path = "%s/resources/fits-files" % main_dir, progress = False)

print "\nDONE: Files saved to /resources/fits-files"

###

if make_active_region_cutouts:
	os.system("python %s/active-region-cutouts.py" % main_dir)
