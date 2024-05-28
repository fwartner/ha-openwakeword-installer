import logging
from datetime import timedelta
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import async_track_time_interval
from .const import DOMAIN, DEFAULT_SCAN_INTERVAL
from .update import check_for_updates

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    repository_url = config_entry.data["repository_url"]
    folder_path = config_entry.data.get("folder_path", "")

    sensor = OpenWakeWordSensor(hass, repository_url, folder_path)
    async_add_entities([sensor], update_before_add=True)

    async def async_update_data(_):
        await sensor.async_update()

    async_track_time_interval(hass, async_update_data, timedelta(seconds=DEFAULT_SCAN_INTERVAL))
    return True

class OpenWakeWordSensor(Entity):
    def __init__(self, hass, repository_url, folder_path):
        self._hass = hass
        self._state = None
        self._repository_url = repository_url
        self._folder_path = folder_path
        self._attr_name = "OpenWakeWord Update Status"
        self._attr_unique_id = f"openwakeword_{repository_url}"
        self._last_update = None

    @property
    def name(self):
        return self._attr_name

    @property
    def state(self):
        return self._state

    @property
    def unique_id(self):
        return self._attr_unique_id

    @property
    def extra_state_attributes(self):
        return {
            "last_update": self._last_update
        }

    async def async_update(self):
        _LOGGER.debug("Checking for updates")
        new_files, last_update = await self._hass.async_add_executor_job(
            check_for_updates, self._repository_url, self._folder_path
        )
        self._state = "updated" if new_files else "no_update"
        self._last_update = last_update
