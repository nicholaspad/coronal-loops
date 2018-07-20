from datetime import datetime
import argparse
import getpass
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from colortext import Color

main_dir = "/Users/%s/Desktop/lmsal" % getpass.getuser()
video_name = "DETECTION_" + str(datetime.now().strftime("%Y-%m-%d %H.%M.%S"))

parser = argparse.ArgumentParser()
parser.add_argument("--framerate")
args = parser.parse_args()

if args.framerate == None:
	print Color.BOLD_YELLOW + "SPECIFY FRAMERATE WITH --framerate <value>" + Color.RESET
	sys.exit()

print Color.BOLD_YELLOW + "\nGENERATING VIDEO...\n" + Color.RESET
os.system("ffmpeg -y -f image2 -start_number 000 -framerate %s -i %s/resources/region-detection-images/cut-detected-%%3d.jpg -q:v 2 -vcodec mpeg4 -b:v 800k \"%s/videos/%s.mp4\"" % (args.framerate, main_dir, main_dir, video_name))

print Color.BOLD_YELLOW + "\nDONE: VIDEO SAVED TO videos/" + Color.RESET
os.system("open \"%s/videos/%s.mp4\"" % (main_dir, video_name))
