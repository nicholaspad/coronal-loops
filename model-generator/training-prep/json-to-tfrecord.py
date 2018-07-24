from colortext import Color
import getpass
import glob
import json
import os
import time

os.system("clear")
os.system("touch temp.txt")

with open("data.json") as f:
	data = json.load(f)

with open("temp.txt", "w") as f:
	f.write("filename,width,height,class,xmin,ymin,xmax,ymax\n")
	for i in range(len(data)):
		for j in range(len(data[i]["Label"]["ACTIVE REGION"])):
			f.write("%s,%d,%d,%s,%d,%d,%d,%d\n" % (
					data[i]["External ID"],
					2204,
					2204,
					"ACTIVE REGION",
					data[i]["Label"]["ACTIVE REGION"][j]["geometry"][1]["x"],
					data[i]["Label"]["ACTIVE REGION"][j]["geometry"][1]["y"],
					data[i]["Label"]["ACTIVE REGION"][j]["geometry"][3]["x"],
					data[i]["Label"]["ACTIVE REGION"][j]["geometry"][3]["y"]
					))

with open("temp.txt") as f:
	info = [line.split(",") for line in f]

for i in range(len(info)):
	info[i][7] = info[i][7][:-1]

names = os.listdir("/Users/%s/Desktop/lmsal/model-generator/training-prep/images" % getpass.getuser())
names.sort()
os.system("rm images/*.xml")
num_files = 0

for name in names:
	if name.endswith(".jpg"):
		num_files += 2
		with open("images/%s.xml" % name[:-4], "w") as f:
			f.write("<annotation>\n")
			f.write("\t<folder>images</folder>\n")
			f.write("\t<filename>%s</filename>\n" % name)
			f.write("\t<path>/Users/%s/Desktop/lmsal/model-generator/training-prep/images/.jpg</path>\n" % (getpass.getuser(), name))
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

print Color.BOLD_YELLOW + "XML files successfully generated" + Color.RESET

os.system("rm temp.txt")

names = os.listdir("/Users/%s/Desktop/lmsal/model-generator/training-prep/images" % getpass.getuser())
names.sort()

train_files = int(num_files * 0.95)

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

os.system("rm images/test/*.xml && rm images/test/*.jpg")
os.system("rm images/train/*.xml && rm images/train/*.jpg")

for name in train_names:
	os.system("cp images/%s images/train" % name)

for name in test_names:
	os.system("cp images/%s images/test" % name)

print Color.BOLD_YELLOW + "Images and annotations successfully sorted into test and train directories" + Color.RESET
time.sleep(1)
os.system("python helper-1.py")
