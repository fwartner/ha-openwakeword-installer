import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import HomeAssistantType

from .const import DOMAIN, CONF_REPOSITORY_URL, CONF_FOLDER_PATH
from .update import update_repository

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistantType, entry: ConfigEntry):
    """Set up WakeWord Installer from a config entry."""
    repository_url = entry.data[CONF_REPOSITORY_URL]
    folder_path = entry.data.get(CONF_FOLDER_PATH, "")

    async def handle_update_wakewords_service(call):
        """Handle the service call to update wake words."""
        _LOGGER.info("Manual update of wake words triggered")
        await hass.async_add_executor_job(update_repository, repository_url, folder_path)

    hass.services.async_register(
        DOMAIN, "update_wakewords", handle_update_wakewords_service
    )

    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )
    return True

async def async_unload_entry(hass: HomeAssistantType, entry: ConfigEntry):
    """Unload WakeWord Installer config entry."""
    hass.services.async_remove(DOMAIN, "update_wakewords")
    await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    return True
