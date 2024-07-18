import asyncio
from homeassistant.helpers.entity import Entity
from homeassistant.const import CONF_URL

from .const import CONF_REPOSITORY_URL, CONF_FOLDER

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Wakeword Installer sensor based on a config entry."""
    repository_url = config_entry.data.get(CONF_REPOSITORY_URL)
    folder = config_entry.data.get(CONF_FOLDER, '')

    if not repository_url:
        hass.components.logger.error("No repository URL provided in the configuration.")
        return

    async_add_entities([WakewordSensor(repository_url, folder)], True)

class WakewordSensor(Entity):
    """Representation of a Wakeword Installer sensor."""

    def __init__(self, repository_url, folder):
        """Initialize the sensor."""
        self._state = None
        self._repository_url = repository_url
        self._folder = folder

    @property
    def name(self):
        """Return the name of the sensor."""
        return 'Wakeword Installer'

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    async def async_update(self):
        """Fetch new state data for the sensor."""
        self._state = await self.fetch_wakewords()

    async def fetch_wakewords(self):
        """Fetch the wakewords from the repository URL."""
        # Implementation for fetching wakewords goes here
        if self._folder:
            return f"Wakewords fetched from {self._repository_url}/{self._folder}"
        else:
            return f"Wakewords fetched from {self._repository_url}"
