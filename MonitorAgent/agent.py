# coding: utf-8
from __future__ import unicode_literals, print_function
import csv
from datetime import datetime
import os
import json
import sys
import time

import psutil
import pygal


def collect():
    # Get system stats
    cpu = psutil.cpu_percent(interval=1)
    cpu_t = psutil.cpu_times_percent(interval=1)
    memory = psutil.virtual_memory()
    swap = psutil.swap_memory()
    net = psutil.net_io_counters()
    processes = psutil.pids()

    data = [
        time.time(),
        cpu,
        cpu_t.user,
        cpu_t.nice,
        cpu_t.system,
        cpu_t.idle,
        memory.percent,
        swap.percent,
        net.bytes_sent,
        net.bytes_recv,
        len(processes),
    ]
    # Write to data file
    data_filename = get_data_filename()
    with open(data_filename, 'a') as wf:
        csv.writer(wf).writerow(data)

    # If it's the last minute of the day, generate images
    now = datetime.now()
    draw_images(data_filename)
    if now.hour == 23 and now.minute == 59:
        draw_images(data_filename)


def draw_images(filename):
    # Draw general CPU usage line chart
    # Draw CPU time percentage line charts
    # Draw memory and SWAP percentage line charts
    # Draw network line charts
    timestamps = []
    cpu, cpu_u, cpu_n, cpu_s, cpu_i = [], [], [], [], []
    memory, swap, net_s, net_r = [], [], [], []
    process = []
    datas = (
        timestamps, cpu, cpu_u, cpu_n, cpu_s, cpu_i,
        memory, swap, net_s, net_r, process,
    )
    with open(filename, 'r') as rf:
        csv_data = csv.reader(rf)
        for row in csv_data:
            for i in range(11):
                datas[i].append(float(row[i]))
    groups = {
        'CPU percent': {
            'CPU percent': cpu
        },
        'CPU times percent': {
            'User': cpu_u,
            'Nice': cpu_n,
            'System': cpu_s,
            'Idle': cpu_i,
        },
        'Memory usage': {
            'Virtual memory': memory,
            'SWAP': swap,
        },
        'Network': {
            'Bytes sent': net_s,
            'Bytes received': net_r,
        },
        'Process': {
            'Process count': process,
        },
    }
    for name in groups.keys():
        chart = pygal.Line()
        chart.config.style.font_family = 'PingFangSC-Regular'
        chart.title = name
        for line_name in groups[name].keys():
            chart.add(line_name, groups[name][line_name])
        base_filename = os.path.splitext(filename)[0]
        chart.render_to_png('{}-{}.png'.format(base_filename, name))


def get_data_filename():
    return os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        'monitoragent-{}.csv'.format(datetime.now().strftime('%Y-%m-%d'))
    )


if __name__ == '__main__':
    collect()

