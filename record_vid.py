import cv2 as cv
from methods import file_name
import os
import sys
import time
from time import sleep

cap = cv.VideoCapture(0)

max_time = 50
try:
    max_time = int(sys.argv[2])
except:
    max_time = 50

# Define the codec and create VideoWriter object
fourcc = cv.VideoWriter_fourcc(*'XVID')
frame_size = (240,240)
filename = os.path.join('/'.join(file_name(f'{sys.argv[1]}/rec_videos','.avi'))) 
out = cv.VideoWriter(filename, fourcc, 20.0, frame_size)
start_time = time.time()

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break
    
    frame = cv.flip(frame, 0)
    frame = cv.resize(frame,frame_size)

    # write the flipped frame
    out.write(frame)
    
    current_time = time.time() - start_time
    
    sleep(0.1)
    if current_time >= max_time:
        print("times up")
        break

    #cv.imshow('frame', frame)
    if cv.waitKey(1) == ord('q'):
        break

# Release everything if job is finished
cap.release()
out.release()
cv.destroyAllWindows()
