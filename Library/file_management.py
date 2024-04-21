import os
import re

def find_latest_zip_file(directory):
    zip_files = [f for f in os.listdir(directory) if f.endswith('.zip')]
    sorted_files = sorted(zip_files, key=lambda x: [int(y) if y.isdigit() else y for y in re.split('(_|\D)', x)])
    return sorted_files[-1] if sorted_files else None

def update_last_processed_file(filename, directory):
    with open(os.path.join(directory, 'last_processed.txt'), 'w') as f:
        f.write(filename)

def get_last_processed_file(directory):
    try:
        with open(os.path.join(directory, 'last_processed.txt'), 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return None
