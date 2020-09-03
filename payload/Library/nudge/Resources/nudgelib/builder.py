import webbrowser
import subprocess
import sys

from os.path import dirname, realpath, join

from .nibbler import Nibbler
from .helpers import nudgelog


class Builder():
    '''Class which build the nudge tool'''

    def __init__(self, path_to_app, more_info_url):
        try:
            self.nudge_path = dirname(dirname(realpath(__file__)))
            self.nudge = Nibbler(join(self.nudge_path, 'nudge.nib'))
        except IOError:
            nudgelog('Unable to load nudge nib file!')
            sys.exit(20)

        self.path_to_app = path_to_app
        self.more_info_url = more_info_url

    def button_moreinfo(self):
        '''Open browser more info button'''
        nudgelog('User clicked on more info button - opening URL in default browser')
        webbrowser.open_new_tab(self.more_info_url)

    def button_update(self, simulated_click=False):
        '''Start the update process'''
        if simulated_click:
            nudgelog('Simulated click on update button - opening update application')
        else:
            nudgelog('User clicked on update button - opening update application')
        cmd = ['/usr/bin/open', self.path_to_app]
        subprocess.Popen(cmd)

    def button_ok(self):
        '''Quit out of nudge if user hits the ok button'''
        nudgelog('User clicked on ok button - exiting application')
        self.nudge.quit()

    def button_understand(self):
        '''Add an extra button to force the user to read the dialog, prior to being
        able to exit the UI.'''
        nudgelog('User clicked on understand button - enabling ok button')
        self.nudge.views['button.understand'].setHidden_(True)
        self.nudge.views['button.understand'].setEnabled_(False)
        self.nudge.views['button.ok'].setHidden_(False)
        self.nudge.views['button.ok'].setEnabled_(True)


if __name__ == '__main__':
    print('This is a library of support tools for the Nudge Tool.')
