#! /usr/bin/env python3
"""
on_connect 

"""
import os
import subprocess
import time

import pyudev

from common.config import connect, DEFAULT_CONFIG_PATH

CONNECT_BACKOFF_SECS = 1.0

def main():
    config_path=os.environ.get("ACM_CONFIG_PATH", DEFAULT_CONFIG_PATH)

    print(f"Connecting devices now and Monitoring USB events for auto-connect-midi using config at {config_path}...")
    connect(config_path)
    next_check_at = time.time() + CONNECT_BACKOFF_SECS

    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by(subsystem='usb')
    monitor.start()

    for device in iter(monitor.poll, None):
        if time.time() > next_check_at:
            connect(config_path)
            next_check_at = time.time() + CONNECT_BACKOFF_SECS

if __name__ == '__main__':
    main()

