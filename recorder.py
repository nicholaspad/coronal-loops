from colortext import Color
from datetime import datetime
from tqdm import tqdm
import getpass
import numpy as np
import os
import time

MAIN_DIR = "/Users/%s/Desktop/lmsal" % getpass.getuser()

class Recorder(object):

	def __init__(self, database_name = ""):
		self.DATABASE_NAME = "/Users/%s/Desktop/lmsal/resources/region-data/%s" % (getpass.getuser(), database_name)
		self.INFO = Color.RESET + Color.GREEN + Color.BOLD + "[INFO]\t" + Color.RESET + Color.WHITE
		self.INPUT = Color.RESET + Color.RED + Color.BOLD + "[INPUT]\t" + Color.RESET + Color.YELLOW
		self.INFO_TAB = Color.RESET + Color.BLUE + Color.BOLD + "[INFO]\t==> " + Color.RESET + Color.YELLOW
		self.WRITE = Color.RESET + Color.GREEN + Color.BOLD + "[WRITE]\t" + Color.RESET + Color.YELLOW
		self.PARAM = Color.RESET + Color.GREEN + "[PARAM]\t" + Color.RESET + Color.YELLOW
		self.SYS = Color.RESET + Color.YELLOW + Color.BOLD + "[SYS]\t" + Color.RESET + Color.WHITE
		self.WARN = Color.RESET + Color.RED + Color.BOLD + "[WARN]\t" + Color.RESET + Color.YELLOW
		self.NEW_LINE = Color.RESET + Color.WHITE + "\n" + "-" * 75

		if database_name != "":
			with open(self.DATABASE_NAME, "w") as db:
				db.write("ID,DATE,TIME,PXL_X,PXL_Y,HPC_X,HPC_Y,PXL_SIZE_X,PXL_SIZE_Y,HPC_SIZE_X,HPC_SIZE_Y,304_LOW_THRESH_INTEN,304_AVG_INTEN,304_MED_INTEN,304_MAX_INTEN,UNSIG_GAUSS,AVG_GAUSS,MED_GAUSS\n")

	def info_text(self, text):
		tqdm.write("\t" + self.INFO + text)

	def sys_text(self, text):
		tqdm.write("\t" + self.SYS + text)

	def write_ID(self, ID):
		print self.INFO + "Loop %05d" % ID
		with open(self.DATABASE_NAME, "a") as db:
			print self.WRITE + "Recording ID"
			print self.INFO_TAB + "%05d" % ID
			db.write("%05d," % ID)
		self.rest()

	def show_instr(self, instr):
		print self.INFO + instr

	def write_datetime(self, datetime):
		with open(self.DATABASE_NAME, "a") as db:
			when = datetime.strftime("%Y-%m-%d %H:%M:%S")
			print self.WRITE + "Recording date and time"
			date = when.split(" ")[0]
			time = when.split(" ")[1]
			print self.INFO_TAB + "%s" % date
			print self.INFO_TAB + "%s" % time
			db.write("%s,%s," % (date, time))
		self.rest()

	def write_xywhere(self, where):
		with open(self.DATABASE_NAME, "a") as db:
			where_x = where[1]
			where_y = where[0]
			print self.WRITE + "Recording cartesian pixel location"
			print self.INFO_TAB + "(%d px, %d px)" % (where_x, where_y)
			db.write("%d,%d," % (where_x, where_y))
		self.rest()

	def write_hpcwhere(self, where):
		with open(self.DATABASE_NAME, "a") as db:
			where_x = where.Tx.value
			where_y = where.Ty.value
			print self.WRITE + "Recording helioprojective coordinate location"
			print self.INFO_TAB + "(%.3f arcsec, %.3f arcsec)" % (where_x, where_y)
			db.write("%.3f,%.3f," % (where_x, where_y))
		self.rest()

	def write_xysize(self, size):
		with open(self.DATABASE_NAME, "a") as db:
			print self.WRITE + "Recording pixel size"
			print self.INFO_TAB + "%d px x %d px" % (size, size)
			db.write("%d,%d," % (size, size))
		self.rest()

	def write_hpcsize(self, bl, tr):
		with open(self.DATABASE_NAME, "a") as db:
			size_x = tr.Tx.value - bl.Tx.value
			size_y = tr.Ty.value - bl.Ty.value
			print self.WRITE + "Recording helioprojective size"
			print self.INFO_TAB + "%d arcsec x %d arcsec" % (size_x, size_y)
			db.write("%d,%d," % (size_x, size_y))
		self.rest()

	def write_inten(self, low_thresh, avg, med, max):
		with open(self.DATABASE_NAME, "a") as db:
			print self.WRITE + "Recording intensity low threshold"
			print self.INFO_TAB + "%.1f" % low_thresh
			db.write("%.1f," % low_thresh)
			print self.WRITE + "Recording average intensity"
			print self.INFO_TAB + "%.1f" % avg
			db.write("%.1f," % avg)
			print self.WRITE + "Recording median intensity"
			print self.INFO_TAB + "%.0f" % med
			db.write("%.0f," % med)
			print self.WRITE + "Recording maximum intensity"
			print self.INFO_TAB + "%.0f" % max
			db.write("%.0f," % max)
		self.rest()

	def write_gauss(self, unsig, avg, median):
		with open(self.DATABASE_NAME, "a") as db:
			print self.WRITE + "Recording total unsigned gauss"
			print self.INFO_TAB + "%.1f" % unsig
			db.write("%.3f," % unsig)
			print self.WRITE + "Recording average signed gauss"
			print self.INFO_TAB + "%.3f" % avg
			db.write("%.3f," % avg)
			print self.WRITE + "Recording median signed gauss"
			print self.INFO_TAB + "%.3f" % median
			db.write("%.3f," % median)
		self.rest()

	def write_image(self, type, id, data, instr, wav):
		if type == 0:
			name = "raw image"
			dir = "resources/region-data/raw-images"
		elif type == 1:
			name = "masked image"
			dir = "resources/region-data/r-masked-images"
		elif type == 2:
			name = "elliptically-masked image"
			dir = "resources/region-data/e-masked-images"
		elif type == 3:
			name = "contour-masked image"
			dir = "resources/region-data/c-masked-images"
		
		print self.WRITE + "Saving '%s' to '%s'" % (name, dir)
		
		print self.INFO_TAB + "%05d%s%d.npy" % (id, instr, int(wav.value))
		np.save("%s/%s/%05d%s%d" % (MAIN_DIR, dir, id, instr, int(wav.value)), data)
		self.rest()

	def new_line(self):
		with open(self.DATABASE_NAME, "rb+") as db:
			print self.INFO + "Finished entry; recording new line" + self.NEW_LINE
			db.seek(-1, os.SEEK_END)
			db.truncate()
			db.write("\n")
		self.rest()

	def line(self):
		print self.NEW_LINE

	def off_disk(self):
		print self.WARN + "Off-disk region identified; skipping"
		with open(self.DATABASE_NAME, "r") as db:
			lines = db.readlines()
		with open(self.DATABASE_NAME, "w") as db:
			for i in range(len(lines) - 1):
				db.write(lines[i])
		self.new_line()

	def too_small(self):
		print self.WARN + "Region to small; skipping"
		with open(self.DATABASE_NAME, "r") as db:
			lines = db.readlines()
		with open(self.DATABASE_NAME, "w") as db:
			for i in range(len(lines) - 1):
				db.write(lines[i])
		self.new_line()

	def rest(self):
		time.sleep(0.05)

	def input_text(self, text):
		return raw_input("\n" + self.INPUT + "%s:\n\t==> " % text + Color.YELLOW)

	def display_item(self, desc, item):
		print "\n" + self.PARAM + "%s\n%s" % (desc, item)

	def display_start_time(self, name):
		self.start_time = datetime.now()
		print "\n" + self.SYS + "Process %s started at %s" % (name, datetime.now().replace(microsecond = 0))
		print self.NEW_LINE

	def display_end_time(self, name):
		self.delta = datetime.now() - self.start_time
		print "\n" + self.SYS + "Process %s ended at %s" % (name, datetime.now().replace(microsecond = 0))
		print self.SYS + "Execution time: %s" % str(self.delta).split(".")[0]
		print self.NEW_LINE
		print Color.RESET

	def remove_duplicates(self):
		print self.WARN + "Removing duplicates"
		with open(self.DATABASE_NAME, "r") as db:
			lines = db.readlines()

		for i in range(len(lines)):
			lines[i] = lines[i].split(",")

		with open(self.DATABASE_NAME, "w") as db:
			db.write(",".join(lines[0]))
			for i in range(2, len(lines)):
				if (np.abs(int(lines[i][3]) - int(lines[i - 1][3])) > 20) and (np.abs(int(lines[i][4]) - int(lines[i - 1][4])) > 20):
					db.write(",".join(lines[i - 1]))
			db.write(",".join(lines[len(lines) - 1]))
