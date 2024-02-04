#! /usr/bin/env python3

import pyudev
import subprocess

def main():
    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by(subsystem='usb')
    monitor.start()

    for device in iter(monitor.poll, None):
        # I can add more logic here, to run different scripts for different devices.
        subprocess.call(['/home/foo/foobar.sh', '--foo', '--bar'])

if __name__ == '__main__':
    main()

