import subprocess
import json
import fleep
import pysubs2

def is_media_file(file_path):
    try:
        with open(file_path, "rb") as f:
            info = fleep.get(f.read(128))
            return any(t in info.type for t in ['audio', 'video'])
    except (FileNotFoundError, IsADirectoryError):
        return False

def is_video_file(file_path):
    try:
        with open(file_path, "rb") as f:
            info = fleep.get(f.read(128))
            return any(t in info.type for t in ['video'])
    except (FileNotFoundError, IsADirectoryError):
        return False