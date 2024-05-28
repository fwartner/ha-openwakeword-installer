import logging
import datetime
import git
import voluptuous as vol

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import CONF_URL
from homeassistant.helpers.event import async_track_time_interval

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = datetime.timedelta(minutes=60)  # Check every hour

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the WakeWord Installer sensor."""
    repository_url = config_entry.data[CONF_URL]
    folder_path = config_entry.data.get("folder_path", "")

    sensor = WakeWordInstallerSensor(repository_url, folder_path)
    async_add_entities([sensor], True)

    async_track_time_interval(hass, sensor.async_update, SCAN_INTERVAL)

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
