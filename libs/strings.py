import json

default_locale = "pt-br"
cached_strings = {}


def refresh():
    global cached_strings
    with open(f"strings/{default_locale}.json") as f:
        cached_strings = json.load(f)
    

def gettext(name):
    return cached_strings[name]

refresh()