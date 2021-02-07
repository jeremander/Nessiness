#!/usr/bin/env python
# -*- coding: utf-8 -*- #

# This file is only used if you use `make publish` or
# explicitly specify it as your config file.

import os
import sys
sys.path.append(os.curdir)
from pelicanconf import *

# If your site is available via HTTPS, make sure SITEURL begins with https://
# SITEURL = 'https://nessiness.com'
SITEURL = 'https://jeremander.github.io/Nessiness'
IMG_DIR = f'{SITEURL}/images'
SITELOGO = f'{IMG_DIR}/logo.png'

RELATIVE_URLS = False

# Links
LINKS[1] = ('Projects', f'{SITEURL}/pages/projects.html')

# Social
SOCIAL[2] = ('rss', f'{SITEURL}/{FEED_ALL_ATOM}')

DELETE_OUTPUT_DIRECTORY = True

# Following items are often useful when publishing

#DISQUS_SITENAME = ""
#GOOGLE_ANALYTICS = ""