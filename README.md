# SaltStack Extension Modules for Mattermost

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/277eff921fb34e05a543e9a52e234bc9)](https://www.codacy.com/app/madrisan/saltstack-mattermost?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=madrisan/saltstack-mattermost&amp;utm_campaign=Badge_Grade)
[![License](https://img.shields.io/badge/License-Apache--2.0-blue.svg)](https://spdx.org/licenses/Apache-2.0.html)

Two SaltStack extension modules for interacting with [Mattermost](https://mattermost.com/) Incoming Webhooks
and for sending posts using the REST API v4.

![](images/mattermost_logo.png?raw=true)

This module requires a configuration profile to be configured in either the minion or, as in our implementation, in the master configuration file (`/etc/salt/master.d/mattermost.conf`).

## Mattermost Incoming Webhooks

This module requires very little configuration:

    mattermost:
      url: https://slack.mydomain.com
      hook: 3tdgo8restnxiykdx88wqtxryr

This Python module should be saved as `salt/_modules/mattermost.py`.

### Implemented Methods

#### mattermost.post_message(message, url=None, channel=None, hook=None, icon_url=None, username=None)

Send a message to a Mattermost channel.

Returns `True` if message was sent successfully, `False` otherwise.

    salt '*' mattermost.post_message 'The application has been deployed' username='myapp'

Arguments:

    message:         The message to send to the Mattermost channel.
    url:             The Mattermost url, if not specified in the configuration.
    channel:         An optional Mattermost channel ID.
    hook:            The Mattermost hook, if not specified in the configuration.
    icon_url:        An optional URL to a custom icon to be used.
    username:        An optional custom user to be displayed.

## Mattermost Posts via REST API v4

This module requires the following configuration:

    mattermost:
      url: https://slack.mydomain.com
      bearer: 2argt6hytstyhvki3ag4qhlnyq
      channels:
        mychannel:
          id: o02pxs06mmtg4fa4wyuzqv1x9z
      verify: /etc/ssl/certs/ca-certificates.crt

This Python module should be saved as `salt/_modules/mattermost.py`.

### Implemented Methods

#### mattermost.query_apiv4(method, endpoint, payload=None)

Make a query to the Mattermost REST API v4.

    salt '*' mattermost.query_apiv4 GET /users

The following additional arguments are also accepted:

    method:          The query method: 'GET', 'LIST', 'POST', 'PUT'.
    endpoint;        The endpoint of the query.
    payload:         An optional query payload to be send.

#### mattermost.posts(message, team, channel, message_prefix=':newspaper_roll: ')

Create a new post in a channel.

The query result in JSON format or an exception in case of error.

    salt '*' mattermost.posts 'This is an important message'

Arguments:

    message:         The message to send to the Mattermost channel.
    team:            The Mattermost team.
    channel:         The Mattermost channel where the message msut be sent.
    message_prefix:  The message profix (by default the the 'newspaper_roll' icon).

#### mattermost.get_user_by_username(username)

Get a user object by providing a username.

Returns the query result in JSON format.

    salt '*' mattermost.get_user_by_username a.username

Arguments:

    username:        The Mattermost channel where the message msut be sent.

#### mattermost.get_users

Get the available informations for all the Mattermost users.

Returns the query result in JSON format.

    salt '*' mattermost.get_users
