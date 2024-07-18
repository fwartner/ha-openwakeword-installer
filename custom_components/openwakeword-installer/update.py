import git
import os

from .const import CONF_REPOSITORY_URL

def update_wakewords(repository_url, target_directory='/share/openwakeword'):
    """Update wakewords from the given repository URL."""
    if not os.path.exists(target_directory):
        os.makedirs(target_directory)

    if os.path.exists(target_directory + '/.git'):
        repo = git.Repo(target_directory)
        repo.remote().pull()
    else:
        git.Repo.clone_from(repository_url, target_directory)
