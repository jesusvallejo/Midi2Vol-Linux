# Midi2Vol-Linux

<img src="https://raw.githubusercontent.com/jesusvallejo/Midi2Vol/master/ReadResources/NanoSlider.png" width="180">  <img src="https://raw.githubusercontent.com/jesusvallejo/Midi2Vol/master/ReadResources/NanoBento.png" width="180"> <img src="https://raw.githubusercontent.com/jesusvallejo/Midi2Vol/master/ReadResources/NanoWavez.png" width="180">

Linux Volume Control for Nano. Slider , ALSA and Pulse compatible -- [Windows](https://github.com/jesusvallejo/Midi2Vol)


This is mainly developed for Nano. Slider, but it can be fairly easily used with any Midi based potentiometer. 
It is written on python3.

This version has per app control when using pulse, it can be configured via the config.json,to add more apps.For it to work on qmk keymap we have to change some things,instancitate an app variable as 0x3E,``` uint8_t app = 0x3E; ``` , on slider function we have to change midi_send_cc to ```midi_send_cc(&midi_device, 2, app, 0x7F - (analogReadPin(SLIDER_PIN) >> 3));``` and last use the macro utility to change ``` app ``` value to what ever is configured in the config.json

ex:
```
uint8_t app = 0x3E;

// Defines the keycodes used by our macros in process_record_user
enum custom_keycodes {
    QMKBEST = SAFE_RANGE,
    SPOTIFY,DISCORD
};
bool process_record_user(uint16_t keycode, keyrecord_t *record) {
    switch (keycode) {
        case SPOTIFY:
            if (record->event.pressed) {
                // when keycode SPOTIFY is pressed
                app= 0x3F;
            } else {
                app= 0x3E;
                // when keycode SPOTIFY is released
            }
            break;
        case DISCORD:
            if (record->event.pressed) {
                // when keycode SPOTIFY is pressed
                app= 0x40;
            } else {
                app= 0x3E;
                // when keycode SPOTIFY is released
            }
            break;
    }
    return true;
}
void slider(void) {
    if (divisor++) { // only run the slider function 1/256 times it's called
        return;
    }

    midi_send_cc(&midi_device, 2, app, 0x7F - (analogReadPin(SLIDER_PIN) >> 3));
}
```


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
- [x] Allow per App control



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
