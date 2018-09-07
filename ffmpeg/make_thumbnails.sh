#!/usr/bin/env bash

# generates three thumbnails per movie

read -p "Enter the name you want your thumbnails to start with: " thumbnail
read -p "Enter the filename of the movie file (including extension): " movie


duration=`ffmpeg -i ${movie} 2>&1 | grep "Duration"| cut -d ' ' -f 4 | sed s/,// | sed 's@\..*@@g' | awk '{ split($1, A, ":"); split(A[3], B, "."); print 3600*A[1] + 60*A[2] + B[1] }'`
echo $duration

start=$(( ${duration} * 1/3 ))
stop=$(( ${duration} * 2/3 ))
length=$((${start}/8))

ffmpeg -i ${movie} -ss ${start} -to ${stop} -vf fps=1/${length} ${thumbnail}%02d.png

# -to 00:55:00