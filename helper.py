import os

def clear_filesystem():
	os.system("rm -rf resources/region-data/raw-images && mkdir resources/region-data/raw-images")
	os.system("rm -rf resources/region-data/raw-masks && mkdir resources/region-data/raw-masks")
	os.system("rm -rf resources/region-data/masked-images && mkdir resources/region-data/masked-images")
	os.system("rm -rf resources/region-data/e-masks && mkdir resources/region-data/e-masks")
	os.system("rm -rf resources/region-data/e-masked-images && mkdir resources/region-data/e-masked-images")
