# Midi2Vol-Linux

<img src="https://raw.githubusercontent.com/jesusvallejo/Midi2Vol-Linux/master/icons/NanoSlider.png" width="180">  <img src="https://raw.githubusercontent.com/jesusvallejo/Midi2Vol-Linux/master/icons/NanoBento.png" width="180"> <img src="https://raw.githubusercontent.com/jesusvallejo/Midi2Vol-Linux/master/icons/NanoWavez.png" width="180"> <img src="https://raw.githubusercontent.com/jesusvallejo/Midi2Vol-Linux/master/icons/NanoMizu.png" width="180">


Linux Volume Control for Nano. Slider , ALSA and Pulse compatible -- [Windows](https://github.com/jesusvallejo/Midi2Vol)


This is mainly developed for Nano. Slider, but it can be fairly easily used with any Midi based potentiometer. 
It is written in python3.

Options:

Command       | Info
:------------ | :----------------------------------------------------------
-p  	      | Pulse
-a            | Alsa
-d            | Debug mode(produces a .log)
-t            | Set .json file
-e            | Elementary OS mode(Icons work different on Elementary OS)
--bento       | NanoBento Notification Icon
--wavez       | NanoWavez Notification Icon
--mizu        | NanoMizu Notification Icon


This version has per app control when using pulse, it can be configured via the config.json,to add more apps.In order to make it work we have to change some things on the qmk keymap,instancitate an app variable as 0x3E,``` uint8_t app = 0x3E; ``` , on slider function we have to change midi_send_cc to ```midi_send_cc(&midi_device, 2, app, 0x7F - (analogReadPin(SLIDER_PIN) >> 3));``` and last use the macro utility to change ``` app ``` value to what ever is configured in the config.json

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
- [x] Add Hot-Plug support
- [x] Test stability
- [x] Allow control when changing audio output Devices(on Pulse only)
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
PS: ~~I could not make it work as a service, still working on it~~

After some time i figured out the problem was not running the service as the logged user so:
Add USER to audio and pulse groups:
```
sudo usermod -a -G audio USER
```
```
sudo usermod -a -G pulse USER 
```
Example:
```
sudo usermod -a -G audio jesus
```
```
sudo usermod -a -G pulse jesus
```
Add this file:
```
sudo nano /etc/systemd/system/midi2vol.service
```
Fill with:
```
    	[Unit]
	Description=midi2vol service.

	[Service]
	User=USER
	Type=simple
	ExecStart=/usr/bin/python3 /home/USER/MidiDev/midi2vol.py -p

	[Install]
	WantedBy=multi-user.target
```
EX:   (NOTE IN THE EXAMPLE -d IS ACTIVE, THIS ENABLES LOGGING, REMEMBER CHANGING THE PATH ON THE CODE OR IT WONT HAVE RIGHTS TO DO SO)
```
    	[Unit]
	Description=midi2vol service.

	[Service]
	User=jesus
	Type=simple
	ExecStart=/usr/bin/python3 /home/jesus/MidiDev/midi2vol.py -p -d
    
	[Install]
	WantedBy=multi-user.target
```
Reload and start
```
sudo systemctl daemon-reload
```
```
 sudo systemctl start midi2vol.service 
```
```
sudo systemctl status midi2vol.service (if everything ok continue)
```
```
sudo systemctl enable midi2vol.service (this makes it run each boot)
```
If you are on a Ubuntu distro(or based on it ex: elementary os), you can make it easier by System settings/Applications/Startup/+ and type in
box 'Type in a custom command':
```
/usr/bin/python3 /home/USER/MidiDev/midi2vol.py -p
```



Some Q/A regarding code:

Why is there two time.sleep()?
- Well , first one time.sleep(10) helps to let (what i think) pulse audio completely init and avoid not having per app volume control,
to this moment i still dont know why this happens but 10 seconds at start up not having volume control with the nano. slider seems a good trade for 
having per app volume control(will implement a flag so its only when per app control is wanted), and the second one is to avoid wasting cpu when 
theres no actual change on the nano slider potentiometer.

Can i make my own .json?
- Yes of course you can as long as it parses and follows the default one,pretty easy to add/delete apps. Remember that your keymap has to send the 
correct hex to work. Also if you loose it the file will be auto generated, and in case it does not work it will make a .bak before creating a new working one.

Does alsa work as pulse?
- Yes and no, alsa only has default device control, and pulse has all sink control and per app control, which means even if you change the output device will work, it wont with alsa.


