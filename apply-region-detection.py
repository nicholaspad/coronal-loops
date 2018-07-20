from collections import defaultdict
from colortext import Color
from matplotlib import pyplot as plt
from tqdm import tqdm
import getpass
import lycon
import numpy as np
import os
import skimage.io
import sys
import tensorflow as tf

sys.path.append("model-generator/")

from utils import label_map_util
from utils import visualization_utils as vis_util





# # # # # # # # # # # OPTIONS # # # # # # # # # # #
# ----------------------------------------------- #
box_border_thickness = 2
# ----------------------------------------------- #
generate_detection_video = False
# ----------------------------------------------- #
# # # # # # # # # # # # # # # # # # # # # # # # # #





os.system("clear")
main_dir = "/Users/%s/Desktop/lmsal" % getpass.getuser()

print Color.BOLD_YELLOW + "\nCLEARING SOURCE FOLDERS..." + Color.RESET
os.system("rm %s/resources/region-detection-images/*.jpg" % main_dir)

print Color.BOLD_YELLOW + "\nSETTING PATHS..." + Color.RESET
graph_path = "%s/model-generator/object_detection/active_region/active_region_frozen_graph.pb" % main_dir
label_path = os.path.join("%s/model-generator/object_detection/training" % main_dir, "object-detection.pbtxt")

print Color.BOLD_YELLOW + "\nIMPORTING DETECTION GRAPH..." + Color.RESET
n_classes = 1
detection_graph = tf.Graph()
with detection_graph.as_default():
	od_graph_def = tf.GraphDef()
	with tf.gfile.GFile(graph_path, "rb") as fid:
		serialized_graph = fid.read()
		od_graph_def.ParseFromString(serialized_graph)
		tf.import_graph_def(od_graph_def, name = "")

print Color.BOLD_YELLOW + "\nINDEXING DETECTION CATEGORIES..." + Color.RESET
label_map = label_map_util.load_labelmap(label_path)
categories = label_map_util.convert_label_map_to_categories(label_map,
															max_num_classes = n_classes,
															use_display_name = True)
category_index = label_map_util.create_category_index(categories)

print Color.BOLD_YELLOW + "\nIMPORTING IMAGES..." + Color.RESET
number_of_images = len(next(os.walk("%s/resources/cutout-images" % main_dir))[2]) - 2
cutout_path = [os.path.join("%s/resources/cutout-images" % main_dir, "cut-{:03}.jpg".format(i)) for i in range(0, number_of_images)]
image_size = (12, 9)

print ""
i = 0
with detection_graph.as_default():
	with tf.Session(graph = detection_graph) as sess:
		for image_path in tqdm(
							cutout_path,
							desc = Color.BOLD_YELLOW + "DETECTING ACTIVE REGIONS",
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
			lycon.save("%s/resources/region-detection-images/cut-detected-%03d.jpg" % (main_dir, i), image_np)

			plt.close()
			i += 1

if generate_detection_video:
	os.system("python %s/video-generators/detection-video.py --framerate %d" % (main_dir, default_frames_per_second))

print Color.BOLD_YELLOW + "\nDONE\n" + Color.RESET
