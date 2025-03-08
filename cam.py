import cv2
import numpy as np
import os
import time
import shutil
import glob
import subprocess
from datetime import datetime

class StorageManager:
    def __init__(self, directory, max_size_gb=None, max_files=100, alert_percentage=90):
        """
        Initialize storage manager for keeping directory size under control
        
        Args:
            directory: Directory to monitor and clean
            max_size_gb: Maximum directory size in GB (if None, only use max_files)
            max_files: Maximum number of files to keep
            alert_percentage: Disk usage percentage that triggers cleanup
        """
        self.directory = directory
        self.max_size_gb = max_size_gb
        self.max_files = max_files
        self.alert_percentage = alert_percentage
        
        # Create directory if it doesn't exist
        if not os.path.exists(directory):
            os.makedirs(directory)
    
    def check_disk_usage(self):
        """Check if disk usage exceeds the alert percentage"""
        try:
            # Get disk usage using df command
            df = subprocess.Popen(["df", "-h", self.directory], stdout=subprocess.PIPE)
            output = df.communicate()[0].decode('utf-8')
            
            # Parse the output to get usage percentage
            lines = output.strip().split('\n')
            if len(lines) >= 2:  # Header line + at least one data line
                usage_line = lines[1]
                # Get the percentage field (typically 5th field)
                usage_percent = int(usage_line.split()[4].strip('%'))
                return usage_percent >= self.alert_percentage
            
            return False
        except Exception as e:
            print(f"Error checking disk usage: {e}")
            return False
    
    def get_directory_size(self):
        """Get total size of directory in bytes"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(self.directory):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if os.path.exists(fp):  # Skip if file disappears
                    total_size += os.path.getsize(fp)
        return total_size
    
    def delete_oldest_files(self, file_pattern="*"):
        """Delete oldest files in directory matching the pattern"""
        # Get all files matching pattern
        pattern = os.path.join(self.directory, file_pattern)
        files = glob.glob(pattern)
        
        # Sort files by creation time (oldest first)
        files.sort(key=os.path.getctime)
        
        # Check if we need to delete by count
        if len(files) > self.max_files:
            # Calculate how many files to delete
            files_to_delete = files[:len(files) - self.max_files]
            
            for file_path in files_to_delete:
                try:
                    os.remove(file_path)
                    print(f"Deleted old file: {os.path.basename(file_path)}")
                except Exception as e:
                    print(f"Error deleting file {file_path}: {e}")
        
        # Check if we need to delete by size
        if self.max_size_gb:
            max_bytes = self.max_size_gb * 1024 * 1024 * 1024
            
            # Get remaining files
            remaining_files = glob.glob(pattern)
            remaining_files.sort(key=os.path.getctime)
            
            # Check total size
            while self.get_directory_size() > max_bytes and remaining_files:
                try:
                    to_delete = remaining_files.pop(0)  # Get oldest file
                    os.remove(to_delete)
                    print(f"Deleted file for size management: {os.path.basename(to_delete)}")
                except Exception as e:
                    print(f"Error deleting file {to_delete}: {e}")
    
    def clean_if_needed(self):
        """Check if cleanup is needed and perform it"""
        # Check disk usage first
        if self.check_disk_usage():
            print(f"Disk usage is above {self.alert_percentage}%, cleaning up old files...")
            self.delete_oldest_files()
            return True
        
        # Then check number of files and directory size
        self.delete_oldest_files()
        return False


# Initialize settings
image_dir = "motion_images"
record_video = False  # Set to True if you want to record videos as well

# Initialize storage manager
storage_manager = StorageManager(
    directory=image_dir,
    max_size_gb=10,       # Maximum 10GB of storage for images and videos
    max_files=500,        # Keep maximum 500 files
    alert_percentage=90   # Clean up when disk is 90% full
)

# Initialize camera (0 for built-in camera, 1 for USB camera)
# Try both options if one doesn't work
camera_index = 0
cap = cv2.VideoCapture(camera_index)

# If camera fails to open with index 0, try index 1
if not cap.isOpened():
    camera_index = 1
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        exit()

print(f"Successfully opened camera with index {camera_index}")

# Set camera resolution (adjust based on your camera capabilities)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Motion detection variables
last_mean = 0
detected_motion = False
cooldown_frames = 0
motion_threshold = 0.5  # Adjust based on sensitivity needed
cooldown_period = 30    # Frames to wait before detecting new motion

# Setup video recording if enabled
out = None
if record_video:
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    video_filename = os.path.join(image_dir, f"motion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.avi")
    out = cv2.VideoWriter(video_filename, fourcc, 20.0, (640, 480))

print("Press 'q' to quit")

# Counter for periodic storage checks (check every 100 frames)
frame_count = 0 

try:
    while True:
        # Capture frame
        ret, frame = cap.read()
        
        if not ret:
            print("Failed to grab frame")
            break
            
        # Process frame for motion detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        current_mean = np.mean(gray)
        mean_diff = np.abs(current_mean - last_mean)
        
        # Update last mean
        last_mean = current_mean
        
        # Display frame if GUI is available
        try:
            cv2.imshow('Camera Feed', frame)
        except:
            pass  # Skip display if running headless
        
        # Check for motion
        if mean_diff > motion_threshold and cooldown_frames <= 0:
            print(f"Motion detected! Difference: {mean_diff:.2f}")
            detected_motion = True
            cooldown_frames = cooldown_period
            
            # Save image on motion detection
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_path = os.path.join(image_dir, f"motion_{timestamp}.jpg")
            cv2.imwrite(image_path, frame)
            print(f"Image saved to {image_path}")
            
        # Record video if motion was detected and video recording is enabled
        if detected_motion and record_video and out is not None:
            out.write(frame)
            
        # Decrease cooldown counter
        if cooldown_frames > 0:
            cooldown_frames -= 1
        
        # Reset motion flag if cooldown is over
        if cooldown_frames == 0:
            detected_motion = False
            
        # Periodically check storage
        frame_count += 1
        if frame_count >= 100:
            storage_manager.clean_if_needed()
            frame_count = 0
            
        # Check for exit command
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Exiting...")
            break
            
except KeyboardInterrupt:
    print("Program interrupted by user")
finally:
    # Clean up
    cap.release()
    if record_video and out is not None:
        out.release()
    cv2.destroyAllWindows()
    print("Resources released. Program ended.")
