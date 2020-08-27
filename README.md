# Midi2Vol-Linux

<img src="https://raw.githubusercontent.com/jesusvallejo/Midi2Vol/master/ReadResources/NanoSlider.png" width="180">  <img src="https://raw.githubusercontent.com/jesusvallejo/Midi2Vol/master/ReadResources/NanoBento.png" width="180"> <img src="https://raw.githubusercontent.com/jesusvallejo/Midi2Vol/master/ReadResources/NanoWavez.png" width="180">

Linux Volume Control for Nano. Slider , ALSA and Pulse compatible


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
