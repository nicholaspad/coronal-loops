import argparse
from colortext import Color
from datetime import datetime
import getpass
import os

main_dir = "/Users/%s/Desktop/lmsal" % getpass.getuser()
video_name = "DETECTION_" + str(datetime.now().strftime("%Y-%m-%d %H.%M.%S"))

parser = argparse.ArgumentParser()
parser.add_argument("--framerate")
args = parser.parse_args()

print Color.YELLOW + Color.BOLD + "\nGENERATING VIDEO...\n" + Color.END
os.system("ffmpeg -y -f image2 -start_number 000 -framerate %s -i %s/resources/region-detected-images/cut-detected-%%3d.jpg -q:v 2 -vcodec mpeg4 -b:v 800k \"%s/videos/%s.mp4\"" % (args.framerate, main_dir, main_dir, video_name))

print Color.BOLD + Color.YELLOW + "\nDONE: VIDEO SAVED TO videos/" + Color.END
os.system("open \"%s/videos/%s.mp4\"" % (main_dir, video_name))
