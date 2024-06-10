import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import HomeAssistantType
from homeassistant.helpers.event import async_track_time_interval
from datetime import timedelta

from .const import DOMAIN, CONF_REPOSITORY_URL, CONF_FOLDER_PATH, CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
from .update import update_repository

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistantType, entry: ConfigEntry):
    """Set up WakeWord Installer from a config entry."""
    repository_url = entry.data[CONF_REPOSITORY_URL]
    folder_path = entry.data.get(CONF_FOLDER_PATH, "")
    scan_interval = timedelta(seconds=entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL))

    async def handle_update_wakewords_service(call):
        """Handle the service call to update wake words."""
        _LOGGER.info("Manual update of wake words triggered")
        await hass.async_add_executor_job(update_repository, repository_url, folder_path)

    hass.services.async_register(
        DOMAIN, "update_wakewords", handle_update_wakewords_service
    )

    sensor = WakeWordInstallerSensor(repository_url, folder_path)
    async_add_entities([sensor], True)

    async_track_time_interval(hass, sensor.async_update, scan_interval)

    return True

async def async_unload_entry(hass: HomeAssistantType, entry: ConfigEntry):
    """Unload WakeWord Installer config entry."""
    hass.services.async_remove(DOMAIN, "update_wakewords")
    await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    return True

class WakeWordInstallerSensor(SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, repository_url, folder_path):
        """Initialize the sensor."""
        self._state = "idle"
        self._last_update = None
        self._repository_url = repository_url
        self._folder_path = folder_path
        self._repo = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return "WakeWord Installer Update Status"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            "last_update": self._last_update
        }

    async def async_update(self, *_):
        """Fetch new state data for the sensor."""
        self._state = "checking"
        _LOGGER.debug("Checking for updates...")

        try:
            if self._repo is None:
                self._repo = git.Repo.clone_from(self._repository_url, '/tmp/wakeword_installer_repo')
            else:
                self._repo.remotes.origin.pull()

            files = [f for f in self._repo.tree().traverse() if f.path.endswith(".tflite")]
            if self._folder_path:
                files = [f for f in files if f.path.startswith(self._folder_path)]

            if files:
                _LOGGER.debug("Wake words found: %s", files)
                self._state = "updating"
                self._last_update = datetime.datetime.now().isoformat()
                # Copy files to the target directory
                for file in files:
                    file_path = f"/share/openwakeword/{file.path.split('/')[-1]}"
                    with open(file_path, 'wb') as f:
                        f.write(file.data_stream.read())
            else:
                _LOGGER.debug("No new wake words found.")
                self._state = "idle"
        except Exception as e:
            _LOGGER.error("Error updating wake words: %s", e)
            self._state = "error"
