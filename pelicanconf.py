#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

ARCHIVES_SAVE_AS = 'archive/index.html'
ARTICLE_PATHS  = ['essays', 'posts', 'poems', 'fiction']
ARTICLE_URL = 'archive/{slug}/'
ARTICLE_SAVE_AS = 'archive/{slug}/index.html'
AUTHOR = 'Cryborg'
DATE_FORMATS = {'en': '%Y.%m.%d'}
DEFAULT_DATE_FORMAT = '%Y.%m.%d'
DEFAULT_LANG = 'en'
DEFAULT_PAGINATION = False
DISPLAY_PAGES_ON_MENU = False
LOAD_CONTENT_CACHE = False
PAGE_PATHS = ['pages']
PAGE_SAVE_AS = '{slug}/index.html'
PAGE_URL = '{slug}/'
PATH = 'content'
SITENAME = 'cryborg'
SITEURL = 'http://cryb.org'
STATIC_PATHS = ['images', 'robots.txt', 'favicon.ico']
EXTRA_PATH_METADATA = {
    'robots.txt': {'path': 'robots.txt'},
    'favicon.ico' : {'path': 'favicon.ico'},
    }
TIMEZONE = 'America/New_York'
USE_FOLDER_AS_CATEGORY = True
MAIN_ARTICLE_SLUG = 'hiatus'

DIRECT_TEMPLATES = ('index', 'categories', 'archives')

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None

DELETE_OUTPUT_DIRECTORY = True
OUTPUT_PATH = '../../../pelican-output/'

# False = absolute URLs (for prod);
# True = document-relative URLs (for dev)
RELATIVE_URLS = False

#specify theme
THEME = "cryborg-theme"
