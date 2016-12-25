#!/bin/bash

echo "file name: $1\n" # without extension
for ((i = 0; i <= $2; i++))
do
echo $1_segment$i.ppm
tesseract images/$1_segment$i.ppm text/$1_segment${i} #_ws
done
