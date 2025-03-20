import cv2
import numpy as np
from time import sleep
from methods import bounding_box, bbox, resize_image


cap = cv2.VideoCapture("Bug.mp4")  # Use 0 for webcam, or replace with video file path

# Read the first frame to initialize
ret, prev_frame = cap.read()
if not ret:
    print("Failed to read the video.")
    cap.release()
    exit()

prev_frame = resize_image(prev_frame)
prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = resize_image(frame)
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    flow = cv2.calcOpticalFlowFarneback(prev_gray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
    magnitude, angle = cv2.cartToPolar(flow[..., 0], flow[..., 1])

    movement_threshold = 2.0
    movement_mask = magnitude > movement_threshold

    contours, _ = cv2.findContours(movement_mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    filtered_bboxes = bounding_box(contours)

    cropped_image = frame
    frame, cropped_image = bbox(frame, filtered_bboxes)

    # Display the frame with bounding boxes
    cv2.imshow("cropped", cropped_image)
    cv2.imshow("Movement Detection", frame)
    sleep(0.1)

    # Update the previous frame for the next iteration
    prev_gray = gray

    # Break the loop if the user presses the "q" key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
