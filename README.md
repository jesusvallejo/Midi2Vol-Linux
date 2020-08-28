# Midi2Vol-Linux

<img src="https://raw.githubusercontent.com/jesusvallejo/Midi2Vol/master/ReadResources/NanoSlider.png" width="180">  <img src="https://raw.githubusercontent.com/jesusvallejo/Midi2Vol/master/ReadResources/NanoBento.png" width="180"> <img src="https://raw.githubusercontent.com/jesusvallejo/Midi2Vol/master/ReadResources/NanoWavez.png" width="180">

Linux Volume Control for Nano. Slider , ALSA and Pulse compatible -- [Windows](https://github.com/jesusvallejo/Midi2Vol)


This is mainly developed for Nano. Slider, but it can be fairly easily used with any Midi based potentiometer. 
It is written on python3.

It is provided as is, and it comes with no guarantee.(see [Licence](https://raw.githubusercontent.com/jesusvallejo/Midi2Vol/master/LICENSE))

Nevertheless any change, update or upgrade is welcomed.

This project uses the following libraries:

- pulsectl: https://pypi.org/project/pulsectl/
- pyalsaaudio: https://pypi.org/project/pyalsaaudio/
- python_rtmidi: https://pypi.org/project/python-rtmidi/

TODO
- [x] Add auto launch on boot
- [ ] Proper installer
- [ ] Add Hot-Plug support
- [ ] Test stability
- [ ] Allow control when changing audio output Devices
- [x] Allow control per app(Only on Pulse Audio)



How to install

Install git & python3 & pip3
```
sudo apt install git python3 python3-pip
```
Import repository(on /home/USER directory , where USER is your user name)
```
git clone https://github.com/jesusvallejo/Midi2Vol-Linux/
```
Install requirements
```
cd /home/USER/MidiDev/
pip3 install requirements.txt
```
To launch on boot create a file called midi2vol.sh
and edit with(where USER is your user name, And -X is either -a for Alsa or -p for Pulse edit accordingly):
```
#!/bin/bash
sleep 5 &&  python3 /home/USER/MidiDev/midi2vol.py -X |&  tee -a /home/USER/MidiDev/midi2vol.log;
```
Then ```crontab -e``` and paste this(remember to edit USER with your user name):
```
@reboot bash /home/USER/MidiDev/midi2vol.sh
```
And last add your user to the audio group (remember to edit USER with your user name):
```
sudo usermod -a -G audio USER
```
PS: I could not make it work as a service, still working on it
