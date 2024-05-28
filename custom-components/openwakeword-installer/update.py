import os
import subprocess
import tempfile
import shutil
from datetime import datetime

def check_for_updates(repo_url, folder_path):
    TARGET_DIR = "/share/openwakeword"
    os.makedirs(TARGET_DIR, exist_ok=True)

    temp_dir = tempfile.mkdtemp()
    new_files = False
    last_update = datetime.now().isoformat()

    try:
        result = subprocess.run(
            ['git', 'clone', '--depth', '1', '--filter=blob:none', '--sparse', repo_url, temp_dir],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        os.chdir(temp_dir)
        if folder_path:
            subprocess.run(['git', 'sparse-checkout', 'set', folder_path], check=True)
        else:
            subprocess.run(['git', 'sparse-checkout', 'set', '*'], check=True)

        for root, _, files in os.walk(temp_dir):
            for file in files:
                if file.endswith('.tflite'):
                    src_file = os.path.join(root, file)
                    dest_file = os.path.join(TARGET_DIR, file)
                    if not os.path.exists(dest_file) or not filecmp.cmp(src_file, dest_file, shallow=False):
                        shutil.copy2(src_file, TARGET_DIR)
                        new_files = True
    finally:
        shutil.rmtree(temp_dir)

    return new_files, last_update
