#!/usr/bin/env python

from datetime import datetime
import os


DEV = (os.environ.get('DEV') == '1')

AUTHOR = 'Jeremy Silver'
SITENAME = 'Nessiness'
SITETITLE = 'Nessiness'

# development site URL
SITEURL = 'http://localhost:8080'

if DEV:
    AUTH_URL = 'http://localhost:8000'
else:
    AUTH_URL = 'https://nessiness-auth.fly.dev'

# include year/month to avoid possible article URL collisions
ARTICLE_URL = '{date:%Y}/{date:%m}/{slug}/'
ARTICLE_SAVE_AS = '{date:%Y}/{date:%m}/{slug}/index.html'

IMG_DIR = f'{SITEURL}/images'
SITELOGO = f'{IMG_DIR}/logo.png'
FAVICON_DIR = f'{IMG_DIR}/favicons'
# BROWSER_COLOR = "#333333"
# PYGMENTS_STYLE = "monokai"

ROBOTS = "index, follow"

THEME = 'theme'
PATH = 'content'

# inside of content directory
STATIC_PATHS = ['docs', 'extra', 'images']

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
SOCIAL_DICT = {
    # 'twitter': 'https://x.com/NessinessDotCom',
    'bluesky': 'https://bsky.app/profile/nessiness.com',
    # 'mastodon': 'https://mathstodon.xyz/@jeremander',
    # 'mastodon': 'https://mathstodon.xyz/@jeremander',
    'github': 'https://github.com/jeremander',
    'rss': f'{SITEURL}/{FEED_ATOM}',
    'envelope': 'mailto:jeremys@nessiness.com?subject=Nessiness',
}

SOCIAL = list(SOCIAL_DICT.items())

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

# ATProto

PLUGIN_PATHS = ['atproto/pelican/plugins']
PLUGINS = ['atproto']

# local path to JSON registry
ATPROTO_REGISTRY_PATH = 'atproto/document_registry.json'
# site URL for blog website
ATPROTO_SITEURL = 'https://nessiness.com'
# DID for ATProto account
ATPROTO_DID = 'did:plc:jypsryjwkklic3bgem5gticy'
# prefix to use for every document rkey
ATPROTO_PUB_PREFIX = 'nessiness'

EXTRA_PATH_METADATA = {
    'extra/site.standard.publication': {'path': '.well-known/site.standard.publication'},
}
