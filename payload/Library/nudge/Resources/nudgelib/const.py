import os

nudge_dismissed_count = 0
acceptable_apps = [
    'com.apple.loginwindow',
    'com.apple.systempreferences',
    'org.python.python'
]
nudge_path = os.path.dirname(os.path.realpath(__file__))
json_path = os.path.join(nudge_path, 'nudge.json')