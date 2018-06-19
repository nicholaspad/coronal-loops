from sunpy.net.helioviewer import HelioviewerClient
import cv2
import os
import re

hv = HelioviewerClient()

# datasources = hv.get_data_sources()

# for observatory, instruments in datasources.items():
# 	for inst, detectors in instruments.items():
# 		for det, measurements in detectors.items():
# 			for meas, params in measurements.items():
# 				print("%s %s: %d" % (observatory, params["nickname"], params["sourceId"]))

hours = 24
fps = 10

# for hour in range(0, hours):
# 	# for min in range (0,60):
# 	# hv.download_png('2018/04/%02d' % (day), 4.8, "[13,1,100]", x0=0, y0=0, width=1024, height=1024)
# 	hv.download_jp2("2016/04/17 %02d:00:00" % (hour), observatory = "SDO", instrument = "HMI", detector = "HMI", measurement = "magnetogram")
# 	print "%.0f percent complete." % (100.0 * (hour + 1)/float(hours))

folder = '/Users/padman/sunpy/data'
name = 'output.mp4'

images = []
for f in os.listdir(folder):
    if f.endswith(".jp2"):
        images.append(f)

def name2num(name):
   m = re.search('img_(\d+)\.?.*', name)
   return int(m.group(1),10)

images.sort(key=name2num)

frame = cv2.imread(os.path.join(folder, images[0]))
height, width, layers = frame.shape

video = cv2.VideoWriter(name, -1, fps, (width,height))

for image in images:
    video.write(cv2.imread(os.path.join(folder, image)))
    
    if (cv2.waitKey(1) & 0xFF) == ord('q'):
    	break

cv2.destroyAllWindows()
video.release()
