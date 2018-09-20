#!/usr/bin/python3

from similarity.cosine import Cosine
import sys
import os
import re
import subprocess

clean_times = [];
clean_lines = [];
part_file_names = [];
time_regex = r'(.+) --> (.+)'
cosine = Cosine(2)
mySrtFileName = ""
mediaFileName = ""
mediaFileExtension = ""
accuracy_decimal = 0.0

def make_part(startTime, endTime, partNum):
    musicFileCopyName = "parts%sCleanPart%s%s" % (os.sep, partNum, mediaFileExtension)
    
    with open(musicFileName) as musicFile:
        bashCommand = "ffmpeg -y -i \"%s\" -ss %s -to %s -c copy \"%s\"" % (musicFileName, startTime, endTime, musicFileCopyName)
        bashCall = subprocess.Popen(bashCommand, shell=True, stdout=subprocess.PIPE)
        output, error = bashCall.communicate()
        part_file_names.append(musicFileCopyName)
        

def clean_and_insert_times(timeLine, textLine, index):
    if re.match(time_regex, timeLine) == None:
        return
    
    matchGroup = re.search(time_regex, timeLine)
    
    startTime = matchGroup.group(1).replace(",", ".")
    startTime = startTime[:-1]
    
    endTime = matchGroup.group(2).replace(",", ".")
    endTime = endTime[:-1]
    
    if index is -1:
        clean_times.append((startTime, endTime))
        clean_lines.append(textLine)
    else:
        clean_times[index] = (startTime, endTime)
        clean_lines[index] = textLine

def compare_first_to_second(firstStr, secondStr):
    if firstStr is "" or secondStr is "":
        return 0.0

    if firstStr.isdigit() or secondStr.isdigit():
        return 0.0
    
    firstProfile = cosine.get_profile(str(firstStr))
    secondProfile = cosine.get_profile(str(secondStr))
    
    return cosine.similarity_profiles(firstProfile, secondProfile)

def get_time_and_textline(mySrtFile):
    if mySrtFile.readline() == '':
        return "", ""
    
    timeLine = mySrtFile.readline()
    timeLine = timeLine[:-1]
    textLine = mySrtFile.readline()
    textLine = textLine[:-1]
    mySrtFile.readline()
    
    return timeLine, textLine

def fuse_parts():
    with open("parts_list.txt", 'w') as partsListFile:
        for fileName in part_file_names:
            partsListFile.write("file '%s'\n" % (fileName))
    
    newFileName = "new%s" % (mediaFileExtension)
    bashCommand = "ffmpeg -y -f concat -safe 0 -i parts_list.txt -c copy %s" % (newFileName)
    bashCall = subprocess.Popen(bashCommand, shell=True, stdout=subprocess.PIPE)
    output, error = bashCall.communicate()

def generate_part_files():
    partNum = 1
    for firstTime, endTime in clean_times:
        make_part(firstTime, endTime, partNum)
        partNum = partNum + 1

# Not the most efficient way of doing this..
# Mainly here just to solve the problem first.
#
# TODO: A hash might help with this. Maybe this?
# https://en.wikipedia.org/wiki/Locality-sensitive_hashing
def get_match_index(currentTextLine):
    index = 0
    for textLine in clean_lines:
        if compare_first_to_second(textLine, currentTextLine) > accuracy_decimal:
            return index
        index = index + 1
    return -1

def make_parts_directory():
    partsPath = os.path.join(os.sep, os.getcwd(), 'parts')
    if not os.path.exists(partsPath):
        os.makedirs(partsPath)

def populate_clean_times():
    if len(sys.argv) is not 4:
        print("Invalid arguments.")
        print("Usage: make_clean_audio.py inputfile.mediatype inputfile.srt decimal_accuracy(ex: 0.5 = 50%)")
        exit(1)
    
    global accuracy_decimal
    accuracy_decimal = float(sys.argv[3])
    global musicFileName
    musicFileName = sys.argv[1]
    global mySrtFileName
    mySrtFileName = sys.argv[2]
    global mediaFileExtension
    filename, mediaFileExtension = os.path.splitext(musicFileName)
    
    with open(mySrtFileName) as mySrtFile:
        while True:
            currentTimeLine, currentTextLine = get_time_and_textline(mySrtFile)
            if currentTextLine is '':
                break
            
            index = get_match_index(currentTextLine)
            clean_and_insert_times(currentTimeLine, currentTextLine, index)
        
if __name__ == "__main__":   
    make_parts_directory()
    populate_clean_times()
    generate_part_files()
    fuse_parts()
