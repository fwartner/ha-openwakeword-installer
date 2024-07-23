import logging
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.exceptions import ConfigEntryNotReady
from datetime import timedelta

from .const import DOMAIN, CONF_REPOSITORIES, CONF_REPOSITORY_URL, CONF_FOLDER_PATH, CONF_SCAN_INTERVAL
from .update import update_wakewords

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the Wakeword Installer sensor."""
    repositories = entry.data.get(CONF_REPOSITORIES, [])

    coordinator = WakewordUpdateCoordinator(hass, repositories)

    await coordinator.async_refresh()

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    async_add_entities(
        [WakewordUpdateStatusSensor(coordinator, repo) for repo in repositories],
        True
    )

class WakewordUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Wakeword update status."""

    def __init__(self, hass, repositories):
        """Initialize."""
        self.repositories = repositories
        update_interval = min(repo.get(CONF_SCAN_INTERVAL, 3600) for repo in repositories)

        super().__init__(
            hass,
            _LOGGER,
            name="Wakeword Update Status",
            update_interval=timedelta(seconds=update_interval),
        )

    async def _async_update_data(self):
        """Fetch data from API endpoint."""
        results = {}
        for repo in self.repositories:
            try:
                success = await self.hass.async_add_executor_job(
                    update_wakewords,
                    repo[CONF_REPOSITORY_URL],
                    repo.get(CONF_FOLDER_PATH, '')
                )
                results[repo[CONF_REPOSITORY_URL]] = "Up to date" if success else "Update failed"
            except Exception as err:
                raise UpdateFailed(f"Error communicating with API: {err}")
        return results

class WakewordUpdateStatusSensor(Entity):
    """Representation of a Wakeword Update Status sensor."""

    def __init__(self, coordinator, repository):
        """Initialize the sensor."""
        self.coordinator = coordinator
        self._repository_url = repository[CONF_REPOSITORY_URL]
        self._folder_path = repository.get(CONF_FOLDER_PATH, '')
        self._name = f"Wakeword Update Status: {self._repository_url}"

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get(self._repository_url, "Unknown")

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            "repository_url": self._repository_url,
            "folder_path": self._folder_path,
        }

    @property
    def should_poll(self):
        """No need to poll. Coordinator notifies entity of updates."""
        return False

    @property
    def available(self):
        """Return if entity is available."""
        return self.coordinator.last_update_success

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        self.async_on_remove(
            self.coordinator.async_add_listener(
                self.async_write_ha_state
            )
        )

    async def async_update(self):
        """Update the entity."""
        await self.coordinator.async_request_refresh()
