#!/usr/bin/python
# -*- coding: utf-8 -*-

import wconfig
import wconstants

config = wconfig.read_settings_file(fallback=False)
firstInstall = False
if config is None:
    config = wconfig.reset_settings_file()
    firstInstall = True

section = "General"
dispSize = int(config[section]["Resolution"][0]), int(config["General"]["Resolution"][1])
lang = config[section]["Language"]
disp_units = wconstants.AVAIL_UNITS[config[section]["Units"]]

section = "Texts"
texts = config[section][lang]
lang_code = texts["Code"]
locale = texts["Locale"]

section = "Appearance"
setAsWallpaper = config[section]["Wallpaper"] == "True"
clockMode = config[section]["Clock_mode"] == "True"
showBkg = config[section]["Show_background"] == "True"
bkgMode = config[section]["Background_mode"]
iconSet = wconstants.AVAIL_ICONSET[config[section]["Icon_set"]]
wsource = wconstants.WEATHER_1
moonMode = config[section]["Moon_position"]
newsMode = config[section]["News_mode"]
showSunSigns = config[section]["Show_Constellations"] == "True"

section = "Background"
if showBkg and bkgMode == wconstants.BKG_WEATHER:
    subsection = "With_Background"
else:
    subsection = "Without_Background"
dimBkg = config[section][subsection]["Dim_background"] == "True"
outline = config[section][subsection]["Outline_mode"]
dimFactor = config[section][subsection]["Dim_factor"]
dimForecasts = config[section][subsection]["Dim_forecasts"] == "True"

# Other
dispRatio = float(dispSize[0]) / float(dispSize[1])
timeout = 20
debug = False


section = "Colors"
if showBkg and bkgMode == wconstants.BKG_WEATHER:
    subsection = "With_Background"
else:
    subsection = "Without_Background"
cBkg = config[section]["Color_Background"]
nBkg = config[section]["Color_News_background"]
clockc = config[section][subsection]["Color_Clock"]
clockh = config[section][subsection]["Color_Header"]
nc = config[section][subsection]["Color_News"]
wc = config[section][subsection]["Color_Weather"]
chighlight = config[section]["Color_highlight"]
cdark = config[section]["Color_dark"]
cdim = config[section]["Color_dim"]
crcm = config[section]["Color_Med_pop"]
crcw = config[section]["Color_High_pop"]
chigh = config[section]["Color_High_temp"]
clow = config[section]["Color_Low_temp"]
byc = config[section]["Color_Title"]


section = "Weather"
location = config[section]["Locations"]
use_current_location = config[section]["Use_current"] == "True"

section = "News"
alternSource = config[section]["Alternate_News_source"] == "True"
showPics = config[section]["Show_News_pics"] == "True"
separator = config[section]["Separator"]
fps = config[section]["FPS"]

section = "World_Clocks"
timeZones = config[section]["Timezones"]
