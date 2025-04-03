import os
from time import strftime
from uuid import uuid4
from cv2 import contourArea, boundingRect, rectangle, imwrite, resize

def compute_iou(bbox1, bbox2):
    x1, y1, w1, h1 = bbox1
    x2, y2, w2, h2 = bbox2
    
    x_left = max(x1, x2)
    y_top = max(y1, y2)
    x_right = min(x1 + w1, x2 + w2)
    y_bottom = min(y1 + h1, y2 + h2)
    
    if x_right <= x_left or y_bottom <= y_top:
        return 0.0
    intersection_area = (x_right - x_left) * (y_bottom - y_top)
    
    bbox1_area = w1 * h1
    bbox2_area = w2 * h2
    union_area = bbox1_area + bbox2_area - intersection_area
    
    iou = intersection_area / union_area
    return iou

def bounding_box(contours):
    bounding_boxes = []
    for contour in contours:
        if contourArea(contour) > 300:  
            x, y, w, h = boundingRect(contour)
            bounding_boxes.append((x, y, w, h))

    filtered_bboxes = []
    for i, bbox1 in enumerate(bounding_boxes):
        keep = True
        for j, bbox2 in enumerate(bounding_boxes):
            if i != j:
                iou = compute_iou(bbox1, bbox2)
                if iou > 0.60:  # If IoU > 50%
                    if contourArea(contour) < contourArea(contours[j]):
                        keep = False
                        break
        if keep:
            filtered_bboxes.append(bbox1)
    
    return filtered_bboxes

def image_dim(image, maxWidth = 56, maxHeight = 63):
    if image.shape[0] > maxWidth and image.shape[1] > maxHeight:
        return True

def bbox(frame, filtered_bboxes, output_dir = "cropped_images", frame_count = 0):
    og_frame = frame
    cropped_image = frame
    for i, bbox in enumerate(filtered_bboxes):
        x, y, w, h = bbox
        cropped_image = og_frame[y:y+h, x:x+w]
        cropped_path = os.path.join("/".join(file_name(output_dir,".png")))
        if image_dim(cropped_image):
            
            # imwrite(cropped_path, cropped_image)
            rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    
    return frame, cropped_image

def resize_image(image, dim = 240):
    return resize(image, (dim, dim))

def file_name(folder, extension):
    if not os.path.exists(folder):
        os.makedirs(folder)
    file_name = strftime("%m-%d-%Y_%H_%M_%S") + "-" + str(uuid4())[:13] + extension
    return [folder, file_name]