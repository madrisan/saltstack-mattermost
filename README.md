# SaltStack Extension Module for Mattermost

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/277eff921fb34e05a543e9a52e234bc9)](https://www.codacy.com/app/madrisan/saltstack-mattermost?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=madrisan/saltstack-mattermost&amp;utm_campaign=Badge_Grade)
[![License](https://img.shields.io/badge/License-Apache--2.0-blue.svg)](https://spdx.org/licenses/Apache-2.0.html)

A SaltStack extension module for interacting with [Mattermost](https://mattermost.com/) Incoming Webhooks

![](images/mattermost_logo.png?raw=true)

This module requires a configuration profile to be configured in either the minion or, as in our implementation, in the master configuration file (`/etc/salt/master.d/mattermost.conf`).

This profile requires very little:

    mattermost:
      url: https://slack.mydomain.com
      hook: 3tdgo8restnxiykdx88wqtxryr

This Python module should be saved as `salt/_modules/mattermost.py`.

## Implemented Methods

### mattermost.post_message

Send a message to a Mattermost channel.
Returns True if message was sent successfully, False otherwise.

    salt '*' mattermost.post_message 'The application has been deployed' username='myapp'

Optional parameters:

    url:         The Mattermost url, if not specified in the configuration.
    channel:     An optional Mattermost channel ID.
    hook:        The Mattermost hook, if not specified in the configuration.
    icon_url:    An optional URL to a custom icon to be used.
    username:    An optional custom user to be displayed.
