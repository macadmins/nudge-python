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
UI_BUTTONS = (
    'button.update',
    'button.moreinfo',
    'button.ok',
    'button.understand')
UI_FIELDS = (
    'field.titletext',
    'field.subtitletext',
    'field.updatetext',
    'field.paragraph1',
    'field.paragraph2',
    'field.paragraph3',
    'field.h1text',
    'field.h2text')
UI_NUDGE_PREFS = (
    'main_title_text',
    'main_subtitle_text',
    'paragraph_title_text',
    'paragraph1_text',
    'paragraph2_text',
    'paragraph3_text',
    'button_title_text',
    'button_sub_titletext')
UI_FIELDS_2 = (
    'field.username',
    'field.serialnumber',
    'field.updated')
COMPANY_LOGO = 'image.companylogo'
UPDATESS = 'image.updatess'
DEFAULT_IMAGES = (
    'company_logo.png',
    'update_ss.png')
UPDATE = 'button.update'
MORE_INFO = 'button.moreinfo'
OK = 'button.ok'
UNDERSTAND = 'button.understand'
TITLE_TEXT = 'field.titletext'
SUBTITLE_TEXT = 'field.subtitletext'
UPDATE_TEXT = 'field.updatetext'
PARAGRAPH1 = 'field.paragraph1'
PARAGRAPH2 = 'field.paragraph2'
PARAGRAPH3 = 'field.paragraph3'
H1TEXT = 'field.h1text'
H2TEXT = 'field.h2text'
USERNAME = 'field.username'
SERIAL_NUMBER = 'field.serialnumber'
UPDATED = 'field.updated'
DAYS_REMAINING = 'field.daysremaining'
DAYS_REMAINING_TEXT = 'field.daysremainingtext'
PAST_DATE = 'Past date!'
NO_TIMER = 'Timer invalidated!'
MIN_BUILD = '10A00'

if __name__ == '__main__':
    print('This is a library of support tools for the Nudge Tool.')
