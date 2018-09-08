import os

def clear_filesystem():
	os.system("rm -rf resources/region-data/raw-images && mkdir resources/region-data/raw-images")
	os.system("rm -rf resources/region-data/binary-images && mkdir resources/region-data/binary-images")
	os.system("rm -rf resources/region-data/threshold-images && mkdir resources/region-data/threshold-images")
	os.system("rm -rf resources/region-data/magnetogram-images && mkdir resources/region-data/magnetogram-images")
	os.system("rm -rf resources/region-data/masked-magnetogram-images && mkdir resources/region-data/masked-magnetogram-images")
