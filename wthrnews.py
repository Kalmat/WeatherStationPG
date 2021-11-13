#!/usr/bin/python
# -*- coding: utf-8 -*-

import importlib
import sys
import threading
import pygame
import pygame_menu
from typing import Tuple, Any
import time
import locale
import urllib.request
import json
import xml.etree.ElementTree as ET
import traceback
import settings
import wconstants
import wconfig
import pgutils
import wutils
import utils
import zoneinfo

# WORK PENDING: use gettext instead of current translation method (not referred to locale)
# import gettext
# es = gettext.translation('wthrnews', localedir='locale', languages=['es'])
# print(_('Hello! What is your name?'))  # prints Spanish

# _ = lambda s: s


class MyWeatherStation:
    screen = None

    def __init__(self, pos=(None, None)):
        if settings.debug: print("INIT", time.strftime("%H:%M:%S"))

        # Change size on settings to try other resolutions (tested 16:9, 16:10, 4:3 and 15.4:9)
        # If size is None or matches/exceeds monitor resolution, it will turn into fullscreen and mouse will be hidden
        self.screen, self.xmax, self.ymax, self.fullscreen, \
        self.screen_x, self.screen_y, self.border_width, self.titlebar_height, \
        self.interpreter, self.archOS = pgutils.init_display(size=settings.dispSize,
                                                             pos=pos,
                                                             icon=wconstants.SYSTEM_ICON,
                                                             caption=wconstants.SYSTEM_CAPTION)
        self.xmin = self.ymin = 0
        self.xmargin = self.xmax * 0.01
        self.ymargin = self.ymax * 0.01
        self.xgap = self.xmargin * 3
        self.ygap = self.ymargin * 3

        # Set system locale according to the language selected on settings. If not possible, it will fallback to default
        # Use 'sudo dpkg-reconfigure locales' to install/set locales (or system preferences on non-Linux OS)
        try:
            self.cLocale = locale.setlocale(locale.LC_ALL, settings.locale)
            print("Current locale:", self.cLocale, "/ Default system locale:", locale.getdefaultlocale())
        except:
            try:
                self.cLocale = locale.setlocale(locale.LC_ALL, "")
            except:
                self.cLocale = locale.setlocale(locale.LC_ALL, locale.getdefaultlocale())
            print("Failed to set locale according to your settings. Using Default instead:", self.cLocale)

        # Get TimeZone
        self.localTZ, self.is_dst = zoneinfo.get_local_tz()
        print("Local Time Zone:", self.localTZ, "/ Daylight Saving Time:", ("+" if time.localtime().tm_isdst >= 0 else "")+str(time.localtime().tm_isdst))

        # These values will change according to some conditions. "Saving" them to self. variables
        self.firstRun = True
        self.bkg = None
        self.nsource = wconstants.nsource1
        self.nURL = wconstants.nURL1
        self.dist_limit = 0
        if settings.use_current_location and not settings.clockMode:
            self.dist_limit = self.check_location()
        self.location = settings.location[0][0]
        self.zip_code = settings.location[0][1]
        self.crc = settings.clockc
        self.prevMinimized = False

        # Settings
        self.iconf = wconstants.ICON_FOLDER + settings.iconSet
        self.iconScaleC = int(self.ymax * wconstants.iconSizeC / wconstants.REF_Y * wconstants.ICON_SCALE.get(settings.iconSet, 1.0))
        self.iconScaleF = int(self.ymax * wconstants.iconSizeF / wconstants.REF_Y * wconstants.ICON_SCALE.get(settings.iconSet, 1.0))
        self.moonIconScale = int(self.ymax * wconstants.moonIconSize / wconstants.REF_Y)
        self.sunsignIconScale = int(self.ymax * wconstants.sunsignIconSize / wconstants.REF_Y)
        self.alertIconScale = int(self.ymax * wconstants.alertIconSize / wconstants.REF_Y)

        # Other variables
        self.counter = 0
        self.wUpdated = False
        self.showingNews = False
        self.menu = None
        self.showingMenu = False
        self.updateWeather = False
        self.menu = None
        self.menu2 = None
        self.WC = None
        self.showingConfig = False
        self.help = None
        self.changedWhileNews = False
        self.brightness = -1
        self.keyP = None
        self.onlyTime = False
        self.onlyTimePrev = None
        self.user_clockMode = False
        self.errCount = 0
        self.sepPos = 0
        self.titles = ''
        self.pics = [None, None, None, None, None]
        self.tzOffset = None
        self.WtzOffset = 0
        self.nightTime = False
        self.xMoon = 0
        self.sunsign = None
        self.sunsign_icon = None
        self.moonHIcon = None
        self.rectHeader = None
        self.imgHeader = None
        self.rectTime = None
        self.imgTime = None
        self.rectCC = None
        self.imgCC = None
        self.rectFF = None
        self.imgFF = None
        self.rectAlert = None
        self.imgAlert = None

        # Weather info initialization
        self.wcc = ''
        self.wff = ''
        self.bkgCode = wconstants.DEFAULT_BKG
        self.iconNow = wconstants.DEFAULT_ICON
        self.iconNowPrev = None
        self.iconImgC = None
        self.bkgCodePrev = None
        self.iconC2 = None
        self.iconC2Prev = None
        self.iconImgC2 = None
        self.temp = ''
        self.temptext = ''
        self.feels_like = '0'
        self.wind_speed = '0'
        self.baro = '29.95'
        self.wind_dir = 'S'
        self.humid = '50.0'
        self.uvi = ''
        self.moon = None
        self.prevMoon = None
        self.moonPrev = None
        self.moonIcon = None
        self.alert_start = ""
        self.alert_end = ""
        self.alert = None
        self.alertIcon = None
        self.wLastUpdate = ''
        self.wPrevUpdate = ''
        self.wLastForecastUpdate = ''
        self.last = ''
        self.day = []
        for i in range(wconstants.NSUB): self.day.append('')
        self.icon = []
        for i in range(wconstants.NSUB): self.icon.append('na')
        self.iconPrev = []
        for i in range(wconstants.NSUB): self.iconPrev.append(None)
        self.iconImg = []
        for i in range(wconstants.NSUB): self.iconImg.append(None)
        self.iconNight = []
        for i in range(wconstants.NSUB): self.iconNight.append('')
        self.rain = []
        for i in range(wconstants.NSUB): self.rain.append('')
        self.temps = []
        for i in range(wconstants.NSUB): self.temps.append(['', ''])
        self.hTemps = []
        for i in range(wconstants.hourly_number): self.hTemps.append('')
        self.hIcons = []
        for i in range(wconstants.hourly_number): self.hIcons.append(None)
        self.hIconPrev = ''
        self.hHours = []
        for i in range(wconstants.hourly_number): self.hHours.append('')
        self.sunrise = '07:00'
        self.sr = '07'
        self.sunset = '20:00'
        self.sn = '20'

        # Colors
        self.convertPGColors()

        # Font Objects according to Text Sizes
        self.byF = pgutils.load_font(wconstants.FONTS_FOLDER, wconstants.font, int(self.ymax * wconstants.byTh), 0)
        self.yearF = pgutils.load_font(wconstants.FONTS_FOLDER, wconstants.font, int(self.ymax * wconstants.yearTh), 0)
        self.wdayF = pgutils.load_font(wconstants.FONTS_FOLDER, wconstants.font, int(self.ymax * wconstants.wdayTh), 0)
        self.monthF = pgutils.load_font(wconstants.FONTS_FOLDER, wconstants.font, int(self.ymax * wconstants.monthTh), 0)
        self.dayF = pgutils.load_font(wconstants.FONTS_FOLDER, wconstants.numberfont, int(self.ymax * wconstants.dayTh), 0)
        self.condF = pgutils.load_font(wconstants.FONTS_FOLDER, wconstants.font, int(self.ymax * wconstants.condTh), 0)
        self.timeF = pgutils.load_font(wconstants.FONTS_FOLDER, wconstants.numberfont, int(self.ymax * wconstants.timeTh), 0)
        self.secF = pgutils.load_font(wconstants.FONTS_FOLDER, wconstants.numberfontbold, int(self.ymax * wconstants.secTh), 1)
        self.cityF = pgutils.load_font(wconstants.FONTS_FOLDER, wconstants.font, int(self.ymax * wconstants.cityTh), 0)
        self.statF = pgutils.load_font(wconstants.FONTS_FOLDER, wconstants.font, int(self.ymax * wconstants.statTh), 0)
        self.ckcityF = pgutils.load_font(wconstants.FONTS_FOLDER, wconstants.font, int(self.ymax * wconstants.statTh * 0.8), 0)
        self.tempF = pgutils.load_font(wconstants.FONTS_FOLDER, wconstants.numberfont, int(self.ymax * wconstants.tempTh), 0)
        self.degF = pgutils.load_font(wconstants.FONTS_FOLDER, wconstants.numberfont, int(self.ymax * wconstants.degTh), 0)
        self.temptxF = pgutils.load_font(wconstants.FONTS_FOLDER, wconstants.font, int(self.ymax * wconstants.temptxTh), 0)
        self.subtempMaxF = pgutils.load_font(wconstants.FONTS_FOLDER, wconstants.numberfont, int(self.ymax * wconstants.subtempTh), 0)
        self.subtempMinF = pgutils.load_font(wconstants.FONTS_FOLDER, wconstants.numberfont, int(self.ymax * wconstants.subtempTh * 0.6), 0)
        self.subHourlyTempF = pgutils.load_font(wconstants.FONTS_FOLDER, wconstants.numberfont, int(self.ymax * wconstants.subtempTh * 0.5), 0)
        self.subHourlyHourF = pgutils.load_font(wconstants.FONTS_FOLDER, wconstants.fontbold, int(self.ymax * wconstants.subtempTh * 0.5), 1)
        self.subrainF = pgutils.load_font(wconstants.FONTS_FOLDER, wconstants.numberfontbold, int(self.ymax * wconstants.subrainTh), 1)
        self.highlightF = pgutils.load_font(wconstants.FONTS_FOLDER, wconstants.font, int(self.ymax * wconstants.highlightTh), 1)
        self.percF = pgutils.load_font(wconstants.FONTS_FOLDER, wconstants.numberfontbold, int(self.ymax * wconstants.subrainTh / 2), 1)
        self.calF = pgutils.load_font(wconstants.FONTS_FOLDER, wconstants.calfontbold, int(self.ymax * wconstants.calTh), 1)
        self.alertF = pgutils.load_font(wconstants.FONTS_FOLDER, wconstants.font, int(self.ymax * wconstants.alertTh), 0)
        self.newsF = pgutils.load_font(wconstants.FONTS_FOLDER, wconstants.fontbold, int(self.ymax * wconstants.newsTh), 1)
        self.nX, self.nY = pgutils.draw_text(self.screen, "B", self.newsF, blit=False)

        # Positions
        self.clockYPos = self.ymax * wconstants.clockYPos  # Clock position
        self.clockSYPos = self.clockYPos + self.ymax * wconstants.secTh * 0.2  # Seconds position
        self.subYPos = self.ymax * wconstants.subYPos  # SubWindows (forecasts) Yaxis start position
        self.CCXPos = self.xmax * wconstants.CCXPos
        self.CCYPos = self.ymax * wconstants.CCYPos
        self.radius = int(self.ymax * wconstants.radius)  # Radius of the world clocks

    def __del__(self):
        """ Destructor to make sure pygame shuts down, etc. """

    def check_location(self):
        if settings.debug: print("GET_LOC", time.strftime("%H:%M:%S"))

        loc = utils.get_location_by_ip(wconstants.gIPURL % settings.lang)
        if loc:
            loc1 = (float(loc[3]), float(loc[4]))
            loc2 = (float(settings.location[0][1].split("lat=")[1].split("&")[0]), float(settings.location[0][1].split("&lon=")[1]))
            dist = utils.get_distance(loc1, loc2, settings.disp_units)
            if dist < int(wconstants.distLimit[settings.disp_units]):
                dist = 0
            if settings.use_current_location:
                locations = [(loc[0] + (", " + loc[1] if loc[1] else "") + (", " + loc[2] if loc[2] else ""),
                              "lat=" + str(loc[3]) + "&lon=" + str(loc[4]))]
                for i in range(0, len(settings.location)):
                    locations.append(settings.location[i])
                settings.location = locations
        else:
            dist = -1

        return dist

    def convertPGColors(self):
        settings.cBkg = pygame.Color(settings.cBkg)
        settings.nBkg = pygame.Color(settings.nBkg)
        settings.clockc = pygame.Color(settings.clockc)
        settings.clockh = pygame.Color(settings.clockh)
        settings.nc = pygame.Color(settings.nc)
        settings.wc = pygame.Color(settings.wc)
        settings.chighlight = pygame.Color(settings.chighlight)
        settings.cdark = pygame.Color(settings.cdark)
        settings.cdim = pygame.Color(settings.cdim)
        settings.crcm = pygame.Color(settings.crcm)
        settings.crcw = pygame.Color(settings.crcw)
        settings.chigh = pygame.Color(settings.chigh)
        settings.clow = pygame.Color(settings.clow)
        settings.byc = pygame.Color(settings.byc)

    def show_all(self, displayAll=False, forceShowWeather=False, updateWeather=False):
        if settings.debug: print("SHOWALL", time.strftime("%H:%M:%S"))

        # PREPARE variables
        rect = []
        if self.firstRun:
            self.firstRun = False
            if len(sys.argv) > 1:
                sys.argv = [sys.argv[0]]
                self.start_help()
            else:
                if settings.firstInstall:
                    self.show_config()
                displayAll = True
                updateWeather = True

        elif self.showingConfig and self.WC is not None and not self.WC.is_alive():
            showingNews = self.showingNews
            changedWhileNews = self.changedWhileNews or self.showingNews
            border_width = self.border_width
            titlebar_height = self.titlebar_height
            clockMode = self.user_clockMode
            location = self.location
            zip_code = self.zip_code
            keep_location = False
            if self.location != settings.location[0][0]:
                keep_location = True
            self.config_back()
            self.showingNews = showingNews
            self.changedWhileNews = changedWhileNews
            self.border_width = border_width
            self.titlebar_height = titlebar_height
            self.user_clockMode = clockMode
            if keep_location:
                self.location = location
                self.zip_code = zip_code
            return rect

        elif self.showingMenu:
            return rect

        disp_header = False
        disp_time = False
        disp_sep = False
        disp_weather = False
        disp_clocks = False
        disp_news = False
        update_news = False

        # Get time
        t = time.strftime("%H:%M:%S")
        hours = int(t[:2])
        minutes = int(t[3:5])
        seconds = int(t[6:])
        hhmm = t[:5]

        # SELECT actions to be accomplished according to time and settings
        if seconds == 0:
            disp_time = True
            if minutes == 0 and hours == 0:
                disp_header = True
            elif self.sunset == hhmm or self.sunrise == hhmm:
                displayAll = True
        else:
            disp_sep = True

        if (settings.clockMode or self.user_clockMode or self.onlyTime) and (seconds == 0 or displayAll):
            disp_clocks = True

        if not settings.clockMode and not self.user_clockMode and not self.onlyTime and \
                (forceShowWeather or displayAll):
            disp_weather = True

        if not settings.clockMode and not self.user_clockMode and \
            (updateWeather or
             ((minutes + 1) % wconstants.min_update_weather == 0 and
              (seconds == wconstants.sec_update_weather or displayAll or settings.newsMode == wconstants.NEWS_ALWAYSON))):
            disp_weather = True
            updateWeather = True

        if not settings.clockMode and not self.showingNews and \
                (settings.newsMode == wconstants.NEWS_ALWAYSON or
                 (settings.newsMode == wconstants.NEWS_PERIOD and
                  (minutes + 1) % wconstants.min_update_news == 0 and seconds == wconstants.sec_update_news)):
            disp_news = True
            update_news = True

        elif not settings.clockMode and not self.showingNews and \
                (settings.newsMode == wconstants.NEWS_ALWAYSON or
                 (settings.newsMode == wconstants.NEWS_PERIOD and
                  minutes % wconstants.min_update_news == 0 and seconds == wconstants.sec_show_news)):
            disp_news = True

        # EXECUTE selected actions
        if disp_sep and not disp_time:
            rect.append(self.display_separator(seconds))

        if disp_weather:
            if updateWeather:
                self.wUpdated = self.update_weather(firstRun=displayAll)

            if self.wUpdated:
                if self.bkg != self.bkgCodePrev:
                    displayAll = True
            elif self.onlyTime:
                disp_weather = False
                disp_clocks = True
                if self.onlyTimePrev != self.onlyTime:
                    displayAll = True
                    self.onlyTimePrev = self.onlyTime

        if displayAll:
            self.display_bkg()
            disp_header = True
            disp_time = True

        if disp_header:
            self.display_header()
            rect.append(self.rectHeader)

        if disp_time:
            self.display_time()
            rect.append(self.rectTime)

        if disp_weather:
            self.show_weather()
            rect.append(self.rectCC)
            rect.append(self.rectFF)
        elif disp_clocks:
            self.show_world_clocks()
            rect.append(self.rectFF)

        if disp_news and (not self.showingNews or settings.newsMode == wconstants.NEWS_ALWAYSON):
            if displayAll and settings.newsMode == wconstants.NEWS_ALWAYSON:
                pygame.display.update()
            if update_news:
                self.update_news()
            if self.titles and (not update_news or settings.newsMode == wconstants.NEWS_ALWAYSON):
                self.show_news()

        # UPDATE display (complete or selected rect)
        if displayAll or not rect:
            pygame.display.update()
        elif rect and not self.showingNews:
            pygame.display.update(rect)

        return rect

    def display_bkg(self):
        if settings.debug: print("DISP_BKG", time.strftime("%H:%M:%S"))

        rect = (self.xmin, self.ymin, self.xmax, self.ymax)

        if settings.showBkg:
            if settings.bkgMode == wconstants.BKG_WEATHER \
                    and not settings.clockMode and not self.user_clockMode and not self.onlyTime:
                code = str(self.bkgCode)
            else:
                code = str(wconstants.DEFAULT_BKG)

            # Prepare Background only if changed since last time
            if code != self.bkgCodePrev:
                self.bkgCodePrev = code
                # Force capturing areas for new bkg
                self.imgUpper = self.imgFF = self.imgTime = self.imgHeader = self.imgCC = self.imgAlert = None

                if self.showingNews:
                    self.changedWhileNews = True

                try:
                    self.bkg = pygame.image.load(utils.resource_path(wconstants.BKG_FOLDER) + code + wconstants.BKG_EXT)
                    self.brightness = -1
                except:
                    print("Error loading background. Loading default background instead. Code:", wconstants.BKG_FOLDER + code)
                    print(traceback.format_exc())

                    try:
                        self.bkg = pygame.image.load(utils.resource_path(wconstants.BKG_FOLDER) + wconstants.NA_BKG + wconstants.BKG_EXT)
                    except:
                        print("Error loading default background (na.jpg). Display blank screen instead")
                        print(traceback.format_exc())
                        pygame.draw.rect(self.screen, settings.cBkg, rect)

                if self.bkg.get_size() != (self.xmax, self.ymax):
                    self.bkg = pygame.transform.smoothscale(self.bkg, (self.xmax, self.ymax))

                self.screen.blit(self.bkg, rect)
                if settings.dimBkg and code != str(wconstants.DEFAULT_BKG):
                    pgutils.dim(self.screen, settings.dimFactor, settings.cdim, rect, False)
        else:
            pygame.draw.rect(self.screen, settings.cBkg, rect)

        return

    def display_header(self):
        if settings.debug: print("DISP_HEADER", time.strftime("%H:%M:%S"))

        self.rectHeader = (self.xmin, self.ymin, self.xmax, self.ygap * 5)

        # Capture area background / Erase previous values
        if settings.showBkg:
            self.imgHeader = pgutils.prepare_area(self.screen, self.imgHeader, self.rectHeader)
        else:
            pygame.draw.rect(self.screen, settings.cBkg, self.rectHeader)

        self.display_calendar()
        self.display_by()
        self.display_location()
        self.display_astronomics()

        return self.rectHeader

    def display_by(self):
        if settings.debug: print("DISP_BY", time.strftime("%H:%M:%S"))

        by = wconstants.SYSTEM_CAPTION[-7:]
        (stx, sty) = pgutils.draw_text(self.screen, settings.wsource, self.byF, blit=False)
        (btx, bty) = pgutils.draw_text(self.screen, " | " + by, self.byF, blit=False)
        x = (self.xmax - (stx + btx)) / 2

        pgutils.draw_text(self.screen, settings.wsource, self.byF, fcolor=settings.byc, blit=True, x=x, y=self.ymargin)
        pgutils.draw_text(self.screen, " | " + by, self.byF, fcolor=settings.clockh, blit=True, x=x + stx, y=self.ymargin)

        return x, self.ymargin, x + stx + btx, self.ymargin + sty

    def display_calendar(self):
        if settings.debug: print("DISP_CALENDAR", time.strftime("%H:%M:%S"))

        tm = time.strftime("%A/%B/%d/%Y/%m").split("/")
        dayofweek = tm[0]
        monthT = tm[1]
        dayT = tm[2]

        (tx1a, ty1a) = pgutils.draw_text(self.screen, dayofweek, self.wdayF, blit=False)
        (tx1b, ty1b) = pgutils.draw_text(self.screen, monthT, self.monthF, blit=False)
        (tx1c, ty1c) = pgutils.draw_text(self.screen, dayT, self.dayF, blit=False)
        x = self.xgap
        y = 0

        pgutils.draw_text(self.screen, dayT, self.dayF, fcolor=settings.clockc, blit=True,
                          x=x, y=y, outline=settings.outline)
        pgutils.draw_text(self.screen, dayofweek, self.wdayF, fcolor=settings.clockc, blit=True,
                          x=x + tx1c + self.xmargin, y=y + self.ygap * 1.3, outline=settings.outline)
        pgutils.draw_text(self.screen, monthT, self.monthF, fcolor=settings.clockc, blit=True,
                          x=x + tx1c + self.xmargin, y=y + self.ygap * 1.3 + ty1a * 0.9, outline=settings.outline)

        return x, y, x + tx1c + max(tx1a, tx1b), ty1c

    def display_location(self):
        if settings.debug: print("DISP_LOC", time.strftime("%H:%M:%S"))

        if not self.location:
            self.location = settings.location[0][0]
        (tx, ty) = pgutils.draw_text(self.screen, self.location, self.cityF, blit=False)

        x = (self.xmax - tx) / 2
        pgutils.draw_text(self.screen, self.location, self.cityF, fcolor=settings.clockh, blit=True,
                          x=x, y=self.ygap * 2.5, outline=settings.outline)

        return x, self.ygap, x + tx, ty

    def display_astronomics(self):
        if settings.debug: print("DISP_ASTRO", time.strftime("%H:%M:%S"))

        x = self.xmax - self.xgap

        if settings.showSunSigns:
            current_sunsign = wutils.get_constellation()

            if self.sunsign != current_sunsign:
                self.sunsign = current_sunsign
                self.sunsign_icon = pgutils.load_icon(current_sunsign, wconstants.SUNSIGNS_FOLDER)
                sx, sy = self.sunsign_icon.get_size()
                self.sunsign_icon = pygame.transform.smoothscale(self.sunsign_icon,
                                                                 (int(sx * (self.sunsignIconScale / sy)),
                                                                  self.sunsignIconScale))

            (sx, sy) = self.sunsign_icon.get_size()
            x = self.xmax - sx - self.xmargin
            self.screen.blit(self.sunsign_icon, (x, 0))

        scale = int(self.sunsignIconScale * 0.5)
        self.xMoon = x - scale
        if not self.nightTime and settings.moonMode in (wconstants.MOON_BOTH, wconstants.MOON_ONHEADER) and \
                not self.onlyTime and not settings.clockMode and not self.user_clockMode:
            if not self.moonHIcon or self.moon != self.prevMoon:
                self.prevMoon = self.moon
                self.moonHIcon = pgutils.load_icon(self.moon, wconstants.MOON_FOLDER)
                self.moonHIcon = pygame.transform.smoothscale(self.moonHIcon, (scale, scale))
            self.screen.blit(self.moonHIcon, (self.xMoon, self.ygap))

        return

    def display_separator(self, seconds):
        if settings.debug: print("DISP_SEP", time.strftime("%H:%M:%S"))

        if seconds % 2 == 0:
            sepColor = settings.clockc
        else:
            sepColor = settings.cdark

        (txsep, tysep) = pgutils.draw_text(self.screen, ":", self.timeF, sepColor, True, self.sepPos, self.clockYPos)

        return self.sepPos, self.clockYPos + tysep * 0.22, txsep, tysep - tysep * 0.4

    def display_time(self):
        if settings.debug: print("DISP_TIME", time.strftime("%H:%M:%S"))

        # Prepare values
        tm = time.strftime("%H:%M")
        hour = tm[:2]
        sep = tm[2:3]
        minute = tm[3:]
        x = self.xmargin

        # Prepare drawing
        (tx2, ty2) = pgutils.draw_text(self.screen, hour, self.timeF, blit=False)
        (txsep, tysep) = pgutils.draw_text(self.screen, sep, self.timeF, blit=False)
        (tx3, ty3) = pgutils.draw_text(self.screen, minute, self.timeF, blit=False)
        if settings.clockMode or self.user_clockMode or self.onlyTime:
            x = (self.xmax - (tx2 + txsep + tx3)) / 2
        self.rectTime = (x, self.rectHeader[3], tx2 + txsep + tx3, ty2 - ty2 * 0.3)

        # Capture area background / Erase previous values
        if settings.showBkg:
            self.imgTime = pgutils.prepare_area(self.screen, self.imgTime, self.rectTime)
        else:
            pygame.draw.rect(self.screen, settings.cBkg, self.rectTime)

        # Separator Xaxis position for further calculations (when drawing just separator)
        self.sepPos = x + tx2

        # Draw time
        pgutils.draw_text(self.screen, hour, self.timeF, fcolor=settings.clockc, blit=True,
                          x=x, y=self.clockYPos, outline=settings.outline)
        pgutils.draw_text(self.screen, sep, self.timeF, fcolor=settings.clockc, blit=True,
                          x=x + tx3, y=self.clockYPos)
        pgutils.draw_text(self.screen, minute, self.timeF, fcolor=settings.clockc, blit=True,
                          x=x + tx3 + txsep, y=self.clockYPos, outline=settings.outline)

        # If time overlaps with alert, re-blit it
        if self.rectTime[1] + self.rectTime[3] > self.subYPos - self.alertIconScale and self.alert:
            self.display_alert()

        return self.rectTime

    def show_world_clocks(self):
        if settings.debug: print("SHOW_WORLDS", time.strftime("%H:%M:%S"))

        if not self.tzOffset or not self.location or self.location.isspace() or self.location == wconstants.currentTZSep:
            self.tzOffset = zoneinfo.get_world_clock_offsets(settings.timeZones)

        self.rectFF = (self.xmin, self.subYPos, self.xmax, self.ymax - self.subYPos)

        # Capture area background / Erase previous values
        if settings.showBkg:
            self.imgFF = pgutils.prepare_area(self.screen, self.imgFF, self.rectFF)
        else:
            pygame.draw.rect(self.screen, settings.cBkg, self.rectFF)

        if self.tzOffset:
            zones = len(self.tzOffset)
            gap = (self.xmax - (self.radius * 2 * zones)) / (zones + 1)
            clockX = int(gap + self.radius)
            clockY = int(self.ymax - self.radius - self.ymargin * 2)

            hm = time.strftime("%H%M")
            h = int(hm[:2])
            m = int(hm[2:])

            for i in range(zones):
                # Get city name and time (adjusted to 24 hours / 60 minutes using modulo)
                city, hOffset, mOffset = self.tzOffset[i]
                hTZ = (h + hOffset) % 24
                mTZ = (m + mOffset) % 60

                # Draw city name
                (tx, ty) = pgutils.draw_text(self.screen, city, self.ckcityF, blit=False)
                pgutils.draw_text(self.screen, city, self.ckcityF, fcolor=settings.clockc, blit=True, x=clockX - tx / 2,
                                  y=clockY - self.radius - ty - self.ymargin)

                # Draw Analog Clock
                pgutils.draw_analog_clock(self.screen, hTZ, mTZ, clockX, clockY, self.radius, 5, 5, settings.clockc,
                                          settings.chighlight)
                clockX = int(clockX + self.radius * 2 + gap)

        return self.rectFF

    def update_weather(self, firstRun=False, only_parse=False):
        if settings.debug: print("UPD_WEATHER", time.strftime("%H:%M:%S"))

        wUpdated = False
        update_error = False
        tb_content = ""

        if not only_parse:
            # Get Weather information from source
            url = wconstants.weatherURL % (self.zip_code, settings.disp_units, settings.lang_code)
            try:
                with urllib.request.urlopen(url, timeout=settings.timeout) as response:
                    # Decoding is needed only by arm-Linux, and only for JSON responses (not XML)
                    self.wcc = json.loads(response.read().decode('utf8'))
            except:
                update_error = True
                tb_content = traceback.format_exc()

        if not update_error:

            wUpdated = self.parse_openweathermap(self.wcc, force=firstRun)

            if not only_parse:

                if self.onlyTime:
                    # Recovering from update failure.
                    # This will force weather info to be drawn despite it changed since last correct update
                    self.onlyTime = False
                    self.onlyTimePrev = True
                    wUpdated = True

        else:
            self.errCount += 1
            if firstRun or self.errCount > wconstants.errMax:
                # No Weather info or obsolete (show clock only)
                self.onlyTime = True
                self.onlyTimePrev = False
                print("No Weather info or obsolete. Falling back to World Clocks")
            else:
                print("Error getting Weather update from", settings.wsource, "at", self.last, self.errCount, "times")
            print(tb_content)

        return wUpdated

    def parse_openweathermap(self, w, force=False):
        if settings.debug: print("PARSE_OPENW", time.strftime("%H:%M:%S"))

        # Current Conditions
        cc = w["current"]
        ff = w["daily"][0]
        self.WtzOffset = int(w["timezone_offset"])
        self.temp = str(int(cc["temp"]))
        self.feels_like = str(int(cc["feels_like"])) + wconstants.degree_sign
        self.iconNow = wutils.convert_weather_code(str(cc["weather"][0]["id"]))
        self.bkgCode = self.iconNow
        self.temptext = str(cc["weather"][0]["description"]).capitalize()
        self.wind_speed = str(cc["wind_speed"] * wconstants.windScale[settings.disp_units])
        self.wind_dir = wutils.convert_win_direction(cc["wind_deg"], settings.lang)
        self.baro = str("%.2f" % (cc["pressure"] * wconstants.baroScale[settings.disp_units]))
        self.humid = str(cc["humidity"])
        self.uvi = str(int(cc["uvi"]))
        self.moon = wutils.convert_moon_phase(ff["moon_phase"])
        self.sunrise = time.strftime("%H:%M", time.gmtime(cc["sunrise"] + self.WtzOffset))
        self.sunset = time.strftime("%H:%M", time.gmtime(cc["sunset"] + self.WtzOffset))
        hmCurrent = time.strftime("%H:%M")
        self.nightTime = (self.sunset <= hmCurrent or self.sunrise > hmCurrent)
        if settings.showBkg and settings.bkgMode == wconstants.BKG_WEATHER:
            if self.nightTime:
                self.bkgCode = wutils.getNightBkg(cc["weather"][0]["icon"][:-1])
            elif self.iconNow == "32":
                if float(self.temp) >= wconstants.tempHigh[settings.disp_units]:
                    self.iconNow = "36"
                    self.bkgCode = "36"
                elif float(self.temp) <= wconstants.tempLow[settings.disp_units]:
                    self.bkgCode = "25"

        self.alert_start = ""
        self.alert_end = ""
        self.alert = None
        wind_speed = float(ff["wind_speed"] * wconstants.windScale[settings.disp_units])
        uvi = float(ff["uvi"])
        if "alerts" in w.keys() and w["alerts"][0]["end"] > cc["dt"]:
            self.alert_start = time.strftime("%H:%M", time.gmtime(w["alerts"][0]["start"] + self.WtzOffset))
            self.alert_end = time.strftime("%H:%M", time.gmtime(w["alerts"][0]["end"] + self.WtzOffset))
            self.alert = w["alerts"][0]["event"]
        elif wind_speed >= wconstants.WindHigh[settings.disp_units]:
            self.alert = settings.texts["121"] + \
                         " - " + str(wind_speed) + " " + wconstants.windSpeed[settings.disp_units]
        elif uvi >= wconstants.UVIHigh:
            self.alert = settings.texts["120"] + " " + \
                         settings.texts[str(wconstants.uviUnits[min(int(uvi), 11)])] + \
                         " - " + str(uvi)

        # No apparent way to detect if data has already been updated
        wUpdated = False
        self.wLastUpdate = self.temp + self.feels_like + self.iconNow + self.temptext + self.wind_speed + self.wind_dir + self.baro + self.humid
        if self.wPrevUpdate != self.wLastUpdate or force:
            self.wPrevUpdate = self.wLastUpdate
            wUpdated = True
            self.last = hmCurrent

            # Daily Forecasts
            i = 0
            j = 0
            current = int(time.strftime("%y%m%d"))
            while i < wconstants.NSUB and j < 8:
                day_data = w["daily"][j]
                if int(time.strftime("%y%m%d", time.gmtime(day_data["dt"]))) >= current:
                    self.day[i] = time.strftime("%A, %d", time.gmtime(day_data["dt"] + self.WtzOffset))
                    self.day[i] = time.strftime("%A", time.gmtime(day_data["dt"] + self.WtzOffset)) \
                                  + time.strftime(", %d", time.gmtime(day_data["dt"] + self.WtzOffset))
                    self.icon[i] = wutils.convert_weather_code(str(day_data["weather"][0]["id"]))
                    self.iconNight[i] = "na"
                    self.rain[i] = str(int(round(day_data["pop"] * 100 / 5, 0)) * 5)
                    self.temps[i][0] = str(int(day_data["temp"]["max"])) + wconstants.degree_sign
                    self.temps[i][1] = str(int(day_data["temp"]["min"])) + wconstants.degree_sign
                    i += 1
                j += 1

            # Hourly Forecasts
            i = 0
            j = 0
            while i < wconstants.hourly_number and j < 48:
                hour_data = w["hourly"][j]
                dt = hour_data["dt"]
                if dt > cc["dt"]:
                    self.hHours[i] = time.strftime("%H:%M", time.gmtime(dt + self.WtzOffset))
                    self.hTemps[i] = str(int(hour_data["temp"])) + wconstants.degree_sign
                    icon = wutils.convert_weather_code(str(hour_data["weather"][0]["id"]))
                    code = str(hour_data["weather"][0]["icon"])
                    if code[-1:] == "n":
                        icon = wutils.get_night_icons(icon)
                    self.hIcons[i] = icon
                    if dt == 1623186000:  # 23:00
                        self.iconNight[0] = icon
                    i += 1
                j += 1

        return wUpdated

    def show_weather(self):
        if settings.debug: print("SHOW_WEATHER", time.strftime("%H:%M:%S"))

        if settings.dimForecasts:
            pgutils.dim(self.screen, settings.dimFactor, settings.cdim,
                        (self.xmin + self.xmargin, self.subYPos, self.xmax - self.xmargin * 2,
                          self.ymax - self.subYPos - self.ymargin))

        # Current Conditions
        ccXPos, ccYPos = self.display_current_conditions()

        # Other conditions
        self.display_other_conditions(ccXPos, ccYPos)

        # Alerts
        self.display_alert()

        self.rectFF = self.xmin, self.subYPos, self.xmax, self.ymax - self.subYPos
        # Capture area background / Erase previous values
        if settings.showBkg:
            self.imgFF = pgutils.prepare_area(self.screen, self.imgFF, self.rectFF)
        else:
            pygame.draw.rect(self.screen, settings.cBkg, self.rectFF)

        # Daily Forecasts
        for i in range(wconstants.NSUB):
            self.display_daily_forecasts(i)

        # Hourly Forecasts
        for i in range(wconstants.hourly_number):
            self.display_hourly_forecasts(i)

        return self.rectFF

    def display_alert(self):
        if settings.debug: print("DISP_ALERT", time.strftime("%H:%M:%S"))

        x = self.xgap * 2
        y = self.subYPos - self.alertIconScale - (self.ymargin if settings.dispRatio <= 1.6 else 0)

        self.rectAlert = x, y, self.xmax, self.alertIconScale
        # Capture area background / Erase previous values
        if settings.showBkg:
            self.imgAlert = pgutils.prepare_area(self.screen, self.imgAlert, self.rectAlert)
        else:
            pygame.draw.rect(self.screen, settings.cBkg, self.rectAlert)

        if self.alert is not None:

            if self.alertIcon is None:
                self.alertIcon = pgutils.load_icon(wconstants.ALERT_ICON, wconstants.ALERT_ICONFOLDER)
                self.alertIcon = pygame.transform.smoothscale(self.alertIcon,
                                                              (self.alertIconScale, self.alertIconScale))
            (ix, iy) = self.alertIcon.get_size()

            self.screen.blit(self.alertIcon, (x, y))

            prefix = ""
            if self.alert_start:
                prefix = self.alert_start + " - " + self.alert_end + ": "
            pgutils.draw_text(self.screen, prefix + self.alert, self.alertF, settings.chigh, True,
                              x + ix + self.xmargin, y + self.ymargin)

        return

    def display_current_conditions(self):
        if settings.debug: print("DISP_CURR", time.strftime("%H:%M:%S"))

        x = self.CCXPos
        y = self.CCYPos
        iconGap = 0
        tempGap = self.xmargin * (3 - len(self.temp))

        # Capture area background / Erase previous values
        self.rectCC = (self.rectTime[0] + self.rectTime[2], y, self.xmax - x, self.rectTime[3])
        if settings.showBkg:
            self.imgCC = pgutils.prepare_area(self.screen, self.imgCC, self.rectCC)
        else:
            pygame.draw.rect(self.screen, settings.cBkg, self.rectCC)

        # PREPARE Current conditions Icon
        icon = self.iconNow
        folder = self.iconf
        scale = self.iconScaleC
        drawMoonWIcon = False
        drawMoonPhase = settings.moonMode in (wconstants.MOON_ONCURRENT, wconstants.MOON_BOTH)
        if self.nightTime:
            icon = wutils.get_night_icons(self.iconNow)
            if drawMoonPhase and self.moon and icon != self.iconNow:
                icon = self.moon
                folder = wconstants.MOON_FOLDER
                scale = self.moonIconScale
                drawMoonPhase = False

                # Until you find a full set of night icons, mix moon + weather icons (if they don't include sun or moon)
                self.iconC2 = wutils.getMoonWIcons(self.iconNow)
                if self.iconC2 is not None:
                    drawMoonWIcon = True
                    if self.iconC2 != self.iconC2Prev or self.iconImgC2 is None:
                        self.iconC2Prev = self.iconC2
                        self.iconImgC2 = pgutils.load_icon(self.iconC2, folder=wconstants.MOON_W_FOLDER)
                        (i2x, i2y) = self.iconImgC2.get_size()
                        self.iconImgC2 = pygame.transform.smoothscale(self.iconImgC2, (int(self.iconScaleC*0.7), int((i2y*(self.iconScaleC/i2x))*0.7)))
                    (i2x, i2y) = self.iconImgC2.get_size()
                    tempGap += i2x / 7

        if icon != self.iconNowPrev:
            self.iconNowPrev = icon
            self.iconImgC = pgutils.load_icon(icon, folder)
            (ix, iy) = self.iconImgC.get_size()

            if ix != scale:
                if ix != iy:
                    # These icons are wider than taller and need a different scale and additional space
                    scaleX = int(scale)
                    scaleY = int(iy * (scale / ix))
                else:
                    scaleX = int(scale)
                    scaleY = int(scale)
                self.iconImgC = pygame.transform.smoothscale(self.iconImgC, (scaleX, scaleY))
        (ix, iy) = self.iconImgC.get_size()
        if ix != iy:
            iconGap = -self.xgap * 0.8
            tempGap = 0

        # PREPARE Outside Temp
        (tx, ty) = pgutils.draw_text(self.screen, self.temp, self.tempF, blit=False)
        (dtx, dty) = pgutils.draw_text(self.screen, wconstants.degree_sign, self.degF, blit=False)
        (ttx, tty) = pgutils.draw_text(self.screen, self.temptext, self.temptxF, blit=False)
        (utx, uty) = pgutils.draw_text(self.screen, settings.texts["106"] + " " + self.last,
                                       self.condF, blit=False)

        # BLIT Current conditions Icon
        iconX = x + iconGap + ((self.xmax - x) - ix - tempGap - tx - dtx) / 2
        self.screen.blit(self.iconImgC, (iconX, y))
        if drawMoonWIcon:
            self.screen.blit(self.iconImgC2, (iconX + self.xgap, y + iy - i2y))
        elif drawMoonPhase and not self.onlyTime and not settings.clockMode and not self.user_clockMode:
                scale = int(self.sunsignIconScale * 0.5)
                if not self.moonHIcon or self.moon != self.prevMoon:
                    self.prevMoon = self.moon
                    self.moonHIcon = pgutils.load_icon(self.moon, wconstants.MOON_FOLDER)
                    self.moonHIcon = pygame.transform.smoothscale(self.moonHIcon, (scale, scale))
                self.screen.blit(self.moonHIcon, (self.xMoon, self.ygap))

        # DRAW Outside Temp
        y = y - self.ygap
        pgutils.draw_text(self.screen, self.temp, self.tempF, fcolor=settings.wc, blit=True,
                          x=iconX + ix + tempGap, y=y, outline=settings.outline)
        y = y + self.ymargin * 2
        pgutils.draw_text(self.screen, wconstants.degree_sign, self.degF, fcolor=settings.wc, blit=True,
                          x=iconX + ix + tempGap + tx, y=y + self.ygap, outline=settings.outline)
        y = y + ty - self.ygap * 2
        pgutils.draw_text(self.screen, self.temptext, self.temptxF, fcolor=settings.wc, blit=True,
                          x=x + ((self.xmax - x) - ttx) / 2, y=y, outline=settings.outline)
        y = y + tty * 1.25
        pgutils.draw_text(self.screen, settings.texts["106"] + " " + self.last, self.condF,
                          fcolor=settings.wc, blit=True, x=x + ((self.xmax - x) - utx) / 2, y=y)

        return self.CCXPos, y + uty * 1.7

    def display_other_conditions(self, XPos, YPos):
        if settings.debug: print("DISP_OTHER", time.strftime("%H:%M:%S"))

        windchill = settings.texts["101"] + " " + self.feels_like
        windspeed = settings.texts["102"] + " " + ("%.0f %s" % (float(self.wind_speed), wconstants.windSpeed[settings.disp_units]))
        winddir = settings.texts["103"] + " " + self.wind_dir
        line = windchill + "   " + windspeed + "   " + winddir
        (tx1, ty1) = pgutils.draw_text(self.screen, line, self.condF, blit=False)
        x = XPos + ((self.xmax - XPos - tx1) / 2)
        pgutils.draw_text(self.screen, line, self.condF, fcolor=settings.wc, blit=True, x=x, y=YPos)

        barometer = settings.texts["104"] + " " + self.baro + wconstants.baroUnits[settings.disp_units]
        humidity = settings.texts["105"] + " " + self.humid + "%"
        uvi = "UVI " + settings.texts[str(wconstants.uviUnits[min(int(self.uvi), 11)])]
        line = barometer + "   " + humidity + "   " + uvi
        (tx2, ty2) = pgutils.draw_text(self.screen, line, self.condF, blit=False)
        x = XPos + ((self.xmax - XPos - tx2) / 2)
        pgutils.draw_text(self.screen, line, self.condF, fcolor=settings.wc, blit=True, x=x, y=YPos + ty1 * 1.25)

        return

    def display_daily_forecasts(self, subwin):
        if settings.debug: print("DISP_DAILY", time.strftime("%H:%M:%S"))

        subwinWidth = (self.xmax - self.xgap * 2) / wconstants.NSUB
        x = (subwinWidth * subwin) + self.xgap*2
        y = self.subYPos

        # Draw day
        tx, ty = pgutils.draw_text(self.screen, self.day[subwin], self.subtempMinF, fcolor=settings.wc, blit=True,
                                   x=x+self.xmargin, y=y)
        y = y + ty

        # Draw icon
        if self.icon[subwin] != self.iconPrev[subwin]:
            self.iconPrev[subwin] = self.icon[subwin]
            self.iconImg[subwin] = pgutils.load_icon(self.icon[subwin], self.iconf)

        (ix, iy) = self.iconImg[subwin].get_size()
        if ix != self.iconScaleF:
            if ix != iy:
                # These icons are wider than longer and need a different scale
                scaleX = int(self.iconScaleF * 1.15)
                scaleY = int(iy * ((self.iconScaleF * 1.15) / ix))
            else:
                scaleX = self.iconScaleF
                scaleY = int(iy * (self.iconScaleF / ix))
            self.iconImg[subwin] = pygame.transform.smoothscale(self.iconImg[subwin], (scaleX, scaleY))
            (ix, iy) = self.iconImg[subwin].get_size()
        if ix != iy:
            x = x - self.xgap*1.5

        self.screen.blit(self.iconImg[subwin], (x, y))

        (tx1, ty1) = pgutils.draw_text(self.screen, self.temps[subwin][0] + " ", self.subtempMaxF, blit=False)
        (tx2, ty2) = pgutils.draw_text(self.screen, self.temps[subwin][1], self.subtempMinF, blit=False)
        pgutils.draw_text(self.screen, self.temps[subwin][0], self.subtempMaxF, settings.wc, blit=True, x=x + ix, y=y)
        y = y + ty1 * 0.3
        pgutils.draw_text(self.screen, self.temps[subwin][1], self.subtempMinF, settings.wc, blit=True, x=x + ix + tx1, y=y)

        # Draw rain chance
        self.crc = settings.clockc
        (rtx, rty) = pgutils.draw_text(self.screen, self.rain[subwin], self.subrainF, self.crc, False)
        (ptx, pty) = pgutils.draw_text(self.screen, "%", self.percF, self.crc, False)
        if int(self.rain[subwin]) >= wconstants.RainHigh:
            self.crc = settings.crcw
        elif int(self.rain[subwin]) >= 20:
            self.crc = settings.crcm
        x = x + ix
        y = y + ty2 * 0.7
        pgutils.draw_text(self.screen, self.rain[subwin], self.subrainF, self.crc, True, x, y)
        x = x + rtx
        y = y + rty / 2.3
        pgutils.draw_text(self.screen, "%", self.percF, self.crc, True, x, y)

        return self.xmin, self.subYPos, self.xmax, y + pty

    def display_hourly_forecasts(self, subwin):
        if settings.debug: print("DISP_HOURLY", time.strftime("%H:%M:%S"))

        subwinWidth = (self.xmax - self.xgap) / wconstants.hourly_number
        subwinCenter = self.xgap / 2 + subwinWidth * (subwin + 1) - subwinWidth / 2
        YPos = self.subYPos + self.ygap * 7.3
        y = YPos

        # Draw temp
        (tx, ty) = pgutils.draw_text(self.screen, self.hTemps[subwin] + " ", self.subHourlyTempF, blit=False)
        pgutils.draw_text(self.screen, self.hTemps[subwin], self.subHourlyTempF, fcolor=settings.wc, blit=True,
                          x=subwinCenter - tx / 2.5, y=y)

        # Draw icon
        y = y + ty
        if self.hIcons[subwin] != self.hIconPrev or subwin == 0:
            self.hIconPrev = self.hIcons[subwin]
            icon = pgutils.load_icon(self.hIcons[subwin], self.iconf)
            ix, iy = icon.get_size()
            subScale = 1.1
            if ix != iy:
                subScale = 1.0
            scaleX = int(subwinWidth * subScale * wconstants.ICON_SCALE.get(settings.iconSet, 1.0))
            scaleY = int(scaleX * (iy / ix))
            icon = pygame.transform.smoothscale(icon, (scaleX, scaleY))
            xGap = 1.9
            if ix != iy:
                xGap = 1.7
            self.screen.blit(icon, (subwinCenter - scaleX / xGap, y))

        # Draw hour
        y = y + ty + self.ygap * 1.5
        if subwin % 2 == 0:
            color = settings.wc
            if int(self.hHours[subwin][:2]) == 0:
                color = settings.clockc
            (rtx, rty) = pgutils.draw_text(self.screen, self.hHours[subwin], self.subHourlyHourF, blit=False)
            pgutils.draw_text(self.screen, self.hHours[subwin], self.subHourlyHourF, fcolor=color, blit=True,
                              x=subwinCenter - rtx / 2, y=y)

        return

    def update_news(self):
        if settings.debug: print("UPD_NEWS", time.strftime("%H:%M:%S"))

        nUpdated = False
        update_error = False

        # Get news from RSS source and parse them into string variable
        try:
            # requests module returns obsolete info (caching?) for rtve API
            with urllib.request.urlopen(self.nURL, timeout=settings.timeout) as response:
                n = response.read()
        except:
            update_error = True
            print("Error getting News from", self.nsource)
            print(traceback.format_exc())

        if not update_error:
            h = time.strftime('%H')
            m = time.strftime('%M')
            if m == "59":
                h = str("%02i" % ((int(h) + 1) % 24))
            m = str("%02i" % ((int(m) + 1) % 60))
            self.titles = self.nsource + " " + h + ":" + m + " " + settings.separator

            if self.nsource == wconstants.NEWS_1:
                nUpdated = self.parse_rtve(n)
            elif self.nsource == wconstants.NEWS_2:
                nUpdated = self.parse_bbc(n)
            else:
                print("ERROR: Unknown News source. Unable to access/parse it. Check settings!")

        if settings.alternSource:
            if self.nsource == wconstants.nsource2:
                self.nsource = wconstants.nsource1
                self.nURL = wconstants.nURL1 % settings.lang
            else:
                self.nsource = wconstants.nsource2
                self.nURL = wconstants.nURL2

        return nUpdated

    def parse_rtve(self, n):
        if settings.debug: print("PARSE_RTVE", time.strftime("%H:%M:%S"))

        n = ET.fromstring(n)

        nUpdated = False
        try:
            i = 0
            for item in n.findall('./page/items/com.irtve.plataforma.rest.model.dto.news.NewsDTO'):
                if i < wconstants.newsNumber:
                    self.titles += item.find('longTitle').text + settings.separator
                    if settings.showPics:
                        try:
                            self.pics[i] = pgutils.load_url_image(item.find('imageSEO').text, timeout=settings.timeout)
                        except:
                            self.pics[i] = None
                            print("Error getting pic", i + 1)
                            print(traceback.format_exc())
                    i += 1
                else:
                    break
            nUpdated = True

        except:
            print("Error parsing News from:", self.nsource)
            print(traceback.format_exc())

        return nUpdated

    def parse_bbc(self, n):
        if settings.debug: print("PARSE_BBC", time.strftime("%H:%M:%S"))

        n = ET.fromstring(n)

        nUpdated = False

        try:
            i = 0
            for item in n.findall('./channel/item'):
                if i < wconstants.newsNumber:
                    self.titles += item.find('title').text + settings.separator
                    i += 1
                else:
                    break
            nUpdated = True

        except:
            print("Error parsing News from:", self.nsource)
            print(traceback.format_exc())

        return nUpdated

    def show_news(self):
        if settings.debug: print("SNOW_NEWS", time.strftime("%H:%M:%S"))

        t = None
        rectPics = None
        (x, y, w, h) = (self.xmin, self.rectTime[1] + self.rectTime[3] - self.ymargin*2, self.xmax, self.nY*1.15)
        self.showingNews = True
        fps = 1.0 / float(settings.fps * (self.xmax / self.ymax))

        if settings.showPics and self.pics:
            # Show News Pics
            rectPics, img = self.display_news_pics(x, y, w, h)
            # Place News ticker under pics (lower side of screen)
            y = self.ymax - h - self.ygap

        else:
            # Save display area which will be overwritten by the News ticker
            img = pgutils.screenshot(self.screen, (x, y, w, h))

        if settings.newsMode == wconstants.NEWS_ALWAYSON:
            # News period will move forward due to weather update and other. Adjust to 5:02 minutes (avoid coinciding)
            i = int(time.strftime("%S")) - 2
        else:
            i = 1

        # Initialize News ticker
        ticker = pgutils.ScrollText(self.screen, self.titles, y, settings.nc, self.newsF, self.nX)

        # Show News ticker
        while i <= wconstants.nTime:
            s = int(time.strftime("%S"))
            rect = (x, y, w, h)

            if s != t:
                rectT = self.show_all()
                rectT.append(rect)
                rect = rectT
                t = s
                i += 1

            pygame.draw.rect(self.screen, settings.nBkg, (x, y, w, h))
            ticker.update(self.screen)
            pygame.display.update(rect)

            if self.event_loop() or self.showingMenu or self.showingConfig:
                self.changedWhileNews = True

            time.sleep(fps)

        self.showingNews = False

        # Display previously saved area on News, or the whole thing if screen changed or in alwaysON mode (for weather)
        if self.changedWhileNews or settings.newsMode == wconstants.NEWS_ALWAYSON or \
                (settings.showPics and (settings.clockMode or self.user_clockMode or self.onlyTime)):
            self.changedWhileNews = False
            self.bkgCodePrev = None
            self.show_all(displayAll=True)
        elif settings.showPics and rectPics:
            self.screen.blit(img, rectPics)
            pygame.display.update(rectPics)
        else:
            self.screen.blit(img, (x, y))
            pygame.display.update((x, y, w, h))

        return

    def display_news_pics(self, x, y, w, h):
        if settings.debug: print("DISP_PICS", time.strftime("%H:%M:%S"))

        # Prepare positions and sizes
        width = int(self.xmax / len(self.pics))
        rectPics = (x, (y + h), w, self.ymax - (y + h))

        # Save and erase display area which will be overwritten by the News ticker and pics
        img = pgutils.screenshot(self.screen, rectPics)
        pygame.draw.rect(self.screen, settings.cBkg, rectPics)

        # Draw News pics
        for i in range(len(self.pics)):
            try:
                if self.pics[i] is not None:
                    (ix, iy) = self.pics[i].get_size()
                    if (ix, iy) != (width, int(iy * (width / ix))):
                        pic = pygame.transform.smoothscale(self.pics[i], (width, int(iy * (width / ix))))
                    self.screen.blit(pic, (width * i, (y + h)))
            except:
                print("ERROR drawing News Image", i)
                print(traceback.format_exc())

        # Free memory used by pics
        self.pics = ["", "", "", "", ""]

        # Update display to draw pics
        pygame.display.update(rectPics)

        return rectPics, img

    def show_menu(self):
        if settings.debug: print("SHOW_MENU", time.strftime("%H:%M:%S"))

        self.showingMenu = True

        if not settings.use_current_location and not settings.clockMode:
            self.dist_limit = self.check_location()

        warn = ""
        if self.dist_limit != 0:
            warn = "(!) "

        self.menu = pygame_menu.Menu(
            width=self.xmax,
            height=self.ymax,
            title='Quick Options',
            theme=pygame_menu.themes.THEME_BLUE
        )

        padding = len(self.location)*3
        locations = []
        for i, loc in enumerate(settings.location):
            if loc[0] == self.location:
                locations.insert(0, (loc[0], i + 1))
            else:
                locations.append((loc[0], i + 1))
        nsources = []
        if self.nsource == wconstants.NEWS_1:
            nsources.append((wconstants.NEWS_1, 1))
            nsources.append((wconstants.NEWS_2, 2))
        else:
            nsources.append((wconstants.NEWS_2, 1))
            nsources.append((wconstants.NEWS_1, 2))

        font_size = int(self.ymax/30)
        font_size_small = int(self.ymax/40)
        pgm_ver_major = int(pygame_menu.__version__.split(".")[0])
        if pgm_ver_major >= 4:
            self.menu.add.button(self.sys_info(), self.sys_info, button_id="sys_info", font_size=font_size_small,
                                 align=pygame_menu.locals.ALIGN_LEFT) \
                                .update_font({"color": (255, 255, 255), "selected_color": (255, 255, 255)}) \
                                .set_background_color(pygame.Color("turquoise3")).set_margin(x=10, y=0) \
                                .set_onmouseover(self.on_mouse_over).set_onmouseleave(self.on_mouse_leave)
            self.menu.add.label('', font_size=font_size_small)
            self.menu.add.label('Select:' + ' ' * padding, font_size=font_size, font_color=pygame.Color("orange"))
            self.menu.add.selector(warn + 'Set Location: ', locations, onchange=self.set_location, font_size=font_size)
            self.menu.add.selector('Next News Source: ', nsources, onchange=self.set_news, font_size=font_size)
            self.menu.add.label('', font_size=font_size)
            self.menu.add.label('Actions:' + ' ' * padding, font_size=font_size, font_color=pygame.Color("orange"))
            self.menu.add.button('Activate News Now', self.activate_news, font_size=font_size)
            if settings.clockMode or self.user_clockMode:
                self.menu.add.button('Set Weather Mode', self.set_weather_mode, font_size=font_size)
            else:
                self.menu.add.button('Set Clock Only Mode', self.set_clock_only, font_size=font_size)
            self.menu.add.button(warn + 'Settings', self.start_config, font_size=font_size)
            self.menu.add.button('Back', self.menu_back, font_size=font_size)
            self.menu.add.button('Help', self.start_help, font_size=font_size)
            self.menu.add.button('Quit', pygame_menu.events.EXIT, font_size=font_size)
            if warn:
                self.menu.add.label("", font_size=font_size_small)
                self.menu.add.label("(!) Location might not be properly set or too far. Check 'Weather' settings", font_size=font_size_small)
        else:
            button = self.menu.add_button(self.sys_info(), self.sys_info, button_id="sys_info", font_size=font_size_small,
                                 align=pygame_menu.locals.ALIGN_LEFT)
            button.update_font({"color": (255, 255, 255), "selected_color": (255, 255, 255)})
            button.set_background_color((0, 197, 205))
            button.set_margin(x=10, y=0)
            self.menu.add_label('', font_size=font_size_small)
            self.menu.add_label('Select:' + ' ' * padding, font_size=font_size, font_color=(255, 165, 0))
            self.menu.add_selector(warn + 'Set Location: ', locations, onchange=self.set_location, font_size=font_size)
            self.menu.add_selector('News Source to activate: ', nsources, onchange=self.set_news, font_size=font_size)
            self.menu.add_label('', font_size=font_size)
            self.menu.add_label('Actions:' + ' ' * padding, font_size=font_size, font_color=(255, 165, 0))
            self.menu.add_button('Activate News Now', self.activate_news, font_size=font_size)
            if settings.clockMode or self.user_clockMode:
                self.menu.add_button('Set Weather Mode', self.set_weather_mode, font_size=font_size)
            else:
                self.menu.add_button('Set Clock Only Mode', self.set_clock_only, font_size=font_size)
            self.menu.add_button(warn + 'Settings', self.start_config, font_size=font_size)
            self.menu.add_button('Back', self.menu_back, font_size=font_size)
            self.menu.add_button('Help', self.start_help, font_size=font_size)
            self.menu.add_button('Quit', pygame_menu.events.EXIT, font_size=font_size)
            if warn:
                self.menu.add_label("", font_size=font_size_small)
                self.menu.add_label("(!) Location might not be properly set or too far. Check 'Weather' settings", font_size=font_size_small)

        self.menu.mainloop(self.screen)

    def menu_back(self):
        if settings.debug: print("MENU_BACK", time.strftime("%H:%M:%S"))
        self.showingMenu = False
        self.menu.disable()
        self.menu.full_reset()
        self.menu = None
        self.bkgCodePrev = None
        self.show_all(displayAll=True, updateWeather=self.updateWeather)
        self.updateWeather = False

    def sys_info(self):
        sys_info = "CPU Usage / Temp: " + utils.get_CPU_usage(self.archOS) + " - " + utils.get_CPU_temp(self.archOS)
        widget = self.menu.get_widget("sys_info")
        if widget is not None:
            widget.set_title(sys_info)
        return sys_info

    def on_mouse_over(self):
        widget = self.menu.get_widget("sys_info")
        if widget is not None:
            widget.set_background_color((255, 165, 0))

    def on_mouse_leave(self):
        widget = self.menu.get_widget("sys_info")
        if widget is not None:
            widget.set_background_color((0, 197, 205))

    def set_location(self, selected: Tuple, value: Any):
        if settings.debug: print("SET_LOC", time.strftime("%H:%M:%S"))
        self.user_clockMode = False
        self.location = settings.location[int(value) - 1][0]
        self.zip_code = settings.location[int(value) - 1][1]
        self.wLastUpdate = ""
        self.bkgCodePrev = None
        self.updateWeather = True

    def set_news(self, selected: Tuple, value: Any):
        if settings.debug: print("SET_NEWS", time.strftime("%H:%M:%S"))
        value = int(value)
        if value == 1:
            self.nsource = wconstants.nsource1
            self.nURL = wconstants.nURL1
        elif value == 2:
            self.nsource = wconstants.nsource2
            self.nURL = wconstants.nURL2

    def activate_news(self):
        if settings.debug: print("ACTIVATE_NEWS", time.strftime("%H:%M:%S"))
        self.menu_back()
        self.update_news()
        if self.titles: self.show_news()

    def set_weather_mode(self):
        self.user_clockMode = False
        self.wLastUpdate = ""
        self.updateWeather = True
        self.menu_back()

    def set_clock_only(self):
        self.user_clockMode = True
        self.bkgCode = wconstants.DEFAULT_BKG
        self.menu_back()

    def start_config(self):
        if settings.debug: print("START_CONFIG", time.strftime("%H:%M:%S"))
        self.show_config()
        self.menu_back()

    def show_config(self):
        self.showingConfig = True
        if self.WC is None:
            app = wconfig.WeatherConfig()
            self.WC = threading.Thread(target=app.run)
        self.WC.start()

    def config_back(self):
        self.showingConfig = False
        self.WC.join()
        if self.fullscreen:
            x = y = None
        else:
            x, y, _, _ = utils.get_screen_pos(wconstants.SYSTEM_CAPTION)
            x += self.border_width
            if "Windows" in self.archOS:
                y += self.titlebar_height
            else:
                y -= self.titlebar_height
        importlib.reload(settings)
        pygame.display.quit()
        self.__init__(pos=(x, y))

    def start_help(self):

        if self.help is None:
            with open(utils.resource_path(wconstants.HELP_FILE), encoding='utf-8') as file:
                self.help = json.load(file)

        if self.menu2 is None:

            self.menu2 = pygame_menu.Menu(
                width=self.xmax,
                height=self.ymax,
                title='Help',
                theme=pygame_menu.themes.THEME_DARK
            )

            size = int(self.ymax/45)
            pgm_ver_major = int(pygame_menu.__version__.split(".")[0])
            if pgm_ver_major >= 4:
                for key in self.help.keys():
                    self.menu2.add.label(self.help[key], font_size=size, align=pygame_menu.locals.ALIGN_LEFT)
                self.menu2.add.button("Back", self.help_back)
            else:
                for key in self.help.keys():
                    self.menu2.add_label(self.help[key], font_size=size, align=pygame_menu.locals.ALIGN_LEFT)
                self.menu2.add_button("Back", self.help_back)

        if self.menu: self.menu.disable()
        self.menu2.enable()
        self.menu2.mainloop(self.screen)

    def help_back(self):
        self.menu2.disable()
        self.menu2.full_reset()
        if self.menu:
            self.menu.enable()
        else:
            self.wLastUpdate = ""
            self.bkgCodePrev = None
            self.show_all(displayAll=True, updateWeather=True)

    def event_loop(self):
        if settings.debug: print("EVENT_LOOP", time.strftime("%H:%M:%S"))

        displayChanged = False

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                # On windowed mode, exit when clicking the "x" (close window)
                pygame.display.quit()
                pygame.quit()
                sys.exit()

            elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
                left, mid, right = pygame.mouse.get_pressed()
                if right and not self.showingMenu:
                    self.show_menu()
                    displayChanged = True

            elif event.type == pygame.KEYUP:

                if event.key in (pygame.K_q, pygame.K_ESCAPE):
                    # On 'q' or Escape pressed, quit the program.
                    pygame.display.quit()
                    pygame.quit()
                    sys.exit()

                elif event.key is not None and event.key != 0 and event.key != self.keyP:
                    self.keyP = event.key

                    if "1" <= pygame.key.name(event.key) <= str(len(settings.location)) and not settings.clockMode:
                        # Change Weather Location (assigned to numbers) and show Weather
                        self.user_clockMode = False
                        self.location = settings.location[int(pygame.key.name(event.key)) - 1][0]
                        self.zip_code = settings.location[int(pygame.key.name(event.key)) - 1][1]
                        self.wLastUpdate = ""
                        self.bkgCodePrev = None
                        self.show_all(displayAll=True, updateWeather=True)
                        displayChanged = True

                    elif event.key == pygame.K_c and not settings.clockMode:
                        # World Clocks Mode (no weather)
                        self.user_clockMode = True
                        self.bkgCode = wconstants.DEFAULT_BKG
                        self.show_all(displayAll=True)
                        displayChanged = True

                    elif event.key == pygame.K_w and self.user_clockMode and not settings.clockMode:
                        # Back to Weather mode
                        self.user_clockMode = False
                        self.wLastUpdate = ""
                        self.show_all(displayAll=True, updateWeather=True)
                        displayChanged = True

                    elif event.key in (pygame.K_a, pygame.K_b) and not settings.clockMode:
                        # Select first (A) or second (B) News source and force update/showing News
                        if event.key == pygame.K_a:
                            self.nsource = wconstants.nsource1
                            self.nURL = wconstants.nURL1
                        elif event.key == pygame.K_b:
                            self.nsource = wconstants.nsource2
                            self.nURL = wconstants.nURL2
                        self.update_news()
                        if self.titles: self.show_news()
                        displayChanged = True

                    elif event.key == pygame.K_s and not self.showingConfig:
                        self.keyP = ""
                        self.show_config()
                        displayChanged = True

                    elif event.key == pygame.K_m and not self.showingMenu:
                        self.keyP = ""
                        self.show_menu()
                        displayChanged = True

                    elif event.key == pygame.K_h and not self.showingMenu:
                        self.keyP = ""
                        self.start_help()
                        displayChanged = True

            elif (pygame.version.vernum >= (2, 0) and event.type == pygame.WINDOWMINIMIZED) or \
                 (pygame.version.vernum < (2, 0) and event.type == pygame.ACTIVEEVENT and event.gain == 0 and event.state == 6):
                self.prevMinimized = True
                displayChanged = True

            elif (pygame.version.vernum >= (2, 0) and event.type == pygame.WINDOWRESTORED and self.prevMinimized) or \
                 (pygame.version.vernum < (2, 0) and event.type == pygame.ACTIVEEVENT and event.gain == 1 and event.state == 4 and self.prevMinimized):
                # Screen needs to be fully refreshed when restoring after minimizing
                self.prevMinimized = False
                self.show_all(displayAll=True, forceShowWeather=True, updateWeather=False)
                displayChanged = True

        return displayChanged


def main():
    WS = MyWeatherStation()

    while True:

        WS.show_all()

        if not WS.event_loop():
            time.sleep(1 - time.time() % 1)


if __name__ == "__main__":
    main()
