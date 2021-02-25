# -*- coding: utf-8 -*-
# Website helper file

import json

import requests

ENDPOINT_CINESCAPE = 'https://cinescape.media/wp-json/tv/roku/'
# ^^^^ uppercase variable are always simple CONSTANTS! do not use like any other variable


def get_cinescape_data():
    """Get feed from Cinescape"""
    try:
        html = requests.get(ENDPOINT_CINESCAPE)
        return json.loads(html.content)
    except Exception:
        # ..todo print to Kodi log what happened and/or warning the user with a message
        raise  # <<< pass the error to the caller code
