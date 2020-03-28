import os
import sys
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
import gurl

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

def get_console_username_info():
    '''Uses Apple's SystemConfiguration framework to get the current
    console username'''
    return SCDynamicStoreCopyConsoleUser(None, None, None)


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
    options.add_option('--jsonurl', help=('Required: URL to json file.'))
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
                return True
    return False

def nudgelog(text):
    '''logger for nudge'''
    NSLog('[Nudge] ' + text)

def pref(pref_name, domain='com.erikng.nudge'):
    """Returns a preference from the specified domain.

    Uses CoreFoundation.

    Args:
      pref_name: str preference name to get.
    """
    pref_value = CFPreferencesCopyAppValue(
        pref_name, domain)
    if isinstance(pref_value, NSDate):
        # convert NSDate/CFDates to strings
        pref_value = str(pref_value)
    return pref_value


def set_pref(pref_name, value, domain='com.erikng.nudge'):
    """Sets a value in Preferences.
    Uses CoreFoundation.
    Args:
       pref_name: str preference name to set.
       value: value to set it to.
    """
    CFPreferencesSetAppValue(pref_name, value, domain)
    CFPreferencesAppSynchronize(domain)

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

    return pref('RecommendedUpdates', 'com.apple.SoftwareUpdate')


def update_app_path():
    software_updates_prefpane = '/System/Library/PreferencePanes/SoftwareUpdate.prefPane'
    if os.path.exists(software_updates_prefpane):
        return 'file://{}'.format(software_updates_prefpane)
    else:
        return 'macappstore://showUpdatesPage'


def pkgregex(pkgpath):
    '''regular expression for pkg'''
    try:
        # capture everything after last / in the pkg filepath
        pkgname = re.compile(r"[^/]+$").search(pkgpath).group(0)
        return pkgname
    except AttributeError as IndexError:
        return pkgpath


def get_minimum_minor_update_days(update_minor_days, pending_apple_updates, nudge_su_prefs):
    '''Lowest number of days before something is forced'''
    if pending_apple_updates == [] or pending_apple_updates is None:
        return update_minor_days

    lowest_days = update_minor_days
    todays_date = datetime.utcnow()
    for item in nudge_su_prefs:
        for update in pending_apple_updates:
            if str(item['name']) == str(update['Product Key']):
                nudgelog('{} has a forced date'.format(update['Product Key']))
                force_date_strp = datetime.strptime(item['force_install_date'], '%Y-%m-%d-%H:%M')
                date_diff_seconds = (force_date_strp - todays_date).total_seconds()
                date_diff_days = int(round(date_diff_seconds / 86400))
                if date_diff_days < lowest_days:
                    lowest_days = date_diff_days

    return lowest_days

if __name__ == '__main__':
    print('This is a library of support tools for the Nudge Tool.')
