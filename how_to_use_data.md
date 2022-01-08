# Installation

## fork both <https://github.com/DavidGillsjo/VideoIMUCapture-Android> and <https://github.com/DavidGillsjo/dockers>

```shell
git clone git@github.com:hibetterheyj/VideoIMUCapture-Android.git
git submodule update --init --recursive
```

## execute docker commands

```shell
cd VideoIMUCapture-Android
cd calibration
# datapath using absolute path: $HOME/Documents/yujie/vo_dataset/VideoIMUCapture-Android/calibration/data/
DATA=$HOME/Documents/yujie/vo_dataset/VideoIMUCapture-Android/calibration/data/ ./run_dockerhub.sh
```

## create calibration board

```shell
kalibr_create_target_pdf -h
Traceback (most recent call last):
  File "/kalibr_workspace/devel/bin/kalibr_create_target_pdf", line 15, in <module>
    exec(compile(fh.read(), python_script, 'exec'), context)
  File "/kalibr_workspace/src/Kalibr/aslam_offline_calibration/kalibr/python/kalibr_create_target_pdf", line 5, in <module>
    from pyx import *
ImportError: No module named pyx
```

- solution

```shell
sudo apt update
sudo apt install python-pyx
```

- rerun the commands

```shell
kalibr_create_target_pdf --h
# create checkerboard
kalibr_create_target_pdf --type checkerboard --nx 6 --ny 7 --csx 0.03 --csy 0.03 checkerboard_6_7_3x3.pdf
```

## download pdf

> copy file from container: https://stackoverflow.com/a/31971697

```yaml
target_type: 'checkerboard' #gridtype
targetCols: 6               #number of internal chessboard corners
targetRows: 7               #number of internal chessboard corners
rowSpacingMeters: 0.03      #size of one chessboard square [m]
colSpacingMeters: 0.03      #size of one chessboard square [m]
```

```shell
docker ps
docker cp c62fe941989d:/calibration/checkerboard_6_7_3x3.pdf ./checkerboard_6_7_3x3.pdf
```

so you can print for calibration

## Resize video resolutions

- target calibration data: `2022_01_07_23_44_44`

```shell
$ ls ../data/2022_01_07_23_44_44
video_meta.pb3  video_recording.mp4
```

- original data is recorded with 3472x4624 pixels
- expected resolutions
  - 1280×960 (top choice!)
  - 800x600
  - 640x480
- resize with `ffmpeg`
  - `sudo apt install ffmpeg -y`
  - `ffmpeg -i video_recording_original.mp4 -vf scale=800:640 -c:v libx264 -crf 18 800_640.mp4`
- rotate 90 degrees counterclockwise
  - https://stackoverflow.com/a/9570992
  - `ffmpeg -i video_recording_original.mp4 -vf "transpose=2" -c:v libx264 -crf 18 -pix_fmt yuv420p video_recording_4624_3472.mp4`
- two commands together: https://stackoverflow.com/a/56364133/13954301
  - `ffmpeg -i video_recording_original.mp4 -vf "transpose=2,scale=800:600" -c:v libx264 -crf 18 -pix_fmt yuv420p video_recording_800_600.mp4`
  - `ffmpeg -i video_recording_original.mp4 -vf "transpose=2,scale=1280:960" -c:v libx264 -crf 18 -pix_fmt yuv420p video_recording.mp4`


## Create calibration bag for calibration

- run script to use kalibr

```shell
cd VideoIMUCapture-Android/calibration/
docker cp ./data2kalibr_new.py c62fe941989d:/calibration/data2kalibr_new.py
```

calibrate with

```shell
# in docker
# python data2kalibr_new.py ../data/2022_01_07_23_44_44 --tag-size 0.03 --subsample 30
python data2kalibr_new.py ../data/2022_01_07_23_44_44 --tag-size 0.03
```

- output logs

```plaintext
../data/2022_01_07_23_44_44/kalibr/kalibr.bag
```

## Misc

> C) Using Through Docker

```shell
chmod +x run_kalibr.sh
# ./run_kalibr.sh <path-to-data-dir>
bash ./run_kalibr.sh custom_data
```
