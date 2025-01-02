# -*- coding: utf-8 -*-
"""Objects, properties, and methods to be shared across other modules in the
trakt package
"""
import json
import logging
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from functools import lru_cache, wraps
from json import JSONDecodeError
from typing import NamedTuple
from urllib.parse import urljoin

import requests
from requests_oauthlib import OAuth2Session

from trakt import errors
from trakt.errors import BadResponseException

__author__ = 'Jon Nappi'
__all__ = ['Airs', 'Alias', 'Comment', 'Genre', 'get', 'delete', 'post', 'put',
           'init', 'BASE_URL', 'CLIENT_ID', 'CLIENT_SECRET', 'DEVICE_AUTH',
           'REDIRECT_URI', 'HEADERS', 'CONFIG_PATH', 'OAUTH_TOKEN',
           'OAUTH_REFRESH', 'PIN_AUTH', 'OAUTH_AUTH', 'AUTH_METHOD',
           'config', 'api',
           'TIMEOUT',
           'APPLICATION_ID']

#: The base url for the Trakt API. Can be modified to run against different
#: Trakt.tv environments
BASE_URL = 'https://api.trakt.tv/'

#: The Trakt.tv OAuth Client ID for your OAuth Application
CLIENT_ID = None

#: The Trakt.tv OAuth Client Secret for your OAuth Application
CLIENT_SECRET = None

#: The OAuth2 Redirect URI for your OAuth Application
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'

#: Default request HEADERS
HEADERS = {'Content-Type': 'application/json', 'trakt-api-version': '2'}

#: Default path for where to store your trakt.tv API authentication information
CONFIG_PATH = os.path.join(os.path.expanduser('~'), '.pytrakt.json')

#: Your personal Trakt.tv OAUTH Bearer Token
OAUTH_TOKEN = None

# OAuth token validity checked
OAUTH_TOKEN_VALID = None

# Your OAUTH token expiration date
OAUTH_EXPIRES_AT = None

# Your OAUTH refresh token
OAUTH_REFRESH = None

#: Flag used to enable Trakt PIN authentication
PIN_AUTH = 'PIN'

#: Flag used to enable Trakt OAuth authentication
OAUTH_AUTH = 'OAUTH'

#: Flag used to enable Trakt OAuth device authentication
DEVICE_AUTH = 'DEVICE'

#: The currently enabled authentication method. Default is ``PIN_AUTH``
AUTH_METHOD = PIN_AUTH

#: The ID of the application to register with, when using PIN authentication
APPLICATION_ID = None

#: Timeout in seconds for all requests
TIMEOUT = 30

#: Global session to make requests with
session = requests.Session()


def init(*args, **kwargs):
    """Run the auth function specified by *AUTH_METHOD*"""
    from trakt.auth import init_auth

    return init_auth(AUTH_METHOD, *args, **kwargs)


@lru_cache(maxsize=None)
def config():
    from trakt.config import AuthConfig

    return AuthConfig(CONFIG_PATH).update(
        APPLICATION_ID=APPLICATION_ID,
        CLIENT_ID=CLIENT_ID,
        CLIENT_SECRET=CLIENT_SECRET,
        OAUTH_EXPIRES_AT=OAUTH_EXPIRES_AT,
        OAUTH_REFRESH=OAUTH_REFRESH,
        OAUTH_TOKEN=OAUTH_TOKEN,
    )


@lru_cache(maxsize=None)
def api():
    from trakt.api import HttpClient, TokenAuth

    client = HttpClient(BASE_URL, session)
    auth = TokenAuth(client=client, config=config())
    client.set_auth(auth)

    return client


class Airs(NamedTuple):
    day: str
    time: str
    timezone: str


class Alias(NamedTuple):
    title: str
    country: str


class Genre(NamedTuple):
    name: str
    slug: str


class Comment(NamedTuple):
    id: str
    parent_id: str
    created_at: str
    comment: str
    spoiler: str
    review: str
    replies: str
    user: str
    updated_at: str
    likes: str
    user_rating: str


# Backward compat with 3.x
def delete(f):
    from trakt.decorators import delete
    return delete(f)


def get(f):
    from trakt.decorators import get
    return get(f)


def post(f):
    from trakt.decorators import post
    return post(f)


def put(f):
    from trakt.decorators import put
    return put(f)
