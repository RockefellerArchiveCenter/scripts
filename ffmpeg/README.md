# ffmpeg 
These scripts use ffmpeg to create clips, gifs, and thumbnails from a video file. Each script should be run from the directory where the video file is.

Ffmpeg is required. For more information, see https://amiaopensource.github.io/ffmprovisr/

## make_clips.sh
Creates video clips from an MP4 file, according to user input for initial start time, end time, length of clips, and time between the start time of each clip.

More information about the ffmpeg command: https://amiaopensource.github.io/ffmprovisr/#excerpt_from_start

## make_gifs.sh
Creates gifs from an MP4 file, according to user input for initial start time, end time, length of gifs, and time between the start time of each gif.

More information about the ffmpeg command: https://amiaopensource.github.io/ffmprovisr/#create_gif

## make_thumbnails.sh
Creates 8 PNG thumbnails from an MP4 file, which start 1/3 and end 2/3 of the way through the video, and are evenly spaced.

More information about the ffmpeg command: https://amiaopensource.github.io/ffmprovisr/#one_thumbnail
