import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

from .const import DOMAIN, CONF_REPOSITORIES, CONF_REPOSITORY_URL, CONF_FOLDER_PATH, CONF_SCAN_INTERVAL

class WakewordInstallerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Wakeword Installer."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        """Initialize."""
        self.repositories = []

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        errors = {}
        if user_input is not None:
            self.repositories.append(user_input)
            return await self.async_step_add_another()

        data_schema = vol.Schema({
            vol.Required(CONF_REPOSITORY_URL): str,
            vol.Optional(CONF_FOLDER_PATH): str,
            vol.Optional(CONF_SCAN_INTERVAL, default=3600): int,
        })

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    async def async_step_add_another(self, user_input=None):
        """Handle adding another repository."""
        if user_input is not None:
            if user_input["add_another"]:
                return await self.async_step_user()
            return self.async_create_entry(title="Wakeword Installer", data={CONF_REPOSITORIES: self.repositories})

        return self.async_show_form(
            step_id="add_another",
            data_schema=vol.Schema({
                vol.Required("add_another"): bool,
            }),
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

        repositories = self.config_entry.data.get(CONF_REPOSITORIES, [])
        options = {}

        for i, repo in enumerate(repositories):
            options[f"{CONF_REPOSITORY_URL}_{i}"] = repo.get(CONF_REPOSITORY_URL, "")
            options[f"{CONF_FOLDER_PATH}_{i}"] = repo.get(CONF_FOLDER_PATH, "")
            options[f"{CONF_SCAN_INTERVAL}_{i}"] = repo.get(CONF_SCAN_INTERVAL, 3600)

        data_schema = vol.Schema({
            vol.Optional(key): (str if "url" in key or "path" in key else int)
            for key in options
        })

        return self.async_show_form(step_id="init", data_schema=data_schema)
