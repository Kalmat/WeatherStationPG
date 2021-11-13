#!/usr/bin/python
# -*- coding: utf-8 -*-

import wkey

### CONSTANTS

# DISPLAY
REF_DISPSIZE = (1280, 800)
REF_X = REF_DISPSIZE[0]
REF_Y = REF_DISPSIZE[1]
REF_DISPRATIO = REF_X / REF_Y
BKG = "BKG"
SEP = "SEP"
HEADER = "HEADER"
MOON = "MOON"
SUNSIGN = "SUNSIGN"
TIME = "TIME"
CC = "CC"
FF_DAILY = "FF_DAILY"
FF_HOURLY = "FF_HOURLY"
NEWS = "NEWS"
ALERT = "ALERT"
ONLY_CLOCK = "CLOCK"

# Units
METRIC = 'metric'
IMPERIAL = 'imperial'
AVAIL_UNITS = {"Metric": METRIC, "Imperial": IMPERIAL}

# Weather sources
WEATHER_1 = 'OpenWeatherMap'

# News
NEWS_1 = 'rtve'
NEWS_2 = 'BBC'
NEWS_PERIOD = 'Period'
NEWS_ALWAYSON = 'Always ON'
NEWS_ALWAYSOFF = 'Always OFF'

# Background Modes
BKG_WEATHER = "Weather"
BKG_FIXED = "Fixed"

# Moon Mode
MOON_NOMOON = 'No Moon'
MOON_ONCURRENT = 'On CurrentT'
MOON_ONHEADER = 'On Header'
MOON_BOTH = 'Both'

# Icon Set
ICONSET_REALISTIC = "A/"
ICONSET_FLATGREY = "B/"
ICONSET_STICKYFULLCOLOR = "C/"
ICONSET_FLATFULLCOLOR = "D/"
AVAIL_ICONSET = {"Realistic": ICONSET_REALISTIC, "Flat Grey": ICONSET_FLATGREY, "Flat Full Color": ICONSET_FLATFULLCOLOR, "Sticky Full Color": ICONSET_STICKYFULLCOLOR}
ICON_SCALE = {ICONSET_REALISTIC: 1.1, ICONSET_FLATGREY: 1.0, ICONSET_STICKYFULLCOLOR: 0.8, ICONSET_FLATFULLCOLOR: 1.0}

# Drawtext highlighting modes
DT_OUTLINE = "Outline"
DT_OUTRECT = "Outrect"
DT_SHADOW = "Shadow"
DT_FADEIN = "FadeIn"
DT_FADEOUT = "FadeOut"

# Folders
RESOURCES_FOLDER = 'resources/'
BKG_FOLDER = 'resources/wbkg/'
ICON_FOLDER = 'resources/icons'
MOON_FOLDER = 'resources/moon/'
MOON_W_FOLDER = ICON_FOLDER + ICONSET_REALISTIC
SUNSIGNS_FOLDER = 'resources/sunsigns/'
FONTS_FOLDER = 'resources/fonts/'
ALERT_ICONFOLDER = 'resources/'

# Other
SETTINGS_FILE = "settings.json"
DEFAULT_SETTINGS_FILE = "resources/defsett.json"
HELP_FILE = "resources/help.json"
ALERT_ICON = "alert"
SYSTEM_CAPTION = "Weather & News by alef"
SYSTEM_CAPTION_CLOCK = "Just a Clock by alef"
SYSTEM_ICON = ICON_FOLDER + ICONSET_FLATFULLCOLOR + "30.png"
SETTINGS_ICON = "resources/settings.ico"
SETTINGS_ICON_LINUX = "resources/settings.xpm"
DEFAULT_ICON = "na"
ICON_EXT = ".png"
BKG_EXT = ".jpg"
NA_BKG = "na"
DEFAULT_BKG = "99"

### FIXED PARAMETERS

# Fonts
# You may choose System installed fonts or Custom fonts (must be placed in resources/fonts folder)
# If System, only name is required. If not available, all installed fonts will be printed. Choose one!
# If Custom, be sure to set full font file name (include bold or condensed fonts files if required)
font = "freesans.ttf"
fontbold = "freesans-bold.ttf"
calfont = "dejavusansmono.ttf"
calfontbold = "dejavusansmono-bold.ttf"
numberfont = "robotocondensed.ttf"
numberfontbold = "robotocondensed-bold.ttf"

# Positions
# WARNING: they all are relative to screen size!
clockYPos = 0.05
CCYPos = 0.155
CCXPos = 0.62
subYPos = 0.63

# Icon Sizes
# Target sizes for a 1280x800 resolution. It will auto-scale to other resolutions
iconSizeC = 230             # Current conditions icon
iconSizeF = 140             # Daily forecasts icons
moonIconSize = 170          # Moon phase icon
sunsignIconSize = 120       # Sun Sign (Constellation) icon
alertIconSize = 40          # Alert icon

# Text Sizes
# WARNING: They all are relative to screen size (Yaxis)!
Th = REF_DISPRATIO/25.1852
byTh = Th*0.5
qTh = byTh*0.5
wdayTh = Th*0.6
monthTh = Th
dayTh = monthTh * 2
yearTh = wdayTh
calTh = Th*0.5
timeTh = Th*7
secTh = timeTh*0.5
cityTh = Th*0.8
statTh = cityTh*0.6
tempTh = Th*3.3
degTh = tempTh/2.25
temptxTh = Th*0.7
condTh = Th/2.7
subtempTh = Th*0.8
subrainTh = Th*1.3
highlightTh = Th*1.1
alertTh = Th*0.5
newsTh = Th             # News font size. Warning: text rendering may fail with larger sizes!

# Weather
# Weather will be updated every 15 minutes, but not when "inside" the periods in which News are being shown
# Be aware you will be banned if you overpass the API query limits (e.g. 1 query per minute  =  14.400 queries per day!)
# Note that other providers may (will) have slight differences in their APIs
NSUB = 4                            # Number of daily forecasts shown (including current day)
min_update_weather = 2             # Minute multiple in which update weather
sec_update_weather = 5              # Second in which update weather
errMax = 8                          # Around 2 hours without a correct weather update (will fall back to world_clocks)
weatherURL = 'https://api.openweathermap.org/data/2.5/onecall?%s&units=%s&lang=%s&exclude=minutely&appid=' + wkey.openweathermap_key
hourly_number = 19                  # Number of hourly forecasts shown
# degree_sign = u'\N{DEGREE SIGN}'    # Unicode for Degree symbol (https://www.ssewconstants.wiswconstants.edu/~tomw/java/unicode.html)
degree_sign = "º"
uviUnits = [110, 110, 110, 111, 111, 111, 112, 112, 113, 113, 113, 114]
RainHigh = 50                       # Rain chance upper threshold
UVIHigh = 8                         # UVI alert (High)
uniTmp = {METRIC: u'\N{DEGREE CELSIUS}',  # Unicode for Celsius Degree symbol
          IMPERIAL: u'\N{DEGREE FAHRENHEIT}'}  # Unicode for Fahrenheit Degree symbol
windSpeed = {METRIC: 'Km/h',
             IMPERIAL: 'mph'}
windScale = {METRIC: 3.6,
             IMPERIAL: 1.0}
baroUnits = {METRIC: ' mb',
             IMPERIAL: ' "Hg'}
baroScale = {METRIC:  1.0,
             IMPERIAL: 29.529980164712 / 1000}
WindHigh = {METRIC: 60,  # High wind alert (Km/h)
            IMPERIAL: 37.5}                   # High wind alert (mph)
tempHigh = {METRIC: 35,  # High temp alert (celsius)
            IMPERIAL: 95}                     # High temo alert (fahrenheit)
tempLow = {METRIC: 4,  # Low temp alert (celsius)
           IMPERIAL: 39.2}                    # Low temp alert (fahrenheit)
distLimit = {METRIC: 100,  # Current - Default locations distance warning (km)
             IMPERIAL: 62}                    # Current - Default locations distance warning (miles)

# News
nTime = 5 * 60                      # Duration in seconds of news ticker
min_update_news = 15                # Minutes multiple in which update news
sec_update_news = 30                # Second in which update new
sec_show_news = 1                   # Second in which show news (the minute right after updating)
newsNumber = 5                      # Number of news to be gathered/shown
nsource1 = NEWS_1                   # News source 1 (or "the only" if alternSource is False)
nURL1 = "http://www.rtve.es/api/noticias.xml?lang=%s&size=" + str(newsNumber)
nsource2 = NEWS_2                   # News source 2
nURL2 = "http://feeds.bbci.co.uk/news/world/rss.xml"

# Clock
radius = 0.11                       # Radius of the clocks when clockMode on, or no weather info available. Relative to Yaxis
currentTZSep = "@"                  # Character to identify and show current TimeZone when in only Clock Mode

# Geolocation
gIPURL = 'http://ip-api.com/json/?lang=%s'     # NO Key required, but not precise (good enough for Time Zone, not for location)
# gURL = 'https://api.ipgeolocation.io/ipgeo?apiKey=%s'  # Or use this instead (more precise, but needs key)
gURL = 'http://nominatim.openstreetmap.org/search?q=%s&format=json&addressdetails=1'  # No key required. Retrieves coordinates from address

# HTTP Connection
# Definitely, requests.get was caching... Maybe "Connection: keep-alive" which seems to be set by default!
headers = {'Cache-Control': 'no-cache, no-store, max-age=0, pre-check=0, post-check=0, must-revalidate, proxy-revalidate',
           'Pragma': 'no-cache',
           'Connection': 'close',
           'Keep-Alive': 'false'}
