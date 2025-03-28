#!/bin/bash

filePath="[!!!FILE-PATH!!!]/gci-init-butterfly-detector" #example "/home/lambopancake/Desktop/gci-init-butterfly-detector"
source "$filePath/.fly/bin/activate"
#sleep 20

#Define the Python files to alternate between
python_files=("$filePath/classify.py" "$filePath/optical_flow.py")

# Total number of repetitions (10 cycles)
#cycles=10
timeA=10
timeB=15
i=0
# Loop for 10 cycles and to test for [cycles] times
#for ((i = 0; i < $cycles; i++))
while true;
do
  # Determine which Python file to run (alternates between record.py and optical.py)
  python_file=${python_files[$((i % 2))]}
  
  echo "Running $python_file for $timeA sec..."
  
  # Run the Python script in the background
  python3 $python_file &
  
  # Get the process ID of the last background process
  pid=$!
  
  # Wait for 1 minute (60 seconds)
  sleep 10
  
  # Stop the Python process after 1 minute
  kill $pid
  
  echo "$python_file stopped. Switching to next..."

  sleep 10

  ((i++))

done

echo "All cycles completed!"
