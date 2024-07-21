import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

from .const import DOMAIN, CONF_REPOSITORY_URL, CONF_FOLDER_PATH, CONF_SCAN_INTERVAL

@config_entries.HANDLERS.register(DOMAIN)
class WakewordInstallerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Wakeword Installer."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        errors = {}
        if user_input is not None:
            return self.async_create_entry(title="Wakeword Installer", data=user_input)

        data_schema = vol.Schema({
            vol.Required(CONF_REPOSITORY_URL): str,
            vol.Optional(CONF_FOLDER_PATH): str,
            vol.Optional(CONF_SCAN_INTERVAL, default=3600): int,
        })

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return WakewordInstallerOptionsFlowHandler(config_entry)

class WakewordInstallerOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle an options flow for Wakeword Installer."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        data_schema = vol.Schema({
            vol.Optional(CONF_REPOSITORY_URL, default=self.config_entry.options.get(CONF_REPOSITORY_URL, self.config_entry.data.get(CONF_REPOSITORY_URL, ''))): str,
            vol.Optional(CONF_FOLDER_PATH, default=self.config_entry.options.get(CONF_FOLDER_PATH, self.config_entry.data.get(CONF_FOLDER_PATH, ''))): str,
            vol.Optional(CONF_SCAN_INTERVAL, default=3600): int,
            vol.Optional("update_wakewords", default=False): bool,
        })

        return self.async_show_form(step_id="init", data_schema=data_schema)
