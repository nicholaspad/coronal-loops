import warnings
warnings.filterwarnings("ignore", message="numpy.dtype size changed")

import argparse
from colortext import Color
import cv2
from matplotlib import pyplot as plt
from tqdm import tqdm
import getpass
import numpy as np
import os
import skimage.io
import sys
import tensorflow as tf

sys.path.append("model-generator/old-training")

from utils import label_map_util
from utils import visualization_utils as vis_util





# # # # # # # # # # # OPTIONS # # # # # # # # # # #
# ----------------------------------------------- #
box_border_thickness = 2
# ----------------------------------------------- #
generate_detection_video = False
# ----------------------------------------------- #
# # # # # # # # # # # # # # # # # # # # # # # # # #




parser = argparse.ArgumentParser()
parser.add_argument("--model")
parser.add_argument("--instr")
args = parser.parse_args()

if args.model == None or args.instr == None:
	print Color.YELLOW + "SPECIFY DETECTION MODEL AND INSTRUMENT WITH --model <filename> --instr <name>" + Color.RESET
	sys.exit()

os.system("clear")
main_dir = "/Users/%s/Desktop/lmsal" % getpass.getuser()

print Color.YELLOW + "MOVING FILES IN DOWNLOAD DIRECTORY TO resources/discarded-files..." + Color.RESET
if args.instr == "aia":
	os.system("mv %s/resources/aia-detected-images/*.jpg %s/resources/discarded-files" % (main_dir, main_dir))
elif args.instr == "hmi":
	os.system("mv %s/resources/hmi-detected-images/*.jpg %s/resources/discarded-files" % (main_dir, main_dir))

print Color.YELLOW + "\nSETTING PATHS..." + Color.RESET
graph_path = "%s/models/%s" % (main_dir, args.model)
label_path = "%s/model-generator/old-training/object_detection/training/object-detection.pbtxt" % main_dir

print Color.YELLOW + "\nIMPORTING DETECTION GRAPH..." + Color.RESET
n_classes = 1
detection_graph = tf.Graph()
with detection_graph.as_default():
	od_graph_def = tf.GraphDef()
	with tf.gfile.GFile(graph_path, "rb") as fid:
		serialized_graph = fid.read()
		od_graph_def.ParseFromString(serialized_graph)
		tf.import_graph_def(od_graph_def, name = "")

print Color.YELLOW + "\nINDEXING DETECTION CATEGORIES..." + Color.RESET
label_map = label_map_util.load_labelmap(label_path)
categories = label_map_util.convert_label_map_to_categories(label_map,
															max_num_classes = n_classes,
															use_display_name = True)
category_index = label_map_util.create_category_index(categories)

print Color.YELLOW + "\nIMPORTING IMAGES..." + Color.RESET
if args.instr == "aia":
	number_of_images = len(next(os.walk("%s/resources/aia-images" % main_dir))[2]) - 2
	names = os.listdir("%s/resources/aia-images" % main_dir)
	names.sort()
	cutout_path = [os.path.join("%s/resources/aia-images" % main_dir, "{}".format(name)) for name in names if name.endswith(".jpg")]
elif args.instr == "hmi":
	number_of_images = len(next(os.walk("%s/resources/hmi-images" % main_dir))[2]) - 2
	names = os.listdir("%s/resources/hmi-images" % main_dir)
	names.sort()
	cutout_path = [os.path.join("%s/resources/hmi-images" % main_dir, "{}".format(name)) for name in names if name.endswith(".jpg")]

image_size = (12, 9)

print ""
i = 0
with detection_graph.as_default():
	with tf.Session(graph = detection_graph) as sess:
		for image_path in tqdm(
							cutout_path,
							desc = Color.YELLOW + "DETECTING ACTIVE REGIONS",
							bar_format = '{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [eta {remaining}, ' '{rate_fmt}]'):
		
			image_np = skimage.io.imread(image_path)
			image_np_expanded = np.expand_dims(image_np, axis = 0)
			image_tensor = detection_graph.get_tensor_by_name("image_tensor:0")

			boxes = detection_graph.get_tensor_by_name("detection_boxes:0")
			scores = detection_graph.get_tensor_by_name("detection_scores:0")
			classes = detection_graph.get_tensor_by_name("detection_classes:0")
			num_detections = detection_graph.get_tensor_by_name("num_detections:0")

			(boxes, scores, classes, num_detections) = sess.run(
					[boxes, scores, classes, num_detections],
					feed_dict = {image_tensor: image_np_expanded})

			vis_util.visualize_boxes_and_labels_on_image_array(
					image_np,
					np.squeeze(boxes),
					np.squeeze(classes).astype(np.int32),
					np.squeeze(scores),
					category_index,
					use_normalized_coordinates = True,
					line_thickness = box_border_thickness)

			plt.figure()

			image_np = image_np[:,:,::-1]

			if args.instr == "aia":
				cv2.imwrite("%s/resources/aia-detected-images/detected-%03d.jpg" % (main_dir, i), image_np)
			elif args.instr == "hmi":
				cv2.imwrite("%s/resources/hmi-detected-images/detected-%03d.jpg" % (main_dir, i), image_np)

			plt.close()
			i += 1

print Color.YELLOW + "\nDONE\n" + Color.RESET
