# 3DGS with Scannet++: The Best Way

``
Note: If you try to use the resized_undistorted_images images provider in the dsrl folder, that will also work to generate splat, but then the coorniate of the splat will not match with the coordinate of the scannet++. If you try to match the coordinate in this way, then it will be much harder to do so.
``

``
First, go to a scere folder. For my case, it was 17268bec90. Then follow the steps
``

```
cd dslr
```

```
mkdir splatData
mkdir splatData/sparse
mkdir splatData/sparse/0
mkdir splatData/dense
```


``
You need to have a colmap environment set up. Because we are going to use some commands of colmap. I created an python environment name colmap and installed the colmap inside it. So before using the colmap command, I need to activate the environment like below.
``

```
conda activate colmap
```


``
Now, as we are in the colmap environment, we can give the below commands to prepare the data we need for splatting
``

```
colmap model_converter \
--input_path dslr/colmap \
--output_path splatData/sparse/0/ \
--output_type BIN
```

```
colmap image_undistorter \
--image_path dslr/resized_images \
--input_path splatData/sparse/0 \
--output_path splatData/dense/0 \
--output_type COLMAP
```

``
Now the data is ready to use. The dense folder is the main data that we will be using for splat training. In my case, I gave the following command to train the splat with the prepared data
``
```
python train.py -s /workspace/mahedi/Data/scannetPP/17268bec90/splatData/dense -m outputModel/scannetPP/17268bec90 --indoor --eval
```
