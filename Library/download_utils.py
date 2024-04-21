import os
import time

def wait_for_download_completion(directory, initial_files, timeout=1000):
    end_time = time.time() + timeout
    while time.time() < end_time:
        current_files = set(os.listdir(directory))
        new_files = current_files - initial_files
        if new_files and all(not file.endswith('.crdownload') and not file.endswith('.tmp') for file in current_files):
            return True
        time.sleep(1)
