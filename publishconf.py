#!/usr/bin/env python
# -*- coding: utf-8 -*- #

# This file is only used if you use `make publish` or
# explicitly specify it as your config file.

import os
import sys
sys.path.append(os.curdir)
from pelicanconf import *

# If your site is available via HTTPS, make sure SITEURL begins with https://
SITEURL = 'https://nessiness.com'
IMG_DIR = f'{SITEURL}/images'
SITELOGO = f'{IMG_DIR}/logo.png'
FAVICON_DIR = f'{IMG_DIR}/favicons'

RELATIVE_URLS = False

FEED_DOMAIN = SITEURL

# Links
LINKS = [('Home', SITEURL), ('Projects', f'{SITEURL}/pages/projects.html')]

# Social
SOCIAL_DICT['rss'] = f'{SITEURL}/{FEED_ATOM}'
SOCIAL = list(SOCIAL_DICT.items())

DELETE_OUTPUT_DIRECTORY = True

# Following items are often useful when publishing

#DISQUS_SITENAME = ""
#GOOGLE_ANALYTICS = ""
