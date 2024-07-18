import git
import os

from .const import CONF_REPOSITORY_URL, CONF_FOLDER

def update_wakewords(repository_url, folder='', target_directory='/share/openwakeword'):
    """Update wakewords from the given repository URL."""
    if folder:
        target_directory = os.path.join(target_directory, folder)

    if not os.path.exists(target_directory):
        os.makedirs(target_directory)

    if os.path.exists(target_directory + '/.git'):
        repo = git.Repo(target_directory)
        repo.remote().pull()
    else:
        git.Repo.clone_from(repository_url, target_directory)
