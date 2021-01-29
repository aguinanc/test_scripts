# General Scripts

### Overall

The scripts in this folder aim to provide general basic scripts useful for automation of simple laboratory tasks.

### Scripts

- `move_and_repeat.py`: Sends commands to the specified PVs of an EPICS IOC which controls the motion of a device. The motion follows a sequence of points specified on a file and optionally cycle through the points.
- `ping_monitor.py`: Constantly pings a device and print to stdout when it fails to respond.
- `tcpip_sock.py`: Provide the most basic command/response funcionality.
