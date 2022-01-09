#!/usr/bin/python
import argparse
import os.path as osp
import os
import cv2
import sys
from data2rosbag import _makedir, adjust_calibration

def undistort_img(cv_img, calibration):
    import yaml
    import numpy as np
    with open(calibration,'r') as f:
        calib = yaml.safe_load(f)

    cam0 = calib['cam0']

    [fu, fv, pu, pv] = cam0['intrinsics']
    #https://medium.com/@kennethjiang/calibrate-fisheye-lens-using-opencv-333b05afa0b0
    K = np.asarray([[fu, 0, pu], [0, fv, pv], [0, 0, 1]]) # K(3,3)
    D = np.asarray(cam0['distortion_coeffs']) #D(4,1)

    # https://docs.opencv.org/3.4/dc/dbb/tutorial_py_calibration.html
    h,  w = cv_img.shape[:2]
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(K, D, (w,h), 1, (w,h))

    undistorted_img = cv2.undistort(cv_img, K, D, None, newcameramtx)
    return undistorted_img

def rotate_img(cv_img, angle=90, expand=True):
    temp_rot_image = cv_img.rotate(angle, expand=True)
    return temp_rot_image

def convert_to_images(
    video_path,
    result_path,
    subsample=1,
    resize=[],
    undistort=True,
    calibration=None
    ):

    if resize:
        resize_f = lambda frame: cv2.resize(frame, tuple(resize), cv2.INTER_AREA)
    else:
        resize_f = lambda frame: frame

    # Open video stream
    try:
        cap = cv2.VideoCapture(video_path)

        # Generate images from video and frame data
        got_frame, frame = cap.read()
        resolution = (frame.shape[1], frame.shape[0])

        i = 0
        while got_frame:
            if (i % subsample) == 0:
                if undistort:
                    frame = undistort_img(frame, calibration)
                frame = resize_f(frame)
                cv2.imwrite(osp.join(result_path,'{:06d}.png'.format(i)), frame)
            got_frame, frame = cap.read()
            i += 1

    finally:
        cap.release()

    return resolution

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Create images from video file')
    parser.add_argument('video_path', type=str, help='Path to video')
    parser.add_argument('--result-dir', type=str, help='Path to result folder, default same as video file', default = None)
    parser.add_argument('--subsample', type=int, help='Take every n-th video frame', default = 1)
    parser.add_argument('--resize', type=int, nargs = 2, default = [], help='Resize image to this <width height>')
    parser.add_argument('--calibration', type=str, help='YAML file with kalibr camera and IMU calibration to copy, will also adjust for difference in resolution.', default = None)
    # added options
    parser.add_argument("--undistort", dest="undistort", action="store_true")
    parser.set_defaults(undistort=True)
    # TODO: rotate and adjust camera parameter (CW90 or CCW90)
    parser.add_argument("--rotate90", dest="rotate90", action="store_true")
    parser.set_defaults(rotate90=True)

    args = parser.parse_args()

    if not osp.isdir(args.video_path):
        result_dir = args.result_dir if args.result_dir else osp.join(osp.dirname(args.video_path), 'images')
        _makedir(result_dir)
        resolution = convert_to_images(args.video_path, result_dir,
                                       subsample = args.subsample,
                                       resize = args.resize)
        if args.calibration:
            out_path = osp.join(result_dir, 'calibration.yaml')
            adjust_calibration(args.calibration, out_path, resolution)
        sys.exit()


    for root, dirnames, filenames in os.walk(args.video_path):
        if not 'video_meta.pb3' in filenames:
            continue

        sub_path = osp.relpath(root,start=args.video_path)
        result_dir = osp.join(args.result_dir, sub_path) if args.result_dir else osp.join(root, 'images')
        _makedir(result_dir)

        video_path = osp.join(root, 'video_recording.mp4')
        resolution = convert_to_images(video_path, result_dir,
                                       subsample = args.subsample,
                                       resize = args.resize,
                                       undistort = args.undistort,
                                       calibration = args.calibration)

        if args.calibration:
            out_path = osp.join(result_dir, 'calibration.yaml')
            adjust_calibration(args.calibration, out_path, resolution)
