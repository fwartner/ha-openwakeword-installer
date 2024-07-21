import os
import logging

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.typing import ConfigType
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN, CONF_REPOSITORY_URL, CONF_FOLDER
from .update import update_wakewords

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Wakeword Installer component."""

    # Change the directory to a path within the Home Assistant configuration directory
    directory_path = hass.config.path("wakeword_installer")

    # Ensure directories are created
    await hass.async_add_executor_job(create_directory, directory_path)

    # Register services
    async def handle_update_wakewords(call: ServiceCall):
        repository_url = call.data.get(CONF_REPOSITORY_URL)
        folder = call.data.get(CONF_FOLDER, '')
        if repository_url:
            _LOGGER.info(f"Updating wakewords from repository: {repository_url} with folder: {folder}")
            await hass.async_add_executor_job(update_wakewords, repository_url, folder, directory_path)
        else:
            _LOGGER.error("No repository URL provided for wakeword update.")

    hass.services.async_register(DOMAIN, 'update_wakewords', handle_update_wakewords)
    _LOGGER.info("Wakeword Installer service registered")

    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Wakeword Installer from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    hass.data[DOMAIN].pop(entry.entry_id)
### Updated `__init__.py`

Ensure this file correctly calls `update_wakewords` and logs the process:

```python
import os
import logging

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.typing import ConfigType
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN, CONF_REPOSITORY_URL, CONF_FOLDER
from .update import update_wakewords

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Wakeword Installer component."""

    # Change the directory to a path within the Home Assistant configuration directory
    directory_path = hass.config.path("wakeword_installer")

    # Ensure directories are created
    await hass.async_add_executor_job(create_directory, directory_path)

    # Register services
    async def handle_update_wakewords(call: ServiceCall):
        repository_url = call.data.get(CONF_REPOSITORY_URL)
        folder = call.data.get(CONF_FOLDER, '')
        if repository_url:
            _LOGGER.info(f"Updating wakewords from repository: {repository_url} with folder: {folder}")
            await hass.async_add_executor_job(update_wakewords, repository_url, folder, directory_path)
        else:
            _LOGGER.error("No repository URL provided for wakeword update.")

    hass.services.async_register(DOMAIN, 'update_wakewords', handle_update_wakewords)
    _LOGGER.info("Wakeword Installer service registered")

    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Wakeword Installer from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    hass.data[DOMAIN].pop(entry.entry_id)
    return True

def create_directory(path: str):
    """Create directory if it does not exist."""
    if not os.path.exists(path):
        os.makedirs(path)
