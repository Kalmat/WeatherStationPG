#!/usr/bin/python
# -*- coding: utf-8 -*-

import wconstants

# Other texts are returned by API using 'lang' parameter. Add them to this list if required.
texts = {
    wconstants.SPANISH: {
        100: "Hoy",
        101: "Sensación térmica",
        102: "Viento",
        103: "Dirección",
        104: "Barómetro",
        105: "Humedad",
        106: "Última Actualización",
        107: "Visibilidad",
        110: "Bajo",
        111: "Medio",
        112: "Alto",
        113: "Muy Alto",
        114: "Extremo",
        120: "Hoy, Índice UV",
        121: "Hoy, Viento Alto"
    },
    wconstants.ENGLISH: {
        100: "Today",
        101: "Windchill",
        102: "Windspeed",
        103: "Direction",
        104: "Barometer",
        105: "Humidity",
        106: "Last Updated",
        107: "Visibility",
        110: "Low",
        111: "Medium",
        112: "High",
        113: "Very High",
        114: "Extreme",
        120: "Today, UV Index",
        121: "Today, High Wind"
    }
}


def translate(lang, code):
    return texts[lang][code]
