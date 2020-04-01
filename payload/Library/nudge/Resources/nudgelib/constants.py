"""
constants.py

Created by Joaquin Cabrerizo on 2020-03-30.

Commonly used constants
"""

BUNDLE_ID = 'com.erikng.nudge'
ACCEPTABLE_APPS = [
    'com.apple.loginwindow',
    'com.apple.systempreferences',
    'org.python.python'
]
NUDGE_DISMISSED_COUNT = 0
APPLE_SUS_PREFS_PATH = '/Library/Preferences/com.apple.SoftwareUpdate'
APPLE_SUS_PREFS = ('AutomaticCheckEnabled',
                   'AutomaticDownload',
                   'AutomaticallyInstallMacOSUpdates')

if __name__ == '__main__':
    print('This is a library of support tools for the Nudge Tool.')