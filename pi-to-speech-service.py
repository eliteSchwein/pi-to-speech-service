#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#===================================================================
#	                PI-TO-SPEECH - SERVICE
# 		                -- VERSION 1.0.1  --
#
#
#
# Description
#==============
# This python script converts the given string message to audio and write it into a file.
# All files are stored locally on the filesystem. Before creation of the audio files, a cache mechanism checks if the audio file with the needed string message exists.
# If the audio file is found, there is no reason to call the tts service or create the audio file again.    
#
#
# TTS Services
#==============
# Uses the Google TTS Service (online) or the pico2wave (offline) application. 
#
#
# Requirements
#==============
# 1. install mpg123
# sudo apt-get install mpg123
#
# 2. install Pico TTS
# sudo apt-get install libpopt-dev; wget http://www.dr-bischoff.de/raspi/pico2wave.deb; sudo dpkg --install pico2wave.deb
#
# 3. install sox to modify sound file (optional - set SOUND_MODIFY to True)
# sudo apt-get install sox libsox-fmt-all 
#
# 4. install mplayer (optional)
# sudo apt-get install mplayer
#
#
#
# Example start command
#========================
# python tts-service.py --text "Hello"
# 
#
# Parameter
#========================
# -t   --text        text to translate                    required
# -p   --provider    the tts provider (google or pico)    optional  defaullt: google
# -d   --device      the output device (e.g. bluetooh)    optional  defaullt: ''
# -q   --quiet       do not print log messages            optional  defaullt: false
# -ns  --noStore     do not store the soundfile           optional  defaullt: false
# -u   --update      update soundfile if exist            optional  defaullt: false
#
#
#
#    ::::::::::::::: www.blogging-it.com :::::::::::::::
#    
# Copyright (C) 2015 Markus Eschenbach. All rights reserved.
# 
# 
# This software is provided on an "as-is" basis, without any express or implied warranty.
# In no event shall the author be held liable for any damages arising from the
# use of this software.
# 
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter and redistribute it,
# provided that the following conditions are met:
# 
# 1. All redistributions of source code files must retain all copyright
#    notices that are currently in place, and this list of conditions without
#    modification.
# 
# 2. All redistributions in binary form must retain all occurrences of the
#    above copyright notice and web site addresses that are currently in
#    place (for example, in the About boxes).
# 
# 3. The origin of this software must not be misrepresented; you must not
#    claim that you wrote the original software. If you use this software to
#    distribute a product, an acknowledgment in the product documentation
#    would be appreciated but is not required.
# 
# 4. Modified versions in source or binary form must be plainly marked as
#    such, and must not be misrepresented as being the original software.
#    
#    ::::::::::::::: www.blogging-it.com :::::::::::::::
#===================================================================


#===================================================================
#	IMPORTS
#===================================================================
import sys, os, io, re, urllib, urllib2, argparse, json, codecs, shlex, shutil
from subprocess import Popen, PIPE
#from pprint import pprint

#===================================================================
#	SETTINGS
#===================================================================
SOUND_FILES_DIR= os.path.dirname(os.path.abspath(__file__)) + "/sounds/"
SOUND_FILE_NAME="sound_%d"
SOUND_INDEX_FILE=SOUND_FILES_DIR + "index.json"
SOUND_PLAYER="mpg123" #Play sound with mplayer, mpg123

#MODIFY SOUND FILE 
SOUND_MODIFY=False
SOUND_MODIFY_SILENCE_BEGIN=3 #silence at beginning of file
SOUND_MODIFY_SILENCE_END=2 #silence at end of file

GOOGLE_MAX_CHARS = 100 #max length of characters per translation request
LANGUAGE = "de-DE" #language
ENCODING = "UTF-8" #character encoding


PROVIDER = {
   		'pico': {
         'func': 'provider_pico_create_data',
         'ext' : '.wav' 
      },
   		'google': {
         'func': 'provider_google_create_data',
         'ext' : '.mp3' 
      }      
}


def log(msg):
   if app_args['verbose'] and msg != '':
      print(msg)
   #end else
   
   return

def util_sound_modify(srcFile):
   if SOUND_MODIFY:	
      log(' modify sound file')  
      if srcFile.endswith('.mp3'):
         modFile = srcFile + '-mod.mp3'
      else:
         modFile = srcFile + '-mod.wav'      
      #end if				      
      
      util_sound_silence(srcFile,modFile)
   #end if

   return
   
def util_sound_silence(srcFile,modFile):   
   cmd = 'sox "' + srcFile + '" "' + modFile + '" pad ' + str(SOUND_MODIFY_SILENCE_BEGIN) + ' ' + str(SOUND_MODIFY_SILENCE_END)
   util_cmd_execute(cmd)
   util_file_move(modFile,srcFile)
   return
 

def util_text_SplitToParts(fullText):
   parts = re.split("[\,\;\.\:]", fullText)

   allTextParts = []

   while len(parts)>0: 
      part = parts.pop(0)

      if len(part)>GOOGLE_MAX_CHARS:
         cutIdx = part.rfind(" ",0,GOOGLE_MAX_CHARS) # last space within the bounds of the GOOGLE_MAX_CHARS

         tmpPart = part[:cutIdx]

         parts.reverse()
         parts.append(part[cutIdx:])
         parts.reverse()
      else:
         tmpPart = part #cutting not needed

         tmpPart = tmpPart.strip()
         if tmpPart is not "":
            allTextParts.append(tmpPart.strip())
         #end if
      #end else
   #end while
      
   return allTextParts

def util_file_is_valid(filePath):
   arg = os.path.abspath(filePath)
   fileExists = False
   if os.path.exists(filePath):
      fileExists = True
   #end if
    
   return fileExists

def util_file_remove(filePath):
   if util_file_is_valid(filePath):
      os.remove(filePath)
      log("remove file: " + filePath)
   #end if      

   return    

def util_file_copy(srcPath,desPath):
   log('copy file from: ' + srcPath + '  to: ' + desPath)
   shutil.copy2(srcPath, desPath)   

   return 

def util_file_move(srcPath,desPath):
   log('move file from: ' + srcPath + '  to: ' + desPath)
   shutil.move(srcPath, desPath)   

   return      
   
    
def util_file_count(dirPath,extension):
    fileCount = len([name for name in os.listdir(dirPath) if os.path.isfile(os.path.join(dirPath, name)) and name.endswith(extension)])
    
    return fileCount   
      
        
def provider_google_create_data(fullText,filePath):
      
   textParts = util_text_SplitToParts(fullText)
   
   fileToStore = open(filePath,"wb")
   
   for part in textParts:
      log("Retrieving google sound for sentence: %s" % (part))
   
      baseurl="http://translate.google.com/translate_tts"
      values={'q': part.encode(ENCODING), 'tl': LANGUAGE, 'ie': ENCODING, 'total': 1, 'idx': 0,'client': 't'}

      encodedQuery=urllib.urlencode(values)
      request=urllib2.Request(baseurl + "?" + encodedQuery)
      request.add_header("User-Agent", "Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11" )
      response=urllib2.urlopen(request)
      data = response.read()
   
      fileToStore.write(data)
   #end for
   
   fileToStore.close() 
   
   return

def provider_pico_create_data(fullText,filePath):
   log("Retrieving pico sound for sentence: %s" % (fullText))
   
   cmd = 'pico2wave -l ' + LANGUAGE + ' -w "' + filePath + '" "' + fullText + '"';
   util_cmd_execute(cmd)
 
   return 

def util_cmd_execute(cmd):
   log('execute command: ' + cmd);
   p = Popen(shlex.split(cmd), stdout=PIPE, stderr=PIPE)
   output, error = p.communicate()
   log(output)      
   log(error)
   #FNULL = open(os.devnull, 'w')
   return

def output_sound(pathToFile, device=''):  
   if util_file_is_valid(pathToFile):
      cmd = SOUND_PLAYER      
      if device != '':
	 	     if SOUND_PLAYER == 'mplayer':
	 	 	 	    cmd += ' -ao alsa:device="' + device + '"'
	 	     else:
	 	 	 	    cmd += ' -a "' + device + '"'
	 	     #end if
      #End if
      
      cmd += ' "' + pathToFile + '"'

      util_cmd_execute(cmd)
   #end if
   
   return


def index_write_to_file(dataDict):
   dataStr = json.dumps(dataDict, ensure_ascii=False, encoding=ENCODING)
   file_output = codecs.open(SOUND_INDEX_FILE, 'w', ENCODING)
   file_output.write(dataStr)
   file_output.close()

   return
   
   
def index_read_data():

   #input_file = open(SOUND_INDEX_FILE)
   input_file= file(SOUND_INDEX_FILE, "r")
   dataStr = input_file.read().decode("utf-8-sig")
   dataDict = json.loads(dataStr)
   input_file.close()

   return dataDict

 
def index_set_sound_info(text, filePath):

   data = index_read_data()
   data['sounds'].append({'text': text,'path': filePath})
   
   #pprint(data)
   
   index_write_to_file(data)
      
   return


def index_get_sound_info(text,fileExtension):
	 data = index_read_data()
	 soundInfo = None

	 for s in data['sounds']:
	 	 if s['text'].lower() == text.lower() and s['path'].endswith(fileExtension):
	 	 	 	 soundInfo = s
	 	 	 	 log('index found: ' + s['path'])
	 	 	 	 break   
	 	 #end if
	 #end for

	 return soundInfo


def init_app():  
   global app_args
	 
   app_args = vars(PARSER.parse_args())
		
   if not os.path.exists(SOUND_FILES_DIR):
      os.makedirs(SOUND_FILES_DIR)
   #end if
 
   if not os.path.exists(SOUND_INDEX_FILE):
      index_write_to_file({u'sounds':[]})
   #end if  
   
   return
   
def create_sound_file_path(fileExt,temp):
   dirPath = SOUND_FILES_DIR 
   
   if temp:
      dirPath += 'tmp/'
      if not os.path.exists(dirPath):
         os.makedirs(dirPath)
      #end if   
   #end if
            
   countFile = util_file_count(dirPath,fileExt)
   
   fullPath = dirPath + SOUND_FILE_NAME % (countFile+1) + fileExt
   
   return fullPath   

def create_sound_file(fullText,provider,filePath):
   
   log("Use provider: " + provider)
   
   providerFunc = PROVIDER.get(provider)['func']
   
   globals()[providerFunc](fullText,filePath)      
   
   log("Saved to file: %s" % filePath)
	
   return
   

#===================================================================
#	MAIN FUNCTION
#===================================================================
def main():
   init_app()
   fullText = app_args['text'].decode('unicode_escape')
   provider = app_args['provider']
   storeFile = app_args['storeFile']
   updateFile = app_args['updateFile']
   outputDevice = app_args['device']
   
   fileExtension = PROVIDER.get(provider)['ext']
   
   soundInfo = index_get_sound_info(fullText,fileExtension)
     
   if soundInfo is None or updateFile:       
      newSoundFilePathTmp = create_sound_file_path(fileExtension,True)
      newSoundFilePathFinal = create_sound_file_path(fileExtension,False)     
      
      create_sound_file(fullText,provider,newSoundFilePathTmp)
        
      util_sound_modify(newSoundFilePathTmp)

      util_file_move(newSoundFilePathTmp, newSoundFilePathFinal)
   	           
      if storeFile:
          index_set_sound_info(fullText,newSoundFilePathFinal)
      #end if      
   else:
      newSoundFilePathFinal = soundInfo['path']
   #end if   
      
   #ouput sound with player
   output_sound(newSoundFilePathFinal,outputDevice)

   if soundInfo is None and not storeFile:
      util_file_remove(newSoundFilePathFinal) #cleanup  
   #end if   
   
   return



#===================================================================
#	INITIALIZE 
#===================================================================
app_args = None

PARSER = argparse.ArgumentParser(prog='text to speech', usage='%(prog)s [options] text')
# Add arguments
PARSER.add_argument('-t', '--text', required=True,  help='text to translate')
PARSER.add_argument('-p', '--provider', nargs='?', default='google', choices=['google','pico'], help='the tts provider')
PARSER.add_argument('-d', '--device', nargs='?', default='', help='the output device (e. g. bluetooth')
PARSER.add_argument('-q', '--quiet', action='store_false', dest='verbose', default=True, help='do not print log messages')
PARSER.add_argument('-ns','--noStore', action='store_false', dest='storeFile', default=True, help='do not store the soundfile')
PARSER.add_argument('-u', '--update', action='store_true', dest='updateFile', default=False, help='update soundfile if exist')

#===================================================================
#	START THE PROGRAMM
#===================================================================
main();

                                                                                                                                                                            
