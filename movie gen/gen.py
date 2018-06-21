import cv2
import os
import re
from tqdm import tqdm

class Gen(object):

	def __init__(self, output_name, fps):
		self.output_name = output_name
		self.source = "/Users/padman/Desktop/lmsal/movie gen/source images"
		self.fps = fps

	def process(self):
		images = []

		for file in os.listdir(self.source):
			if file.endswith(".jp2"):
				images.append(file)

		images.sort(key = self.sorthelper)

		frame = cv2.imread(os.path.join(self.source, images[0]))
		height, width, layers = frame.shape

		video = cv2.VideoWriter(self.output_name, -1, self.fps, (width,height))

		for image in tqdm(images, desc = "PROCESSING"):
			video.write(cv2.imread(os.path.join(self.source, image)))

		cv2.destroyAllWindows()
		video.release()

		print "\n%s saved to working directory." % (self.output_name)

	def sorthelper(self, name):
		n = re.search('source_(\d+)\.?.*', name)
		return int(n.group(1), 10)

# g = Gen("output.mp4", 12)
# g.process()