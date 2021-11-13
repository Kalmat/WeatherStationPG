#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import datetime
import math
import decimal


def convert_weather_code(code):
    # https://openweathermap.org/weather-conditions#Weather-Condition-Codes-2

    conv_icons = {"200": "0", "201": "0", "202": "0", "210": "0", "211": "0", "212": "0", "221": "37", "230": "0", "231": "0", "232": "0",
                  "300": "13", "301": "14", "302": "16", "310": "7", "311": "6", "312": "5", "313": "41", "314": "41", "321": "41",
                  "500": "9", "501": "11", "502": "12", "503": "12", "504": "40", "511": "10", "520": "39", "521": "39", "522": "39", "531": "39",
                  "600": "13", "601": "14", "602": "16", "611": "18", "612": "8", "613": "10", "615": "6", "616": "5", "620": "41", "621": "41", "622": "41",
                  "701": "20", "711": "21", "721": "22", "731": "19", "741": "20", "751": "19", "761": "21", "762": "22", "771": "23", "781": "23",
                  "800": "32", "801": "34", "802": "30", "803": "28", "804": "26",
                  "900": "na"}

    return conv_icons[code]


def convert_icon_code(icon):
    # https://www.weatherbit.io/api/codes

    conv_icons = {"a01d": "20", "a01n": "20", "a02d": "22", "a02n": "22", "a03d": "21", "a03n": "21", "a04d": "19",
                  "a04n": "19", "a05d": "20", "a05n": "20", "a06d": "25", "a06n": "25", "c01d": "32", "c01n": "33",
                  "c02d": "34", "c02n": "31", "c03d": "30", "c03n": "29", "c04d": "26", "c04n": "26", "d01d": "9",
                  "d01n": "9", "d02d": "9", "d02n": "9", "d03d": "11", "d03n": "11", "f01d": "8", "f01n": "8",
                  "r01d": "9", "r01n": "9", "r02d": "11", "r02n": "11", "r03d": "12", "r03n": "12", "r04d": "39",
                  "r04n": "45", "r05d": "39", "r05n": "45", "r06d": "39", "r06n": "45", "s01d": "13", "s01n": "13",
                  "s02d": "16", "s02n": "16", "s03d": "18", "s03n": "18", "s04d": "5", "s04n": "5", "s05d": "6",
                  "s06d": "15", "s06n": "15", "t01d": "37", "t01n": "47", "t02d": "0", "t02n": "0", "t03d": "3",
                  "t03n": "3", "t04d": "4", "t04n": "4", "t05d": "17", "t05n": "17", "u00d": "na", "u00n": "na"}

    return conv_icons[icon]


def get_night_icons(key):
    # Corresponding weather icons at night time
    nightIcons = {"28": "27", "30": "29", "32": "33", "34": "31", "36": "33", "37": "47", "38": "47", "39": "45", "41": "46"}
    return nightIcons.get(key, key)


def getNightBkg(key):
    # Night time backgrounds
    nightBkg = {"01": "31", "02": "33", "03": "29", "04": "27", "09": "2", "10": "45", "11": "0", "13": "46", "50": "20"}
    return nightBkg.get(key, key)


def getMoonWIcons(key):
    # Corresponding weather icons when showing Moon Phases instead of current conditions icon "onCURRENT" mode
    moonWIcons = {"27": "26", "29": "20", "31": "20", "33": None, "45": "12", "46": "16", "47": "3", "28": "26", "30": "20", "32": None, "34": "20", "36": None, "37": "35", "39": "12", "41": "16", "44": "20"}
    return moonWIcons.get(key, None)


def get_moon_position(now=None):
    """
    Author: Sean B. Palmer, inamidst.com
    Cf. http://en.wikipedia.org/wiki/Lunar_phase#Lunar_phase_calculation
    """

    dec = decimal.Decimal
    if now is None:
        now = datetime.datetime.now()
    diff = now - datetime.datetime(2001, 1, 1)
    days = dec(diff.days) + (dec(diff.seconds) / dec(86400))
    lunations = dec("0.20439731") + (days * dec("0.03386319269"))

    return lunations % dec(1)


def get_moon_phase(pos=None):
    """
    Author: Sean B. Palmer, inamidst.com
    Cf. http://en.wikipedia.org/wiki/Lunar_phase#Lunar_phase_calculation
    """

    dec = decimal.Decimal
    if pos is None:
        pos = get_moon_position()
    index = (pos * dec(8)) + dec("0.5")
    index = math.floor(index)
    return {
      0: "New",
      1: "Waxing Crescent",
      2: "First Quarter",
      3: "Waxing Gibbous",
      4: "Full",
      5: "Waning Gibbous",
      6: "Last Quarter",
      7: "Waning Crescent"
    }[int(index) & 7]


def convert_moon_phase(moon_phase):

    if moon_phase == 0: return "New"
    elif 0 < moon_phase < 0.125: return "New Waxing"
    elif 0.125 <= moon_phase < 0.25: return "Waxing Crescent"
    elif moon_phase == 0.25: return "First Quarter"
    elif 0.25 < moon_phase < 0.5: return "Waxing Gibbous"
    elif moon_phase == 0.5: return "Full"
    elif 0.5 < moon_phase < 0.75: return "Waning Gibbous"
    elif moon_phase == 0.75: return "Last Quarter"
    elif 0.75 < moon_phase <= 0.875: return "Waning Crescent"
    elif 0.875 < moon_phase <= 1: return "New Waning"


def get_constellation():
    # Constellations
    ZD = [119, 218, 320, 419, 520, 620, 722, 822, 922, 1022, 1121, 1221, 1231]
    ZN = ['Capricorn', 'Aquarius', 'Pisces', 'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpius',
          'Sagittarius', 'Capricorn']

    sunsign = ""

    mdd = int(time.strftime("%m%d"))

    for i in range(len(ZD)):
        if mdd <= ZD[i]:
            sunsign = ZN[i]
            break

    return sunsign


def convert_win_direction(code, lang):
    value = int((code / 22.5) + 0.5)

    direction = {
        "Default": ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"],
        "Alternative": ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSO", "SO", "OSO", "O", "ONO", "NO", "NNO"]
    }

    return direction[lang][(value % 16)]
