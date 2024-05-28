import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN, CONF_REPOSITORY_URL, CONF_FOLDER_PATH

class OpenWakeWordConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="OpenWakeWord", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_REPOSITORY_URL): str,
                vol.Optional(CONF_FOLDER_PATH, default=""): str,
            })
        )
