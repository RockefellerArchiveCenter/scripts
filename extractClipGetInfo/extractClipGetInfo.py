#!/usr/bin/env python

import json, csv, os, getpass, configparser, math
from asnake.client import ASnakeClient

# get refId - used to make clips from original video with the filename [refid].mp4, and get information from ArchivesSpace
def getRefId():
    while True:
        refId = input("Enter the ArchivesSpace RefId: ")
        if len(refId) != 32: # in our implementation of ArchivesSpace, all RefIds are 32 characters
            print("Enter the ArchivesSpace RefId: ")
        else:
            return refId

def getCount():
    return input("Enter the number to append to the filename: ")

# get start time and length of clip
def getStartTime():
    while True:
        startHours =  input("Enter the hours of the start time: ") 
        startMinutes = input("Enter the minutes of the start time: ") 
        startSeconds = input("Enter the seconds of the start time: ") 
        return startHours.zfill(2) + ":" + startMinutes.zfill(2) + ":" + startSeconds.zfill(2) # adds leading zero for single-digit numbers

def getLength():
    minutes = int(input("Enter the minutes of the duration: "))
    seconds = float(input("Enter the seconds of the duration: "))
    return str((minutes * 60) + seconds)

# create clip
def makeClip(refId,startTime,length,count):
    inputName = refId + ".mp4"
    global outputFile
    outputFile = refId + "_" + str(count) + ".mp4"
    ffmpegCommand = "ffmpeg -ss " + startTime + " -i " + inputName + " -c copy -t " + length + " " + "Clips/" + outputFile
    os.system(ffmpegCommand)

# get information from archivesspace
def getAo(refId):
    url = 'repositories/2/find_by_id/archival_objects?ref_id[]=' + refId
    ao = client.get(url).json()
    ao_ref = ao["archival_objects"][0]["ref"]
    return client.get(ao_ref).json()

def getObjectTitle(ao):
    return ao["title"]

def getScopeContent(ao):
    if ao["notes"]:
        for n in ao["notes"]:
            if n["type"] == "scopecontent":
                return (n["subnotes"][0]["content"]).replace('\n', ' ')

def getAvNumber(ao):
    #get top container ref
    container = client.get(ao["instances"][0]["sub_container"]["top_container"]["ref"]).json()
    #get top container indicator
    return container["indicator"]

def getObjectDates(ao):
    return (ao["dates"][0]["expression"])

def getCollectionInfo(ao):
    return client.get(ao["resource"]["ref"]).json()

def getCollectionTitle(collectionInfo):
    return collectionInfo["title"]

def getCollectionId(collectionInfo):
    return collectionInfo["id_0"]

def makeRow():
    row = []
    row.append(outputFile) # write column: filename
    row.append(refId) # write column: refId
    row.append(getObjectTitle(ao).replace('\n', ' ')) # write column: original video title
    row.append(getObjectDates(ao)) # write column: original video dates
    row.append(getAvNumber(ao)) # write column: av number
    row.append(getCollectionTitle(collectionInfo).replace('\n', ' ') + " (" + getCollectionId(collectionInfo) + ")") # write column: collection title and FA #
    row.append(getScopeContent(ao)) # write column: scope and contents
    row.append(startTime) # write column: clip start time
    row.append(str(int(math.ceil(float(length))) // 60).zfill(2) + ":" + str(int(math.ceil(float(length))) % 60).zfill(2)) # format duration of clip as MM:SS and rounds up seconds
    writer.writerow(row)

# enter aspace login info
config = configparser.ConfigParser()
config.read('local_settings.cfg')
baseurl= config.get('ArchivesSpace', 'baseURL')
user = input('ArchivesSpace username: ')
pw = getpass.getpass('ArchivesSpace password:')

# start aspace session

client = ASnakeClient(baseurl=baseurl,username=user,password=pw)
print("Logging into ArchivesSpace...")
client.authorize()
#columnHeadings = ["Filename","Reference ID","Original Title","Dates","AV Number","Collection","Scope and Contents","Start Time","Duration"]
while True:
    inp = input("New RefId? y/n/q: ")
    if inp == "q" or inp == "quit":
        break
    elif inp == "y" or inp == "yes":
        spreadsheet = open("inventory.csv", "a")
        writer = csv.writer(spreadsheet)
        refId = getRefId()
        count = int(input("Number to start appending to file (e.g., 1): "))
        startTime = getStartTime()
        length = getLength()
        makeClip(refId,startTime,length,count)
        ao = getAo(refId)
        collectionInfo = getCollectionInfo(ao)
        # writer.writerow([])
        makeRow()
        print('Row added!')
        spreadsheet.close()
    elif inp == "n" or inp == "no":
        spreadsheet = open("inventory.csv", "a")
        writer = csv.writer(spreadsheet)
        count += 1
        startTime = getStartTime()
        length = getLength()
        makeClip(refId,startTime,length,count)
        ao = getAo(refId)
        collectionInfo = getCollectionInfo(ao)
        makeRow()
        print('Row added!')
        spreadsheet.close()
    else:
        break
    
