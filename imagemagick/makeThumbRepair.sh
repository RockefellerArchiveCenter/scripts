#!/bin/bash
WWW=/var/www
# Make thumbnails from first page of PDFs
cd $WWW;
if [ "$(ls -A $WWW)" ]; then
    for file in `ls *.pdf`; do
        sudo chmod 777 $file
        #Make a thumbnail with a height of 100px
        convert $file[0] -thumbnail 'x100' `echo $file | sed 's/\.pdf$/\_thumb.jpg/'`
        #Make a square thumbnail 75x75 px
        convert $file[0] -thumbnail '75x75^' -gravity 'Center' -crop '75x75+0+0' `echo $file | sed 's/\.pdf$/\_thumb75.jpg/'`
        #Make a square thumbnail 75x75 px
        convert $file[0] -thumbnail '300x300^' -gravity 'Center' -crop '300x300+0+0' `echo $file | sed 's/\.pdf$/\_thumb300.jpg/'`
        #Make a large file with proportions of 1.9w to 1h
        convert $file[0] -gravity 'North' -crop '100%x53%+0+0' `echo $file | sed 's/\.pdf$/\_thumbfb.jpg/'`

        #reset file permissions
        for file in `ls *.*`; do
            sudo chmod 664 $file
        done
    done
    else
        echo 'No files to convert'
fi


#in another script: move files, change permissions