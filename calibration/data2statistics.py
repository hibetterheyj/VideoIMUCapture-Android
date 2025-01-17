#!/usr/bin/python


import os
import os.path as osp
import sys
import argparse

proto_python_path = os.path.join(os.getcwd(), "proto_python", "protobuf")

sys.path.append(proto_python_path)

print(proto_python_path)

from recording_pb2 import VideoCaptureData

import numpy as np
import matplotlib.pyplot as plt


FIG_SIZE = (20.0, 12.0)


def stats(proto, result_path, show=True):

    print(proto.camera_meta)
    print(proto.imu_meta)

    camera_stats(proto, result_path)

    imu_stats(proto, result_path)

    if show:
        plt.show()
    plt.close('all')


def camera_stats(proto, result_path):
    scalar_stats = {
        'exposure_time_ns': [],
        'frame_duration_ns': [],
        'frame_readout_ns': [],
        'est_focal_length_pix': [],
        'focus_locked': [],
    }
    time_ns = []
    frame_nbr = []

    # Generate stats from video frame data
    for i, frame_data in enumerate(proto.video_meta):
        time_ns.append(frame_data.time_ns)
        frame_nbr.append(frame_data.frame_number)

        for stat, stat_list in scalar_stats.items():
            stat_list.append(getattr(frame_data, stat))

    fig, ax = plt.subplots(len(scalar_stats) + 1, 1, sharex='all', figsize=FIG_SIZE)
    for i, (stat, stat_list) in enumerate(scalar_stats.items()):
        ax[i].set_title(stat)
        ax[i].plot(time_ns, stat_list, '.-')

    # Plot timestamp diff
    ax[-1].set_title("Timestamp diff [ms] vs frame nbr diff")
    time_ms = np.array(time_ns) * 1e-6
    diff = time_ms[1:] - time_ms[:-1]
    ax[-1].plot(time_ns[1:], diff, 'b.-')
    ax[-1].set_xlabel('Timestamp [ns]')
    ax[-1].set_ylabel('Diff [ms]')

    ax2 = ax[-1].twinx()
    frame_nbr = np.array(frame_nbr, np.int)
    fnbr_diff = frame_nbr[1:] - frame_nbr[:-1]
    ax2.plot(time_ns[1:], fnbr_diff, 'r.--')
    ax2.set_ylabel('Diff [int]')
    fig.tight_layout()
    plt.savefig(osp.join(result_path, 'video_meta.svg'))

    np.savetxt(osp.join(result_path, 'camera_ts.csv'), time_ms, delimiter=',')

    if proto.video_meta[0].OIS_samples:
        ois_stats(proto, result_path)


def ois_stats(proto, result_path):
    time_ns = []
    ois_data = {
        'x_shift': [],
        'y_shift': [],
    }

    for frame_data in proto.video_meta:
        for ois_sample in frame_data.OIS_samples:
            time_ns.append(ois_sample.time_ns)
            for stat, stat_list in ois_data.items():
                stat_list.append(getattr(ois_sample, stat))

    fig, ax = plt.subplots(len(ois_data), 1, sharex='all', figsize=FIG_SIZE)
    for i, (stat, stat_list) in enumerate(ois_data.items()):
        ax[i].set_title(stat)
        ax[i].plot(time_ns, stat_list, '.-')
    ax[-1].set_xlabel('Timestamp')
    fig.tight_layout()
    plt.savefig(osp.join(result_path, 'ois_samples.svg'))


def imu_stats(proto, result_path):
    scalar_stats = [
        ('gyro_accuracy', []),
        ('accel_accuracy', []),
    ]
    xyz_stats = [
        ('accel', [[], [], []]),
        ('gyro', [[], [], []]),
    ]
    bias_xyz_stats = [
        ('accel_bias', [[], [], []]),
        ('gyro_drift', [[], [], []]),
    ]
    time_ns = []

    # np.save(np.array(time_ns))

    # Generate stats from video frame data
    for i, frame_data in enumerate(proto.imu):
        time_ns.append(frame_data.time_ns)

        for stat, stat_list in scalar_stats:
            stat_list.append(getattr(frame_data, stat))

        for stat, xyz_list in xyz_stats:
            xyz = getattr(frame_data, stat)
            for i, d in enumerate(xyz):
                xyz_list[i].append(d)

        for stat, xyz_list in bias_xyz_stats:
            xyz = getattr(frame_data, stat)
            for i, d in enumerate(xyz):
                xyz_list[i].append(d)

    nbr_plots = len(scalar_stats) + 3 * len(xyz_stats)
    fig, ax = plt.subplots(nbr_plots, 1, sharex='all', figsize=FIG_SIZE)
    for i, (stat, stat_list) in enumerate(scalar_stats):
        ax[i].set_title(stat)
        ax[i].plot(time_ns, stat_list, '.-')

    for i, (stat, stat_list) in enumerate(xyz_stats):
        j = 3 * i + len(scalar_stats)
        xyz = np.array(stat_list)
        xyz_bias = np.array(bias_xyz_stats[i][1])
        for k, (d, d_bias) in enumerate(zip(xyz, xyz_bias)):
            ax[k + j].set_title('{}_{}'.format(stat, k))
            ax[k + j].set_ylabel(stat)
            ax[k + j].plot(time_ns, d, 'b.-')
            ax[k + j].plot(time_ns, d - d_bias, 'r.-')

    # for i, (stat, stat_list) in enumerate(twin_xyz_stats):
    #     j = 3*i + len(scalar_stats)
    #     for k, d in enumerate(stat_list):
    #         my_ax = ax[k+j].twinx()
    #         my_ax.plot(time_ns, d, 'r.--')
    #         my_ax.set_ylabel(stat)

    ax[-1].set_xlabel('Timestamp')
    fig.tight_layout()
    plt.savefig(osp.join(result_path, 'imu.svg'))

    np.savetxt(osp.join(result_path, 'imu_ts.csv'), time_ns, delimiter=',')


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Statistics for proto')
    parser.add_argument(
        '--proto_file',
        type=str,
        help='Path to protobuf video_meta.pb3',
        default='/mnt/c/repos/data/2022_01_03_12_39_22/video_meta.pb3',
    )
    parser.add_argument(
        '--result-dir',
        type=str,
        help='Path to result folder, default same as proto',
        default=None,
    )
    parser.add_argument(
        '--hide-plot', action='store_true', help='Hide plot, only save to file'
    )

    args = parser.parse_args()
    result_dir = (
        args.result_dir
        if args.result_dir
        else osp.join(osp.dirname(args.proto_file), 'statistics')
    )
    try:
        os.mkdir(result_dir)
    except OSError:
        pass

    # Read proto
    with open(args.proto_file, 'rb') as f:
        proto = VideoCaptureData.FromString(f.read())

    stats(proto, result_dir, show=not args.hide_plot)
