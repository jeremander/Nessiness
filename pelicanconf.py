#!/usr/bin/env python
# -*- coding: utf-8 -*- #

from datetime import datetime
import os

DEV = (os.environ.get('DEV') == '1')

AUTHOR = 'Jeremy Silver'
SITENAME = 'Nessiness'
SITETITLE = 'Nessiness'

SITEURL = 'http://localhost:8080'

if DEV:
    AUTH_URL = 'http://localhost:8000'
else:
    AUTH_URL = 'https://nessiness-auth.fly.dev'

IMG_DIR = f'{SITEURL}/images'
SITELOGO = f'{IMG_DIR}/logo.png'
FAVICON_DIR = f'{IMG_DIR}/favicons'
# BROWSER_COLOR = "#333333"
# PYGMENTS_STYLE = "monokai"

ROBOTS = "index, follow"

THEME = 'theme'
# THEME = "/Users/jerm/Programming/Web/pelican-themes/Flex"
PATH = 'content'

# inside of content directory
STATIC_PATHS = ['docs', 'images']

TEMPLATE_PAGES = {
    'login.html': 'login.html',
    'pages/projects.html': 'pages/projects.html',
    'profile.html': 'profile.html',
    'reset_password.html': 'reset_password.html'
}

TIMEZONE = 'America/New_York'

DEFAULT_LANG = 'en'

# Feeds
# Feed generation is usually not desired when developing
FEED_DOMAIN = SITEURL
FEED_ATOM = 'feed/atom.xml'
FEED_ALL_ATOM = 'feed/all.atom.xml'
CATEGORY_FEED_ATOM = 'feeds/{slug}.atom.xml'
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
# AUTHOR_FEED_RSS = None

# Blogroll
LINKS = [('Home', SITEURL), ('Projects', f'{SITEURL}/pages/projects.html')]
DISABLE_URL_HASH = True

PAGES_SORT_ATTRIBUTE = 'category'
FILENAME_METADATA = '(?P<date>\d{4}\d{2}\d{2})_(?P<slug>.*)'

# Social widget
SOCIAL = [
    # ('twitter', 'https://twitter.com/Morosoph1729'),
    ('mastodon', 'https://mathstodon.xyz/@jeremander'),
    ('github', 'https://github.com/jeremander'),
    ('rss', f'{SITEURL}/{FEED_ATOM}'),
    ('envelope', 'mailto:jeremys@nessiness.com?subject=Nessiness'),
]

# MAIN_MENU = True
# MENUITEMS = (
#     ('Archives', '/archives.html'),
#     ('Categories', '/categories.html'),
#     ('Tags', '/tags.html'),
# )

LOGIN_NAV = DEV

COPYRIGHT_YEAR = datetime.now().year
COPYRIGHT_NAME = 'Nessiness'
DEFAULT_DATE_FORMAT = '%b %d, %Y'

DEFAULT_PAGINATION = False

# Uncomment following line if you want document-relative URLs when developing
# RELATIVE_URLS = True

# THEME_COLOR = 'dark'
# THEME_COLOR_AUTO_DETECT_BROWSER_PREFERENCE = True
# THEME_COLOR_ENABLE_USER_OVERRIDE = True

USE_LESS = True

# markdown-link-attr-modifier extension

MARKDOWN = {
    'extension_configs': {
        'markdown.extensions.codehilite': {
            'css_class': 'highlight',
            'linenums': False,
            'guess_lang': False,
        },
        'markdown.extensions.extra': {},
        'markdown.extensions.meta': {},
        'markdown.extensions.toc': {},

        'markdown_link_attr_modifier': {
            # config here
        },
    },
    'output_format': 'html5',
}