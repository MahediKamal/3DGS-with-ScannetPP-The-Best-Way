# 3DGS-with-Scannet--The-Best-Way
3D Gaussian Splatting on ScanNet++ Data: Best Practices and Workflow Guide. In this way, the splat coordinate will match the coordinate system with the Scannet++ coordinate. Same workflow for Triangle Splatting+, MeshSplatting

cd dslr

mkdir splatData
mkdir splatData/sparse
mkdir splatData/sparse/0
mkdir splatData/dense


conda activate colmap

colmap model_converter \
--input_path dslr/colmap \
--output_path splatData/sparse/0/ \
--output_type BIN


colmap image_undistorter \
--image_path dslr/resized_images \
--input_path splatData/sparse/0 \
--output_path splatData/dense/0 \
--output_type COLMAP


python train.py -s <path_to_scenes> -m <output_model_path> --indoor --eval
