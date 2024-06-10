import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
import git
from .const import DOMAIN, CONF_REPOSITORY_URL, CONF_FOLDER_PATH

@callback
def configured_instances(hass):
    return [entry.data[CONF_REPOSITORY_URL] for entry in hass.config_entries.async_entries(DOMAIN)]

class WakeWordInstallerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for WakeWord Installer."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            if user_input[CONF_REPOSITORY_URL] in configured_instances(self.hass):
                errors["base"] = "already_configured"
            else:
                is_valid, error = await self.hass.async_add_executor_job(self._validate_repository, user_input[CONF_REPOSITORY_URL])
                if is_valid:
                    return self.async_create_entry(title="WakeWord Installer", data=user_input)
                else:
                    errors["base"] = error

        data_schema = vol.Schema({
            vol.Required(CONF_REPOSITORY_URL): str,
            vol.Optional(CONF_FOLDER_PATH, default=""): str,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    def _validate_repository(self, url):
        """Validate that the URL is a valid Git repository."""
        try:
            repo = git.Repo.clone_from(url, '/tmp/temp_repo', depth=1)
            # Cleanup the cloned repository
            import shutil
            shutil.rmtree('/tmp/temp_repo')
            return True, None
        except git.exc.GitError as e:
            return False, "invalid_repository"
        except Exception as e:
            return False, "cannot_connect"

    async def async_step_import(self, user_input=None):
        """Handle the import from configuration.yaml."""
        return await self.async_step_user(user_input)
