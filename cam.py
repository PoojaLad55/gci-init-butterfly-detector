import cv2
  2 import numpy as np
  3 import os
  4 import time
  5 import shutil
  6 import glob
  7 import subprocess
  8 from datetime import datetime
  9
 10 class StorageManager:
 11     def __init__(self, directory, max_size_gb=None, max_files=100, alert_percentage=90):
 12         """
 13         Initialize storage manager for keeping directory size under control
 14
 15         Args:
 16             directory: Directory to monitor and clean
 17             max_size_gb: Maximum directory size in GB (if None, only use max_files)
 18             max_files: Maximum number of files to keep
 19             alert_percentage: Disk usage percentage that triggers cleanup
 20         """
 21         self.directory = directory
 22         self.max_size_gb = max_size_gb
 23         self.max_files = max_files
 24         self.alert_percentage = alert_percentage
 25
 26         # Create directory if it doesn't exist
 27         if not os.path.exists(directory):
 28             os.makedirs(directory)
 29
 30     def check_disk_usage(self):
 31         """Check if disk usage exceeds the alert percentage"""
 32         try:
 33             # Get disk usage using df command
 34             df = subprocess.Popen(["df", "-h", self.directory], stdout=subprocess.PIPE)
 35             output = df.communicate()[0].decode('utf-8')
 36
 37             # Parse the output to get usage percentage
 38             lines = output.strip().split('\n')
 39             if len(lines) >= 2:  # Header line + at least one data line
 40                 usage_line = lines[1]
 41                 # Get the percentage field (typically 5th field)
 42                 usage_percent = int(usage_line.split()[4].strip('%'))
 43                 return usage_percent >= self.alert_percentage
 44
 45             return False
 46         except Exception as e:
 47             print(f"Error checking disk usage: {e}")
"cam.py" 227L, 8039B
