# HOW TO:
# - Place your addon directory in the "Blender Foundation/Blender/VERSION/scripts/addons" directory
# - Place this file in the root directory of your multifile addon
# - Start blender and change e.g. the version number of your addon to see live refresh working

# - Below you can change what files should trigger a refresh and disable the logs
# - When sharing your addon you can remove this file or disable live refresh below
#     - You don't need to do this if you add files that could change when the addon is installed to the blacklist and disable logs

# Contribute at https://github.com/joshuaKnauber/easy_modules/tree/main

import os
import sys
from threading import Thread
from time import sleep

# When True, when a file in this directory is changed, the addon will be reregistered
LIVE_REFRESH = True

# When True, logs will be printed to the console
LOGS = True

# File extensions that should trigger a refresh. Specific files can be overwritten in the blacklist
EXTENSIONS = [
    "py",
]

# Add relative paths to files to the root of your addon like "settings/settings.json" that shouldn't trigger a refresh
BLACKLIST = [
    "file_watch.py",
]


def init():
    start_watching_file_changes()


tracked_times = {}  # dict to store relative filepaths and their last modified times


def start_watching_file_changes():
    """ Watch for file changes in the current directory and trigger a refresh """
    if LOGS:
        print("LIVE REFRESH: Watching for file changes in " +
              os.path.dirname(__file__))
    # TODO blender sometimes stops with an exit violation, is this because of another addon or because of the thread?
    thread = Thread(target=check_file_changes, daemon=True)
    thread.start()


def check_file_changes():
    """ Checks all files in this directory for changes and calls refresh if a change is found """
    # Walk through all files and refresh if they have been edited
    curr_directory = os.path.dirname(__file__)
    for root, _, files in os.walk(curr_directory):
        for file in files:
            file = os.path.relpath(os.path.join(root, file), curr_directory)
            time = os.stat(os.path.join(curr_directory, file)).st_mtime
            # Don't track files in the blacklist
            if not file.split(".")[-1] in EXTENSIONS or file in BLACKLIST:
                continue
            # Track untracked files
            if file not in tracked_times:
                tracked_times[file] = time
                continue
            # Refresh if the file has been edited
            if time > tracked_times[file]:
                tracked_times[file] = time
                refresh(file)
                sleep(4)
                check_file_changes()
                return
    sleep(1)
    check_file_changes()


def refresh(changed_file):
    if LOGS:
        print("LIVE REFRESH: Refreshing, changed " + changed_file)
    reload_modules(changed_file)


def reload_modules(changed_file):
    bpy.ops.script.reload()


# Run init if live refresh is enabled
if LIVE_REFRESH:
    init()
