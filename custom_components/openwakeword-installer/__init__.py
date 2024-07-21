import os
import shutil
import logging
import datetime
import homeassistant.util.dt as dt_util

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.typing import ConfigType
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.event import async_track_time_interval

from .const import DOMAIN, CONF_REPOSITORY_URL, CONF_FOLDER_PATH, CONF_SCAN_INTERVAL
from .update import update_wakewords

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Wakeword Installer component."""

    # Ensure directories are created
    await hass.async_add_executor_job(create_directory, '/share/openwakeword')

    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Wakeword Installer from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    # Clone the repository immediately after configuration
    await hass.async_add_executor_job(update_wakewords, entry.data[CONF_REPOSITORY_URL], entry.data.get(CONF_FOLDER_PATH, ''))

    # Schedule regular updates
    scan_interval = entry.data.get(CONF_SCAN_INTERVAL, 3600)
    async def scheduled_update(_):
        await hass.async_add_executor_job(update_wakewords, entry.data[CONF_REPOSITORY_URL], entry.data.get(CONF_FOLDER_PATH, ''))

    # Schedule the update at the specified interval
    async_track_time_interval(hass, scheduled_update, datetime.timedelta(seconds=scan_interval))

    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    hass.data[DOMAIN].pop(entry.entry_id)

    # Delete the openwakeword directory
    await hass.async_add_executor_job(delete_directory, '/share/openwakeword')

    return True

def create_directory(path: str):
    """Create directory if it does not exist."""
    if not os.path.exists(path):
        os.makedirs(path)

def delete_directory(path: str):
    """Delete directory if it exists."""
    if os.path.exists(path):
        shutil.rmtree(path)
        _LOGGER.info(f"Deleted directory: {path}")
