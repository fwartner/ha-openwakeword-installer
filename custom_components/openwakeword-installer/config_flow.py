import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

from .const import DOMAIN

@callback
def configured_instances(hass):
    return [entry.data["repository_url"] for entry in hass.config_entries.async_entries(DOMAIN)]

class WakeWordInstallerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for WakeWord Installer."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            if user_input["repository_url"] in configured_instances(self.hass):
                errors["base"] = "already_configured"
            else:
                # Validate the URL
                # Add your validation code here
                return self.async_create_entry(title="WakeWord Installer", data=user_input)

        data_schema = vol.Schema({
            vol.Required("repository_url"): str,
            vol.Optional("folder_path", default=""): str,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    async def async_step_import(self, user_input=None):
        """Handle the import from configuration.yaml."""
        return await self.async_step_user(user_input)
