INSTRUCTIONS FOR PREPARING TRAINING OBJECTS AND DIRECTORIES

Note: object_detection directory on GitHub does not include TensorFlow training files (too large). Contact me for the training files (including train.py and export_inference_graph.py).

-------------

1. Use LabelBox to annotate images.

2. Download annotation data as a .json file.

3. Rename the file to data.json and move it to training-prep directory.

4. Move the original images into the images directory.

5. Run json-to-tfrecord.py.

6. Copy data and images directories to object_detection directory.

7. Train the model until reaching a loss number of about 1.0:

==> python train.py --logtostderr --train_dir=training/ --pipeline_config_path=ssd_mobilenet_v1_coco_2018_01_28/pipeline.config

8. Export the inference graph (change CKPT_NUM and GRAPH_NAME):

==> python export-inference-graph.py \
    --input_type image_tensor \
    --pipeline_config_path ssd_mobilenet_v1_coco_2018_01_28/pipeline.config \
    --checkpoint_path training/model.ckpt-CKPT_NUM \
    --inference_graph_path inference_graphs/GRAPH_NAME.pb

-------------

If import errors occur, run:

==> export PYTHONPATH=$PYTHONPATH:`pwd`:`pwd`/slim
