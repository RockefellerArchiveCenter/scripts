#!/usr/bin/env bash

read -p "Enter the name you want your gifs to start with: " gifName
read -p "Enter the filename of the movie file (including extension): " movie
read -p "Start time (seconds): " startTime
read -p "Stop time (seconds): " stopTime
read -p "Length of gifs (seconds): " length
read -p "Time between gifs (seconds): " between
echo "Making gifs from ${movie} to ${gifName}.gif"

# make palette
ffmpeg -ss ${startTime} -i ${movie} -filter_complex "fps=10,scale=500:-1:flags=lanczos,palettegen" -t 3 palette.png

# make gif

increment=1

while [ $startTime -le $stopTime ]
do
	ffmpeg -ss ${startTime} -i ${movie} -i palette.png -filter_complex "[0:v]fps=10, scale=500:-1:flags=lanczos[v], [v][1:v]paletteuse" -t ${length} ${gifName}_${increment}.gif
	startTime=$(($startTime+$between))
	echo $startTime
	increment=$(($increment+1))
	echo $increment
done
