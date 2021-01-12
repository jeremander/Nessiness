#!/usr/bin/env python
# -*- coding: utf-8 -*- #

from datetime import datetime

AUTHOR = 'Jeremy Silver'
SITENAME = 'Nessiness'
SITETITLE = 'Nessiness'
SITEURL = 'http://localhost:8000'
# SITEURL = 'https://nessiness.com'
# SITELOGO = 'images/red_yoshi.png'
SITELOGO = f'{SITEURL}/images/red_yoshi.png'

# SITELOGO = ''
# FAVICON = '/images/favicon.ico'
# BROWSER_COLOR = "#333333"
# PYGMENTS_STYLE = "monokai"

ROBOTS = "index, follow"

THEME = 'theme'
PATH = 'content'

# inside of content directory
STATIC_PATHS = ['images']

TIMEZONE = 'America/New_York'

DEFAULT_LANG = 'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = (
    ('Projects', '#'),
    ('Blog', '#'),
    ('About Me', '#'),
    ('Links', '#')
)

# Social widget
SOCIAL = (
    ('twitter', 'https://twitter.com/Morosoph1729'),
    ('github', 'https://github.com/jeremander'),
    ('envelope', 'mailto:jsilver9887@gmail.com?subject=Nessiness')
)

# MAIN_MENU = True
MENUITEMS = (
    ('Archives', '/archives.html'),
    ('Categories', '/categories.html'),
    ('Tags', '/tags.html'),
)

COPYRIGHT_YEAR = datetime.now().year
COPYRIGHT_NAME = 'Nessiness'

DEFAULT_PAGINATION = False

# Uncomment following line if you want document-relative URLs when developing
# RELATIVE_URLS = True

# THEME_COLOR = 'dark'
# THEME_COLOR_AUTO_DETECT_BROWSER_PREFERENCE = True
# THEME_COLOR_ENABLE_USER_OVERRIDE = True

USE_LESS = True