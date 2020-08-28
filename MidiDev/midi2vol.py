import sys
import os
import rtmidi
import math
import time
import pulsectl
import alsaaudio
import json
import logging
from datetime import datetime

defaultfile='config.json'


def openNano(midi_in):
	count = 0
	for port_name in midi_in.get_ports():
		if (port_name.split(":")[0] == "nano. slider"): 		   #try to connect to nano. slider 
			midi_in.open_port(count)
			logging.debug('nano. slider found')
			return True
		else:
			count = count + 1
	logging.debug('could not find nano. slider')
	return False

def execution(midi_in,sinkType,config):
	oldVolumeRaw = -1
	paready = False
	if (openNano(midi_in)): 										# if connected to nano , check if there's a message 
		while True:
			midiMessage= midi_in.get_message()
			if midiMessage: 										# if rtmidi gives None as a message , sleep the thread to avoid overloading cpu
	 	 		message,time_stamp = midiMessage					# rtmidi lib , passes a tuple [midiMessage , timeStamp], we need the message
	 	 		applicationRaw=message[1]					        # gives option to change volume of source ex: Spotify , Chrome, etc.
	  			volumeRaw = message[2] 								# Message is an array in wich the third argument is the value of the potentiometer slider from 0 to 127
	  			if volumeRaw != oldVolumeRaw: 						# check if slider positon has changed
	  				oldVolumeRaw= volumeRaw 						#update value for next iteration

	  				if(sinkType=="alsa"):							# if alsa is chosen values go from 0 to 100
	  					volume = math.floor((volumeRaw/3)*2.38)
	  					alsaaudio.Mixer().setvolume(volume) 		# change volume with alsa

	  				elif(sinkType=="pulse"): 						# if pulse audio is chosen values go from 0 to 1 , in 0.01 steps
	  					if(paready==False):							# check if pulse audio server is running or will panick
	  						stat = os.system('pulseaudio --check')
	  						if(stat == 0):
	  							paready = True
	  							logging.debug('midi2vol -p is ready')
	  						else:
	  							logging.debug('PulseAudio server is not avaible')
	  					else:	 									#if PulseAudio server is ready change volume with pulse
	  						pulseSink(midi_in,applicationRaw,volumeRaw,config)
	  					
			time.sleep(0.01)
	else:
		logging.debug('could not open nano. slider midi interface')


def pulseSink(MidiIn,applicationRaw,volumeRaw,config):
	volume = math.floor((volumeRaw/3)*2.38)/100 
	with pulsectl.Pulse('event-printer') as pulse:
				default = config['default']
				if (hex(applicationRaw)== default['AppRaw']):
					pulseAllSink(volume,pulse)
				else:
					pulseApp(volume,pulse,applicationRaw,config)




def pulseAllSink(volume,pulse):
	for sink in pulse.sink_list():
		pulse.volume_set_all_chans(sink, volume)
	logging.debug('Volume %d set for all sinks'%(volume*100))

def pulseApp(volume,pulse,applicationRaw,config):
	for app in config['Apps']:
		if(app['AppRaw'] == hex(applicationRaw)):
			for source in pulse.sink_input_list():
		   		name = source.name
		   		if (name == app['PulseName']): # if sink input exists
		   			sinkVolume = source.volume
		   			sinkVolume.value_flat = volume
		   			pulse.volume_set(source,sinkVolume)
		   			logging.debug('Volume %d set for application %s'%(volume*100,app['name']))
		   			break
	

def main():
	argv = sys.argv
	if (len(argv)>1):
		count=0
		targetfile = defaultfile
		for arg in argv:	
			if(arg == "-d"):
				logging.basicConfig(filename='midi2vol.log',level=logging.DEBUG)
				logging.debug('----------------------------')
				logging.debug(datetime.now())
				logging.debug('----------------------------')
			if(arg =='-t'):
				targetfile = argv[count+1]
				logging.debug(targetfile)
			count = count+1

		try:
			with open(targetfile) as f:
				try:
					config = json.load(f)
					logging.debug('%s correctly loaded'%(targetfile))
				except:
					os.rename(os.path.realpath(targetfile), os.path.realpath(targetfile)+".bak")
					f = open(os.path.realpath(targetfile), "w")
					logging.debug('Error loading %s,backing up old one, creating new one(check parsing)'%(targetfile))
					f.write("{\"default\": {\"AppRaw\":\"0x3e\"},\"Apps\":[{\"name\": \"None\",\"AppRaw\": \"0x00\",\"PulseName\": \"None\"}]}")
					f.close()
					main()
		except:
			logging.debug('Error loading %s, will create a new one'%(targetfile))
			f= open(targetfile,"w+")
			f.write("{\"default\": {\"AppRaw\":\"0x3e\"},\"Apps\":[{\"name\": \"None\",\"AppRaw\": \"0x00\",\"PulseName\": \"None\"}]}")
			f.close()
			main()

		for arg in argv:
			if(arg== "--pulse" or arg== "-p"):
				try:
					midi_in = rtmidi.MidiIn()
					execution(midi_in,"pulse",config)
				except:
					logging.exception("Error with rtmidi")
					sys.exit("Error, check log")  

			elif(arg== "--alsa" or arg== "-a"):
				try:
					midi_in = rtmidi.MidiIn()
					execution(midi_in,"alsa",config)
				except:
					logging.exception("Error with rtmidi")
					sys.exit("Error, check log")  
		

	else:
		print("Please call me with a valid argument")
		print("Unknown agument, For alsa sink use aguments --alsa/-a or --pulse/-p for pulse sink")
		sys.exit()  
	

if __name__== "__main__":
  	main()



"""
To launch on boot create a file called midi2vol.sh
and edit with(where USER is your user name, And -X is either -a for Alsa or -p for Pulse edit accordingly): 

#!/bin/bash
sleep 5 &&  python3 /home/USER/MidiDev/midi2vol.py -X |&  tee -a /home/USER/MidiDev/midi2vol.log;

Then crontab -e

@reboot bash /home/jesus/MidiDev/midi2vol.sh

And last add your user to the audio group:

sudo usermod -a -G audio USER

PS: I could not make it work as a service, still working on it.

"""
