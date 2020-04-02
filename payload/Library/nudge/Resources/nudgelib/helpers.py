import os
import sys
import random
import time
import subprocess
import optparse
import platform
from datetime import datetime, timedelta
import re
from distutils.version import LooseVersion

from SystemConfiguration import SCDynamicStoreCopyConsoleUser
from Foundation import NSBundle, NSString, NSLog, NSDate
from CoreFoundation import (CFPreferencesAppSynchronize,
                            CFPreferencesCopyAppValue,
                            CFPreferencesSetAppValue)

import objc
from . import gurl

from .prefs import pref
from .constants import MIN_BUILD

def downloadfile(options):
    '''download file with gurl'''
    connection = gurl.Gurl.alloc().initWithOptions_(options)
    percent_complete = -1
    bytes_received = 0
    connection.start()
    try:
        filename = options['name']
    except KeyError:
        nudgelog(('No \'name\' key defined in json for %s' %
               pkgregex(options['file'])))
        sys.exit(1)

    try:
        while not connection.isDone():
            if connection.destination_path:
                # only print progress info if we are writing to a file
                if connection.percentComplete != -1:
                    if connection.percentComplete != percent_complete:
                        percent_complete = connection.percentComplete
                        nudgelog(('Downloading %s - Percent complete: %s ' % (
                            filename, percent_complete)))
                elif connection.bytesReceived != bytes_received:
                    bytes_received = connection.bytesReceived
                    nudgelog(('Downloading %s - Bytes received: %s ' % (
                        filename, bytes_received)))

    except (KeyboardInterrupt, SystemExit):
        # safely kill the connection then fall through
        connection.cancel()
    except Exception:  # too general, I know
        # Let us out! ... Safely! Unexpectedly quit dialogs are annoying ...
        connection.cancel()
        # Re-raise the error
        raise

    if connection.error is not None:
        nudgelog(('Error: %s %s ' % (str(connection.error.code()),
                                  str(connection.error.localizedDescription()))))
        if connection.SSLerror:
            nudgelog('SSL error: %s ' % (str(connection.SSLerror)))
    if connection.response is not None:
        nudgelog('Status: %s ' % (str(connection.status)))
        nudgelog('Headers: %s ' % (str(connection.headers)))
    if connection.redirection != []:
        nudgelog('Redirection: %s ' % (str(connection.redirection)))

def get_console_username():
    '''Uses Apple's SystemConfiguration framework to get the current
    console username'''
    user_name, current_user_uid, _ = SCDynamicStoreCopyConsoleUser(None, None, None)
    return user_name

def not_in_userland():
    '''Bail if we are not in a user session'''
    user_name = get_console_username()
    if user_name in (None, 'loginwindow', '_mbsetupuser'):
        nudgelog('not in a user session')
        return True

def get_os_sub_build_version():
    '''Return sub build of macOS'''
    cmd = ['/usr/sbin/sysctl', '-n', 'kern.osversion']
    run = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = run.communicate()[0]
    return LooseVersion(output.decode("utf-8").strip())

def get_os_version():
    '''Return OS version.'''
    return LooseVersion(platform.mac_ver()[0])


def get_os_version_major():
    '''Return major OS version.'''
    full_os = platform.mac_ver()[0]
    # Sometimes the OS version will return without the dot release
    # For example, it may show as 10.15.0 instead of 10.15
    if len(full_os.split('.')) == 3:
        return LooseVersion(full_os.rsplit('.', 1)[0])
    elif len(full_os.split('.')) == 2:
        return LooseVersion(full_os)
    else:
        nudgelog('Cannot reliably determine OS major version. Exiting...')
        exit(1)

def get_parsed_options():
    '''Return the parsed options and args for this application.'''
    # Options
    usage = '%prog [options]'
    options = optparse.OptionParser(usage=usage)
    options.add_option('--headers', help=('Optional: Auth headers'))
    options.add_option('--jsonurl', help=('Optional: URL to json file.'))
    options.add_option('--config', help=('Optional: Get Nudge config info.'))
    return options.parse_args()


def get_serial():
    '''Get system serial number'''
    # Credit to Michael Lynn
    IOKit_bundle = NSBundle.bundleWithIdentifier_('com.apple.framework.IOKit')

    functions = [("IOServiceGetMatchingService", b"II@"),
                 ("IOServiceMatching", b"@*"),
                 ("IORegistryEntryCreateCFProperty", b"@I@@I"),
                ]

    objc.loadBundleFunctions(IOKit_bundle, globals(), functions)
    # pylint: disable=undefined-variable
    serial = IORegistryEntryCreateCFProperty(
        IOServiceGetMatchingService(
            0,
            IOServiceMatching(
                "IOPlatformExpertDevice".encode("utf-8")
            )),
        NSString.stringWithString_("IOPlatformSerialNumber"),
        None,
        0)
    # pylint: enable=undefined-variable
    return serial

def nudge_already_loaded():
    '''Check if nudge is already loaded'''
    nudge_string = '/Library/nudge/Resources/nudge'
    cmd = ['/bin/ps', '-o', 'pid', '-o', 'command']
    run = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = run.communicate()
    status = output.split(b'\n')
    current_pid = str(os.getpid())
    for line in status:
        if bytes(nudge_string, 'utf-8') in line:
            if bytes(current_pid, 'utf-8') in line:
                pass
            else:
                nudgelog('nudge already loaded!')
                return True
    return False

def nudgelog(text):
    '''logger for nudge'''
    NSLog('[Nudge] ' + text)

def download_apple_updates():
    '''Download everything Softwareupdate has to offer'''

    cmd = [
        '/usr/sbin/softwareupdate',
        '-da',
        '--force'
    ]

    try:
        return subprocess.check_output(cmd)
    except subprocess.CalledProcessError:
        return None


def pending_apple_updates():
    '''Pending apple updates
    Returns a dict of pending updates'''

    return pref('RecommendedUpdates', BUNDLE_ID='com.apple.SoftwareUpdate')


def update_app_path():
    software_updates_prefpane = '/System/Library/PreferencePanes/SoftwareUpdate.prefPane'
    if os.path.exists(software_updates_prefpane):
        return 'file://{}'.format(software_updates_prefpane)
    else:
        return 'macappstore://showUpdatesPage'

def update_need_restart():
    swupd_output = subprocess.check_output(['/usr/sbin/softwareupdate', '-la'])
    for line in swupd_output.splitlines():
        if b'restart' in line.lower():
            return True
    return False

def pkgregex(pkgpath):
    '''regular expression for pkg'''
    try:
        # capture everything after last / in the pkg filepath
        pkgname = re.compile(r"[^/]+$").search(pkgpath).group(0)
        return pkgname
    except AttributeError as IndexError:
        return pkgpath

def random_delay(delay=True):
    if delay:
       rand_delay = random.randint(1,1200)
       nudgelog(f'Delaying run for {rand_delay} seconds...')
       time.sleep(rand_delay)

def threshold_by_version(min_build, min_os, min_major, update_minor):
    full = get_os_version()
    major = get_os_version_major()
    build = get_os_sub_build_version()
    if build >= LooseVersion(min_build) and update_minor:
        nudgelog(f'OS build is higher or equal to the minimum threshold: {str(build)}')
        sys.exit(0)
    if full >= LooseVersion(min_os) and not update_minor:
        nudgelog(f'OS version is higher or equal to the minimum threshold: {str(full)}')
        sys.exit(0)
    if major >= LooseVersion(min_major) and not update_minor:
        part1 = 'OS major version is higher or equal to the minimum threshold'
        part2 = 'minor updates not enabled' 
        nudgelog(f'{part1} and {part2}: {str(full)}')
        sys.exit(0)
    nudgelog(f'OS version is below the minimum threshold: {str(full)}')
    if update_minor and LooseVersion(min_build) > build:
        nudgelog(f'OS version is below the minimum threshold subversion: {str(build)}')

def start_info(minimum_os_version, update_minor,
               minimum_os_sub_build_version,
               dismissal_count_threshold):
    nudgelog(f'Target OS version: {minimum_os_version}')
    if update_minor:
        if minimum_os_sub_build_version == MIN_BUILD:
            update_minor = False
        else:
            nudgelog(f'Target OS subversion: {minimum_os_sub_build_version}')
    nudgelog(f'Dismissal count threshold: {dismissal_count_threshold}')
    return update_minor


if __name__ == '__main__':
    print('This is a library of support tools for the Nudge Tool.')
