# -*- coding: utf-8 -*-
'''
A simple SaltStack extension module for interacting with
Mattermost Incoming Webhooks
Copyright (C) 2019 Davide Madrisan <davide.madrisan@gmail.com>

This module requires a configuration profile to be configured
in either the minion or, as in our implementation, in the master
configuration file (/etc/salt/master.d/mattermost.conf).
This profile requires very little:

.. code-block:: yaml

    mattermost:
      api_url: https://slack.mydomain.com
      hook: 3tdgo8restnxiykdx88wqtxryr

This file should be saved as salt/_modules/mattermost.py
'''

# Import Python libs
import logging
import requests

# Import Salt libs
import salt.config
from salt.exceptions import CommandExecutionError
from salt.exceptions import SaltInvocationError
from salt.ext.six.moves.urllib.parse import urljoin as _urljoin
from salt.ext import six

log = logging.getLogger(__name__)

__virtualname__ = 'mattermost'

def __virtual__():
    '''
    Return virtual name of the module.
    :return: The virtual name of the module.
    '''
    return __virtualname__

def _config():
    '''
    Return the SaltStack configuration for Mattermost
    '''
    try:
        master_opts = salt.config.client_config('/etc/salt/master')
    except Exception as err:
        log.error('Failed to read configuration for Mattermost! %s: %s',
                  type(err).__name__, err)
        raise CommandExecutionError(err)

    config = master_opts.get('mattermost', {})
    return config

def _get_hook():
    '''
    Retrieves and return the Mattermost's configured hook

    :return:            String: the hook string
    '''
    mattermost_config = _config()
    hook = mattermost_config.get('hook', None)
    if not hook:
        raise SaltInvocationError('No Mattermost Hook found')

    return hook


def _get_api_url():
    '''
    Retrieves and return the Mattermost's configured api url

    :return:            String: the api url string
    '''
    mattermost_config = _config()
    api_url = mattermost_config.get('api_url', None)
    if not api_url:
        raise SaltInvocationError('No Mattermost API URL found')

    return api_url

def _mattermost_query(url, message, channel, icon_url, username):
    '''
    Perform a query directly against the Mattermost Webhooks REST API.

    :param url:         The Mattermost Webhooks URL.
    :param message;     The message to send to the Mattermost channel.
    :return:            Boolean if message was sent successfully.
    '''
    headers = {
        'Content-Type': 'application/json'
    }

    payload = {
        'text': message
    }
    if channel:
        payload['channel'] = channel
    if icon_url:
        payload['icon_url'] = icon_url
    if username:
        payload['username'] = username

    response = requests.request('POST',
                                url,
                                headers=headers,
                                json=payload)

    if response.status_code != requests.codes.ok:
        response.raise_for_status()

    return True

def post_message(message,
                 api_url=None,
                 channel=None,
                 hook=None,
                 icon_url=None,
                 username=None):
    '''
    Send a message to a Mattermost channel.

    :param message:     The message to send to the Mattermost channel.
    :param api_url:     The Mattermost api url, if not specified in the configuration.
    :param channel:     An optional Mattermost channel ID.
    :param hook:        The Mattermost hook, if not specified in the configuration.
    :param icon_url:    An optional URL to a custom icon to be used.
    :param username:    An optional custom user to be displayed.
    :return:            Boolean if message was sent successfully.

    CLI Example:

    .. code-block:: bash

        salt '*' mattermost.post_message message='Build is done'
    '''

    if not api_url:
        api_url = _get_api_url()

    if not hook:
        hook = _get_hook()

    if not message:
        log.error('message is a required option.')

    base_url = _urljoin(api_url, '/hooks/')
    url = _urljoin(base_url, six.text_type(hook))

    res = _mattermost_query(url,
                            ':saltstack: ' + message,
                            channel,
                            icon_url,
                            username)
    return res
