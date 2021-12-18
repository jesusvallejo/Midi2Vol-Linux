#!/usr/bin/python3
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
import threading
import subprocess
import shutil
from datetime import datetime
import pystray
from PIL import Image, ImageDraw

# paths
defaultPath=os.path.dirname(os.path.realpath(__file__)) #  to force the location os.path.expanduser('~/MidiDev/')
eOS_iconPath=os.path.expanduser('~/.local/share/icons/')
iconsPath=os.path.join(defaultPath,'icons')

# filenames
filename=os.path.splitext(os.path.basename(__file__))[0]
defaultConfigFile='config.json'
defaultLogginFile=filename+'.log'# to force a logging name 'midi2vol.log'
iconCon_img='NanoSlider.png'
iconDis_img='NanoSliderDis.png'
iconCon_tray='TrayWhiteIconCon.png'
iconDis_tray='TrayWhiteIconDis.png'

# flags
elementaryOS=False
noNotify = False



def eOSNotification(defaultPath,eOS_iconPath,iconCon_img,iconDis_img):
	global elementaryOS
	elementaryOS = True
	if os.path.isfile(os.path.join(eOS_iconPath,iconCon_img)) == False:
		shutil.copyfile(os.path.join(iconsPath,iconCon_img), os.path.join(eOS_iconPath,iconCon_img))
	if os.path.isfile(os.path.join(eOS_iconPath,iconDis_img)) == False:
		shutil.copyfile(os.path.join(iconsPath,iconDis_img), os.path.join(eOS_iconPath,iconDis_img))

def bento():
	global iconCon_img
	global iconDis_img
	iconCon_img = 'NanoBento.png'
	iconDis_img = 'NanoBentoDis.png'
	if elementaryOS == True:
		eOSNotification(iconsPath,eOS_iconPath,iconCon_img,iconDis_img)
	return

def wavez():
	global iconCon_img
	global iconDis_img
	iconCon_img = 'NanoWavez.png'
	iconDis_img = 'NanoWavezDis.png'
	if elementaryOS == True:
		eOSNotification(iconsPath,eOS_iconPath,iconCon_img,iconDis_img)
	return


def mizu():
	global iconCon_img
	global iconDis_img
	iconCon_img = 'NanoMizu.png'
	iconDis_img = 'NanoMizuDis.png'
	if elementaryOS == True:
		eOSNotification(iconsPath,eOS_iconPath,iconCon_img,iconDis_img)
	return


def trayIcon(icon_img):
	global icon
	image=Image.open(icon_img)
	icon=pystray.Icon(filename, image)
	return icon




def sendmessage(status):
	if(noNotify):
		return

	global iconCon,iconDis,iconConTray,iconDisTray
	iconCon = os.path.join(iconsPath,iconCon_img)
	iconDis = os.path.join(iconsPath,iconDis_img)
	iconConTray = os.path.join(iconsPath,iconCon_tray)
	iconDisTray = os.path.join(iconsPath,iconDis_tray)
	if(status =='connected'):
		image=Image.open(iconConTray)
		icon.icon = image
		text='nano. slider is ready'
		img = iconCon
		if(elementaryOS):
			img= os.path.splitext(iconCon_img)[0]
	elif(status == 'disconnected'):
		image=Image.open(iconDisTray)
		icon.icon = image
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
    	logging.warning('openNano: opened port successfully')
    	return True
    else:
    	logging.error('openNanoError: could not find nano. slider')
    	return False

def nanoIsConnected(midi_in):                 #if nano is connected returns position in list, if not returns -1
	count = 0
	for port_name in midi_in.get_ports():
		if (port_name.split(":")[0] == "nano. slider"):
		    #logging.warning('nano. slider found')
		    return count
		else:
			count = count + 1
	logging.warning('could not find nano. slider')
	return -1


def execution(midi_in,sinkType,config):
	global iconCon,iconDis
	iconCon = os.path.join(iconsPath,iconCon_img)
	iconDis = os.path.join(iconsPath,iconDis_img)
	oldVolumeRaw = -1
	paready = False
	if (openNano(midi_in)): 										# if connected to nano , check if there's a message 
		while (nanoIsConnected(midi_in) != -1):
			global reported
			reported=False
			midiMessage= midi_in.get_message()
			if (midiMessage): 										# if rtmidi gives None as a message , sleep the thread to avoid overloading cpu
	 	 		message = midiMessage[0]					# rtmidi lib , passes a tuple [midiMessage , timeStamp], we need the message
	 	 		applicationRaw=message[1]					        # gives option to change volume of source ex: Spotify , Chrome, etc.
	  			volumeRaw = message[2] 								# Message is an array in wich the third argument is the value of the potentiometer slider from 0 to 127
	  			if (volumeRaw > oldVolumeRaw+1 or volumeRaw < oldVolumeRaw-1): 						# check if slider positon has changed
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
	  							logging.warning('midi2vol -p is ready')
	  						else:
	  							logging.warning('PulseAudio server is not avaible')
	  					else:
	  						logging.warning('llamada a pulse')	 					#if PulseAudio server is ready change volume with pulse
	  						pulseSink(midi_in,applicationRaw,volumeRaw,config)
			time.sleep(0.005)
	logging.error('executionError: could find nano. slider midi interface')
	sendmessage('disconnected')
	if (midi_in.is_port_open()):
		midi_in.close_port()
	while (nanoIsConnected(midi_in)==-1):
		time.sleep(0.5) # to not overflow the recursion stack
	execution(midi_in,sinkType,config)




def pulseSink(MidiIn,applicationRaw,volumeRaw,config):
	volume = math.floor((volumeRaw/3)*2.38)/100 
	with pulsectl.Pulse('event-printer') as pulse:
				default = config['default']
				if (hex(applicationRaw)== default['AppRaw']):
					pulseAllSink(volume,pulse)
				else:
					logging.warning('App Volume selected:%s'%(hex(applicationRaw)))
					pulseApp(volume,pulse,applicationRaw,config)

def pulseAllSink(volume,pulse):
	for sink in pulse.sink_list():
		pulse.volume_set_all_chans(sink, volume)
	logging.warning('Volume %d set for all sinks'%(volume*100))

def pulseApp(volume,pulse,applicationRaw,config):
	for app in config['Apps']:
		if(app['AppRaw'] == hex(applicationRaw)):
			if(pulse.sink_input_list()==[]):
				logging.warning('no apps playing audio')
			for source in pulse.sink_input_list():
		   		name = source.name
		   		if (name == app['PulseName']): # if sink input exists
		   			sinkVolume = source.volume
		   			sinkVolume.value_flat = volume
		   			pulse.volume_set(source,sinkVolume)
		   			logging.warning('Volume %d set for application %s: %s'%(volume*100,app['name'],hex(applicationRaw)))
		   			break

def main():
	argv = sys.argv
	if (len(argv)>1):
		count=0
		targetfile = os.path.join(defaultPath,defaultConfigFile)
		for arg in argv:
			if(arg == '--noicon'):
				global noNotify
				noNotify= True
			if(arg == '--bento'):
				bento()
			if(arg == '--wavez'):
				wavez()
			if(arg == '--mizu'):
				mizu()
			if(arg == "-e"):
				eOSNotification(defaultPath,eOS_iconPath,iconCon_img,iconDis_img)
			if(arg == "-d"):
				logging.basicConfig(filename=os.path.join(defaultPath,defaultLogginFile),level=logging.WARNING)
				logging.warning('----------------------------')
				logging.warning(datetime.now())
				logging.warning('----------------------------')
				logging.warning(getpass.getuser())
				logging.warning('----------------------------')
			if(arg =='-t'):
				targetfile = argv[count+1]
				logging.warning(targetfile)
			count = count+1

		try:
			with open(targetfile) as f:
				try:
					config = json.load(f)
					logging.warning('%s correctly loaded'%(targetfile))
				except:
					os.rename(os.path.realpath(targetfile), os.path.realpath(targetfile)+".bak")
					f = open(os.path.realpath(targetfile), "w")
					logging.warning('Error loading %s,backing up old one, creating new one(check parsing)'%(targetfile))
					f.write("{\"default\": {\"AppRaw\":\"0x3e\"},\"Apps\":[{\"name\": \"None\",\"AppRaw\": \"0x00\",\"PulseName\": \"None\"}]}")
					f.close()
					main()
		except:
			logging.warning('Error loading %s, will create a new one'%(targetfile))
			f= open(targetfile,"w+")
			f.write("{\"default\": {\"AppRaw\":\"0x3e\"},\"Apps\":[{\"name\": \"None\",\"AppRaw\": \"0x00\",\"PulseName\": \"None\"}]}")
			f.close()
			main()

		for arg in argv:
			if(arg== "--pulse" or arg== "-p"):
				try:
					global icon
					icon = trayIcon(os.path.join(iconsPath,iconCon_tray))
					time.sleep(3)	# SEEMS TO HELP WITH APPS PROBLEM(PULSEAUDIO SEES ALL SINKS, BUT DOESNT SINK INPUTS, RESULTING IN PER APP CONTROL NOT WORKING) 
					midi_in = rtmidi.MidiIn()
					t=threading.Thread(name = 'midiExecution',target = execution,args =(midi_in,"pulse",config))
					t.start()
					icon.run()
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
   
