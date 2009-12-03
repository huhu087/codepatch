#----------------------------------------------------------------------------
# Logicking's CodePatch
#----------------------------------------------------------------------------
# CodePatch is an utility that works in two modes: merging code, and
# creating code patches.
#
# In merge mode it takes files from three folders ('base', 
# 'my' and 'theirs') and put merged files into the result folder. 
# CodePatch also updates binary files, calls external merge
# programs (e.g. WinMerge) to resolve occurred conflicts in text files,
# and writes statistics of performed actions.
# In creating patch mode CodePatch just checks files in 'base' and 'my' folders
# and put files that have been modified in 'my' into the result folder.
#
# CodePatch uses 'pymerge3' (http://code.google.com/p/pymerge3/)
# library to merge two files that have a common ancestor into a single file.
#
#----------------------------------------------------------------------------
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#----------------------------------------------------------------------------
# Copyright (C) 2009 Logicking.com
#----------------------------------------------------------------------------

#----------------------------------------------------------------------------
# File: codePatch.py
# Desc: CodePatch utility main file.
#----------------------------------------------------------------------------


import sys
import os
import subprocess
import shutil
import string
import ConfigParser
import filecmp

from merge3 import Merge3
import merge3.bzrlib.textfile


#using unicode
import sys, locale
reload(sys)
sys.setdefaultencoding(locale.getdefaultlocale()[1])


#Paths for the sources to be merged
baseCodePath = ""
theirCodePath = ""
myCodePath = ""
resultCodePath = ""

useExternalMergeProgram = False
mergeProgramPath = ""
mergeProgramArgs =  ""

#name of .cfg file
cfgFileName = 'codepatch.cfg' 
#name of log file
logFileName = "_codePatch.txt"

#------------------------------------------------------------------------------
# Name: readFileLines() writeFileLines()
# Desc: Helper functions to read and write text files
#------------------------------------------------------------------------------
def readFileLines(filename):
    try:
        f = open(filename, 'rU')    # rU for universal newline mode
    except:
        #File not exists
        return [], False

    #binary or text file
    first_chunk = f.read(1024)
    if '\x00' in first_chunk:
        f.close()
        return [], True
    
    f.seek(0);
    lines = f.readlines()
    f.close()
        
    return lines, False

def writeFileLines(filename, lines):
    f = open(filename, 'w')
    f.writelines(lines)
    f.close()
   
    


#------------------------------------------------------------------------------
# Name: resolveConflictFile()
# Desc: Calls external diff program to perform manual merge or mark conflicts
#------------------------------------------------------------------------------
def resolveConflictFile( myFile, theirFile=None):
    callList = [mergeProgramPath]
    callList.extend(mergeProgramArgs.split())
    myFile = myFile
    callList.append(myFile)
    if theirFile != None:
        callList.append(theirFile)

    try:
        retcode = subprocess.call(callList)
    except:
        retcode = -1

    if retcode != 0:
        print "Failed to load external diff program:\n" \
             , mergeProgramPath , " " , mergeProgramArgs , " " \
             , myFile, " ",  theirFile
        return False
    
    return True
#------------------------------------------------------------------------------
# Name: diff3MergeFiles()
# Desc: Uses Merge3 algorithm to merge files
#------------------------------------------------------------------------------
def diff3MergeFiles(baseFile, mineFile, theirFile, resultFile):
    isBinary = False
    baseText, tempIsBinary = readFileLines(baseFile)
    isBinary = isBinary or tempIsBinary
    mineText, tempIsBinary = readFileLines(mineFile)
    isBinary = isBinary or tempIsBinary
    theirText, tempIsBinary = readFileLines(theirFile)
    isBinary = isBinary or tempIsBinary

    #binary files
    if isBinary:
        print "File is binary."

    mineUpdated = False
    theirUpdated = False
    theirExists = os.path.isfile(theirFile)
    baseExists = os.path.isfile(baseFile)
    if os.path.isfile(mineFile):
        if theirExists and filecmp.cmp(mineFile, theirFile, shallow=0):
            print "No change needed"
            return
        if os.path.isfile(baseFile):
            mineUpdated = not filecmp.cmp(baseFile, mineFile, shallow=0)
        else:
            mineUpdated = True
    if theirExists:
        if baseExists:
            theirUpdated = not filecmp.cmp(baseFile, theirFile, shallow=0)
        else:
            theirUpdated = True
   
    if not theirUpdated and mineUpdated:
        print "'Mine' file used"
        return
    if theirUpdated and not mineUpdated:
        print "'Their' file used"
        
        try:
            shutil.copy2(theirFile, resultFile)
        except:
            print("Copy failed, are files same?")

        if isBinary:
            addStatistics("binary updated", resultFile)
        else:
            addStatistics("merged files", resultFile)
        return
    else:
        if isBinary:
            print "Conflict in binaries"
            addStatistics("!!! binary files with conflict, check them manualy", resultFile)
            return

    #Need to merge text files
    m = Merge3(baseText, mineText, theirText)

    start_marker = '<<<<<<<'
    mid_marker = '\n======='
    end_marker = '\n>>>>>>>'

    result = m.merge_lines(mineFile, theirFile, baseFile,
                            start_marker, mid_marker, end_marker)

    lines = [l for l in result]
    
    #check for conflicts
    conflicts = False
    for entry in lines:
        if string.find(entry, start_marker) == 0:
            conflicts = True
            break

    writeFileLines(resultFile, lines)
                
    if conflicts:
        print "Conflict in " + resultFile
        addStatistics("! text files with conflict", resultFile)
        #call external diff if needed
        if useExternalMergeProgram:
            print "Resolving"
            result = resolveConflictFile(resultFile)
            if(result): return
    
    if not conflicts:
        print "Merged"
        addStatistics("merged files", resultFile)

#------------------------------------------------------------------------------
# Name: mergeDirWalker()
# Desc: Call-back function for use with os.path.walk()
#------------------------------------------------------------------------------
def mergeDirWalker( rootPath, dirName, nameList ):

    subdir = os.path.relpath(dirName, rootPath)
       
    for entry in nameList:
         myFile = os.path.join( dirName, entry )

         resultFile = os.path.join( os.path.join( resultCodePath, subdir) , entry )

         #make sure we have the same dir structure in "my" and "result" folders 
         if os.path.isdir(myFile) :
             if not os.path.isdir(resultFile) :
                 os.mkdir(resultFile)
             continue

         #coping myFile to result
         try:
             shutil.copy2(myFile, resultFile)
         except:
            print("Copy failed, are files same?")
         
         
         theirFile = os.path.join( os.path.join( theirCodePath, subdir) , entry )
         #merge files
         if os.path.isfile(theirFile) :
             baseFile = os.path.join( os.path.join( baseCodePath, subdir) , entry )
             print "Checking file " + subdir + "\\" + entry
             diff3MergeFiles(baseFile, myFile, theirFile, resultFile)

#------------------------------------------------------------------------------
# Name: copyAbsentDirWalker()
# Desc: Copy all files from their to result, skip all existing files
#       because they were already merged
#------------------------------------------------------------------------------
def copyAbsentDirWalker( rootPath, dirName, nameList ):

    subdir = os.path.relpath(dirName, rootPath)

    for entry in nameList:
         myFile = os.path.join( dirName, entry )
         resultFile = os.path.join( os.path.join( resultCodePath, subdir) , entry )

         #make sure we have the same dir structure in "their" and "result" folders 
         if os.path.isdir(myFile) :
             if not os.path.isdir(resultFile) :
                 os.mkdir(resultFile)
             continue
         elif not os.path.isfile(resultFile) :
             #coping myFile to result
             print "Copying theirFile: " + subdir + "\\" +  myFile
             try:
                 shutil.copy2(myFile, resultFile)
             except:
                print("Copy failed, are files same?")
            
             addStatistics("copied files", myFile)

#------------------------------------------------------------------------------
# Name: readCfg()
# Desc: reads info from cfg file
#------------------------------------------------------------------------------
def readCfg() :
    config = ConfigParser.SafeConfigParser({'base_path' : '\\~',
                                            'my_path' : '\\~',
                                            'their_path' : '\\~',
                                            'result_path' : '\\~'})
    config.read(cfgFileName)


    global baseCodePath
    global theirCodePath
    global myCodePath
    global resultCodePath

    global useExternalMergeProgram
    global mergeProgramPath
    global mergeProgramArgs

    try:
        baseCodePath = config.get("dirs", 'base_path')
        theirCodePath = config.get("dirs", 'their_path')
        myCodePath = config.get("dirs", 'my_path')
        resultCodePath = config.get("dirs", 'result_path')

        useExternalMergeProgram = config.getboolean("merge", 'use_external_merge_program')
        mergeProgramPath = config.get("merge", 'merge_program_path')
        mergeProgramArgs = config.get("merge", 'merge_program_args')
    except ConfigParser.NoSectionError:
        print "Error in cfg, using defaults"
        

#------------------------------------------------------------------------------
# Name: saveCfg()
# Desc: saves config params
#------------------------------------------------------------------------------
def saveCfg():
    config = ConfigParser.ConfigParser()
    config.read(cfgFileName)

    try:
        config.add_section("dirs")
    except:
        print ""
        
        
    config.set("dirs", 'base_path', baseCodePath)
    config.set("dirs", 'their_path', theirCodePath)
    config.set("dirs", 'my_path', myCodePath)
    config.set("dirs", 'result_path', resultCodePath)

    try:
        config.add_section("merge")
    except:
        print ""
        
    config.set("merge", 'use_external_merge_program', useExternalMergeProgram)
    config.set("merge", 'merge_program_path', mergeProgramPath)
    config.set("merge", 'merge_program_args', mergeProgramArgs)

    with open(cfgFileName, 'wb') as configfile:
        config.write(configfile)

#------------------------------------------------------------------------------
# Name: checkDirs()
# Desc: checking dirs and give warning if no dir at specified path exists
#       or dir contains no file that need to be merged
#------------------------------------------------------------------------------
def checkSimilaritiesWithBase( rootPath, dirName, nameList ):
    global similaritiesFound
    if similaritiesFound:
        return
    
    subdir = os.path.relpath(dirName, rootPath)

    for entry in nameList:
        theirFile = os.path.join( dirName, entry )
        baseFile = os.path.join( os.path.join( baseCodePath, subdir) , entry )
        myFile = os.path.join( os.path.join( myCodePath, subdir) , entry )

        #we have at least one file to merge
        if os.path.isfile(theirFile) and (os.path.isfile(baseFile) or
                                       os.path.isfile(myFile)):
            similaritiesFound = True
            break

def checkDirs(mergeMode = True):
    result = True
    msg = ""

    if not os.path.isdir(myCodePath):
        result = False
        msg = msg + "Wrong path for myPath: " + myCodePath + "\n"
    if not os.path.isdir(baseCodePath):
        result = False
        msg = msg + "Wrong path for basePath: " + baseCodePath + "\n"
    if mergeMode and not os.path.isdir(theirCodePath):
        result = False
        msg = msg + "Wrong path for theirPath: " + theirCodePath + "\n"
    if not os.path.isdir(resultCodePath):
        result = False
        msg = msg + "Wrong path for resultPath: " + resultCodePath + "\n"

    if not mergeMode or not result:
        return result, msg

    global similaritiesFound
    similaritiesFound = False
    os.path.walk( theirCodePath, checkSimilaritiesWithBase, theirCodePath )
    if not similaritiesFound:
        result = False
        msg = msg + "No files to merge  in theirPath  " + resultCodePath + "\n"

    return result, msg

#------------------------------------------------------------------------------
# Name: performPatch()
# Desc: Patches source code from specified dirs
#------------------------------------------------------------------------------
def performPatch():
    clearStatistics()
    print "Updating...\n"
    os.path.walk( myCodePath, mergeDirWalker, myCodePath )
    print "\n" + "Copying..."
    os.path.walk( theirCodePath, copyAbsentDirWalker, theirCodePath )
    writeStatisticsLog(True)
    print "\n" + "Completed successfully"


#------------------------------------------------------------------------------
# Name: createPatch() and copyDifferentDirWalker()
# Desc: Creates patch checking specified dirs
#------------------------------------------------------------------------------

def copyDifferentDirWalker( rootPath, dirName, nameList ):

    subdir = os.path.relpath(dirName, rootPath)

    for entry in nameList:
        myFile = os.path.join( dirName, entry )

        if os.path.isdir(myFile): continue
         
        baseFile = os.path.join( os.path.join( baseCodePath, subdir) , entry )
        resultFile = os.path.join( os.path.join( resultCodePath, subdir) , entry )

        if not os.path.isfile(baseFile) or \
                not filecmp.cmp(myFile, baseFile, shallow=0):
            resultDir = os.path.join( resultCodePath, subdir)
            if not os.path.isdir(resultDir): os.makedirs(resultDir)
            try:
                shutil.copy2(myFile, resultFile)
            except:
                print("Copy failed, are files same?")
                
            myFile = os.path.normpath(myFile)
            print "Copy " + os.path.normpath(myFile)
            addStatistics("copied files", myFile);

def createPatch():
    clearStatistics()
    print "Copying..."
    os.path.walk( myCodePath, copyDifferentDirWalker, myCodePath )
    writeStatisticsLog(False)
    print "\n" + "Completed successfully"

#------------------------------------------------------------------------------
# Functions to operate with statistics info
#------------------------------------------------------------------------------
statisticsInfo = {}

def addStatistics(recordType, recordInfo):
    global statisticsInfo
    if not recordType in statisticsInfo:
        statisticsInfo[recordType] = []
    statisticsInfo[recordType].append(recordInfo)
    statisticsInfo[recordType].append("\n")

def clearStatistics():
    global statisticsInfo
    statisticsInfo = {}
    
def writeStatisticsLog(isPatching):

    lines = []
    for entry in statisticsInfo:
        lines.extend(statisticsInfo[entry])
        lines.append("\n------------------------------------------------------")
        lines.append("\n\n\n"+ entry )

    header = ""
    if (isPatching):
        header = """Code is patched. \n
base:       %s
my:         %s
their:      %s
result:     %s
                   """ % (baseCodePath, myCodePath, theirCodePath, resultCodePath)
    else:
        header = """Patch is created. \n
base:       %s
my:         %s
result:     %s
                   """ % (baseCodePath, myCodePath, resultCodePath)
    lines.append(header)
    lines.reverse()

    logFile = os.path.join( resultCodePath, logFileName)
    writeFileLines(logFile, lines)
    
    subprocess.Popen("\""+ logFile + "\"", shell=True)

#------------------------------------------------------------------------------
# Script entry point...
#------------------------------------------------------------------------------

if __name__ == '__main__':

    arg = ""
    if len(sys.argv) > 1:
        arg = sys.argv[1]

    readCfg()

    if arg == "-c":
        result, msg = checkDirs(False)
        if not result:
            print msg
        else:        
            createPatch()

    elif arg == "-p":
        result, msg = checkDirs()
        if not result:
            print msg
        else:        
            performPatch()
    else:
        print """Logicking's CodePatch

-c  to create patch from base_path to my_path.
-p  to update my_path from to their_path, using base_path as \
common ancestor.

Result will be placed in result_path in both cases.
Change %s to specify path.
                """ % (cfgFileName)
    saveCfg()

    #raw_input( '\n\nPress Enter to exit...' )

