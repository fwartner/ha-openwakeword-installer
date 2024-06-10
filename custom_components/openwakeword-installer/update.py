import os
import shutil
import tempfile
import git
import logging

_LOGGER = logging.getLogger(__name__)

def update_repository(repo_url, folder_path):
    """Clone or update the repository and copy .tflite files to the target directory."""
    TARGET_DIR = "/share/openwakeword"
    os.makedirs(TARGET_DIR, exist_ok=True)

    temp_dir = tempfile.mkdtemp()
    try:
        repo = git.Repo.clone_from(repo_url, temp_dir, depth=1)
        if folder_path:
            repo.git.sparse_checkout_set(folder_path)
        else:
            repo.git.sparse_checkout_set("*")

        files = [f for f in repo.tree().traverse() if f.path.endswith(".tflite")]
        for file in files:
            src_file = os.path.join(temp_dir, file.path)
            dest_file = os.path.join(TARGET_DIR, os.path.basename(file.path))
            shutil.copy2(src_file, dest_file)

    except git.exc.GitError as e:
        _LOGGER.error(f"Git error: {e}")
    except Exception as e:
        _LOGGER.error(f"Error updating wake words: {e}")
    finally:
        shutil.rmtree(temp_dir)
