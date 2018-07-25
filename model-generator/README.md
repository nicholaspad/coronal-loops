INSTRUCTIONS FOR PREPARING TRAINING OBJECTS AND DIRECTORIES

Note: object_detection directory on GitHub does not include TensorFlow training files (too large). Contact me for the training files (including train.py and export_inference_graph.py).

-------------

1. Use LabelBox to annotate images.

2. Download annotation data as a .json file.

3. Rename the file to data.json and move it to training-prep directory.

4. Move the original images into the images directory.

5. Run json-to-tfrecord.py.

6. Copy data and images directories to object_detection directory.

7. Train the model (run in object_detection directory):

==> python model_main.py \
	--pipeline_config_path=models/model/pipeline.config \
	--model_dir=training \
	--num_train_steps=50000 \
	--num_eval_steps=2000 \
	--logtostderr

[old]

==> python train.py \
	--logtostderr \
	--train_dir=training/ \
	--pipeline_config_path=ssd_mobilenet_v1_coco_2018_01_28/pipeline.config

8. Export the inference graph (run in object_detection directory):

==> python export_inference_graph.py \
    --input_type image_tensor \
    --pipeline_config_path models/model/pipeline.config \
    --trained_checkpoint_prefix training/model.ckpt-0 \
    --output_directory /Users/padman/Desktop/lmsal/models

[old]

==> python export_inference_graph.py \
	--input_type image_tensor \
	--pipeline_config_path ssd_mobilenet_v1_coco_2018_01_28/pipeline.config \
	--checkpoint_path training/model.ckpt-0 \
	--inference_graph_path /Users/padman/Desktop/lmsal/models/NAME.pb

-------------

If import errors occur, run in model-generator directory:

==> export PYTHONPATH=$PYTHONPATH:`pwd`:`pwd`/slim

Command for running apply-region-detection.py:

==> export PYTHONPATH=$PYTHONPATH:`pwd`/model-generator:`pwd`model-generator/slim
