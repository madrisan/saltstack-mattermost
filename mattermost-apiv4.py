# -*- coding: utf-8 -*-
'''
A simple SaltStack extension module for sending posts messages
using the REST API v4 provided by Mattermost.
Copyright (C) 2020 Davide Madrisan <davide.madrisan@gmail.com>

This module requires a configuration profile to be configured
in either the minion or, as in our implementation, in the master
configuration file (/etc/salt/master.d/mattermost.conf).
This profile requires very little:

.. code-block:: yaml

    mattermost:
      url: https://slack.mydomain.com
      bearer: 2argt6hytstyhvki3ag4qhlnyq
      channels:
        mychannel:
          id: o02pxs06mmtg4fa4wyuzqv1x9z
      verify: /etc/ssl/certs/ca-certificates.crt

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

def query_apiv4(method, endpoint, payload=None):
    '''
    Make a query to the Mattermost REST API v4.

    :param method:      The query method: 'GET', 'LIST', 'POST', 'PUT'.
    :param endpoint;    The endpoint of the query.
    :param:             An optional query payload tp be send.
    :return:            The query result in JSON format or an exception in case of error.

    CLI Example:

    .. code-block:: bash

        salt '*' mattermost.query_apiv4 GET /users
    '''
    mattermost_config = _config()

    try:
        mattermost_url = mattermost_config['url']
        bearer = mattermost_config['bearer']
    except KeyError as err:
        log.error('Failed to get the required Mattermost configuration! %s: %s',
                  type(err).__name__, err)
        raise salt.exceptions.CommandExecutionError(
            "Cannot find the required Mattemost configuration!")

    verify = mattermost_config.get('verify', '/etc/ssl/certs/ca-certificates.crt')

    # avoid the duplication of the heading slash because it's not allowed
    # by the Mattermost API
    if endpoint.startswith('/'):
        endpoint = endpoint[1:]

    resource = 'api/v4/{0}'.format(endpoint)
    url = "{0}/{1}".format(mattermost_url, resource)
    headers = {
        'Authorization': 'Bearer {0}'.format(bearer)
    }

    response = requests.request(method,
                                url,
                                headers=headers,
                                json=payload,
                                verify=verify)

    if response.status_code == requests.codes.not_found:
        raise salt.exceptions.CommandExecutionError(
            'resource not found: {}'.format(url))

    if response.status_code != requests.codes.ok:
        response.raise_for_status()

    return response.json()

def get_user_by_username(username):
    '''
    Get a user object by providing a username.

    :param username:    A Mattermost user name.
    :return:            The query result in JSON format.

    CLI Example:

    .. code-block:: bash

        salt '*' mattermost.get_user_by_username a.username
    '''
    res = query_apiv4('GET', '/users/username/{0}'.format(username))
    return res

def get_users():
    '''
    Get the available informations for all the Mattermost users.

    :return:            The query result in JSON format.

    CLI Example:

    .. code-block:: bash

        salt '*' mattermost.get_users
    '''
    res = query_apiv4('GET', '/users')
    return res

def posts(message,
          team,
          channel,
          message_prefix=':newspaper_roll: '):
    '''
    Create a new post in a channel.

    :param message:     The message to send to the Mattermost channel.
    :param team:        The Mattermost team.
    :param channel:     The Mattermost channel where the message msut be sent.
    :message_prefix:    The message profix (by default the the 'newspaper_roll' icon).
    :return:            The query result in JSON format or an exception in case of error.

    CLI Example:

    .. code-block:: bash

        salt '*' mattermost.posts 'This is an important message'
    '''
    def _get_channel_by_name(team, channel_name):
        channel_info = {}
        try:
            team_info = _get_team_by_name(team)
            team_id = team_info.get('id')
            channel_info = query_apiv4('GET',
                                      '/teams/{}/channels/name/{}'.format(
                                          team_id,
                                          channel_name))
        except Exception as err:
            log.error('Cannot get the channel informations! %s: %s',
                      type(err).__name__, err)

        return channel_info

    def _get_team_by_name(team_name):
        res = query_apiv4('GET', '/teams/name/{}'.format(team_name))
        return res

    mattermost_config = _config()
    channel_id = (mattermost_config
                  .get('channels', {})
                  .get(channel, {})
                  .get('id', None))

    # the configuration does not provide the id of the required channel,
    # fallback to the mattermost API
    if not channel_id:
        channel_info = _get_channel_by_name(team, channel)
        channel_id = channel_info.get('id', None)

    if not channel_id:
        raise salt.exceptions.CommandExecutionError(
            'cannot found the channel id for {}'.format(channel))

    payload = {
        'channel_id': channel_id,
        'message': '{0}{1}'.format(message_prefix, message),
        'props': { }
    }

    res = query_apiv4('POST', '/posts', payload)
    return res
