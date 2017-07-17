#!/usr/bin/env python

import os, requests, json, sys, logging

config = ConfigParser.ConfigParser()
config.read('local_settings.cfg')
# Logging configuration
logging.basicConfig(filename=config.get('Logging', 'filename'),format=config.get('Logging', 'format', 1), datefmt=config.get('Logging', 'datefmt', 1), level=config.get('Logging', 'level', 0))
# Sets logging of requests to WARNING to avoid unneccessary info
logging.getLogger("requests").setLevel(logging.WARNING)
# Adds randomly generated commit message from external text file
#commitMessage = line = random.choice(open(config.get('Git', 'commitMessageData')).readlines());











# get a list of identifers
def getArchivalobjectsID ()



#This wil get get the data from the archival object URL
def getAOData (AOIDs)



def checkInstanceType (Moving Images, Audio)


def MakeList ResourceList


def deduplicates_list (Resources URI)





def getResourceData 
