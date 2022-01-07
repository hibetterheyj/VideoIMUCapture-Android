# yujie_experience

```shell
bash ./proto_install.sh
```

data: `/mnt/c/repos/data/`

```
ll /mnt/c/repos/data/
total 0
drwxrwxrwx 1 he he 4.0K Jan  3 13:14 ./
drwxrwxrwx 1 he he 4.0K Jan  3 13:12 ../
drwxrwxrwx 1 he he 4.0K Jan  3 13:12 2022_01_03_12_06_22/
drwxrwxrwx 1 he he 4.0K Jan  3 13:13 2022_01_03_12_08_30/
drwxrwxrwx 1 he he 4.0K Jan  3 13:13 2022_01_03_12_08_46/
drwxrwxrwx 1 he he 4.0K Jan  3 13:13 2022_01_03_12_08_48/
drwxrwxrwx 1 he he 4.0K Jan  3 13:13 2022_01_03_12_09_59/
drwxrwxrwx 1 he he 4.0K Jan  3 13:13 2022_01_03_12_10_58/
drwxrwxrwx 1 he he 4.0K Jan  3 13:13 2022_01_03_12_39_22/
```

- add following scripts before running the code

```python
proto_python_path = os.path.join(os.getcwd(), "proto_python", "protobuf")

sys.path.append(proto_python_path)

print(proto_python_path)
```

```
#Run script to get imu.svg and video_meta.svg
cd VideoIMUCapture-Android/
python3 calibration/data2statistics.py <datafolder>/<datetime>/video_meta.pb3

python calibration/data2statistics.py /mnt/c/repos/data/2022_01_03_12_39_22/video_meta.pb3
python calibration/data2statistics.py /mnt/c/repos/data/2022_01_03_12_39_22/video_meta.pb3
```

