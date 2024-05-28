from homeassistant.helpers.entity import Entity

from .const import DOMAIN

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the OpenWakeWord sensor."""
    async_add_entities([OpenWakeWordSensor(hass, config_entry.data)], True)

class OpenWakeWordSensor(Entity):
    """Representation of a Sensor."""

    def __init__(self, hass, config):
        """Initialize the sensor."""
        self.hass = hass
        self._state = None
        self._last_update = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return "OpenWakeWord Update Status"

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

    def update(self):
        """Fetch new state data for the sensor."""
        # Logic to update sensor state
        self._state = "idle"  # Example state
        self._last_update = "2023-05-27T12:34:56"  # Example last update time
