import cv2
import numpy as np
from time import sleep
import time
from methods import bounding_box, bbox, resize_image
import sys

frame_size = 140

cap = cv2.VideoCapture("videos/yes04-12-2025_13_29_33-6abab022-5f22.avi")  # Use 0 for webcam, or replace with video file path
#AMAZing04-12-2025_12_46_30-85a3a75a-2ec6.avi
#yes04-12-2025_13_29_33-6abab022-5f22.avi
#yes04-12-2025_14_05_01-ad6202ee-c4c1.avi
#perfect04-14-2025_12_34_01-5141fc2a-4c45.avi

max_time = 50

try:
    max_time = int(sys.argv[2])
except:
    max_time = 50

start_time = time.time()

# Read the first frame to initialize
ret, prev_frame = cap.read()
if not ret:
    print("Failed to read the video.")
    cap.release()
    exit()

prev_frame = resize_image(prev_frame, dim = frame_size)
prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
# hsv = np.zeros_like(prev_gray)
# hsv[..., 1] = 255
while True:
    ret, og_frame = cap.read()
    if not ret:
        break

    frame = resize_image(og_frame, dim = frame_size)
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    flow = cv2.calcOpticalFlowFarneback(prev_gray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
    magnitude, angle = cv2.cartToPolar(flow[..., 0], flow[..., 1])
    # hsv[..., 0] = angle*180/np.pi/2
    # hsv[..., 2] = cv2.normqalize(magnitude, None, 0, 255, cv2.NORM_MINMAX)
    # bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    movement_threshold = 1
    movement_mask = magnitude > movement_threshold
    

    contours, _ = cv2.findContours(movement_mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    filtered_bboxes = bounding_box(contours, lower_contour_area_limit = 100)

    cropped_image = frame
    frame, cropped_image = bbox(frame, filtered_bboxes, og_frame)#, output_dir=f'{sys.argv[1]}/images')

    # Display the frame with bounding boxes
    cv2.imshow("Movement Detection", frame)
    cv2.imshow("og_frame", og_frame)
    cv2.imshow("cropped", cropped_image)
    cv2.imshow("opticalflow", movement_mask.astype(np.uint8)* 255)
    # sleep(0.1)

    # Update the previous frame for the next iteration
    prev_gray = gray

    current_time = time.time() - start_time

    # if current_time >= max_time:
    #     print("OP timer up")
    #     break

    # Break the loop if the user presses the "q" key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
