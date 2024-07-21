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
            vol.Required(CONF_REPOSITORY_URL, description="Enter the URL of the GitHub repository containing the wakewords"): str,
            vol.Optional(CONF_FOLDER_PATH, description="Specify an optional folder within the repository containing the wakewords (e.g., 'en')"): str,
            vol.Optional(CONF_SCAN_INTERVAL, default=3600, description="Enter the scan interval in seconds"): int,
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
            if user_input.get("update_wakewords"):
                self.hass.async_create_task(
                    self.hass.services.async_call(
                        DOMAIN, "update_wakewords",
                        {
                            CONF_REPOSITORY_URL: user_input[CONF_REPOSITORY_URL],
                            CONF_FOLDER_PATH: user_input.get(CONF_FOLDER_PATH, ''),
                            CONF_SCAN_INTERVAL: user_input.get(CONF_SCAN_INTERVAL, 3600)
                        }
                    )
                )
            return self.async_create_entry(title="", data=user_input)

        data_schema = vol.Schema({
            vol.Optional(CONF_REPOSITORY_URL, default=self.config_entry.options.get(CONF_REPOSITORY_URL, self.config_entry.data.get(CONF_REPOSITORY_URL, '')), description="Enter the URL of the GitHub repository containing the wakewords"): str,
            vol.Optional(CONF_FOLDER_PATH, default=self.config_entry.options.get(CONF_FOLDER_PATH, self.config_entry.data.get(CONF_FOLDER_PATH, '')), description="Specify an optional folder within the repository containing the wakewords (e.g., 'en')"): str,
            vol.Optional(CONF_SCAN_INTERVAL, default=self.config_entry.options.get(CONF_SCAN_INTERVAL, 3600), description="Enter the scan interval in seconds"): int,
            vol.Optional("update_wakewords", default=False, description="Enable this option to update the wakewords now"): bool,
        })

        return self.async_show_form(step_id="init", data_schema=data_schema)
