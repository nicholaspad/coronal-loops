import warnings
warnings.filterwarnings("ignore", message="numpy.dtype size changed")

from colortext import Color
import glob
import os
import pandas as pd
import xml.etree.ElementTree as ET

def xml_to_csv(path):
	xml_list = []
	for xml_file in glob.glob(path + "/*.xml"):
		tree = ET.parse(xml_file)
		root = tree.getroot()
		for member in root.findall("object"):
			value = (root.find("filename").text,
					 int(root.find("size")[0].text),
					 int(root.find("size")[1].text),
					 member[0].text,
					 int(member[4][0].text),
					 int(member[4][1].text),
					 int(member[4][2].text),
					 int(member[4][3].text)
					 )
			xml_list.append(value)
	column_name = ["filename", "width", "height", "class", "xmin", "ymin", "xmax", "ymax"]
	xml_df = pd.DataFrame(xml_list, columns=column_name)
	return xml_df

def main():
	os.system("rm data/test_labels.csv && rm data/train_labels.csv")
	for directory in ["train","test"]:
		image_path = os.path.join(os.getcwd(), "images/{}".format(directory))
		xml_df = xml_to_csv(image_path)
		xml_df.to_csv("{}_labels.csv".format(directory), index=None)
		print Color.YELLOW + "Successfully generated {}_labels.csv".format(directory) + Color.RESET
	os.system("mv test_labels.csv data && mv train_labels.csv data")
	os.system("python helper-2.py --csv_input=data/train_labels.csv  --output_path=data/train.record")
	os.system("python helper-2.py --csv_input=data/test_labels.csv  --output_path=data/test.record")
	os.system("rm data/test_labels.csv && rm data/train_labels.csv")
	print Color.YELLOW + "Successfully created train.record and test.record"
	print Color.YELLOW + "Copy contents of 'data' directory to 'object_detection/data' and begin training with model_main.py" + Color.RESET
	os.system("rm -rf images/test && rm -rf images/train && rm images/*.xml")

main()
