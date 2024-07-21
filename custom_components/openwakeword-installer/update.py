import git
import os
import logging

from .const import CONF_REPOSITORY_URL, CONF_FOLDER

_LOGGER = logging.getLogger(__name__)

def update_wakewords(repository_url, folder='', target_directory='/config/wakeword_installer'):
    """Update wakewords from the given repository URL."""
    if folder:
        target_directory = os.path.join(target_directory, folder)

    try:
        if not os.path.exists(target_directory):
            os.makedirs(target_directory)
            _LOGGER.info(f"Created target directory: {target_directory}")

        if os.path.exists(os.path.join(target_directory, '.git')):
            repo = git.Repo(target_directory)
            _LOGGER.info(f"Pulling latest changes in repository: {repository_url} to {target_directory}")
            repo.remote().pull()
        else:
            _LOGGER.info(f"Cloning repository: {repository_url} to {target_directory}")
            git.Repo.clone_from(repository_url, target_directory)
        _LOGGER.info(f"Repository {repository_url} has been successfully updated in {target_directory}")
    except Exception as e:
        _LOGGER.error(f"Error updating wakewords from repository {repository_url} to {target_directory}: {e}")
