#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import datetime
import pytz


def get_world_clock_offsets(timeZones):
    # timeZone parameter must be a list of tuples: [("TimeZone", "city name")]

    # Prepare time
    utc = pytz.utc
    utc_dt = datetime.datetime.utcfromtimestamp(time.time()).replace(tzinfo=utc)
    localH = int(time.strftime("%H"))
    localM = int(time.strftime("%M"))

    # Get World Clocks offset from local TimeZone
    tzOffset = []
    for i in range(len(timeZones)):
        try:
            tz_tz = pytz.timezone(timeZones[i][0])
            tz_dt = tz_tz.normalize(utc_dt.astimezone(tz_tz))
            tzH = int(tz_dt.strftime("%H"))
            hOffset = tzH - localH
            tzM = int(tz_dt.strftime("%M"))
            mOffset = tzM - localM
        except Exception as e:
            print("Error getting Time Zones offset. Check settings.timeZones values. Invalid timezone:", timeZones[i])
            print(e)
            hOffset = mOffset = 0
        city = timeZones[i][1]
        tzOffset.append((city, hOffset, mOffset))

    # Return current time zone and list of ["city name", "TZ Hours offset", "TZ minutes offset"]
    return tzOffset


def get_local_tz():

    localTZ = datetime.timezone(datetime.timedelta(seconds=-time.timezone))
    is_dst = time.daylight and time.localtime().tm_isdst
    return localTZ, is_dst


def add_utc_offset(init_time):

    is_dst = time.daylight and time.localtime().tm_isdst > 0
    utc_offset = int(-(time.altzone if is_dst else time.timezone) / 3600)
    if ":" in init_time:
        sep_time = init_time.split(":")
        sep_time[0] = str("%02i" % ((int(sep_time[0]) + utc_offset) % 24))
        final_time = ':'.join(x for x in sep_time)
    else:
        final_time = str("%02i" % ((int(init_time[:2]) + utc_offset) % 24)) + init_time[2:]

    return final_time, utc_offset
