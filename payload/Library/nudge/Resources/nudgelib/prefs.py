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
# PyLint cannot properly find names inside Cocoa libraries, so issues bogus
# No name 'Foo' in module 'Bar' warnings. Disable them.
# pylint: disable=E0611
from Foundation import (NSDate,
                        CFPreferencesAppSynchronize,
                        CFPreferencesAppValueIsForced,
                        CFPreferencesCopyAppValue,
                        CFPreferencesCopyKeyList,
                        CFPreferencesCopyValue,
                        CFPreferencesSetValue,
                        kCFPreferencesAnyUser,
                        kCFPreferencesAnyHost,
                        kCFPreferencesCurrentUser,
                        kCFPreferencesCurrentHost)

from CoreFoundation import (CFPreferencesAppSynchronize,
                            CFPreferencesCopyAppValue,
                            CFPreferencesSetAppValue)

# pylint: enable=E0611

from constants import BUNDLE_ID

DEFAULT_PREFS = {
    "button_title_text": "Ready to start the update?",
    "button_sub_titletext": "Click on the button below.",
    "cut_off_date": False,
    "cut_off_date_warning": 3,
    "days_between_notifications": 0,
    "dismissal_count_threshold": 9999999,
    "logo_path": "company_logo.png",
    "main_subtitle_text": "A friendly reminder from your local IT team",
    "main_title_text": "macOS Update",
    "minimum_os_sub_build_version": "10A00",
    "minimum_os_version": "10.14.6",
    "minimum_os_version_major": None,  #'minimum_os_version'.rsplit('.', 1)[0]
    "more_info_url": False,
    "no_timer": False,
    "paragraph1_text": "A fully up-to-date device is required to ensure that IT can your accurately protect your computer.",
    "paragraph2_text": "If you do not update your computer, you may lose access to some items necessary for your day-to-day tasks.",
    "paragraph3_text": "To begin the update, simply click on the button below and follow the provided steps.",
    "paragraph_title_text": "A security update is required on your machine.",
    "path_to_app": "/Applications/Install macOS Mojave.app",
    "screenshot_path": "update_ss.png",
    "local_url_for_upgrade": False,
    "timer_day_1": 600,
    "timer_day_3": 7200,
    "timer_elapsed": 10,
    "timer_final": 60,
    "timer_initial": 14400,
    "random_delay": False,
    "nudge_su_prefs": [],
    "update_minor": False,
    "update_minor_days": 14
}

class Preferences(object):
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

    def __iter__(self):
        """Iterator for keys in the specific 'level' of preferences; this
        will fail to iterate all available keys for the preferences domain
        since OS X reads from multiple 'levels' and composites them."""
        keys = CFPreferencesCopyKeyList(
            self.bundle_id, self.user, kCFPreferencesCurrentHost)
        if keys is not None:
            for i in keys:
                yield i

    def __contains__(self, pref_name):
        """Since this uses CFPreferencesCopyAppValue, it will find a preference
        regardless of the 'level' at which it is stored"""
        pref_value = CFPreferencesCopyAppValue(pref_name, self.bundle_id)
        return pref_value is not None

    def __getitem__(self, pref_name):
        """Get a preference value. Normal OS X preference search path applies"""
        return CFPreferencesCopyAppValue(pref_name, self.bundle_id)

    def __setitem__(self, pref_name, pref_value):
        """Sets a preference. if the user is kCFPreferencesCurrentUser, the
        preference actually gets written at the 'ByHost' level due to the use
        of kCFPreferencesCurrentHost"""
        CFPreferencesSetValue(
            pref_name, pref_value, self.bundle_id, self.user,
            kCFPreferencesCurrentHost)
        CFPreferencesAppSynchronize(self.bundle_id)

    def __delitem__(self, pref_name):
        """Delete a preference"""
        self.__setitem__(pref_name, None)

    def __repr__(self):
        """Return a text representation of the class"""
        return '<%s %s>' % (self.__class__.__name__, self.bundle_id)

    def get(self, pref_name, default=None):
        """Return a preference or the default value"""
        if not pref_name in self:
            return default
        return self.__getitem__(pref_name)
    
    def contains(self, pref_name):
        """Return whether a preference is available or not"""
        return self.__contains__(pref_name)


class ManagedInstallsPreferences(Preferences):
    """Preferences which are read using 'normal' OS X preferences precedence:
        Managed Preferences (MCX or Configuration Profile)
        ~/Library/Preferences/ByHost/ManagedInstalls.XXXX.plist
        ~/Library/Preferences/ManagedInstalls.plist
        /Library/Preferences/ManagedInstalls.plist
    Preferences are written to
        /Library/Preferences/ManagedInstalls.plist
    Since this code is usually run as root, ~ is root's home dir"""
    # pylint: disable=too-few-public-methods
    def __init__(self):
        Preferences.__init__(self, 'ManagedInstalls', kCFPreferencesAnyUser)


class SecureManagedInstallsPreferences(Preferences):
    """Preferences which are read using 'normal' OS X preferences precedence:
        Managed Preferences (MCX or Configuration Profile)
        ~/Library/Preferences/ByHost/ManagedInstalls.XXXX.plist
        ~/Library/Preferences/ManagedInstalls.plist
        /Library/Preferences/ManagedInstalls.plist
    Preferences are written to
        ~/Library/Preferences/ByHost/ManagedInstalls.XXXX.plist
    Since this code is usually run as root, ~ is root's home dir"""
    # pylint: disable=too-few-public-methods
    def __init__(self):
        Preferences.__init__(self, 'ManagedInstalls', kCFPreferencesCurrentUser)


def reload_prefs():
    """Uses CFPreferencesAppSynchronize(BUNDLE_ID)
    to make sure we have the latest prefs. Call this
    if you have modified /Library/Preferences/ManagedInstalls.plist
    or /var/root/Library/Preferences/ManagedInstalls.plist directly"""
    CFPreferencesAppSynchronize(BUNDLE_ID)


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

def pref(pref_name, BUNDLE_ID=BUNDLE_ID):
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
    pref_value = CFPreferencesCopyAppValue(pref_name, BUNDLE_ID)

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
        pref_value = str(pref_value)
    return pref_value


def get_config_level(domain, pref_name, value):
    '''Returns a string indicating where the given preference is defined'''
    if value is None:
        return '[not set]'
    if CFPreferencesAppValueIsForced(pref_name, domain):
        return '[MANAGED]'
    # define all the places we need to search, in priority order
    levels = [
        {'file': ('/var/root/Library/Preferences/ByHost/'
                  '%s.xxxx.plist' % domain),
         'domain': domain,
         'user': kCFPreferencesCurrentUser,
         'host': kCFPreferencesCurrentHost
        },
        {'file': '/var/root/Library/Preferences/%s.plist' % domain,
         'domain': domain,
         'user': kCFPreferencesCurrentUser,
         'host': kCFPreferencesAnyHost
        },
        {'file': ('/var/root/Library/Preferences/ByHost/'
                  '.GlobalPreferences.xxxx.plist'),
         'domain': '.GlobalPreferences',
         'user': kCFPreferencesCurrentUser,
         'host': kCFPreferencesCurrentHost
        },
        {'file': '/var/root/Library/Preferences/.GlobalPreferences.plist',
         'domain': '.GlobalPreferences',
         'user': kCFPreferencesCurrentUser,
         'host': kCFPreferencesAnyHost
        },
        {'file': '/Library/Preferences/%s.plist' % domain,
         'domain': domain,
         'user': kCFPreferencesAnyUser,
         'host': kCFPreferencesCurrentHost
        },
        {'file': '/Library/Preferences/.GlobalPreferences.plist',
         'domain': '.GlobalPreferences',
         'user': kCFPreferencesAnyUser,
         'host': kCFPreferencesCurrentHost
        },
    ]
    for level in levels:
        if (value == CFPreferencesCopyValue(
                pref_name, level['domain'], level['user'], level['host'])):
            return '[%s]' % level['file']
    if value == DEFAULT_PREFS.get(pref_name):
        return '[default]'
    return '[unknown]'


def print_config():
    '''Prints the current Nudge configuration'''
    print('Current Nudge configuration:')
    max_pref_name_len = max([len(pref_name) for pref_name in DEFAULT_PREFS])
    for pref_name in sorted(DEFAULT_PREFS):
        if pref_name in ('first_seen', 'last_seen'):
            # skip it
            continue
        value = pref(pref_name)
        where = get_config_level(BUNDLE_ID, pref_name, value)
        repr_value = value
        print(('%' + str(max_pref_name_len) + 's: %5s %s ') % (
            pref_name, repr_value, where))
    # also print com.apple.SoftwareUpdate CatalogURL config if
    # Munki is configured to install Apple updates
    if pref('InstallAppleSoftwareUpdates'):
        print('Current Apple softwareupdate configuration:')
        domain = 'com.apple.SoftwareUpdate'
        pref_name = 'CatalogURL'
        value = CFPreferencesCopyAppValue(pref_name, domain)
        where = get_config_level(domain, pref_name, value)
        repr_value = value
        print(('%' + str(max_pref_name_len) + 's: %5s %s ') % (
            pref_name, repr_value, where))


if __name__ == '__main__':
    print('This is a library of support tools for the Nudge Tool.')