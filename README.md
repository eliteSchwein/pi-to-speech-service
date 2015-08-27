PI-TO-SPEECH - SERVICE
=====================================

### Description

This python script converts the given string message to audio and write it into a file.
All files are stored locally on the filesystem. Before creation of the audio files, a cache mechanism checks if the audio file with the needed string message exists.
If the audio file is found, there is no reason to call the tts service or create the audio file again.   


### TTS Services

Uses the Google TTS Service (online) or the pico2wave (offline) application. 

### Requirements

1. install mpg123
```
  $ sudo apt-get install mpg123
```

2. install Pico TTS
```
  $ sudo apt-get install libpopt-dev; wget http://www.dr-bischoff.de/raspi/pico2wave.deb; sudo dpkg --install pico2wave.deb
```

3. install omxplayer (optional)
```
  $ sudo apt-get install omxplayer
```


### Example start command
```
  $ python tts-service.py --text "Hello"
```

### Parameter

Parameter | Description | Optional | Default
--------- | ------------| -------- | -------  
 -t   --text      |  text to translate                  | false  |
 -p   --provider  |  the tts provider (google or pico)  | true   | google
 -q   --quiet     |  do not print log messages          | true   | false
 -ns  --noStore   |  do not store the soundfile         | true   | false
 -u   --update    |  update soundfile if exist          | true   | false


### License
The license is committed to the repository in the project folder as `LICENSE.txt`.
Please see the `LICENSE.txt` file for full informations.


----------------------------------

Markus Eschenbach  
http://www.blogging-it.com
