import sys

from distutils.version import LooseVersion
from os.path import exists
from datetime import datetime

from .helpers import (nudgelog, 
                      download_apple_updates,
                      pending_apple_updates,
                      update_need_restart,
                      update_app_path,
                      get_os_version_major)                     
from .prefs import set_app_pref, app_pref, pref
from .constants import APPLE_SUS_PREFS_PATH, APPLE_SUS_PREFS

class NudgeLogic(object):
    def __init__(self, nudge_prefs):
        self.nudge_prefs = nudge_prefs
        self.min_major = nudge_prefs['minimum_os_version_major']
        self.local_url = nudge_prefs['local_url_for_upgrade']
        self.path_to_app = nudge_prefs['path_to_app']
        self.update_minor = nudge_prefs['update_minor']
        self.days_between_notif = nudge_prefs['days_between_notifications']
        self.major_version = get_os_version_major()
        self.minor_updates_required = False
        self.first_seen = False
        self.last_seen = False
    
    def start(self):
        if LooseVersion(self.min_major) > self.major_version:
            self._check_local_url()
        else:
            self._check_updates_availability()
            _only_background_updates(self.minor_updates_required())
            self._no_nudge_all_time()
        return self._update_nudgeprefs()
        
    def _check_local_url(self):
        if self.local_url:
            self.path_to_app = self.local_url
        else:
            if not exists(self.path_to_app):
                nudgelog('Update application not found! Exiting...')
                sys.exit(1)
    
    def _check_updates_availability(self):
        if self.update_minor:
            _download_updates()
    
    def _minor_updates_required(self):
        self.first_seen = app_pref('first_seen')
        self.last_seen = app_pref('last_seen')
        self.path_to_app = update_app_path()
        if _all_apple_sus_prefs():
            return update_need_restart()
        else:
            return True

    def _no_nudge_all_time(self):
        if (self.days_between_notif > 0 and
            self.first_seen and self.last_seen):
            difference = _last_seen_vs_today(self.last_seen)
            nudgelog(str(difference.days))
            if difference.days < self.days_between_notif:
                nudgelog(f'Last seen date is within notification threshold: {str(self.days_between_notif)}')
                sys.exit(0)
        if not self.first_seen:
            set_app_pref('first_seen', datetime.utcnow())
            self.first_seen = app_pref('first_seen')
    
    def _update_nudgeprefs(self):
        self.nudge_prefs['minimum_os_version_major'] = self.min_major
        self.nudge_prefs['local_url_for_upgrade'] = self.local_url
        self.nudge_prefs['path_to_app'] = self.path_to_app
        self.nudge_prefs['update_minor'] = self.update_minor
        self.nudge_prefs['days_between_notifications'] = self.days_between_notif
        return self.nudge_prefs

def _download_updates():
    nudgelog('Checking for minor updates.')
    swupd_output = download_apple_updates()
    if not swupd_output:
            nudgelog('Could not run softwareupdate')
            # Exit 0 as we might be offline
            # TODO: Check if we're offline to exit with the
            # appropriate code
            sys.exit(0)
    if pending_apple_updates() == [] or pending_apple_updates() is None:
            nudgelog('No Software updates to install')
            set_app_pref('first_seen', None)
            set_app_pref('last_seen', None)
            sys.exit(0)

def _all_apple_sus_prefs():
    sus_prefs =  [pref(key, APPLE_SUS_PREFS_PATH) for key in APPLE_SUS_PREFS]
    if False in sus_prefs:
        return False
    return True

def _only_background_updates(minor_updates_required):
    if not minor_updates_required:
        nudgelog('Only updates that can be installed in the background pending.')
        set_app_pref('first_seen', None)
        set_app_pref('last_seen', None)
        exit()

def _last_seen_vs_today(last_seen):
    today = datetime.utcnow()
    last_seen_strp = datetime.strptime(last_seen, '%Y-%m-%d %H:%M:%S +0000')
    difference = today - last_seen_strp