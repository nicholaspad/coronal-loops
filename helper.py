import os

def clear_filesystem():
	os.system("rm -rf resources/region-data/raw-images && mkdir resources/region-data/raw-images")
	os.system("rm -rf resources/region-data/r-masks && mkdir resources/region-data/r-masks")
	os.system("rm -rf resources/region-data/e-masks && mkdir resources/region-data/e-masks")
	os.system("rm -rf resources/region-data/c-masks && mkdir resources/region-data/c-masks")
	os.system("rm -rf resources/region-data/r-masked-images && mkdir resources/region-data/r-masked-images")
	os.system("rm -rf resources/region-data/e-masked-images && mkdir resources/region-data/e-masked-images")
	os.system("rm -rf resources/region-data/c-masked-images && mkdir resources/region-data/c-masked-images")
