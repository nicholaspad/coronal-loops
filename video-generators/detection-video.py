from datetime import datetime
import argparse
import getpass
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from colortext import Color
from recorder import Recorder

MAIN_DIR = "/Users/%s/Desktop/lmsal" % getpass.getuser()
PRINTER = Recorder()
NAME = "DETECTION_" + str(datetime.now().strftime("%Y-%m-%d %H.%M.%S"))

parser = argparse.ArgumentParser()
parser.add_argument("--framerate")
args = parser.parse_args()

if args.framerate == None:
	PRINTER.info_text("Specify framerate with '--framerate <value>'")
	sys.exit()

FRAMERATE = args.framerate

PRINTER.info_text("Generating video")
os.system("ffmpeg -y -f image2 -start_number 000 -framerate %s -i %s/resources/region-detection-images/detected-%%3d.jpg -q:v 2 -vcodec mpeg4 -b:v 800k \"%s/videos/%s.mp4\"" % (FRAMERATE, MAIN_DIR, MAIN_DIR, NAME))

PRINTER.info_text("Done: video saved to 'videos/'")
os.system("open \"%s/videos/%s.mp4\"" % (MAIN_DIR, NAME))
