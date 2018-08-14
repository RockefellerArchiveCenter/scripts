#!/usr/bin/env bash

read -p "Enter the name you want your clips to start with: " clipName
read -p "Enter the filename of the movie file (including extension): " movie
read -p "Start time (seconds): " startTime
read -p "Stop time (seconds): " stopTime
read -p "Length of clips (seconds): " length
read -p "Time between start time of clips (seconds): " between
echo "Making clips from ${movie} to ${clipName}.mp4"

increment=1

while [ $startTime -le $stopTime ]
do
	ffmpeg -ss ${startTime} -i ${movie} -c copy -t ${length} ${clipName}_${increment}.mp4
	startTime=$(($startTime+$between))
	echo $startTime
	increment=$(($increment+1))
	echo $increment
done
