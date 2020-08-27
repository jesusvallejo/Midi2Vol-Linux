import sys
import os
import rtmidi
import math
import time
import pulsectl
import alsaaudio

def openNano(midi_in):
	count = 0
	for port_name in midi_in.get_ports():
		if (port_name.split(":")[0] == "nano. slider"): 		   #try to connect to nano. slider 
			midi_in.open_port(count)
			return True
		else:
			count = count + 1
	return False

def execution(midi_in,sinkType):
	oldVolumeRaw = -1
	paready = False
	if (openNano(midi_in)): 										# if connected to nano , check if there's a message 
		while True:
			midiMessage= midi_in.get_message()
			if midiMessage: 										# if rtmidi gives None as a message , sleep the thread to avoid overloading cpu
	 	 		message,time_stamp = midiMessage 					# rtmidi lib , passes a tuple [midiMessage , timeStamp], we need the message
	  			volumeRaw = message[2] 								# Message is an array in wich the third argument is the value of the potentiometer slider from 0 to 127
	  			if volumeRaw != oldVolumeRaw: 						# check if slider positon has changed
	  				oldVolumeRaw= volumeRaw 						#update value for next iteration


	  				if(sinkType=="alsa"): 							# if alsa is chosen values go from 0 to 100
	  					volume = math.floor((volumeRaw/3)*2.38)
	  					alsaaudio.Mixer().setvolume(volume) 		# change volume with alsa


	  				elif(sinkType=="pulse"): 						# if pulse audio is chosen values go from 0 to 1 , in 0.01 steps

	  					if(paready==False):							# check if pulse audio server is running or will panick
	  						stat = os.system('pulseaudio --check')
	  						if(stat == 0):
	  							paready = True
	  						else:
	  							print('Pulse audio not ready')
	  					else: 										#if server is ready change volume with pulse
	  						volume = math.floor((volumeRaw/3)*2.38)/100 
	  						with pulsectl.Pulse('event-printer') as pulse:
	  							for sink in pulse.sink_list():
	  								pulse.volume_set_all_chans(sink, volume)
			time.sleep(0.01)
	else:
		print('could not open nano. slider midi interface')


def main():
	argv = sys.argv
	if (len(argv)>1):
		if(argv[1]== "--pulse" or argv[1]== "-p"):
			midi_in = rtmidi.MidiIn()
			execution(midi_in,"pulse")
		elif(argv[1]== "--alsa" or argv[1]== "-a"):
			midi_in = rtmidi.MidiIn()
			execution(midi_in,"alsa")				
	else:
		print("Please call me with a valid argument")
		print("Unknown agument, For alsa sink use aguments --alsa/-a or --pulse/-p for pulse sink")
	

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