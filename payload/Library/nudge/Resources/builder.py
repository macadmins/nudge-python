import os
import webbrowser
import subprocess

from nibbler import *
from nudge_helpers import nudgelog

class Builder(object):
    '''Class which build the nudge tool'''

    def __init__(self, nudge_path, path_to_app, more_info_url):
        try:
            self.nudge = Nibbler(os.path.join(nudge_path, 'nudge.nib'))
        except IOError:
            nudgelog('Unable to load nudge nib file!')
            exit(20)
        
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
        self.nudge.views['button.ok'].setHidden_(False)
        self.nudge.views['button.ok'].setEnabled_(True)