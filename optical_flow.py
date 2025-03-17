import cv2
import numpy as np
import os

def compute_iou(bbox1, bbox2):
    """Compute the Intersection over Union (IoU) of two bounding boxes."""
    # Unpack the bounding boxes
    x1, y1, w1, h1 = bbox1
    x2, y2, w2, h2 = bbox2
    
    # Calculate the (x, y)-coordinates of the intersection rectangle
    x_left = max(x1, x2)
    y_top = max(y1, y2)
    x_right = min(x1 + w1, x2 + w2)
    y_bottom = min(y1 + h1, y2 + h2)
    
    # If there's no intersection, return IoU as 0
    if x_right <= x_left or y_bottom <= y_top:
        return 0.0
    
    # Compute area of intersection
    intersection_area = (x_right - x_left) * (y_bottom - y_top)
    
    # Compute areas of the bounding boxes
    bbox1_area = w1 * h1
    bbox2_area = w2 * h2
    
    # Compute the union area
    union_area = bbox1_area + bbox2_area - intersection_area
    
    # Compute IoU
    iou = intersection_area / union_area
    return iou

def bounding_box(contours):
    bounding_boxes = []
    for contour in contours:
        if cv2.contourArea(contour) > 500:  # Ignore small contours (can adjust this threshold)
            # Get bounding box of the contour
            x, y, w, h = cv2.boundingRect(contour)
            bounding_boxes.append((x, y, w, h))
    # return bounding_boxes
    filtered_bboxes = []
    
    for i, bbox1 in enumerate(bounding_boxes):
        keep = True
        for j, bbox2 in enumerate(bounding_boxes):
            if i != j:
                iou = compute_iou(bbox1, bbox2)
                if iou > 0.9:  # If IoU > 90%, discard the smaller bounding box
                    if cv2.contourArea(contour) < cv2.contourArea(contours[j]):
                        keep = False
                        break
        if keep:
            filtered_bboxes.append(bbox1)
    
    return filtered_bboxes

def bbox(frame, filtered_bboxes):
    og_frame = frame
    cropped_image = frame
    for i, bbox in enumerate(filtered_bboxes):
        x, y, w, h = bbox
        cropped_image = og_frame[y:y+h, x:x+w]
        
        # Save cropped image as PNG
        cropped_filename = os.path.join(output_dir, f"cropped_{frame_count}_{i}.png")
        cv2.imwrite(cropped_filename, cropped_image)

        # Optionally, draw bounding boxes on the original frame for visualization
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    return frame, cropped_image


# Initialize video capture (can be from a webcam or video file)
cap = cv2.VideoCapture("hibiscus2.mp4")  # Use 0 for webcam, or replace with video file path

# Read the first frame to initialize
ret, prev_frame = cap.read()
if not ret:
    print("Failed to read the video.")
    cap.release()
    exit()

# Convert to grayscale
prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)

# Create a directory to save cropped images (if it doesn't already exist)
output_dir = "cropped_images"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

frame_count = 0  # To name the cropped images uniquely

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Convert to grayscale for optical flow calculation
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Calculate optical flow using Farneback method
    flow = cv2.calcOpticalFlowFarneback(prev_gray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)

    # Calculate magnitude and angle of the flow vectors
    magnitude, angle = cv2.cartToPolar(flow[..., 0], flow[..., 1])

    # Set a threshold for significant movement (you can adjust this value)
    movement_threshold = 2.0
    movement_mask = magnitude > movement_threshold

    # Find contours of the movement mask
    contours, _ = cv2.findContours(movement_mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # List to hold bounding boxes
    filtered_bboxes = bounding_box(contours)

    # Draw the filtered bounding boxes and save the cropped images
    cropped_image = frame
    frame, cropped_image = bbox(frame, filtered_bboxes)

    # Display the frame with bounding boxes
    cv2.imshow("cropped", cropped_image)
    cv2.imshow("Movement Detection", frame)

    # Update the previous frame for the next iteration
    prev_gray = gray
    frame_count += 1

    # Break the loop if the user presses the "q" key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
