STEP 1
Create directories: data, images, training
Drag folder containing the model (mobilenet) into base directory.

STEP 2
Export images using active-region-video.py from lmsal repo.

STEP 3
Use labelImg to annotate each image. Use label "active region." Be sure that annotations are in xml format.

STEP 4
COPY 90% of the images into images/train. COPY the remaining images into images/test.

STEP 5
Run xml_to_csv.py

STEP 6
Run generate tf_record.py

STEP 7
Copy data and images directories into object_detection directory.

STEP 8
Run in object_detection directory:
python train.py --logtostderr --train_dir=training/ --pipeline_config_path=ssd_mobilenet_v1_coco_2018_01_28/pipeline.config

Keep the above process running until loss value reaches about 1.0.

STEP 9
Run in generate-model directory (must in bash shell):
export PYTHONPATH=$PYTHONPATH:`pwd`:`pwd`/slim

STEP 10
Export the inference graph by running inside object_detection directory (update CKPT_NUM):
python export_inference_graph.py \
    --input_type image_tensor \
    --pipeline_config_path ssd_mobilenet_v1_coco_2018_01_28/pipeline.config \
    --checkpoint_path training/model.ckpt-CKPT_NUM \
    --inference_graph_path active_region/active_region_frozen_graph.pb

STEP 11
Use active_region/active_region_frozen_graph.pb and training/object-detection.pbtxt as inputs to the active region detection script!
