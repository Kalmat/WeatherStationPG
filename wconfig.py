#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import tkinter as tk
from tkinter import ttk
import urllib.parse
import json
import utils
import wconstants

settings_file = wconstants.SETTINGS_FILE
default_settings_file = utils.resource_path(wconstants.DEFAULT_SETTINGS_FILE)


def read_settings_file(fallback=True):

    config = None
    try:
        with open(settings_file, encoding='UTF-8', errors='ignore') as file:
            config = json.load(file)
    except:
        if fallback:
            config = reset_settings_file()

    return config


def reset_settings_file():

    with open(default_settings_file, encoding='UTF-8', errors='ignore') as file:
        config = json.load(file)

    write_settings_file(config)

    return config


def write_settings_file(config):

    with open(settings_file, "w", encoding='UTF-8') as file:
        json.dump(config, file, ensure_ascii=False, sort_keys=False, indent=4)

    return


class WeatherConfig:

    def __init__(self):
        self.root = None
        self.config = None

    def __del__(self):
        """ Destructor to make sure resources are released """

    def terminate(self):
        self.root.destroy()

    def apply(self):

        self.set_general()
        self.set_appearance()
        self.set_texts()
        self.set_colors()
        self.set_background()
        self.set_Weather()
        self.set_News()
        self.set_WorldClocks()

        write_settings_file(self.config)

        self.terminate()

    def run(self):

        self.config = read_settings_file()

        self.padx = (0, 0)
        self.gapx = (30, 0)
        self.pady = (5, 0)

        self.root = tk.Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.terminate)
        self.root.geometry('+%d+%d' % (self.root.winfo_screenwidth() / 3, 10))
        self.root.title("Weather & News Settings")
        if sys.platform.startswith('win'):
            icon = utils.resource_path(wconstants.SETTINGS_ICON)
            self.root.iconbitmap(icon)
        # Not working on Linux yet (though converted to .xbm or .xpm)
        # else:
        #     icon = utils.resource_path(wconstants.SETTINGS_ICON_LINUX)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(padx=5)

        apply = tk.Button(self.root, text="Apply", command=self.apply)
        apply.pack(side=tk.RIGHT, padx=20, pady=(5, 5))
        cancel = tk.Button(self.root, text="Cancel", command=self.terminate)
        cancel.pack(side=tk.RIGHT, padx=0, pady=(5, 5))

        self.general_tab = ttk.Frame(self.notebook)
        self.appearance_tab = ttk.Frame(self.notebook)
        self.texts_tab = ttk.Frame(self.notebook)
        self.colors_tab = ttk.Frame(self.notebook)
        self.background_tab = ttk.Frame(self.notebook)
        self.weather_tab = ttk.Frame(self.notebook)
        self.news_tab = ttk.Frame(self.notebook)
        self.clocks_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.general_tab, text="General", padding=5)
        self.notebook.add(self.appearance_tab, text="Appearance", padding=5)
        self.notebook.add(self.texts_tab, text="Translation", padding=5)
        self.notebook.add(self.colors_tab, text="Colors", padding=5)
        self.notebook.add(self.background_tab, text="Background", padding=5)
        self.notebook.add(self.weather_tab, text="Weather", padding=5)
        self.notebook.add(self.news_tab, text="News", padding=5)
        self.notebook.add(self.clocks_tab, text="Clocks", padding=5)

        self.get_general(self.general_tab)
        self.get_appearance(self.appearance_tab)
        self.get_texts(self.texts_tab)
        self.get_colors(self.colors_tab)
        self.get_background(self.background_tab)
        self.get_Weather(self.weather_tab)
        self.get_News(self.news_tab)
        self.get_WorldClocks(self.clocks_tab)

        self.root.mainloop()

    def get_general(self, tab):

        section = "General"

        label = tk.Label(tab, text="Size (X, Y):")
        label.grid(row=0, column=0, sticky=tk.NW, padx=self.padx, pady=self.pady)
        self.xsize = tk.Entry(tab, width=4)
        self.xsize.insert(0, str(self.config[section]["Resolution"][0]))
        self.xsize.grid(row=0, column=1, sticky=tk.NW, padx=self.padx, pady=self.pady)
        sep = tk.Label(tab, text=",")
        sep.grid(row=0, column=2, sticky=tk.NW)
        self.ysize = tk.Entry(tab, width=4)
        self.ysize.insert(0, str(self.config[section]["Resolution"][1]))
        self.ysize.grid(row=0, column=3, sticky=tk.NW, padx=self.padx, pady=self.pady)

        label = tk.Label(tab, text="Language:")
        label.grid(row=1, column=0, sticky=tk.NW, padx=self.padx, pady=self.pady)
        self.lan = tk.Listbox(tab, width=10, exportselection=False)
        for i, key in enumerate(self.config[section]["Available_Languages"]):
            self.lan.insert(tk.END, self.config[section]["Available_Languages"][key])
            if key == self.config[section]["Language"]:
                self.lan.activate(i)
                self.lan.selection_set(i)
        self.lan.config(height=0)
        self.lan.grid(row=1, column=1, rowspan=2, columnspan=3, sticky=tk.NW, padx=self.padx, pady=self.pady)

        label = tk.Label(tab, text="Units:")
        label.grid(row=3, column=0, sticky=tk.NW, padx=self.padx, pady=self.pady)
        self.uni = tk.Listbox(tab, width=10, exportselection=False)
        for i, key in enumerate(self.config[section]["Available_Units"]):
            self.uni.insert(tk.END, key)
            if key == self.config[section]["Units"]:
                self.uni.activate(i)
                self.uni.selection_set(i)
        self.uni.config(height=0)
        self.uni.grid(row=3, column=1, rowspan=2, columnspan=3, sticky=tk.NW, padx=self.padx, pady=self.pady)

        label = tk.Label(tab, text="Your IP location (might not be accurate): ")
        label.grid(row=6, column=0, columnspan=5, sticky=tk.NW, padx=self.padx, pady=self.pady)

        cLocation = utils.get_location_by_ip(wconstants.gIPURL % self.config["General"]["Language"])
        if cLocation:
            currloc = (cLocation[0] + (", " + cLocation[1] if cLocation[1] else "") +
                       (", " + cLocation[2] if cLocation[2] else ""))
            self.lat = cLocation[3]
            self.lon = cLocation[4]
            self.currSuccess = True
        else:
            currloc = "(Not found)"
            self.lat = "0"
            self.lon = "0"
            self.currSuccess = False
        self.loc = tk.Entry(tab, width=30)
        self.loc.insert(0, currloc)
        self.loc.config(state="readonly")
        self.loc.grid(row=6, column=6, sticky=tk.NW, padx=self.padx, pady=self.pady)

        label = tk.Label(tab, text="Default Weather location (stored on settings): ")
        label.grid(row=7, column=0, columnspan=5, sticky=tk.NW, padx=self.padx, pady=self.pady)

        defloc = tk.Entry(tab, width=30)
        currloc = self.config["Weather"]["Locations"][0][0]
        defloc.insert(0, currloc)
        defloc.config(state="readonly")
        defloc.grid(row=7, column=6, sticky=tk.NW, padx=self.padx, pady=self.pady)

        if not self.config["Weather"]["Use_current"] == "True" and self.currSuccess:
            loc1 = (float(self.lat), float(self.lon))
            loc2 = (float(self.config["Weather"]["Locations"][0][1].split("lat=")[1].split("&")[0]), float(self.config["Weather"]["Locations"][0][1].split("&lon=")[1]))
            dist = utils.get_distance(loc1, loc2, self.config[section]["Units"])
            if dist > int(wconstants.distLimit[wconstants.AVAIL_UNITS[self.config["General"]["Units"]]]):
                label = tk.Label(tab, text=("(!) WARNING. Weather data might be wrong since Current and Default locations are far ("
                                            + str(dist) + (" miles)" if self.config["General"]["Units"] == wconstants.IMPERIAL else " Km)")))
                label.grid(row=8, column=0, columnspan=7, sticky=tk.NW, padx=self.padx, pady=(4, 0))
                label = tk.Label(tab, text="Access 'Weather' tab to use Current location or store a new Default one of your choice in settings")
                label.grid(row=9, column=0, columnspan=7, sticky=tk.NW, padx=self.padx, pady=(0, 0))

        self.reset = tk.Button(tab, text="Reset Settings", command=(lambda:self.reset_settings(tab)))
        self.reset.grid(row=12, column=0, sticky=tk.NW, padx=self.padx, pady=(40, 0))

    def reset_settings(self, tab):

        self.reset.config(state=tk.DISABLED)

        self.reset_label = tk.Label(tab, text="WARNING! This action can not be undone. Please confirm:")
        self.reset_label.grid(row=13, column=0, columnspan=7, sticky=tk.NW, padx=self.padx, pady=self.pady)

        self.reset_cancel = tk.Button(tab, text="Cancel", command=self.reset_cancel)
        self.reset_cancel.grid(row=14, column=0, sticky=tk.NW, padx=self.padx, pady=self.pady)

        self.reset_confirm = tk.Button(tab, text="Confirm", command=self.reset_confirm)
        self.reset_confirm.grid(row=14, column=1, sticky=tk.NW, padx=self.padx, pady=self.pady)

    def reset_cancel(self):

        self.reset_label.grid_remove()
        self.reset_cancel.grid_remove()
        self.reset_confirm.grid_remove()
        self.reset.config(state=tk.NORMAL)

    def reset_confirm(self):

        self.config = reset_settings_file()
        self.terminate()
        self.run()

    def set_general(self):

        section = "General"

        self.config[section]["Resolution"] = [int(self.xsize.get()), int(self.ysize.get())]
        if self.lan.get(tk.ACTIVE) == self.config[section]["Available_Languages"]["Default"]:
            self.config[section]["Language"] = "Default"
        else:
            self.config[section]["Language"] = "Alternative"
        self.config[section]["Units"] = self.uni.get(tk.ACTIVE)

    def get_appearance(self, tab):

        section = "Appearance"

        self.clock = tk.StringVar(master=self.root, value=self.config[section]["Clock_mode"])
        clock = tk.Checkbutton(tab, text='Only Clock', variable=self.clock, onvalue="True", offvalue="False")
        clock.grid(row=0, column=0, sticky=tk.NW, padx=self.padx, pady=self.pady)

        self.bkg = tk.StringVar(master=self.root, value=self.config[section]["Show_background"])
        bkg = tk.Checkbutton(tab, text='Show Background', variable=self.bkg, onvalue="True", offvalue="False")
        bkg.grid(row=1, column=0, sticky=tk.NW, padx=self.padx, pady=self.pady)

        label = tk.Label(tab, text="Background Mode:")
        label.grid(row=2, column=0, sticky=tk.NW, padx=self.padx, pady=self.pady)
        self.bkgmode = tk.Listbox(tab, width=10, exportselection=False)
        for i, key in enumerate(self.config[section]["Available_Background_modes"]):
            self.bkgmode.insert(tk.END, key)
            if key == self.config[section]["Background_mode"]:
                self.bkgmode.activate(i)
                self.bkgmode.selection_set(i)
        self.bkgmode.config(height=0)
        self.bkgmode.grid(row=2, column=1, sticky=tk.NW, rowspan=2, columnspan=3, padx=self.padx, pady=self.pady)

        label = tk.Label(tab, text="Icon Set:")
        label.grid(row=4, column=0, sticky=tk.NW, padx=self.padx, pady=self.pady)
        self.icon = tk.Listbox(tab, width=20, exportselection=False)
        for i, key in enumerate(self.config[section]["Available_Icon_set"]):
            self.icon.insert(tk.END, key)
            if key == self.config[section]["Icon_set"]:
                self.icon.activate(i)
                self.icon.selection_set(i)
        self.icon.config(height=0)
        self.icon.grid(row=4, column=1, sticky=tk.NW, rowspan=4, columnspan=3, padx=self.padx, pady=self.pady)

        label = tk.Label(tab, text="Moon Icon position:")
        label.grid(row=8, column=0, sticky=tk.NW, padx=self.padx, pady=self.pady)
        self.moon = tk.Listbox(tab, width=20, exportselection=False)
        for i, key in enumerate(self.config[section]["Available_Moon_position"]):
            self.moon.insert(tk.END, key)
            if key == self.config[section]["Moon_position"]:
                self.moon.activate(i)
                self.moon.selection_set(i)
        self.moon.config(height=0)
        self.moon.grid(row=8, column=1, sticky=tk.NW, rowspan=4, columnspan=3, padx=self.padx, pady=self.pady)

        self.sun = tk.StringVar(master=self.root, value=self.config[section]["Show_Constellations"])
        sun = tk.Checkbutton(tab, text='Show Constellations', variable=self.sun, onvalue="True", offvalue="False")
        sun.grid(row=12, column=0, sticky=tk.NW, padx=self.padx, pady=self.pady)

        label = tk.Label(tab, text="News Mode:")
        label.grid(row=13, column=0, sticky=tk.NW, padx=self.padx, pady=self.pady)
        self.news = tk.Listbox(tab, width=15, exportselection=False)
        for i, key in enumerate(self.config[section]["Available_News_mode"]):
            self.news.insert(tk.END, key)
            if key == self.config[section]["News_mode"]:
                self.news.activate(i)
                self.news.selection_set(i)
        self.news.config(height=0)
        self.news.grid(row=13, column=1, sticky=tk.NW, rowspan=4, columnspan=3, padx=self.padx, pady=self.pady)

    def set_appearance(self):

        section = "Appearance"

        self.config[section]["Clock_mode"] = self.clock.get()
        self.config[section]["Show_background"] = self.bkg.get()
        self.config[section]["Background_mode"] = self.bkgmode.get(tk.ACTIVE)
        self.config[section]["Icon_set"] = self.icon.get(tk.ACTIVE)
        self.config[section]["Weather_source"] = self.config[section]["Available_Weather_source"][0]
        self.config[section]["Moon_position"] = self.moon.get(tk.ACTIVE)
        self.config[section]["Show_Constellations"] = self.sun.get()
        self.config[section]["News_mode"] = self.news.get(tk.ACTIVE)

    def get_texts(self, tab):

        section = "Texts"
        subdef = "Default"
        subalt = "Alternative"

        for i in range(3):
            label = tk.Label(tab, text=self.config[section]["Comment"+str(i + 1)])
            label.grid(row=i, column=0, columnspan=10, sticky=tk.NW, padx=self.padx, pady=(0, 0))

        langdesc = tk.Entry(tab, width=15)
        langdesc.insert(0, str(self.config["General"]["Available_Languages"][subdef]))
        langdesc.config(state="readonly")
        langdesc.grid(row=3, column=0, columnspan=2, sticky=tk.NW, padx=self.padx, pady=self.pady)

        code = tk.Entry(tab, width=2)
        code.insert(0, str(self.config[section][subdef]["Code"]))
        code.config(state="readonly")
        code.grid(row=3, column=2, sticky=tk.NW, padx=self.padx, pady=self.pady)

        label = tk.Label(tab, text="/")
        label.grid(row=3, column=3, sticky=tk.NW, padx=(0, 0), pady=self.pady)
        locale = tk.Entry(tab, width=12)
        locale.insert(0, str(self.config[section][subdef]["Locale"]))
        locale.config(state="readonly")
        locale.grid(row=3, column=4, sticky=tk.NW, padx=self.padx, pady=self.pady)

        self.langdesc = tk.Entry(tab, width=15)
        self.langdesc.insert(0, str(self.config["General"]["Available_Languages"][subalt]))
        self.langdesc.focus_set()
        self.langdesc.grid(row=3, column=5, columnspan=2, sticky=tk.NW, padx=(0, 0), pady=self.pady)

        self.langcode = tk.Entry(tab, width=2)
        self.langcode.insert(0, str(self.config[section][subalt]["Code"]))
        self.langcode.grid(row=3, column=7, sticky=tk.NW, padx=self.padx, pady=self.pady)

        label = tk.Label(tab, text="/")
        label.grid(row=3, column=8, sticky=tk.NW, padx=(0, 0), pady=self.pady)
        self.locale = tk.Entry(tab, width=12)
        self.locale.insert(0, str(self.config[section][subalt]["Locale"]))
        self.locale.grid(row=3, column=9, sticky=tk.NW, padx=self.padx, pady=self.pady)

        t100 = tk.Entry(tab, width=25)
        t100.insert(0, str(self.config[section][subdef]["100"]))
        t100.config(state="readonly")
        t100.grid(row=4, column=2, columnspan=3, sticky=tk.NW, padx=self.padx, pady=self.pady)
        self.t100 = tk.Entry(tab, width=25)
        self.t100.insert(0, str(self.config[section][subalt]["100"]))
        self.t100.grid(row=4, column=7, columnspan=3, sticky=tk.NW, padx=self.padx, pady=self.pady)

        t101 = tk.Entry(tab, width=25)
        t101.insert(0, str(self.config[section][subdef]["101"]))
        t101.config(state="readonly")
        t101.grid(row=5, column=2, columnspan=3, sticky=tk.NW, padx=self.padx, pady=self.pady)
        self.t101 = tk.Entry(tab, width=25)
        self.t101.insert(0, str(self.config[section][subalt]["101"]))
        self.t101.grid(row=5, column=7, columnspan=3, sticky=tk.NW, padx=self.padx, pady=self.pady)

        t102 = tk.Entry(tab, width=25)
        t102.insert(0, str(self.config[section][subdef]["102"]))
        t102.config(state="readonly")
        t102.grid(row=6, column=2, columnspan=3, sticky=tk.NW, padx=self.padx, pady=self.pady)
        self.t102 = tk.Entry(tab, width=25)
        self.t102.insert(0, str(self.config[section][subalt]["102"]))
        self.t102.grid(row=6, column=7, columnspan=3, sticky=tk.NW, padx=self.padx, pady=self.pady)

        t103 = tk.Entry(tab, width=25)
        t103.insert(0, str(self.config[section][subdef]["103"]))
        t103.config(state="readonly")
        t103.grid(row=7, column=2, columnspan=3, sticky=tk.NW, padx=self.padx, pady=self.pady)
        self.t103 = tk.Entry(tab, width=25)
        self.t103.insert(0, str(self.config[section][subalt]["103"]))
        self.t103.grid(row=7, column=7, columnspan=3, sticky=tk.NW, padx=self.padx, pady=self.pady)

        t104 = tk.Entry(tab, width=25)
        t104.insert(0, str(self.config[section][subdef]["104"]))
        t104.config(state="readonly")
        t104.grid(row=8, column=2, columnspan=3, sticky=tk.NW, padx=self.padx, pady=self.pady)
        self.t104 = tk.Entry(tab, width=25)
        self.t104.insert(0, str(self.config[section][subalt]["104"]))
        self.t104.grid(row=8, column=7, columnspan=3, sticky=tk.NW, padx=self.padx, pady=self.pady)

        t105 = tk.Entry(tab, width=25)
        t105.insert(0, str(self.config[section][subdef]["105"]))
        t105.config(state="readonly")
        t105.grid(row=9, column=2, columnspan=3, sticky=tk.NW, padx=self.padx, pady=self.pady)
        self.t105 = tk.Entry(tab, width=25)
        self.t105.insert(0, str(self.config[section][subalt]["105"]))
        self.t105.grid(row=9, column=7, columnspan=3, sticky=tk.NW, padx=self.padx, pady=self.pady)

        t106 = tk.Entry(tab, width=25)
        t106.insert(0, str(self.config[section][subdef]["106"]))
        t106.config(state="readonly")
        t106.grid(row=10, column=2, columnspan=3, sticky=tk.NW, padx=self.padx, pady=self.pady)
        self.t106 = tk.Entry(tab, width=25)
        self.t106.insert(0, str(self.config[section][subalt]["106"]))
        self.t106.grid(row=10, column=7, columnspan=3, sticky=tk.NW, padx=self.padx, pady=self.pady)

        t107 = tk.Entry(tab, width=25)
        t107.insert(0, str(self.config[section][subdef]["107"]))
        t107.config(state="readonly")
        t107.grid(row=11, column=2, columnspan=3, sticky=tk.NW, padx=self.padx, pady=self.pady)
        self.t107 = tk.Entry(tab, width=25)
        self.t107.insert(0, str(self.config[section][subalt]["107"]))
        self.t107.grid(row=11, column=7, columnspan=3, sticky=tk.NW, padx=self.padx, pady=self.pady)

        t110 = tk.Entry(tab, width=25)
        t110.insert(0, str(self.config[section][subdef]["110"]))
        t110.config(state="readonly")
        t110.grid(row=12, column=2, columnspan=3, sticky=tk.NW, padx=self.padx, pady=self.pady)
        self.t110 = tk.Entry(tab, width=25)
        self.t110.insert(0, str(self.config[section][subalt]["110"]))
        self.t110.grid(row=12, column=7, columnspan=3, sticky=tk.NW, padx=self.padx, pady=self.pady)

        t111 = tk.Entry(tab, width=25)
        t111.insert(0, str(self.config[section][subdef]["111"]))
        t111.config(state="readonly")
        t111.grid(row=13, column=2, columnspan=3, sticky=tk.NW, padx=self.padx, pady=self.pady)
        self.t111 = tk.Entry(tab, width=25)
        self.t111.insert(0, str(self.config[section][subalt]["111"]))
        self.t111.grid(row=13, column=7, columnspan=3, sticky=tk.NW, padx=self.padx, pady=self.pady)

        t112 = tk.Entry(tab, width=25)
        t112.insert(0, str(self.config[section][subdef]["112"]))
        t112.config(state="readonly")
        t112.grid(row=14, column=2, columnspan=3, sticky=tk.NW, padx=self.padx, pady=self.pady)
        self.t112 = tk.Entry(tab, width=25)
        self.t112.insert(0, str(self.config[section][subalt]["112"]))
        self.t112.grid(row=14, column=7, columnspan=3, sticky=tk.NW, padx=self.padx, pady=self.pady)

        t113 = tk.Entry(tab, width=25)
        t113.insert(0, str(self.config[section][subdef]["113"]))
        t113.config(state="readonly")
        t113.grid(row=15, column=2, columnspan=3, sticky=tk.NW, padx=self.padx, pady=self.pady)
        self.t113 = tk.Entry(tab, width=25)
        self.t113.insert(0, str(self.config[section][subalt]["113"]))
        self.t113.grid(row=15, column=7, columnspan=3, sticky=tk.NW, padx=self.padx, pady=self.pady)

        t114 = tk.Entry(tab, width=25)
        t114.insert(0, str(self.config[section][subdef]["114"]))
        t114.config(state="readonly")
        t114.grid(row=16, column=2, columnspan=3, sticky=tk.NW, padx=self.padx, pady=self.pady)
        self.t114 = tk.Entry(tab, width=25)
        self.t114.insert(0, str(self.config[section][subalt]["114"]))
        self.t114.grid(row=16, column=7, columnspan=3, sticky=tk.NW, padx=self.padx, pady=self.pady)

        t120 = tk.Entry(tab, width=25)
        t120.insert(0, str(self.config[section][subdef]["120"]))
        t120.config(state="readonly")
        t120.grid(row=17, column=2, columnspan=3, sticky=tk.NW, padx=self.padx, pady=self.pady)
        self.t120 = tk.Entry(tab, width=25)
        self.t120.insert(0, str(self.config[section][subalt]["120"]))
        self.t120.grid(row=17, column=7, columnspan=3, sticky=tk.NW, padx=self.padx, pady=self.pady)

        t121 = tk.Entry(tab, width=25)
        t121.insert(0, str(self.config[section][subdef]["121"]))
        t121.config(state="readonly")
        t121.grid(row=18, column=2, columnspan=3, sticky=tk.NW, padx=self.padx, pady=self.pady)
        self.t121 = tk.Entry(tab, width=25)
        self.t121.insert(0, str(self.config[section][subalt]["121"]))
        self.t121.grid(row=18, column=7, columnspan=3, sticky=tk.NW, padx=self.padx, pady=self.pady)

    def set_texts(self):

        section = "Texts"
        subalt = "Alternative"

        self.config["General"]["Available_Languages"][subalt] = self.langdesc.get()
        self.config[section][subalt]["Code"] = self.langcode.get()
        self.config[section][subalt]["Locale"] = self.locale.get()
        self.config[section][subalt]["100"] = self.t100.get()
        self.config[section][subalt]["101"] = self.t101.get()
        self.config[section][subalt]["102"] = self.t102.get()
        self.config[section][subalt]["103"] = self.t103.get()
        self.config[section][subalt]["104"] = self.t104.get()
        self.config[section][subalt]["105"] = self.t105.get()
        self.config[section][subalt]["106"] = self.t106.get()
        self.config[section][subalt]["107"] = self.t107.get()
        self.config[section][subalt]["110"] = self.t110.get()
        self.config[section][subalt]["111"] = self.t111.get()
        self.config[section][subalt]["112"] = self.t112.get()
        self.config[section][subalt]["113"] = self.t113.get()
        self.config[section][subalt]["114"] = self.t114.get()
        self.config[section][subalt]["120"] = self.t120.get()
        self.config[section][subalt]["121"] = self.t121.get()

    def get_colors(self, tab):

        section = "Colors"

        label = tk.Label(tab, text=self.config[section]["Comment1"])
        label.grid(row=0, column=0, columnspan=6, sticky=tk.NW, padx=self.padx)
        entry = tk.Entry(tab, width=len(self.config[section]["Comment2"]) - 20)
        entry.insert(0, self.config[section]["Comment2"])
        entry.config(state="readonly")
        entry.grid(row=1, column=0, columnspan=5, sticky=tk.NW, padx=self.padx, pady=self.pady)

        label = tk.Label(tab, text="General Background Color:")
        label.grid(row=2, column=0, sticky=tk.NW, padx=self.padx, pady=self.pady)
        self.bkgc = tk.Entry(tab, width=15)
        self.bkgc.insert(0, str(self.config[section]["Color_Background"]))
        self.bkgc.grid(row=2, column=1, sticky=tk.NW, padx=self.padx, pady=self.pady)

        label = tk.Label(tab, text="News Background Color:")
        label.grid(row=3, column=0, sticky=tk.NW, padx=self.padx, pady=self.pady)
        self.nbkgc = tk.Entry(tab, width=15)
        self.nbkgc.insert(0, str(self.config[section]["Color_News_background"]))
        self.nbkgc.grid(row=3, column=1, sticky=tk.NW, padx=self.padx, pady=self.pady)

        subsection = "With_Background"

        label = tk.Label(tab, text="Font colors when background active (required to improve visibility):")
        label.grid(row=4, column=0, columnspan=4, sticky=tk.NW, padx=self.padx, pady=self.pady)

        label = tk.Label(tab, text="Clock Color:")
        label.grid(row=5, column=0, sticky=tk.NW, padx=self.gapx, pady=self.pady)
        self.bclockc = tk.Entry(tab, width=15)
        self.bclockc.insert(0, str(self.config[section][subsection]["Color_Clock"]))
        self.bclockc.grid(row=5, column=1, sticky=tk.NW, padx=self.padx, pady=self.pady)

        label = tk.Label(tab, text="Header Color:")
        label.grid(row=6, column=0, sticky=tk.NW, padx=self.gapx, pady=self.pady)
        self.bheaderc = tk.Entry(tab, width=15)
        self.bheaderc.insert(0, str(self.config[section][subsection]["Color_Header"]))
        self.bheaderc.grid(row=6, column=1, sticky=tk.NW, padx=self.padx, pady=self.pady)

        label = tk.Label(tab, text="News Color:")
        label.grid(row=7, column=0, sticky=tk.NW, padx=self.gapx, pady=self.pady)
        self.bnewsc = tk.Entry(tab, width=15)
        self.bnewsc.insert(0, str(self.config[section][subsection]["Color_News"]))
        self.bnewsc.grid(row=7, column=1, sticky=tk.NW, padx=self.padx, pady=self.pady)

        label = tk.Label(tab, text="Weather Color:")
        label.grid(row=8, column=0, sticky=tk.NW, padx=self.gapx, pady=self.pady)
        self.bweatherc = tk.Entry(tab, width=15)
        self.bweatherc.insert(0, str(self.config[section][subsection]["Color_Weather"]))
        self.bweatherc.grid(row=8, column=1, sticky=tk.NW, padx=self.padx, pady=self.pady)

        subsection = "Without_Background"

        label = tk.Label(tab, text="Font colors when no background:")
        label.grid(row=9, column=0, columnspan=4, sticky=tk.NW, padx=self.padx, pady=self.pady)

        label = tk.Label(tab, text="Clock Color:")
        label.grid(row=10, column=0, sticky=tk.NW, padx=self.gapx, pady=self.pady)
        self.nbclockc = tk.Entry(tab, width=15)
        self.nbclockc.insert(0, str(self.config[section][subsection]["Color_Clock"]))
        self.nbclockc.grid(row=10, column=1, sticky=tk.NW, padx=self.padx, pady=self.pady)

        label = tk.Label(tab, text="Header Color:")
        label.grid(row=11, column=0, sticky=tk.NW, padx=self.gapx, pady=self.pady)
        self.nbheaderc = tk.Entry(tab, width=15)
        self.nbheaderc.insert(0, str(self.config[section][subsection]["Color_Header"]))
        self.nbheaderc.grid(row=11, column=1, sticky=tk.NW, padx=self.padx, pady=self.pady)

        label = tk.Label(tab, text="News Color:")
        label.grid(row=12, column=0, sticky=tk.NW, padx=self.gapx, pady=self.pady)
        self.nbnewsc = tk.Entry(tab, width=15)
        self.nbnewsc.insert(0, str(self.config[section][subsection]["Color_News"]))
        self.nbnewsc.grid(row=12, column=1, sticky=tk.NW, padx=self.padx, pady=self.pady)

        label = tk.Label(tab, text="Weather Color:")
        label.grid(row=13, column=0, sticky=tk.NW, padx=self.gapx, pady=self.pady)
        self.nbweatherc = tk.Entry(tab, width=15)
        self.nbweatherc.insert(0, str(self.config[section][subsection]["Color_Weather"]))
        self.nbweatherc.grid(row=13, column=1, sticky=tk.NW, padx=self.padx, pady=self.pady)

        label = tk.Label(tab, text="Highlight Color:")
        label.grid(row=14, column=0, sticky=tk.NW, padx=self.padx, pady=self.pady)
        self.highlightc = tk.Entry(tab, width=15)
        self.highlightc.insert(0, str(self.config[section]["Color_highlight"]))
        self.highlightc.grid(row=14, column=1, sticky=tk.NW, padx=self.padx, pady=self.pady)

        label = tk.Label(tab, text="Dark Color:")
        label.grid(row=15, column=0, sticky=tk.NW, padx=self.padx, pady=self.pady)
        self.darkc = tk.Entry(tab, width=15)
        self.darkc.insert(0, str(self.config[section]["Color_dark"]))
        self.darkc.grid(row=15, column=1, sticky=tk.NW, padx=self.padx, pady=self.pady)

        label = tk.Label(tab, text="Dim (darken background) Color:")
        label.grid(row=16, column=0, sticky=tk.NW, padx=self.padx, pady=self.pady)
        self.dimc = tk.Entry(tab, width=15)
        self.dimc.insert(0, str(self.config[section]["Color_dim"]))
        self.dimc.grid(row=16, column=1, sticky=tk.NW, padx=self.padx, pady=self.pady)

        label = tk.Label(tab, text="High Rain Probability Color:")
        label.grid(row=17, column=0, sticky=tk.NW, padx=self.padx, pady=self.pady)
        self.highpopc = tk.Entry(tab, width=15)
        self.highpopc.insert(0, str(self.config[section]["Color_High_pop"]))
        self.highpopc.grid(row=17, column=1, sticky=tk.NW, padx=self.padx, pady=self.pady)

        label = tk.Label(tab, text="Med Rain Probability Color:")
        label.grid(row=18, column=0, sticky=tk.NW, padx=self.padx, pady=self.pady)
        self.medpopc = tk.Entry(tab, width=15)
        self.medpopc.insert(0, str(self.config[section]["Color_Med_pop"]))
        self.medpopc.grid(row=18, column=1, sticky=tk.NW, padx=self.padx, pady=self.pady)

        label = tk.Label(tab, text="High Temperature Color:")
        label.grid(row=19, column=0, sticky=tk.NW, padx=self.padx, pady=self.pady)
        self.htempc = tk.Entry(tab, width=15)
        self.htempc.insert(0, str(self.config[section]["Color_High_temp"]))
        self.htempc.grid(row=19, column=1, sticky=tk.NW, padx=self.padx, pady=self.pady)

        label = tk.Label(tab, text="Low Temperature Color:")
        label.grid(row=20, column=0, sticky=tk.NW, padx=self.padx, pady=self.pady)
        self.ltempc = tk.Entry(tab, width=15)
        self.ltempc.insert(0, str(self.config[section]["Color_Low_temp"]))
        self.ltempc.grid(row=20, column=1, sticky=tk.NW, padx=self.padx, pady=self.pady)

        label = tk.Label(tab, text="Title Color:")
        label.grid(row=21, column=0, sticky=tk.NW, padx=self.padx, pady=self.pady)
        self.titlec = tk.Entry(tab, width=15)
        self.titlec.insert(0, str(self.config[section]["Color_Title"]))
        self.titlec.grid(row=21, column=1, sticky=tk.NW, padx=self.padx, pady=self.pady)

    def set_colors(self):

        section = "Colors"

        self.config[section]["Color_Background"] = self.bkgc.get()
        self.config[section]["Color_News_background"] = self.nbkgc.get()

        subsection = "With_Background"
        self.config[section][subsection]["Color_Clock"] = self.bclockc.get()
        self.config[section][subsection]["Color_Header"] = self.bheaderc.get()
        self.config[section][subsection]["Color_News"] = self.bnewsc.get()
        self.config[section][subsection]["Color_Weather"] = self.bweatherc.get()

        subsection = "Without_Background"
        self.config[section][subsection]["Color_Clock"] = self.nbclockc.get()
        self.config[section][subsection]["Color_Header"] = self.nbheaderc.get()
        self.config[section][subsection]["Color_News"] = self.nbnewsc.get()
        self.config[section][subsection]["Color_Weather"] = self.nbweatherc.get()

        self.config[section]["Color_highlight"] = self.highlightc.get()
        self.config[section]["Color_dark"] = self.darkc.get()
        self.config[section]["Color_dim"] = self.dimc.get()
        self.config[section]["Color_High_pop"] = self.highpopc.get()
        self.config[section]["Color_Med_pop"] = self.medpopc.get()
        self.config[section]["Color_High_temp"] = self.htempc.get()
        self.config[section]["Color_Low_temp"] = self.ltempc.get()
        self.config[section]["Color_Title"] = self.titlec.get()

    def get_background(self, tab):

        section = "Background"

        label = tk.Label(tab, text=self.config[section]["Comment"])
        label.grid(row=0, column=0, columnspan=6, sticky=tk.NW, padx=self.padx, pady=self.pady)

        subsection = "With_Background"

        label = tk.Label(tab, text="Settings when background active (required to improve visibility):")
        label.grid(row=1, column=0, columnspan=4, sticky=tk.NW, padx=self.padx, pady=self.pady)

        self.bdim = tk.StringVar(master=self.root, value=self.config[section][subsection]["Dim_background"])
        dim = tk.Checkbutton(tab, text="Dim (darken) Background", variable=self.bdim, onvalue="True", offvalue="False")
        dim.grid(row=2, column=0, columnspan=3, sticky=tk.NW, padx=self.gapx, pady=self.pady)

        label = tk.Label(tab, text="Dim Factor (0-255):")
        label.grid(row=3, column=0, sticky=tk.NW, padx=self.gapx, pady=self.pady)
        self.bdimf = tk.Entry(tab, width=5)
        self.bdimf.insert(0, str(self.config[section][subsection]["Dim_factor"]))
        self.bdimf.grid(row=3, column=1, sticky=tk.NW, padx=self.gapx, pady=self.pady)

        label = tk.Label(tab, text="Outline text style:")
        label.grid(row=4, column=0, sticky=tk.NW, padx=self.gapx, pady=self.pady)
        self.boutline = tk.Listbox(tab, width=10, exportselection=False)
        for i, key in enumerate(self.config[section]["Available_Outline_mode"]):
            self.boutline.insert(tk.END, key)
            if key == self.config[section][subsection]["Outline_mode"]:
                self.boutline.activate(i)
                self.boutline.selection_set(i)
        self.boutline.config(height=0)
        self.boutline.grid(row=4, column=1, sticky=tk.NW, rowspan=4, columnspan=3, padx=self.gapx, pady=self.pady)

        self.bdimff = tk.StringVar(master=self.root, value=self.config[section][subsection]["Dim_forecasts"])
        dim = tk.Checkbutton(tab, text="Dim (darken) Forecasts area", variable=self.bdimff, onvalue="True", offvalue="False")
        dim.grid(row=9, column=0, columnspan=3, sticky=tk.NW, padx=self.gapx, pady=self.pady)

        subsection = "Without_Background"

        label = tk.Label(tab, text="Settings when no background:")
        label.grid(row=10, column=0, columnspan=4, sticky=tk.NW, padx=self.padx, pady=self.pady)

        self.nbdim = tk.StringVar(master=self.root, value=self.config[section][subsection]["Dim_background"])
        dim = tk.Checkbutton(tab, text="Dim (darken) Background", variable=self.nbdim, onvalue="True", offvalue="False")
        dim.grid(row=11, column=0, columnspan=3, sticky=tk.NW, padx=self.gapx, pady=self.pady)

        label = tk.Label(tab, text="Dim Factor (0-255):")
        label.grid(row=12, column=0, sticky=tk.NW, padx=self.gapx, pady=self.pady)
        self.nbdimf = tk.Entry(tab, width=5)
        self.nbdimf.insert(0, str(self.config[section][subsection]["Dim_factor"]))
        self.nbdimf.grid(row=12, column=1, sticky=tk.NW, padx=self.gapx, pady=self.pady)

        label = tk.Label(tab, text="Outline text style:")
        label.grid(row=13, column=0, sticky=tk.NW, padx=self.gapx, pady=self.pady)
        self.nboutline = tk.Listbox(tab, width=10, exportselection=False)
        for i, key in enumerate(self.config[section]["Available_Outline_mode"]):
            self.nboutline.insert(tk.END, key)
            if key == self.config[section][subsection]["Outline_mode"]:
                self.nboutline.activate(i)
                self.nboutline.selection_set(i)
        self.nboutline.config(height=0)
        self.nboutline.grid(row=13, column=1, sticky=tk.NW, rowspan=4, columnspan=3, padx=self.gapx, pady=self.pady)

        self.nbdimff = tk.StringVar(master=self.root, value=self.config[section][subsection]["Dim_forecasts"])
        dim = tk.Checkbutton(tab, text="Dim (darken) Forecasts area", variable=self.nbdimff, onvalue="True", offvalue="False")
        dim.grid(row=18, column=0, columnspan=3, sticky=tk.NW, padx=self.gapx, pady=self.pady)

    def set_background(self):

        section = "Background"

        subsection = "With_Background"
        self.config[section][subsection]["Dim_background"] = self.bdim.get()
        self.config[section][subsection]["Dim_factor"] = int(self.bdimf.get())
        self.config[section][subsection]["Outline_mode"] = self.boutline.get(tk.ACTIVE)
        self.config[section][subsection]["Dim_forecasts"] = self.bdimff.get()

        subsection = "Without_Background"
        self.config[section][subsection]["Dim_background"] = self.nbdim.get()
        self.config[section][subsection]["Dim_factor"] = int(self.nbdimf.get())
        self.config[section][subsection]["Outline_mode"] = self.nboutline.get(tk.ACTIVE)
        self.config[section][subsection]["Dim_forecasts"] = self.nbdimff.get()

    def get_Weather(self, tab):

        section = "Weather"

        label = tk.Label(tab, text="Current location (extracted from your IP, so it might be wrong): ")
        label.grid(row=0, column=0, columnspan=5, sticky=tk.NW, padx=self.padx, pady=self.pady)

        label = tk.Label(tab, text="City description:")
        label.grid(row=1, column=0, sticky=tk.NW, padx=self.gapx, pady=self.pady)
        loc = tk.Entry(tab, width=20)
        loc.insert(0, self.loc.get())
        loc.config(state="readonly")
        loc.grid(row=1, column=1, sticky=tk.NW, padx=self.padx, pady=self.pady)

        label = tk.Label(tab, text="Latitude:")
        label.grid(row=1, column=2, sticky=tk.NW, padx=self.padx, pady=self.pady)
        lat = tk.Entry(tab, width=10)
        lat.insert(0, self.lat)
        lat.config(state="readonly")
        lat.grid(row=1, column=3, sticky=tk.NW, padx=self.padx, pady=self.pady)

        label = tk.Label(tab, text="Longitude:")
        label.grid(row=1, column=4, sticky=tk.NW, padx=self.padx, pady=self.pady)
        lon = tk.Entry(tab, width=10)
        lon.insert(0, self.lon)
        lon.config(state="readonly")
        lon.grid(row=1, column=5, sticky=tk.NW, padx=self.padx, pady=self.pady)

        self.usecurr = tk.StringVar(master=self.root, value=self.config[section]["Use_current"])
        curr = tk.Checkbutton(tab, text="Use this current location (If wrong, uncheck and set a new Default location below)",
                              variable=self.usecurr, onvalue="True", offvalue="False")
        if not self.currSuccess:
            curr.config(state=tk.DISABLED)
        curr.grid(row=2, column=0, columnspan=4, sticky=tk.NW, padx=self.gapx, pady=self.pady)

        label = tk.Label(tab, text="Locations stored on Settings (use Search feature to find and set other locations):")
        label.grid(row=3, column=0, columnspan=3, sticky=tk.NW, padx=self.padx, pady=self.pady)

        label = tk.Label(tab, text="Default:")
        label.grid(row=4, column=0, sticky=tk.NW, padx=self.gapx, pady=self.pady)
        self.loc1 = tk.Entry(tab, width=20)
        self.loc1.insert(0, str(self.config[section]["Locations"][0][0]))
        self.loc1.grid(row=4, column=1, sticky=tk.NW, padx=self.padx, pady=self.pady)

        label = tk.Label(tab, text="Latitude:")
        label.grid(row=4, column=2, sticky=tk.NW, padx=self.padx, pady=self.pady)
        self.lat1 = tk.Entry(tab, width=10)
        self.lat1.insert(0, str(self.config[section]["Locations"][0][1]).split("lat=")[1].split("&")[0])
        self.lat1.grid(row=4, column=3, sticky=tk.NW, padx=self.padx, pady=self.pady)

        label = tk.Label(tab, text="Longitude:")
        label.grid(row=4, column=4, sticky=tk.NW, padx=self.padx, pady=self.pady)
        self.lon1 = tk.Entry(tab, width=10)
        self.lon1.insert(0, str(self.config[section]["Locations"][0][1]).split("&lon=")[1])
        self.lon1.grid(row=4, column=5, sticky=tk.NW, padx=self.padx, pady=self.pady)

        label = tk.Label(tab, text="Location 2:")
        label.grid(row=5, column=0, sticky=tk.NW, padx=self.gapx, pady=self.pady)
        self.loc2 = tk.Entry(tab, width=20)
        self.loc2.insert(0, str(self.config[section]["Locations"][1][0]))
        self.loc2.grid(row=5, column=1, sticky=tk.NW, padx=self.padx, pady=self.pady)

        label = tk.Label(tab, text="Latitude:")
        label.grid(row=5, column=2, sticky=tk.NW, padx=self.padx, pady=self.pady)
        self.lat2 = tk.Entry(tab, width=10)
        self.lat2.insert(0, str(self.config[section]["Locations"][1][1]).split("lat=")[1].split("&")[0])
        self.lat2.grid(row=5, column=3, sticky=tk.NW, padx=self.padx, pady=self.pady)

        label = tk.Label(tab, text="Longitude:")
        label.grid(row=5, column=4, sticky=tk.NW, padx=self.padx, pady=self.pady)
        self.lon2 = tk.Entry(tab, width=10)
        self.lon2.insert(0, str(self.config[section]["Locations"][1][1]).split("&lon=")[1])
        self.lon2.grid(row=5, column=5, sticky=tk.NW, padx=self.padx, pady=self.pady)

        label = tk.Label(tab, text="Location 3:")
        label.grid(row=6, column=0, sticky=tk.NW, padx=self.gapx, pady=self.pady)
        self.loc3 = tk.Entry(tab, width=20)
        self.loc3.insert(0, str(self.config[section]["Locations"][2][0]))
        self.loc3.grid(row=6, column=1, sticky=tk.NW, padx=self.padx, pady=self.pady)

        label = tk.Label(tab, text="Latitude:")
        label.grid(row=6, column=2, sticky=tk.NW, padx=self.padx, pady=self.pady)
        self.lat3 = tk.Entry(tab, width=10)
        self.lat3.insert(0, str(self.config[section]["Locations"][2][1]).split("lat=")[1].split("&")[0])
        self.lat3.grid(row=6, column=3, sticky=tk.NW, padx=self.padx, pady=self.pady)

        label = tk.Label(tab, text="Longitude:")
        label.grid(row=6, column=4, sticky=tk.NW, padx=self.padx, pady=self.pady)
        self.lon3 = tk.Entry(tab, width=10)
        self.lon3.insert(0, str(self.config[section]["Locations"][2][1]).split("&lon=")[1])
        self.lon3.grid(row=6, column=5, sticky=tk.NW, padx=self.padx, pady=self.pady)

        label = tk.Label(tab, text="Search city coordinates:")
        label.grid(row=7, column=0, columnspan=3, sticky=tk.NW, padx=self.padx, pady=self.pady)

        label = tk.Label(tab, text="City:")
        label.grid(row=8, column=0, sticky=tk.NW, padx=self.gapx, pady=self.pady)
        self.city = tk.Entry(tab, width=20)
        self.city.grid(row=8, column=1, sticky=tk.NW, padx=self.padx, pady=self.pady)

        label = tk.Label(tab, text="Region:")
        label.grid(row=8, column=2, sticky=tk.NW, padx=self.padx, pady=self.pady)
        self.prov = tk.Entry(tab, width=10)
        self.prov.grid(row=8, column=3, sticky=tk.NW, padx=self.padx, pady=self.pady)

        label = tk.Label(tab, text="Country:")
        label.grid(row=8, column=4, sticky=tk.NW, padx=self.padx, pady=self.pady)
        self.country = tk.Entry(tab, width=10)
        self.country.grid(row=8, column=5, sticky=tk.NW, padx=self.padx, pady=self.pady)

        search = tk.Button(tab, text="Search", command=(lambda: self.search(tab)))
        search.grid(row=9, column=5, sticky=tk.NW, padx=self.padx, pady=self.pady)

    def search(self, tab):

        q = urllib.parse.quote(self.city.get() + ("," + self.prov.get() if self.prov.get() else "") + ("," + self.country.get() if self.country.get() else ""))
        coord = utils.get_coordinates(wconstants.gURL % q)

        if coord:
            text = "Search results (copy-paste latitude and longitude to change stored settings location)"
        else:
            text = "No results found. Please check/refine your search"

        label = tk.Label(tab, text=text)
        label.grid(row=10, column=0, columnspan=5, sticky=tk.NW, padx=self.padx, pady=self.pady)

        for i in range(10):

            if i >= len(coord):
                coord.append(["", "", ""])

            label = tk.Label(tab, text="City description")
            label.grid(row=11+i, column=0, sticky=tk.NW, padx=self.gapx, pady=self.pady)
            desc = tk.Entry(tab, width=30)
            desc.insert(0, coord[i][0])
            desc.config(state="readonly")
            desc.grid(row=11+i, column=1, sticky=tk.NW, padx=self.padx, pady=self.pady)

            label = tk.Label(tab, text="Latitude")
            label.grid(row=11+i, column=2, sticky=tk.NW, padx=self.padx, pady=self.pady)
            lat = tk.Entry(tab, width=10)
            lat.insert(0, coord[i][1])
            lat.config(state="readonly")
            lat.grid(row=11+i, column=3, sticky=tk.NW, padx=self.padx, pady=self.pady)

            label = tk.Label(tab, text="Longitude")
            label.grid(row=11+i, column=4, sticky=tk.NW, padx=self.padx, pady=self.pady)
            lon = tk.Entry(tab, width=10)
            lon.insert(0, coord[i][2])
            lon.config(state="readonly")
            lon.grid(row=11+i, column=5, sticky=tk.NW, padx=self.padx, pady=self.pady)

    def set_Weather(self):

        section = "Weather"

        self.config[section]["Use_current"] = self.usecurr.get()
        self.config[section]["Locations"][0][0] = self.loc1.get()
        self.config[section]["Locations"][0][1] = "lat=%s&lon=%s" % (self.lat1.get(), self.lon1.get())
        self.config[section]["Locations"][1][0] = self.loc2.get()
        self.config[section]["Locations"][1][1] = "lat=%s&lon=%s" % (self.lat2.get(), self.lon2.get())
        self.config[section]["Locations"][2][0] = self.loc3.get()
        self.config[section]["Locations"][2][1] = "lat=%s&lon=%s" % (self.lat3.get(), self.lon3.get())

    def get_News(self, tab):

        section = "News"

        self.altern = tk.StringVar(master=self.root, value=self.config[section]["Alternate_News_source"])
        altern = tk.Checkbutton(tab, text='Alternate News source', variable=self.altern, onvalue="True", offvalue="False")
        altern.grid(row=0, column=0, sticky=tk.NW, padx=self.padx, pady=self.pady)

        self.pics = tk.StringVar(master=self.root, value=self.config[section]["Show_News_pics"])
        pics = tk.Checkbutton(tab, text='Show News pictures', variable=self.pics, onvalue="True", offvalue="False")
        pics.grid(row=1, column=0, sticky=tk.NW, padx=self.padx, pady=self.pady)

        label = tk.Label(tab, text="News separator")
        label.grid(row=2, column=0, sticky=tk.NW, padx=self.padx, pady=self.pady)
        self.sep = tk.Entry(tab, width=10)
        self.sep.insert(0, str(self.config[section]["Separator"]))
        self.sep.grid(row=2, column=1, sticky=tk.NW, padx=self.padx, pady=self.pady)

        label = tk.Label(tab, text="News ticker FPS:")
        label.grid(row=3, column=0, sticky=tk.NW, padx=self.padx, pady=self.pady)
        self.fps = tk.Entry(tab, width=4)
        self.fps.insert(0, str(self.config[section]["FPS"]))
        self.fps.grid(row=3, column=1, sticky=tk.NW, padx=self.padx, pady=self.pady)
        label = tk.Label(tab, text="(*) " + self.config[section]["Comment"])
        label.grid(row=4, column=0, columnspan=5, sticky=tk.NW, padx=self.padx)

    def set_News(self):

        section = "News"

        self.config[section]["Alternate_News_source"] = self.altern.get()
        self.config[section]["Show_News_pics"] = self.pics.get()
        self.config[section]["Separator"] = self.sep.get()
        self.config[section]["FPS"] = int(self.fps.get())

    def get_WorldClocks(self, tab):

        section = "World_Clocks"

        label = tk.Label(tab, text="Clock Timezone 1:")
        label.grid(row=0, column=0, sticky=tk.NW, padx=self.padx, pady=self.pady)
        self.tz1 = tk.Entry(tab, width=30)
        self.tz1.insert(0, str(self.config[section]["Timezones"][0][0]))
        self.tz1.grid(row=0, column=1, sticky=tk.NW, padx=self.padx, pady=self.pady)

        label = tk.Label(tab, text="City name:")
        label.grid(row=0, column=2, sticky=tk.NW, padx=self.padx, pady=self.pady)
        self.tzc1 = tk.Entry(tab, width=30)
        self.tzc1.insert(0, str(self.config[section]["Timezones"][0][1]))
        self.tzc1.grid(row=0, column=3, sticky=tk.NW, padx=self.padx, pady=self.pady)

        label = tk.Label(tab, text="Clock Timezone 2:")
        label.grid(row=1, column=0, sticky=tk.NW, padx=self.padx, pady=self.pady)
        self.tz2 = tk.Entry(tab, width=30)
        self.tz2.insert(0, str(self.config[section]["Timezones"][1][0]))
        self.tz2.grid(row=1, column=1, sticky=tk.NW, padx=self.padx, pady=self.pady)

        label = tk.Label(tab, text="City name:")
        label.grid(row=1, column=2, sticky=tk.NW, padx=self.padx, pady=self.pady)
        self.tzc2 = tk.Entry(tab, width=30)
        self.tzc2.insert(0, str(self.config[section]["Timezones"][1][1]))
        self.tzc2.grid(row=1, column=3, sticky=tk.NW, padx=self.padx, pady=self.pady)

        label = tk.Label(tab, text="Clock Timezone 3:")
        label.grid(row=2, column=0, sticky=tk.NW, padx=self.padx, pady=self.pady)
        self.tz3 = tk.Entry(tab, width=30)
        self.tz3.insert(0, str(self.config[section]["Timezones"][2][0]))
        self.tz3.grid(row=2, column=1, sticky=tk.NW, padx=self.padx, pady=self.pady)

        label = tk.Label(tab, text="City name:")
        label.grid(row=2, column=2, sticky=tk.NW, padx=self.padx, pady=self.pady)
        self.tzc3 = tk.Entry(tab, width=30)
        self.tzc3.insert(0, str(self.config[section]["Timezones"][2][1]))
        self.tzc3.grid(row=2, column=3, sticky=tk.NW, padx=self.padx, pady=self.pady)

        label = tk.Label(tab, text="Clock Timezone 4:")
        label.grid(row=3, column=0, sticky=tk.NW, padx=self.padx, pady=self.pady)
        self.tz4 = tk.Entry(tab, width=30)
        self.tz4.insert(0, str(self.config[section]["Timezones"][3][0]))
        self.tz4.grid(row=3, column=1, sticky=tk.NW, padx=self.padx, pady=self.pady)

        label = tk.Label(tab, text="City name:")
        label.grid(row=3, column=2, sticky=tk.NW, padx=self.padx, pady=self.pady)
        self.tzc4 = tk.Entry(tab, width=30)
        self.tzc4.insert(0, str(self.config[section]["Timezones"][3][1]))
        self.tzc4.grid(row=3, column=3, sticky=tk.NW, padx=self.padx, pady=self.pady)

        label = tk.Label(tab, text="Clock Timezone 5:")
        label.grid(row=4, column=0, sticky=tk.NW, padx=self.padx, pady=self.pady)
        self.tz5 = tk.Entry(tab, width=30)
        self.tz5.insert(0, str(self.config[section]["Timezones"][4][0]))
        self.tz5.grid(row=4, column=1, sticky=tk.NW, padx=self.padx, pady=self.pady)

        label = tk.Label(tab, text="City name:")
        label.grid(row=4, column=2, sticky=tk.NW, padx=self.padx, pady=self.pady)
        self.tzc5 = tk.Entry(tab, width=30)
        self.tzc5.insert(0, str(self.config[section]["Timezones"][4][1]))
        self.tzc5.grid(row=4, column=3, sticky=tk.NW, padx=self.padx, pady=self.pady)

    def set_WorldClocks(self):

        section = "World_Clocks"

        self.config[section]["Timezones"][0][0] = self.tz1.get()
        self.config[section]["Timezones"][0][1] = self.tzc1.get()
        self.config[section]["Timezones"][1][0] = self.tz2.get()
        self.config[section]["Timezones"][1][1] = self.tzc2.get()
        self.config[section]["Timezones"][2][0] = self.tz3.get()
        self.config[section]["Timezones"][2][1] = self.tzc3.get()
        self.config[section]["Timezones"][3][0] = self.tz4.get()
        self.config[section]["Timezones"][3][1] = self.tzc4.get()
        self.config[section]["Timezones"][4][0] = self.tz5.get()
        self.config[section]["Timezones"][4][1] = self.tzc5.get()


def main():
    app = WeatherConfig()
    app.run()


if __name__ == "__main__":
    main()
