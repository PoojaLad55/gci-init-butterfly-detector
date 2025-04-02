#!/bin/bash

gci_file_path="/home/lambopancake/Desktop/gci-init-butterfly-detector"
source "$gci_file_path/.fly/bin/activate"

store_folder="$(date +%s)_cap"
echo $store_folder


#Define the Python files to alternate between
python_files=("$gci_file_path/record_vid.py" "$gci_file_path/optical_flow.py")

# Total number of repetitions (10 cycles)
timeA=60
timeB=60
i=0
# Loop for 10 cycles and to test for [cycles] times
#for ((i = 0; i < 5; i++))
while true;
do
  # Determine which Python file to run (alternates between record.py and optical.py)
  python_file=${python_files[$((i % 2))]}
  
  echo "Running $python_file for $timeA sec..."
  
  # Run the Python script in the background
  python3 "$python_file" "$store_folder" "$timeA"
  
  # Get the process ID of the last background process
  pid=$!
  
  # Wait for 1 minute (60 seconds)
  sleep 30
  
  # Stop the Python process after 1 minute
  kill $pid
  
  echo "$python_file stopped. Switching to next..."

  sleep 15

  ((i++))

done
