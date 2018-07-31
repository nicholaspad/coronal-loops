from colortext import Color
from datetime import datetime
import getpass
import numpy as np
import os

class Recorder(object):

	def __init__(self, database_name):
		self.DATABASE_NAME = "/Users/%s/Desktop/lmsal/resources/region-data/%s" % (getpass.getuser(), database_name)
		self.INFO = Color.RED + "[INFO]\t" + Color.YELLOW
		self.WRITE = Color.GREEN + "[WRITE]\t" + Color.YELLOW
		self.NEW_LINE = Color.WHITE + "\n" + "-" * 75

		with open(self.DATABASE_NAME, "w") as db:
			db.write("ID,DATE,TIME,PXL_X,PXL_Y,HPC_X,HPC_Y,PXL_SIZE_X,PXL_SIZE_Y,HPC_SIZE_X,HPC_SIZE_Y,INTEN_LOW_THRESH,INTEN_HIGH_THRESH,AVG_INTEN,MED_INTEN,MAX_INTEN,\n")

		print self.NEW_LINE

	def write_ID(self, ID):
		print self.INFO + "Loop ID %05d" % ID
		with open(self.DATABASE_NAME, "a") as db:
			print self.WRITE + "Recording ID"
			db.write("%05d," % ID)

	def write_datetime(self, datetime):
		with open(self.DATABASE_NAME, "a") as db:
			when = datetime.strftime("%Y-%m-%d %H:%M:%S")
			print self.WRITE + "Recording datetime"
			date = when.split(" ")[0]
			time = when.split(" ")[1]
			db.write("%s,%s," % (date, time))

	def write_xywhere(self, where):
		with open(self.DATABASE_NAME, "a") as db:
			where_x = where[0]
			where_y = where[1]
			print self.WRITE + "Recording cartesian pixel location"
			db.write("%d,%d," % (where_x, where_y))

	def write_hpcwhere(self, where):
		with open(self.DATABASE_NAME, "a") as db:
			where_x = where.Tx.value
			where_y = where.Ty.value
			print self.WRITE + "Recording helioprojective coordinate location"
			db.write("%.3f,%.3f," % (where_x, where_y))

	def write_xysize(self, size):
		with open(self.DATABASE_NAME, "a") as db:
			print self.WRITE + "Recording pixel size"
			db.write("%d,%d," % (size, size))

	def write_hpcsize(self, bl, tr):
		with open(self.DATABASE_NAME, "a") as db:
			size_x = tr.Tx.value - bl.Tx.value
			size_y = tr.Ty.value - bl.Ty.value
			print self.WRITE + "Recording helioprojective size"
			db.write("%d,%d," % (size_x, size_y))

	def write_inten(self, avg, med, max):
		with open(self.DATABASE_NAME, "a") as db:
			print self.WRITE + "Recording average intensity"
			db.write("%.3f," % avg)
			print self.WRITE + "Recording median intensity"
			db.write("%.3f," % med)
			print self.WRITE + "Recording maximum intensity"
			db.write("%.3f," % max)

	def new_line(self):
		with open(self.DATABASE_NAME, "rb+") as db:
			print self.INFO + "Finished entry, Recording new line" + self.NEW_LINE
			db.seek(-1, os.SEEK_END)
			db.truncate()
			db.write("\n")
