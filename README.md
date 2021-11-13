## What is this for

This is a python 3 script, based on pygame, intended to show:

- Time, as a digital clock
- Date, as day of month, day of week and month
- Weather from OpenWeatherMap, including current and forecasts (18 hours and 3 days in advance)
- News from RTVE and BBC (alternatively), and News pics (RTVE only)
- Moon phase
- Sun position Constellation
- World Clocks if no Internet connection or no weather info gathered or obsolete

The recommended configuration is a dedicated Raspberry Pi (working fine on a RPi 1) connected to a 10-inches IPS LED screen (or larger). Looks awesome in any sitting room!!!

The weather station should look like this when all graphic resources are downloaded and options activated (see Configuration section):

![](/resources/Capture-1.JPG)

Same full configuration, but showing News ticker:

![](/resources/Capture-4.JPG)

It should look like this with background, moon and sunsigns options disabled, using a different icon set:

![](/resources/Capture-2.JPG)

And finally, it should look like this with no Internet connection, or "Only Clock" option enabled, and using "fixed" background option:

![](/resources/Capture-3.JPG)

---

## Installation

##### For Raspberry Pi (otherwise, only steps 3 to 7 apply)

1. Make a fresh new install of Raspbian on your RPi (well, not strictly necessary)
2. Access your RPi (directly or remotely using ssh, VNC or any other method of your choice)
3. Check if python is installed : "python -V" or "python3 -V". If not, install it as per <https://www.python.org/downloads> (likely pre-installed on RPi)
4. Install pip to get all other required modules: "sudo apt install python3-pip" (or, for other non-Linux OSs, download and run get-pip.py)
5. Download the Weather & News archive, extract it and place it wherever you want to (e.g. /home/pi/Weather)
6. Install the required modules: "pip3 install module-name" or "python3 -m pip install module-name". The modules you will most likely need to install are: pytz, pygame-menu and pygame (this last one should be already pre-installed on RPi)
7. OpenWeatherMap API key is required (No-Key API days are gone!). Get your own at openweathermap.com, and modify wkey.py script inserting your key in there (openweathermap_key = "YOUR_KEY_HERE"). Should you want other sources, you will have to adapt/struggle with APIs (check pywapi and newsapi to ease integration)

### WARNING
This script uses several graphic resources from third parties. Though they all are free for non-commercial purposes (which is my case), I am not including them to avoid any legal issue or missunderstanding. You can download your own and place them into the resources/ folder, directly or in these other sub-folders, and renaming them with these exact names (or the script will fail):
- [REQUIRED] alert.png: Icon to show when there is a weather alert
- [REQUIRED] settings.ico: Icon for settings application
- [REQUIRED] weather.ico: Icon for Weather & News application
- [REQUIRED] fonts (folder): PROVIDED (no need to download them, I included them under GNU license)
- [REQUIRED] iconsA (folder): Icons for weather conditions. Be sure to rename the icons according to weather.com API codes
- [OPTIONAL] iconsB / iconsC / iconsD / iconsE (folders): you can download other icon sets to change appearance at your will. Be sure to rename them properly as well
- [OPTIONAL if background option is disabled] wbkg (folder): you can download wallpapers to be shown for each specific weather condition. Rename them in the same way than the icons explained above. Remember to add a "99.jpg" wallpaper for "fixed background" option. You can then activate the option to show weather background and choose "weather" or "fixed" style (they will be automatically resized, don't worry)
- [OPTIONAL if Moon option is set to NO MOON] moon (folder): Will show the moon phases. Be sure to rename them as per the included .txt file. Then you can activate the option to show Moon Phases on the screen (they will be automatically resized, don't worry)
- [OPTIONAL if constellations option is disabled] sunsigns (folder): Will show the current constellation. Be sure to rename them as per the included .txt file. Then you can activate the option to show Constellations on the screen (they will be automatically resized, don't worry)

## IMPORTANT: Check "Special Thanks and Mentions" section for more resources information and download suggestions

---

## Configuration

##### You can change many things by running settings (wconfig.py)!!!
Take your time to understand the settings and very likely you will not need to program anything!

You can access Settings in four ways:

- It will automatically show up when you run the application for the first time
- From outside the script: Running wconfig as stand-alone application
- While the script is running: Press 'm' key or click and hold right mouse button to access Quick Options menu
- (Strongly NOT recommended) manually changing settings.json 

You may want to look for and play around with:

- Resolution: (XXXX, YYYY) - set the window size (in pixels). If this size matches the screen resolution, it will turn Full Screen
- Language: SPANISH / ENGLISH
- Units: METRIC / IMPERIAL
- Show Background: True / False - will force showing a background image or a solid color
- Background Mode: FIXED / WEATHER - Will show a fixed image (99.jpg) or a changing image according to weather conditions (0-47.jpg)
- Clock Mode: True / False - will force to always show world clocks (no Internet connection required, so weather will not be shown), or weather info
- Moon Position: ONCURRENT - instead of Current weather icon (at night time only) / None - no moon phase icon
- Show Constellation: True / False - Will display Sun position Constellation
- Show News pics: True / False - Will show News pics (hiding weather info while showing news. UPDATE: BBC not providing pics any more)
- Time Zones: The Time Zones and cities you would like to show on World Clocks (when no connection or no weather info available)

You can also change other behaviors, colors, positions and sizes to adapt it to your needs ... and many other things! 

Available languages are Spanish and English. If you want other languages, modify the content of settings.json (TODO: localise using gettext instead)
- Translate all strings in the "Texts" section of the language you want to replace (recommended you replace the "Alternative" entry)
- Then, define proper code (as per OpenWeatherMap API definitions) and locale entries on that same section
- Finally, set your desired values on section "General": "Available_Languages" and "Language" (this will be the language the script will use)

---

## Run it

To run the script:

0. Connect to your RPi (if applies)
1. Open a terminal
2. "cd" to the folder you unzipped/copied the script (e.g. /home/pi/Weather)
3. Run this

```
    python3 wthrnews.py
```

---

## Use it

While running, you can:

- Press 'm' or click & hold right mouse button to access Quick Options Menu
- Press '1', '2' or '3' to change Weather location
- Press 'c' to show World Clocks (no Internet connection required)
- Press 'w' or '1', '2' or '3' to go back to weather info
- Press 'a' or 'b' to select News source and force updating and showing News immediately (will alternate between sources)
- Press 'h' to show Help screen (also available if you add '-h' argument from command line)
- Press 'q' or 'Escape' to exit the program

---

## RPi OPTIONAL (but recommended) INSTALLATION STEPS

#### [OPTIONAL] If your time doesn't automatically update:

- Connect to your RPi and, on a terminal, run:

```
        sudo raspi-config
```

- Look for and run the 4th option called "Internationalisation Options" and set your timezone.
- With the timezone set and ntpd (network time protocol daemon) running the Pi will always display the correct time within a couple of milliseconds!

#### [OPTIONAL]: If you want wthrnews.py to be run when RPi boots:

- Connect to your RPi and open a terminal
- Install xterm:

```
        sudo apt install xterm
```

- Add this at the bottom of /home/pi/.config/lxsession/LXDE-pi/autostart:

```    
        @sh -c /home/pi/Desktop/StartPi.sh
```

- Create a file named StartPi.sh, and copy/paste this (be aware the path):

```	
        #!/bin/sh
        sleep 60
        xterm -hold -fn fixed -e "cd /home/pi/Weather/; python3 wthrnews.py; bash" &
```

- Place that file on /home/pi/Desktop/

- Give it execution permissions, by running:
	
```	
        chmod +x /home/pi/Desktop/StartPi.sh
```

#### [OPTIONAL]: If you intend to have it continuously running and want to periodically reboot it (e.g. for updates). Do this:

- Connect to your RPi and, on a terminal, run:

```
        crontab -e
```

- Add this line at the very bottom of the file (it will reboot your RPi every day at 4:56 AM every first day of the month)

```
        56 4 1 * * sudo reboot
```

- Save (^O) and Exit (^X)


#### [OPTIONAL] If you find troubles with your locales (will only affect to weather API language):

- Connect to your RPi and, on a terminal, run:

```
        sudo dpkg-reconfigure locales
```

   ... and select your own


#### [OPTIONAL] If you are using a screen with a non-supported resolution on Raspberry Pi (blank or not full screen)

- Connect to your RPi and, on a terminal, run:

```
        sudo nano /boot/config.txt
```

- add this line

```
        hdmi_cvt=XXXX YYY FF M 0 0 0

```
XXXX and YYYY is your display/desired resolution in pixels (e.g. 1280 800), FF is your display frequency (e.g. 60), and M is the aspect ratio code (e.g. 3 for 16:9). Maybe you have to google around to find proper parameters for your display resolution and characteristics.

- then find, uncomment and modify these other lines

```
        hdmi_group=2
        hdmi_mode=87
```


## SPECIAL THANKS AND MENTIONS
This could never be done without the work and the will to share of these guys. Thank you so much!!!

- WEATHER: Jim Kemp <https://www.instructables.com/id/Raspberry-Pi-Internet-Weather-Station/> (Inspired me to learn Python and code this script)
- ICONS: VClouds <http://vclouds.deviantart.com/>
- BACKGROUNDS: I was not able to find a complete free pack, so I had to search and download them separatedly (I think the packs from DrToxic, DarkScout, Nuka1195 and Timdog82001 are not available any more)
- MOON: toby_goodlock <http://watchmaker.haz.wiki/sprites>
- CONSTELLATIONS: In-Finity <https://www.vectorstock.com/royalty-free-vector/zodiac-constellations-set-space-and-stars-vector-17402471>  
- NEWS APIs:
    - Spain's RTVE: Ulises Gascon <https://github.com/UlisesGascon/RTVE-API>
    - Other NEWS: SlapBOT News API <https://github.com/SlapBot/newsapi>
- NEWS TICKER (ScrollText): Gunny26 <https://github.com/gunny26/pygame/blob/master/ScrollText.py>
- WRAP TEXT: ColdrickSotK <https://github.com/ColdrickSotK/yamlui/blob/master/yamlui/util.py#L82-L143>
- SCREEN DIMMER: Thobias Thelen <http://www.pygame.org/pcr/screen_dimmer/index.php>
- TFT SCREENS: wborelli <https://www.instructables.com/id/Raspberry-Pi-Internet-Weather-Station/>

---

## TFT GPIO Touchscreen Support (by wborelli)

#### WARNING: NOT TESTED

- At InitDisplay() function within disputil.py module:


```
    print 'Driver Used:', driver
    devices = map(InputDevice, list_devices())
    eventX=""
    for dev in devices:
        if dev.name == "ADS7846 Touchscreen":
                eventX = dev.self.fn
    print eventX
    """
    os.environ["SDL_FBDEV"] = "/dev/fb1"
    os.environ["SDL_MOUSEDRV"] = "TSLIB"
    os.environ["SDL_MOUSEDEV"] = eventX
    pygame.init()
    screen = pygame.display.set_mode((480, 320), 0, 32)
    """
```
