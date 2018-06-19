import csv
import time
import tools

class Importer(object):

	def __init__(self):
		self.data_file_names = []
		self.filepath = ""

	def importlist(self):
		path = self.asklistpath()
		with open(path, "r") as dl:
			self.loadprogress()
			data = csv.reader(dl)
			for datum in data:
				self.data_file_names.append(datum)
		self.asktoview()

	def asklistpath(self):
		prompt = "Specify data list filepath: (Example: data/file_list.txt)\n==> "
		path = raw_input(prompt)
		self.filepath = path
		return path

	def asktoview(self):
		input = raw_input("View list? (y/n)\n==> ")
		if input != "y" and input != "n":
			self.asktoview()
		elif input == "y":
			print self
		else:
			print "Continuing..."
			time.sleep(0.15)

	def loadprogress(self):
		final = 100
		n = 0
		while n <= final:
			tools.bar(n, final, " IMPORTING")
			time.sleep(0.15)
			n += 5

	def __str__(self):
		repr = ""
		id = 1
		for file in self.data_file_names:
			for name in file:
				if name[0] != "#":
					repr += "(ID#%02d) > %s | %s | %s | %s | %s\n" % (id, name[0:3].upper(), "lev " + str(name[7]), str(name[9:11] + " A"), "%s %s, %s" % (tools.parsemonth(int(name[18:20])), name[21:23], name[13:17]), name[24:32])
					id += 1
		return repr
