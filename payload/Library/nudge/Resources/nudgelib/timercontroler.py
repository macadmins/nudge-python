import time

from urllib.parse import unquote, urlparse

# pylint: disable=no-name-in-module
from AppKit import NSWorkspace, NSApplication
from Foundation import NSObject
# pylint: enable=no-name-in-module

from .helpers import nudgelog
from .constants import DEFERRAL_COUNT


class TimerController(NSObject):
    '''Thanks to frogor for help in figuring this part out'''
    def initWithDC_AA_DCT_NO_(self,
                              nudge_dismissed_count,
                              acceptable_apps,
                              dismissal_count_threshold,
                              nudge_obj):
        self.nudge_dismissed_count = nudge_dismissed_count
        self.acceptable_apps = acceptable_apps
        self.dismissall_count_threshold = dismissal_count_threshold
        self.nudge = nudge_obj
        return self

    def activateWindow_(self, timer_obj):
        self.determine_state_and_nudge()

    def determine_state_and_nudge(self):
        '''Determine the state of nudge and re-fresh window'''
        workspace = NSWorkspace.sharedWorkspace()
        currently_active = NSApplication.sharedApplication().isActive()
        frontmost_app = workspace.frontmostApplication().bundleIdentifier()

        if not currently_active and frontmost_app not in self.acceptable_apps:
            nudgelog('Nudge or acceptable applications not currently active')
            # If this is the under max dismissed count, just bring nudge back to the forefront
            # This is the old behavior
            if self.nudge_dismissed_count < self.dismissall_count_threshold:
                nudgelog('Nudge dismissed count under threshold')
                self.nudge_dismissed_count += 1
                bring_nudge_to_forefront(self.nudge)
            else:
                # Get more aggressive - new behavior
                nudgelog('Nudge dismissed count over threshold')
                self.nudge_dismissed_count += 1
                nudgelog('Enforcing acceptable applications')
                # Loop through all the running applications
                for app in NSWorkspace.sharedWorkspace().runningApplications():
                    app_name = str(app.bundleIdentifier())
                    app_bundle = str(app.bundleURL())
                    if app_bundle:
                        # The app bundle contains file://, quoted path and trailing slashes
                        app_bundle_path = unquote(urlparse(app_bundle).path).rstrip('/')
                        # Add Software Update pane or macOS upgrade app to acceptable app list
                        if app_bundle_path == self.nudge.path_to_app:
                            self.acceptable_apps.append(app_name)
                    else:
                        # Some of the apps from NSWorkspace don't have bundles,
                        # so force empty string
                        app_bundle_path = ''
                    # Hide any apps that are not in acceptable list or are not the macOS upgrade app
                    if (app_name not in self.acceptable_apps) or (app_bundle_path != self.nudge.path_to_app):
                        app.hide()
                        # Race condition with NSWorkspace. Python is faster :)
                        time.sleep(0.001)
                # Another small sleep to ensure we can bring Nudge on top
                time.sleep(0.5)
                bring_nudge_to_forefront(self.nudge)
                # Pretend to open the button and open the update mechanism
                self.nudge.button_update(True)
            self.ux_when_timer_is_controlling()

    def ux_when_timer_is_controlling(self):
        nudgelog(f'Setting up DEFERRAL COUNT value to: {self.nudge_dismissed_count}')
        self.nudge.nudge.views[DEFERRAL_COUNT].setStringValue_(str(self.nudge_dismissed_count))


def bring_nudge_to_forefront(nudge):
    '''Brings nudge to the forefront - old behavior'''
    nudgelog('Nudge not active - Activating to the foreground')
    # We have to bring back python to the forefront since nibbler is a giant cheat
    NSApplication.sharedApplication().activateIgnoringOtherApps_(True)
    # Now bring the nudge window itself to the forefront
    # Nibbler objects have a .win property (...should probably be .window)
    # that contains a reference to the first NSWindow it finds
    nudge.nudge.win.makeKeyAndOrderFront_(None)


if __name__ == '__main__':
    print('This is a library of support tools for the Nudge Tool.')
