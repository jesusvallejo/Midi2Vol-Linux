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
defaultAppConfigFile='appConfig.json'
defaultConfigFile='config.json'
defaultLogginFile=filename+'.log'# to force a logging name 'midi2vol.log'
iconCon_img='NanoSlider.png'
iconDis_img='NanoSliderDis.png'
iconCon_tray='TrayWhiteIconCon.png'
iconDis_tray='TrayWhiteIconDis.png'

# Default json
appConfigJson = """ [
    {"name": "Default","AppRaw": "0x3e","PulseName": "default"},
    {"name": "Spotify","AppRaw": "0x3f","PulseName": "Spotify"},
    {"name": "Discord","AppRaw": "0x40","PulseName": "playStream"},
    {"name": "Google Chrome","AppRaw": "0x41","PulseName": "Playback"},
    {"name": "Firefox","AppRaw": "0x41","PulseName": "AudioStream"}
]"""
configJson = """  {
    "NotifyStatus": "true",
    "trayBarIcon": "default",
    "audioService":"pulse"
  } """
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


def execution(midi_in,sinkType,appConfig):
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
	 	 		message = midiMessage[0]							# rtmidi lib , passes a tuple [midiMessage , timeStamp], we need the message
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
	  						logging.warning('llamada a pulse')	 	# If PulseAudio server is ready change volume with pulse
	  						pulseSink(midi_in,applicationRaw,volumeRaw,appConfig)
         
			time.sleep(0.01)  										# Sleep thread for a while
   
	logging.error('executionError: could find nano. slider midi interface')
	sendmessage('disconnected')
 
	if (midi_in.is_port_open()):									# Close midi port
		midi_in.close_port()
	while (nanoIsConnected(midi_in)==-1):							# Actively poll to detect nano slider reconnection
		time.sleep(0.5) 											# To not overflow the recursion stack
	execution(midi_in,sinkType,appConfig)								# Nano is now present launch thread


def pulseSink(MidiIn,applicationRaw,volumeRaw,appConfig):   			# Checks midi hex against the json
	volume = math.floor((volumeRaw/3)*2.38)/100 
	with pulsectl.Pulse('event-printer') as pulse:
				default = appConfig[0]
				if (hex(applicationRaw)== default['AppRaw']):
					pulseAllSink(volume,pulse)
				else:
					logging.warning('App Volume selected:%s'%(hex(applicationRaw)))
					pulseApp(volume,pulse,applicationRaw,appConfig)


def pulseAllSink(volume,pulse):											# Changes all output sinks volume
	for sink in pulse.sink_list():
		pulse.volume_set_all_chans(sink, volume)
	logging.warning('Volume %d set for all sinks'%(volume*100))


def pulseApp(volume,pulse,applicationRaw,appConfig):						# Controls per app volume using pulse
	for app in appConfig:
		if(app['AppRaw'] == hex(applicationRaw)):
			if(pulse.sink_input_list()==[]):
				logging.warning('no apps playing audio')
			for source in pulse.sink_input_list():
		   		name = source.name
		   		if (name == app['PulseName']): 							# if sink input exists
		   			sinkVolume = source.volume
		   			sinkVolume.value_flat = volume
		   			pulse.volume_set(source,sinkVolume)
		   			logging.warning('Volume %d set for application %s: %s'%(volume*100,app['name'],hex(applicationRaw)))
		   			break
    
    
def loadAppConfig(targetfile):
	try:
		with open(targetfile) as f:
			try:
				global	appConfig
				appConfig = json.load(f)
				logging.warning('%s correctly loaded'%(targetfile))
			except:
				os.rename(os.path.realpath(targetfile), os.path.realpath(targetfile)+".bak")
				f = open(os.path.realpath(targetfile), "w")
				logging.warning('Error loading %s,backing up old one, creating new one(check parsing)'%(targetfile))
				f.write(appConfigJson)
				f.close()
				main()
	except:
		logging.warning('Error loading %s, will create a new one'%(targetfile))
		f= open(targetfile,"w+")
		f.write(appConfigJson)
		f.close()
		main()
  
  
def loadConfig(targetfile):
	try:
		with open(targetfile) as f:
			try:
				global	config
				config = json.load(f)
				logging.warning('%s correctly loaded'%(targetfile))
			except:
				os.rename(os.path.realpath(targetfile), os.path.realpath(targetfile)+".bak")
				f = open(os.path.realpath(targetfile), "w")
				logging.warning('Error loading %s,backing up old one, creating new one(check parsing)'%(targetfile))
				f.write(configJson)
				f.close()
				main()
	except:
		logging.warning('Error loading %s, will create a new one'%(targetfile))
		f= open(targetfile,"w+")
		f.write(configJson)
		f.close()
		main()

def main():
	global appConfig , config
	argv = sys.argv
	if (len(argv)>1): 													# console mode
		count=0
		targetfile = os.path.join(defaultPath,defaultAppConfigFile)
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

		loadAppConfig(targetfile)

		for arg in argv:
			if(arg== "--pulse" or arg== "-p"):
				try:
					global icon
					icon = trayIcon(os.path.join(iconsPath,iconCon_tray))
					time.sleep(3)	# SEEMS TO HELP WITH APPS PROBLEM(PULSEAUDIO SEES ALL SINKS, BUT DOESNT SINK INPUTS, RESULTING IN PER APP CONTROL NOT WORKING) 
					midi_in = rtmidi.MidiIn()
					t=threading.Thread(name = 'midiExecution',target = execution,args =(midi_in,"pulse",appConfig))
					t.start()
					icon.run()
				except:
					logging.exception("Error with rtmidi")
					sys.exit("Error, check log")  

			elif(arg== "--alsa" or arg== "-a"):
				try:
					midi_in = rtmidi.MidiIn()
					execution(midi_in,"alsa",appConfig)
				except:
					logging.exception("Error with rtmidi")
					sys.exit("Error, check log") 
			else:
				print("Please call me with a valid argument")
				print("Unknown argument, For alsa sink use arguments --alsa/-a or --pulse/-p for pulse sink")
				sys.exit() 
		
	else:
		targetfile = os.path.join(defaultPath,defaultAppConfigFile)# AppConfig file
		loadAppConfig(targetfile)
		targetfile = os.path.join(defaultPath,defaultConfigFile)# AppConfig file
		loadConfig(targetfile)
		if(config["audioService"]=="pulse"):
			try:
					#global icon
					icon = trayIcon(os.path.join(iconsPath,iconCon_tray))
					time.sleep(3)	# SEEMS TO HELP WITH APPS PROBLEM(PULSEAUDIO SEES ALL SINKS, BUT DOESNT SINK INPUTS, RESULTING IN PER APP CONTROL NOT WORKING) 
					midi_in = rtmidi.MidiIn()
					t=threading.Thread(name = 'midiExecution',target = execution,args =(midi_in,"pulse",appConfig))
					t.start()
					icon.run()
			except:
					logging.exception("Error with rtmidi")
					sys.exit("Error, check log")  
		elif(config["audioService"]=="alsa"):
				try:
						midi_in = rtmidi.MidiIn()
						execution(midi_in,"alsa",appConfig)
				except:
						logging.exception("Error with rtmidi")
						sys.exit("Error, check log")
		else:
				print("Invalid audioService , check config.json")
				sys.exit()
	
 
	

if __name__== "__main__":
  	main()
   
