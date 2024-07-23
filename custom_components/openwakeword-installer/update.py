import git
import os
import logging
import shutil

from .const import CONF_REPOSITORY_URL, CONF_FOLDER_PATH

_LOGGER = logging.getLogger(__name__)

def update_wakewords(repository_url, folder='', base_directory='/share/openwakeword'):
    """Update wakewords from the given repository URL."""
    try:
        repo_name = os.path.basename(repository_url.rstrip('/'))
        target_repo_dir = os.path.join(base_directory, repo_name)

        if not os.path.exists(target_repo_dir):
            os.makedirs(target_repo_dir)
            _LOGGER.info(f"Created target directory: {target_repo_dir}")

        if os.path.exists(os.path.join(target_repo_dir, '.git')):
            repo = git.Repo(target_repo_dir)
            _LOGGER.info(f"Pulling latest changes in repository: {repository_url} to {target_repo_dir}")
            repo.remote().pull()
        else:
            _LOGGER.info(f"Cloning repository: {repository_url} to {target_repo_dir}")
            git.Repo.clone_from(repository_url, target_repo_dir)
        _LOGGER.info(f"Repository {repository_url} has been successfully updated in {target_repo_dir}")

        # Handle folder specific logic
        target_path = os.path.join(target_repo_dir, folder) if folder else target_repo_dir
        process_files(target_path, base_directory)

    except Exception as e:
        _LOGGER.error(f"Error updating wakewords from repository {repository_url} to {target_repo_dir}: {e}")

def process_files(source_directory, target_directory):
    """Process .tflite files from the source directory to the target directory."""
    try:
        if not os.path.exists(target_directory):
            os.makedirs(target_directory)

        for root, dirs, files in os.walk(source_directory):
            for file in files:
                if file.endswith('.tflite'):
                    full_file_path = os.path.join(root, file)
                    shutil.copy(full_file_path, target_directory)
                    _LOGGER.info(f"Copied {file} to {target_directory}")
    except Exception as e:
        _LOGGER.error(f"Error processing files from {source_directory} to {target_directory}: {e}")
