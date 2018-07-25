import warnings
warnings.filterwarnings("ignore", message="numpy.dtype size changed")

from colortext import Color
import getpass
import glob
import json
import numpy as np
import os
import time

os.system("clear")
os.system("touch temp.txt")
os.system("mkdir images/train")
os.system("mkdir images/test")

with open("data.json") as f:
	data = json.load(f)

with open("temp.txt", "w") as f:
	f.write("filename,width,height,class,xmin,ymin,xmax,ymax\n")
	for i in range(len(data)):
		if data[i]["Label"] != "Skip":
			for j in range(len(data[i]["Label"]["active region"])):
				f.write("%s,%d,%d,%s,%d,%d,%d,%d\n" % (
						data[i]["External ID"],
						2204,
						2204,
						"active region",
						data[i]["Label"]["active region"][j]["geometry"][1]["x"],
						data[i]["Label"]["active region"][j]["geometry"][1]["y"],
						data[i]["Label"]["active region"][j]["geometry"][3]["x"],
						data[i]["Label"]["active region"][j]["geometry"][3]["y"]
						))

data = []
with open("temp.txt") as f:
	data.append([line.split(",") for line in f])

data = np.array(data)
data = data.reshape(data.shape[1:])
data = np.delete(data, 0, 0)

for i in range(1, len(data)):
	if int(data[i][6]) <= int(data[i][4]):
		data[i][6], data[i][4] = data[i][4], data[i][6]
	elif int(data[i][7]) <= int(data[i][5]):
		data[i][7], data[i][5] = data[i][5], data[i][7]

with open("temp.txt", "w") as f:
	f.write("filename,width,height,class,xmin,ymin,xmax,ymax\n")
	for i in range(0, len(data)):
		f.write("%s,%d,%d,%s,%d,%d,%d,%s\n" % (
				data[i][0],
				2204,
				2204,
				"active region",
				int(data[i][4]),
				int(data[i][5]),
				int(data[i][6]),
				int(data[i][7])
				))

to_delete = ["cut-%03d.jpg" % i for i in range(242)]
to_delete = np.array(to_delete)

with open("to_delete.txt", "w") as f:
	for i in range(len(data)):
		name = np.argwhere(to_delete == data[i][0])
		to_delete = np.delete(to_delete, name, 0)

for i in range(len(to_delete)):
	os.system("rm images/%s" % to_delete[i])

os.system("rm to_delete.txt")

with open("temp.txt") as f:
	info = [line.split(",") for line in f]

for i in range(len(info)):
	info[i][7] = info[i][7][:-1]

names = os.listdir("/Users/%s/Desktop/lmsal/model-generator/training-prep/images" % getpass.getuser())
os.system("rm images/*.xml")
num_files = 0

for name in names:
	if name.endswith(".jpg"):
		num_files += 2
		with open("images/%s.xml" % name[:-4], "w") as f:
			f.write("<annotation>\n")
			f.write("\t<folder>images</folder>\n")
			f.write("\t<filename>%s</filename>\n" % name)
			f.write("\t<path>/Users/%s/Desktop/lmsal/model-generator/training-prep/images/%s.jpg</path>\n" % (getpass.getuser(), name))
			f.write("\t<source>\n")
			f.write("\t\t<database>Unknown</database>\n")
			f.write("\t</source>\n")
			f.write("\t<size>\n")
			f.write("\t\t<width>2204</width>\n")
			f.write("\t\t<height>2204</height>\n")
			f.write("\t\t<depth>3</depth>\n")
			f.write("\t</size>\n")
			f.write("\t<segmented>0</segmented>\n")

			for j in range(len(info)):
				if info[j][0] == ("%s" % name):
					f.write("\t<object>\n")
					f.write("\t\t<name>active region</name>\n")
					f.write("\t\t<pose>Unspecified</pose>\n")
					f.write("\t\t<truncated>0</truncated>\n")
					f.write("\t\t<difficult>0</difficult>\n")
					f.write("\t\t<bndbox>\n")
					f.write("\t\t\t<xmin>%s</xmin>\n" % info[j][4])
					f.write("\t\t\t<ymin>%s</ymin>\n" % info[j][5])
					f.write("\t\t\t<xmax>%s</xmax>\n" % info[j][6])
					f.write("\t\t\t<ymax>%s</ymax>\n" % info[j][7])
					f.write("\t\t</bndbox>\n")
					f.write("\t</object>\n")

			f.write("</annotation>\n")

print Color.YELLOW + "XML files successfully generated" + Color.RESET

os.system("rm temp.txt")

names = os.listdir("/Users/%s/Desktop/lmsal/model-generator/training-prep/images" % getpass.getuser())
names.sort()

train_files = int(num_files * 0.9)

if train_files % 2 != 0:
	train_files -= 1

train_names = []
test_names = []

for i in range(0, train_files):
	if names[i].endswith(".jpg") | names[i].endswith(".xml"):
		train_names.append(names[i])

for i in range(train_files, len(names)):
	if names[i].endswith(".jpg") | names[i].endswith(".xml"):
		test_names.append(names[i])

for name in train_names:
	os.system("cp images/%s images/train" % name)

for name in test_names:
	os.system("cp images/%s images/test" % name)

print Color.YELLOW + "Images and annotations successfully sorted into test and train directories" + Color.RESET
os.system("python helper-1.py")
