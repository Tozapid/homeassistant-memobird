"""
Custom component for Home Assistant to enable print messages via Memobird.

Example configuration.yaml entry:

notify:
  - name: memobird
    platform: memobird
    api_key: ***
    device_id: ***
    
With this custom component loaded, you can print messaged to Memobird.
"""

import logging

import voluptuous as vol

from homeassistant.components.notify import (
    ATTR_DATA, ATTR_TITLE, ATTR_TITLE_DEFAULT,
    PLATFORM_SCHEMA, BaseNotificationService)
from homeassistant.const import CONF_API_KEY
import homeassistant.helpers.config_validation as cv

REQUIREMENTS = ['pymobird==0.2.1']

_LOGGER = logging.getLogger(__name__)

CONF_DEVICE_ID = 'device_id'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_API_KEY): cv.string,
    vol.Required(CONF_DEVICE_ID): cv.string,
})


# pylint: disable=unused-argument
def get_service(hass, config, discovery_info=None):
    """Get the Memobird notification service."""
    from custom_components.memobird.pymobird.pymobird import SimplePymobird

    memobird = SimplePymobird(config[CONF_API_KEY], config[CONF_DEVICE_ID])
    
    return MemobirdNotificationService(memobird)


class MemobirdNotificationService(BaseNotificationService):
    """Implement the notification service for the Memobird Printer."""

    def __init__(self, bird):
        """Initialize the service."""
        self.memobird = bird

    def send_message(self, message=None, have_title=True, have_datetime=True, **kwargs):
        """Print a message."""
        from custom_components.memobird.pymobird.pymobird import Content
        import datetime
        SEPARATOR = "--------------------------------\n"
        #
        if not message:
            raise ValueError("You can't print an empty message! It wastes paper! :(")
        #
        title = kwargs.get(ATTR_TITLE, ATTR_TITLE_DEFAULT)
        title = '[{title}]'.format(title=title)
        title = title.center(32, '=')
        #
        now = datetime.datetime.now()
        now = now.isoformat().split('.')[0].replace('T', ' ').replace('-', '/')
        now = now.strip().center(32, ' ')
        #
        c = Content()
        if have_title:
            c.add_text(title)
        else:
            c.add_text(SEPARATOR)
        #
        if have_datetime:
            c.add_text(now)
            c.add_text(SEPARATOR)
        #
        message = message.strip()
        if not message.endswith('\n') and len(message) != 32:
            message += '\n'
        c.add_text(message)
        c.add_text(SEPARATOR)
        #
        printId = self.memobird.print_multi_part_content(c)
        _LOGGER.info("Print sheduled with id: {id}".format(id=printId) + " The message is: {message}".format(message=message))
