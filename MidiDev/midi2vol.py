import sys
import os
import rtmidi
import math
import time
import pulsectl
import alsaaudio
import json
import logging
import getpass
import subprocess
import shutil
from datetime import datetime
#import pystray
#from PIL import Image, ImageDraw

# paths
defaultPath=os.path.dirname(os.path.realpath(__file__)) #  to force the location os.path.expanduser('~/MidiDev/')
eOS_iconPath=os.path.expanduser('~/.local/share/icons/')

# filenames
filename=os.path.splitext(os.path.basename(__file__))[0]
defaultConfigFile='config.json'
defaultLogginFile=filename+'.log'# to force a logging name 'midi2vol.log'
iconCon_img='NanoSlider.png'
iconDis_img='NanoSliderDis.png'

# flags
elementaryOS=False



def eOSNotification(defaultPath,eOS_iconPath,iconCon_img,iconDis_img):
	global elementaryOS
	elementaryOS = True
	if os.path.isfile(os.path.join(eOS_iconPath,iconCon_img)) == False:
		shutil.copyfile(os.path.join(defaultPath,iconCon_img), os.path.join(eOS_iconPath,iconCon_img))
	if os.path.isfile(os.path.join(eOS_iconPath,iconDis_img)) == False:
		shutil.copyfile(os.path.join(defaultPath,iconDis_img), os.path.join(eOS_iconPath,iconDis_img))




# def pulseIconDis(icon_img):
# 	width=12
# 	height=12
# 	image = Image.open(icon_img)
# 	icon = pystray.Icon("midi2vol", image)
# 	return icon

# def runIcon(icon):
# 	icon.run()
# 	icon.visible = True





def sendmessage(status):
	text=''
	iconCon = os.path.join(defaultPath,iconCon_img)
	iconDis = os.path.join(defaultPath,iconDis_img)
	if(status =='connected'):
		text='nano. slider is ready'
		img = iconCon
		if(elementaryOS):
			img= os.path.splitext(iconCon_img)[0]
	elif(status == 'disconnected'):
		text='nano. slider is not present'
		img = iconDis
		if(elementaryOS):
			img= os.path.splitext(iconDis_img)[0]

	subprocess.Popen(["notify-send", "-i", img, filename, text])
	return

def openNano(midi_in):
    count=nanoIsConnected(midi_in) # returns true if port is correctly opened, false if not
    if (count!=-1):
    	midi_in.open_port(count)
    	logging.debug('openNano: opened port successfully')
    	return True
    else:
    	logging.error('openNanoError: could not find nano. slider')
    	return False

def nanoIsConnected(midi_in):                 #if nano is conected returns position in list, if not returns -1
	count = 0
	for port_name in midi_in.get_ports():
		if (port_name.split(":")[0] == "nano. slider"):
		    #logging.debug('nano. slider found')
		    return count
		else:
			count = count + 1
	logging.debug('could not find nano. slider')
	return -1


def execution(midi_in,sinkType,config):
	oldVolumeRaw = -1
	paready = False
	if (openNano(midi_in)): 										# if connected to nano , check if there's a message 
		while (nanoIsConnected(midi_in) != -1):
			reported=False
			midiMessage= midi_in.get_message()
			if (midiMessage): 										# if rtmidi gives None as a message , sleep the thread to avoid overloading cpu
	 	 		message,time_stamp = midiMessage					# rtmidi lib , passes a tuple [midiMessage , timeStamp], we need the message
	 	 		applicationRaw=message[1]					        # gives option to change volume of source ex: Spotify , Chrome, etc.
	  			volumeRaw = message[2] 								# Message is an array in wich the third argument is the value of the potentiometer slider from 0 to 127
	  			if (volumeRaw != oldVolumeRaw): 						# check if slider positon has changed
	  				oldVolumeRaw= volumeRaw 						#update value for next iteration
	  				if(sinkType=="alsa"):							# if alsa is chosen values go from 0 to 100
	  					volume = math.floor((volumeRaw/3)*2.38)
	  					alsaaudio.Mixer().setvolume(volume) 		# change volume with alsa
	  				elif(sinkType=="pulse"):						# if pulse audio is chosen values go from 0 to 1 , in 0.01 steps
	  					if(paready==False):							# check if pulse audio server is running or will panick
	  						stat = os.system('pulseaudio --check')
	  						if(stat == 0):
	  							paready = True
	  							sendmessage('connected')
	  							logging.debug('midi2vol -p is ready')
	  						else:
	  							logging.debug('PulseAudio server is not avaible')
	  					else:
	  						logging.debug('llamada a pulse')	 					#if PulseAudio server is ready change volume with pulse
	  						pulseSink(midi_in,applicationRaw,volumeRaw,config)
			time.sleep(0.01)
	logging.error('executionError: could find nano. slider midi interface')
	sendmessage('disconnected')
	if (midi_in.is_port_open()):
		midi_in.close_port()
	while (nanoIsConnected(midi_in)==-1):
		time.sleep(0.2) # to not overflow the recursion stack
	execution(midi_in,sinkType,config)




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
			if(pulse.sink_input_list()==[]):
				logging.debug('no apps playing audio')
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
		targetfile = os.path.join(defaultPath,defaultConfigFile)
		for arg in argv:
			if(arg == "-e"):
				eOSNotification(defaultPath,eOS_iconPath,iconCon_img,iconDis_img)
			if(arg == "-d"):
				logging.basicConfig(filename=os.path.join(defaultPath,defaultLogginFile),level=logging.DEBUG)
				logging.debug('----------------------------')
				logging.debug(datetime.now())
				logging.debug('----------------------------')
				logging.debug(getpass.getuser())
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
					time.sleep(10)	# SEEMS TO HELP WITH APPS PROBLEM(PULSEAUDIO SEES ALL SINKS, BUT DOESNT SINK INPUTS, RESULTING IN PER APP CONTROL NOT WORKING) 
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

PS: False(I could not make it work as a service, still working on it.)
    After some time i figured out the problem was not running the service as the logged user so:

    Add USER to audio and pulse groups:
    sudo usermod -a -G audio USER (ex: sudo usermod -a -G audio jesus)
    sudo usermod -a -G pulse USER (ex: sudo usermod -a -G pulse jesus)

    Add this file

    sudo nano /etc/systemd/system/midi2vol.service

    fill with:
    --------------------------------     
    [Unit]
	Description=midi2vol service.

	[Service]
	User=USER
	Type=simple
	ExecStart=/usr/bin/python3 /home/USER/MidiDev/midi2vol.py -p

	[Install]
	WantedBy=multi-user.target
    --------------------------------
    EX:   (NOTE IN THE EXAMPLE -d IS ACTIVE, THIS ENABLES LOGGING, REMEMBER CHANGING THE PATH ON THE CODE OR IT WONT HAVE RIGHTS TO DO SO)
    --------------------------------
    [Unit]
	Description=midi2vol service.

	[Service]
	User=jesus
	Type=simple
	ExecStart=/usr/bin/python3 /home/jesus/MidiDev/midi2vol.py -p -d


	[Install]
	WantedBy=multi-user.target
    --------------------------------
	
    sudo systemctl daemon-reload
    sudo systemctl start midi2vol.service 
    sudo systemctl status midi2vol.service (if everything ok continue)
    sudo systemctl enable midi2vol.service (this makes it run each boot)

    If you are on a Ubuntu distro(or based on it ex: elementary os), you can make it easier by System settings/Applications/Startup/+ and add to
    box 'Type in a custom command' and type   /usr/bin/python3 /home/USER/MidiDev/midi2vol.py -p




"""
