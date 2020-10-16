# encoding: utf-8
#
# Copyright 2009-2020 Greg Neagle.
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
prefs.py
Created by Greg Neagle on 2016-12-13.
Preferences functions and classes used by the munki tools.

Adapted for Nudge Tool by Joaquin Cabrerizo on 2020-03-27.
"""
# pylint: disable=broad-except
# PyLint cannot properly find names inside Cocoa libraries, so issues bogus
# No name 'Foo' in module 'Bar' warnings. Disable them.
# pylint: disable=E0611
from Foundation import (NSDate,
                        CFPreferencesAppValueIsForced,
                        CFPreferencesSetValue,
                        kCFPreferencesAnyUser,
                        kCFPreferencesCurrentHost)

from CoreFoundation import (CFPreferencesAppSynchronize,
                            CFPreferencesCopyAppValue,
                            CFPreferencesSetAppValue)

# pylint: enable=E0611

from .constants import BUNDLE_ID

DEFAULT_PREFS = {
    "button_title_text": "Ready to start the update?",
    "button_sub_titletext": "Click on the button below.",
    "cut_off_date": False,  # set it in the form "Y-m-d:H:M" or leave it as False
    "cut_off_date_warning": 3,
    "time_between_notifications": 0,
    "dismissal_count_threshold": 9999999,
    "dismissed_count": 0,
    "logo_path": "company_logo.png",
    "main_subtitle_text": "A friendly reminder from your local IT team",
    "main_title_text": "macOS Update",
    "minimum_os_sub_build_version": "10A00",
    "minimum_os_version": "10.14.6",
    "minimum_os_version_major": None,  # 'minimum_os_version'.rsplit('.', 1)[0]
    "more_info_url": False,
    "no_timer": False,
    # pylint: disable=line-too-long
    "paragraph1_text": "A fully up-to-date device is required to ensure that IT can your accurately protect your computer.",
    "paragraph2_text": "If you do not update your computer, you may lose access to some items necessary for your day-to-day tasks.",
    "paragraph3_text": "To begin the update, simply click on the button below and follow the provided steps.",
    # pylint: enable=line-too-long
    "paragraph_title_text": "A security update is required on your machine.",
    "path_to_app": "/Applications/Install macOS Mojave.app",
    "screenshot_path": "update_ss.png",
    "local_url_for_upgrade": False,  # set it as a string munki://detail-<item name> for instance
    "timer_day_1": 600,
    "timer_day_3": 7200,
    "timer_elapsed": 10,
    "timer_final": 60,
    "timer_initial": 14400,
    "random_delay": False,
    "update_minor": False,
    "update_minor_days": 14
}


class Preferences():
    """Class which directly reads/writes Apple CF preferences."""

    def __init__(self, bundle_id, user=kCFPreferencesAnyUser):
        """Init.

        Args:
            bundle_id: str, like 'ManagedInstalls'
        """
        if bundle_id.endswith('.plist'):
            bundle_id = bundle_id[:-6]
        self.bundle_id = bundle_id
        self.user = user

    def __getitem__(self, pref_name):
        """Get a preference value. Normal OS X preference search path applies"""
        return CFPreferencesCopyAppValue(pref_name, self.bundle_id)

    def get(self, pref_name, default=None):
        """Return a preference or the default value"""
        if pref_name not in self:
            return default
        return self.__getitem__(pref_name)

    def is_managed(self, pref_name):
        """Return if a preference is managed or not"""
        return CFPreferencesAppValueIsForced(pref_name, self.bundle_id)


def set_pref(pref_name, pref_value):
    """Sets a preference, writing it to
    /Library/Preferences/ManagedInstalls.plist.
    This should normally be used only for 'bookkeeping' values;
    values that control the behavior of munki may be overridden
    elsewhere (by MCX, for example)"""
    try:
        CFPreferencesSetValue(
            pref_name, pref_value, BUNDLE_ID,
            kCFPreferencesAnyUser, kCFPreferencesCurrentHost)
        CFPreferencesAppSynchronize(BUNDLE_ID)
    except BaseException:
        pass


def set_app_pref(pref_name, value):
    """Sets a value in Preferences.
    Uses CoreFoundation.
    Args:
       pref_name: str preference name to set.
       value: value to set it to.
    """
    CFPreferencesSetAppValue(pref_name, value, BUNDLE_ID)
    CFPreferencesAppSynchronize(BUNDLE_ID)


def pref(pref_name, bundle_id=BUNDLE_ID):
    """
    Return a preference and whether exists or not.
    Since this uses CFPreferencesCopyAppValue, Preferences
    can be defined several places. Precedence is:
        - MCX/configuration profile
        - /var/root/Library/Preferences/ByHost/ManagedInstalls.XXXXXX.plist
        - /var/root/Library/Preferences/ManagedInstalls.plist
        - /Library/Preferences/ManagedInstalls.plist
        - .GlobalPreferences defined at various levels (ByHost, user, system)
        - default_prefs defined here.
    """
    pref_value = CFPreferencesCopyAppValue(pref_name, bundle_id)

    if pref_value is None:
        pref_value = DEFAULT_PREFS.get(pref_name)
        # we're using a default value. We'll write it out to
        # /Library/Preferences/<BUNDLE_ID>.plist for admin
        # discoverability
        if pref_value is not None:
            set_pref(pref_name, pref_value)
    if isinstance(pref_value, NSDate):
        # convert NSDate/CFDates to strings
        pref_value = str(pref_value)
    return pref_value


def app_pref(pref_name):
    """Returns a preference from the specified domain.

    Uses CoreFoundation.

    Args:
      pref_name: str preference name to get.
    """
    pref_value = CFPreferencesCopyAppValue(pref_name, BUNDLE_ID)
    if pref_value is None:
        pref_value = DEFAULT_PREFS.get(pref_name)
        # we're using a default value. We'll write it out to
        # ~/Library/Preferences/<BUNDLE_ID>.plist for admin
        # discoverability
        if pref_value is not None:
            set_app_pref(pref_name, pref_value)

        if isinstance(pref_value, NSDate):
            # convert NSDate/CFDates to strings
            pref_value = str(str(pref_value))
    if isinstance(pref_value, NSDate):
        # convert NSDate/CFDates to strings
        pref_value = str(str(pref_value))
    return pref_value


if __name__ == '__main__':
    print('This is a library of support tools for the Nudge Tool.')
