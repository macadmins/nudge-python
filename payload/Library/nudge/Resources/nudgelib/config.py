import sys
import json
import tempfile
import shutil
import time

from urllib.parse import unquote, urlparse
from urllib.error import URLError
from urllib.request import urlopen
from os.path import dirname, realpath, isfile, join

from .prefs import (Preferences, DEFAULT_PREFS,
                    set_app_pref, app_pref)
from .helpers import get_parsed_options, nudgelog, downloadfile
from .constants import BUNDLE_ID


class Config():
    '''Class which set up the nudge tool configuration'''
    def __init__(self, config_type, sidecar=None):
        self.config_type = config_type
        self.sidecar = sidecar

    def get_config(self):
        '''This function will return preferences to use in nudge tool'''
        if self.config_type == 'Managed':
            nudge_prefs = _get_prefs()
            return nudge_prefs

        if self.config_type == 'Bundled' and self.sidecar is not None:
            nudge_prefs = _get_bundled_json(self.sidecar)
            return nudge_prefs

        if self.config_type == 'Downloaded' and self.sidecar is not None:
            json_data = _get_json_data(self.sidecar)
            json_url = json_data['url']
            json_path = json_data['file']
            if _url_scheme(json_data['url']) == 'file':
                nudge_prefs = _get_file_json(json_url, json_path)
                return nudge_prefs
            nudge_prefs = _get_web_json(json_data, json_url, json_path)
            return nudge_prefs

        nudgelog('Wrong config type')
        sys.exit(1)


def get_config_type():
    '''Get nudge config type'''
    preferences = Preferences(BUNDLE_ID)

    if [preferences.is_managed(key) for key in DEFAULT_PREFS
            if preferences.is_managed(key)]:
        nudgelog('Using managed preferences...')
        return ('Managed', None)

    nudge_path = dirname(dirname(realpath(__file__)))
    json_path = join(nudge_path, 'nudge.json')
    if isfile(json_path):
        nudgelog('Using bundled nudge JSON file...')
        return ('Bundled', json_path)

    opts, _ = get_parsed_options()
    if opts.jsonurl:
        nudgelog('Getting nudge JSON file from {} ...'.format(opts.jsonurl))
        return ('Downloaded', opts)

    nudgelog('nudge JSON file not specified!')
    sys.exit(1)


def _get_prefs():
    nudge_prefs = DEFAULT_PREFS
    [nudge_prefs.update({key: app_pref(key)})
     for key in nudge_prefs if app_pref(key) is not None]
    _set_special_key(nudge_prefs)
    _set_pref_domain(nudge_prefs)
    nudge_prefs = json.loads(json.dumps(nudge_prefs))
    return nudge_prefs


def _get_bundled_json(json_path):
    json_raw = open(json_path).read()
    nudge_prefs = json.loads(json_raw)
    _complete_nudge_prefs(nudge_prefs)
    _set_special_key(nudge_prefs)
    return nudge_prefs


def _get_file_json(json_url, json_path):
    try:
        json_raw = urlopen(json_url).read()
        nudge_prefs = json.loads(json_raw)
        _complete_nudge_prefs(nudge_prefs)
        _set_special_key(nudge_prefs)
        return nudge_prefs
    except URLError as err:
        _clean_up(json_path, err)
        sys.exit(1)


def _get_web_json(json_data, json_url, json_path):
    while not isfile(json_path):
        nudgelog(('Starting download: %s' % (unquote(json_url))))
        downloadfile(json_data)
        time.sleep(0.5)
    nudge_prefs = json.loads(open(json_path).read())
    _set_special_key(nudge_prefs)
    return nudge_prefs


def _get_json_data(opts):
    json_path = _make_json_path()
    json_data = {
        'url': opts.jsonurl,
        'file': json_path,
        'name': 'nudge.json'
    }
    if opts.headers:
        headers = {'Authorization': opts.headers}
        json_data.update({'additional_headers': headers})
    return json_data


def _set_special_key(nudge_prefs):
    min_vers = nudge_prefs['minimum_os_version']
    nudge_prefs['minimum_os_version_major'] = min_vers.rsplit('.', 1)[0]
    if '.' not in nudge_prefs['minimum_os_version_major']:
        nudge_prefs['minimum_os_version_major'] = min_vers


def _set_pref_domain(nudge_prefs):
    for key in nudge_prefs:
        set_app_pref(key, nudge_prefs[key])


def _complete_nudge_prefs(nudge_prefs):
    [nudge_prefs.update({key: DEFAULT_PREFS[key]})
     for key in DEFAULT_PREFS if key not in nudge_prefs]


def _make_json_path():
    return join(tempfile.mkdtemp(), 'nudge.json')


def _url_scheme(json_url):
    return urlparse(json_url).scheme


def _clean_up(file, message):
    nudgelog(message)
    shutil.rmtree(file)


if __name__ == '__main__':
    print('This is a library of support tools for the Nudge Tool.')
