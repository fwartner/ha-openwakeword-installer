import os
import shutil
import logging
import datetime
import homeassistant.util.dt as dt_util

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.typing import ConfigType
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.event import async_track_time_interval

from .const import DOMAIN, CONF_REPOSITORIES, CONF_REPOSITORY_URL, CONF_FOLDER_PATH, CONF_SCAN_INTERVAL
from .update import update_wakewords

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Wakeword Installer component."""
    await hass.async_add_executor_job(create_directory, '/share/openwakeword')

    async def handle_update_wakewords_service(call: ServiceCall):
        repositories = call.data.get(CONF_REPOSITORIES, [])
        for repository in repositories:
            repository_url = repository.get(CONF_REPOSITORY_URL)
            folder_path = repository.get(CONF_FOLDER_PATH, '')
            success = await hass.async_add_executor_job(update_wakewords, repository_url, folder_path)
            if success:
                _LOGGER.info(f"Wakewords updated from {repository_url} (folder: {folder_path})")
            else:
                _LOGGER.error(f"Failed to update wakewords from {repository_url} (folder: {folder_path})")

    hass.services.async_register(DOMAIN, "update_wakewords", handle_update_wakewords_service)

    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Wakeword Installer from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    for repository in entry.data.get(CONF_REPOSITORIES, []):
        await hass.async_add_executor_job(update_wakewords, repository[CONF_REPOSITORY_URL], repository.get(CONF_FOLDER_PATH, ''))

        scan_interval = repository.get(CONF_SCAN_INTERVAL, 3600)
        async def scheduled_update(_):
            await hass.async_add_executor_job(update_wakewords, repository[CONF_REPOSITORY_URL], repository.get(CONF_FOLDER_PATH, ''))

        async_track_time_interval(hass, scheduled_update, datetime.timedelta(seconds=scan_interval))

    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    hass.data[DOMAIN].pop(entry.entry_id)

    for repository in entry.data.get(CONF_REPOSITORIES, []):
        repo_name = os.path.basename(repository[CONF_REPOSITORY_URL].rstrip('/'))
        repository_dir = os.path.join('/share/openwakeword', repo_name)
        await hass.async_add_executor_job(delete_directory, repository_dir)

    return True

async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)

def create_directory(path: str):
    """Create directory if it does not exist."""
    if not os.path.exists(path):
        os.makedirs(path)

def delete_directory(path: str):
    """Delete directory if it exists."""
    if os.path.exists(path):
        shutil.rmtree(path)
        _LOGGER.info(f"Deleted directory: {path}")
