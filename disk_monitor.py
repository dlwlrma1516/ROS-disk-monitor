#!/usr/bin/env python

import rospy
import psutil
from std_srvs.srv import Trigger, TriggerResponse

from dynamic_reconfigure.server import Server
from syswork.cfg import DiskMonitorConfigConfig  

warning_threshold = 10.0
alarm_threshold = 5.0

def get_monitored_partitions():
    partitions = psutil.disk_partitions(all=False)
    monitored = []
    for p in partitions:
        if 'rw' in p.opts and not p.device.startswith('/dev/loop'):
            monitored.append(p.mountpoint)
    return monitored

def get_disk_usage(mount_point):
    usage = psutil.disk_usage(mount_point)
    free_gb = usage.free / (1024.0 ** 3)
    total_gb = usage.total / (1024.0 ** 3)
    used_percent = usage.percent
    return free_gb, total_gb, used_percent

def handle_disk_status(req):
    msg_lines = []
    for mount_point in get_monitored_partitions():
        free_gb, total_gb, used_percent = get_disk_usage(mount_point)
        msg = "[{}] {:.2f}GB free / {:.2f}GB total ({:.1f}% used)".format(
            mount_point, free_gb, total_gb, used_percent)
        msg_lines.append(msg)
    return TriggerResponse(success=True, message="\n".join(msg_lines))

def dynamic_reconfigure_callback(config, level):
    global warning_threshold, alarm_threshold
    warning_threshold = config.warning_threshold_gb
    alarm_threshold = config.alarm_threshold_gb
    rospy.loginfo("Reconfigure request: warning=%.2f GB, alarm=%.2f GB", warning_threshold, alarm_threshold)
    return config

if __name__ == '__main__':
    rospy.init_node("disk_monitor")

    srv = Server(DiskMonitorConfigConfig, dynamic_reconfigure_callback)

    service = rospy.Service("disk_status_check", Trigger, handle_disk_status)

    rate = rospy.Rate(0.033)

    while not rospy.is_shutdown():
        try:
            for mount_point in get_monitored_partitions():
                free_gb, total_gb, used_percent = get_disk_usage(mount_point)

                rospy.loginfo("[{}] {:.2f}GB free / {:.2f}GB total ({:.1f}% used)".format(
                    mount_point, free_gb, total_gb, used_percent))

                if free_gb < alarm_threshold:
                    rospy.logerr(" CRITICAL: [{}] only {:.2f}GB left!".format(mount_point, free_gb))
                elif free_gb < warning_threshold:
                    rospy.logwarn(" Warning: [{}] low disk space ({:.2f}GB left)".format(mount_point, free_gb))

        except Exception as e:
            rospy.logerr("Exception in disk monitor: {}".format(str(e)))

        rate.sleep()
