import warnings
warnings.filterwarnings("ignore", message = "numpy.dtype size changed")

from colortext import Color
from matplotlib import pyplot as plt
from recorder import Recorder
from tqdm import tqdm
import argparse
import cv2
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





MAIN_DIR = "/Users/%s/Desktop/lmsal" % getpass.getuser()
PRINTER = Recorder()
PRINTER.display_start_time("apply-region-detection")
parser = argparse.ArgumentParser()
parser.add_argument("--model")
parser.add_argument("--instr")
args = parser.parse_args()

#########################

if args.model == None or args.instr == None:
	PRINTER.info_text("Specify model and instrument with '--model <filename> --instr <name>'")
	PRINTER.line()
	sys.exit()

INSTRUMENT = args.instr.lower()
MODEL = args.model.lower()

#########################

PRINTER.info_text("Moved files in download directory to 'resources/discarded-files'")
if INSTRUMENT == "aia":
	os.system("mv %s/resources/aia-detected-images/*.jpg %s/resources/discarded-files" % (MAIN_DIR, MAIN_DIR))
elif INSTRUMENT == "hmi":
	os.system("mv %s/resources/hmi-detected-images/*.jpg %s/resources/discarded-files" % (MAIN_DIR, MAIN_DIR))

#########################

PRINTER.info_text("Setting paths")
GRAPH_PATH = "%s/models/%s" % (MAIN_DIR, MODEL)
LABEL_PATH = "%s/model-generator/old-training/object_detection/training/object-detection.pbtxt" % MAIN_DIR

#########################

PRINTER.info_text("Importing graph")
NUM_CLASSES = 1
GRAPH = tf.Graph()

#########################

with GRAPH.as_default():
	od_graph_def = tf.GraphDef()
	with tf.gfile.GFile(GRAPH_PATH, "rb") as fid:
		serialized_graph = fid.read()
		od_graph_def.ParseFromString(serialized_graph)
		tf.import_graph_def(od_graph_def, name = "")

#########################

PRINTER.info_text("Indexing detection categories")
LABEL_MAP = label_map_util.load_labelmap(LABEL_PATH)
CATEGORIES = label_map_util.convert_label_map_to_categories(LABEL_MAP,
															max_num_classes = NUM_CLASSES,
															use_display_name = True)
CATEGORY_INDEX = label_map_util.create_category_index(CATEGORIES)

#########################

PRINTER.info_text("Importing images")
if INSTRUMENT == "aia":
	number_of_images = len(next(os.walk("%s/resources/aia-images" % MAIN_DIR))[2]) - 2
	names = os.listdir("%s/resources/aia-images" % MAIN_DIR)
	names.sort()
	cutout_path = [os.path.join("%s/resources/aia-images" % MAIN_DIR, "{}".format(name)) for name in names if name.endswith(".jpg")]
elif INSTRUMENT == "hmi":
	number_of_images = len(next(os.walk("%s/resources/hmi-images" % MAIN_DIR))[2]) - 2
	names = os.listdir("%s/resources/hmi-images" % MAIN_DIR)
	names.sort()
	cutout_path = [os.path.join("%s/resources/hmi-images" % MAIN_DIR, "{}".format(name)) for name in names if name.endswith(".jpg")]

#########################

PRINTER.line()

print ""
ID = 0

with GRAPH.as_default():
	with tf.Session(graph = GRAPH) as sess:
		for image_path in tqdm(
							cutout_path,
							desc = Color.YELLOW + "Detecting",
							bar_format = "{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [eta {remaining}, " "{rate_fmt}]"):
		
			image_np = skimage.io.imread(image_path)
			image_np_expanded = np.expand_dims(image_np, axis = 0)
			image_tensor = GRAPH.get_tensor_by_name("image_tensor:0")

			boxes = GRAPH.get_tensor_by_name("detection_boxes:0")
			scores = GRAPH.get_tensor_by_name("detection_scores:0")
			classes = GRAPH.get_tensor_by_name("detection_classes:0")
			num_detections = GRAPH.get_tensor_by_name("num_detections:0")

			(boxes, scores, classes, num_detections) = sess.run(
					[boxes, scores, classes, num_detections],
					feed_dict = {image_tensor: image_np_expanded})

			vis_util.visualize_boxes_and_labels_on_image_array(
					image_np,
					np.squeeze(boxes),
					np.squeeze(classes).astype(np.int32),
					np.squeeze(scores),
					CATEGORY_INDEX,
					use_normalized_coordinates = True,
					line_thickness = box_border_thickness)

			plt.figure()

			image_np = image_np[:, :, ::-1]

			if INSTRUMENT == "aia":
				cv2.imwrite("%s/resources/aia-detected-images/detected-%03d.jpg" % (MAIN_DIR, ID), image_np)
			elif INSTRUMENT == "hmi":
				cv2.imwrite("%s/resources/hmi-detected-images/detected-%03d.jpg" % (MAIN_DIR, ID), image_np)

			plt.close()
			ID += 1

#########################

PRINTER.info_text("Done")
PRINTER.line()
