# pylint: disable=too-many-instance-attributes, missing-module-docstring
# pylint: disable=invalid-name, expression-not-assigned

from os.path import join
from datetime import datetime, timedelta

# pylint: disable=no-name-in-module
from Foundation import NSURL, NSData, NSTimer, NSDate
from AppKit import NSImage
# pylint: enable=no-name-in-module

from .constants import (DEFAULT_IMAGES, COMPANY_LOGO, UPDATESS,
                        UI_NUDGE_PREFS, UI_FIELDS, USERNAME,
                        DEFERRAL_COUNT, SERIAL_NUMBER, UPDATED,
                        MORE_INFO, DAYS_REMAINING,
                        DAYS_REMAINING_TEXT, PAST_DATE,
                        NUDGE_DISMISSED_COUNT, ACCEPTABLE_APPS,
                        OK, UNDERSTAND, NO_TIMER)
from .timercontroler import TimerController
from .helpers import (get_console_username,
                      get_serial,
                      pending_apple_updates,
                      nudgelog)
from .prefs import set_app_pref


class UX():
    '''Class that define the UX a user will have'''
    def __init__(self, builder_obj, nudge_prefs):
        self.nibbler = builder_obj
        self.nudge = self.nibbler.nudge
        self.nudge_path = self.nibbler.nudge_path
        self.nudge_prefs = nudge_prefs
        self.date_diff_seconds = 0
        self.date_diff_days = 0
        self.cut_off_warn = False
        self.timer = 0

    def build(self):
        '''Function that will build the UX for the user'''
        self._set_images()
        self._set_buttons()
        self._set_static_fields()
        self._set_dynamic_fields()
        self._hide_more_info()
        self._set_timer_logic()

    def run(self):
        '''Function that will run nudge experience'''
        set_app_pref('last_seen', NSDate.new())
        self.nudge.hidden = True
        self.nudge.run()

    def _set_images(self):
        for index, path in enumerate([self.nudge_prefs['logo_path'],
                                      self.nudge_prefs['screenshot_path']]):
            if path in DEFAULT_IMAGES:
                local_png_path = join(
                    self.nudge_path, path).replace(' ', '%20')
            else:
                local_png_path = join(path).replace(' ', '%20')
            foundation_nsurl_path = NSURL.URLWithString_(
                f'file:{local_png_path}')
            foundation_nsdata = NSData.dataWithContentsOfURL_(
                foundation_nsurl_path)
            foundation_nsimage = NSImage.alloc().initWithData_(
                foundation_nsdata)
            if index == 0:
                self.nudge.views[COMPANY_LOGO].setImage_(foundation_nsimage)
            else:
                self.nudge.views[UPDATESS].setImage_(foundation_nsimage)

    def _set_buttons(self):
        self.nudge.attach(self.nibbler.button_update, 'button.update')
        self.nudge.attach(self.nibbler.button_moreinfo, 'button.moreinfo')
        self.nudge.attach(self.nibbler.button_ok, 'button.ok')
        self.nudge.attach(self.nibbler.button_understand, 'button.understand')

    def _set_static_fields(self):
        ui_nudge_prefs = iter(UI_NUDGE_PREFS)
        [self.nudge.views[field].setStringValue_(
            self.nudge_prefs[next(ui_nudge_prefs)]) for field in UI_FIELDS]

    def _set_dynamic_fields(self):
        self.nudge.views[USERNAME].setStringValue_(str(get_console_username()))
        self.nudge.views[SERIAL_NUMBER].setStringValue_(str(get_serial()))
        self.nudge.views[UPDATED].setStringValue_('No')
        self.nudge.views[DEFERRAL_COUNT].setStringValue_(str(NUDGE_DISMISSED_COUNT))

    def _hide_more_info(self):
        if not self.nudge_prefs['more_info_url']:
            self.nudge.views[MORE_INFO].setHidden_(True)

    def _set_timer_logic(self):
        cut_off_date = self.nudge_prefs['cut_off_date']
        if cut_off_date or pending_apple_updates():
            self._get_date_diff_days()
            self._set_days_remaining()
            self._get_cut_off_warn()
            self._init_timer_controller()
            self.timer = self._determine_timer()()
            self.nibbler.timer = _set_Nibbler_timer(self.timer,
                                                    self.nibbler.timer_controller)
        else:
            self._set_no_cutoff_date_ux()
        self._no_timer()

    def _get_date_diff_days(self):
        today = datetime.utcnow()
        cut_off_date = self.nudge_prefs['cut_off_date']
        update_minor_days = self.nudge_prefs['update_minor_days']
        if not cut_off_date:
            cut_off_date_strp = today + timedelta(days=update_minor_days)
        else:
            cut_off_date_strp = datetime.strptime(cut_off_date,
                                                  '%Y-%m-%d-%H:%M')
        self.date_diff_seconds = (cut_off_date_strp - today).total_seconds()
        self.date_diff_days = int(round(self.date_diff_seconds / 86400))

    def _set_days_remaining(self, hide=False):
        if self.date_diff_seconds >= 0:
            self.nudge.views[DAYS_REMAINING].setStringValue_(
                self.date_diff_days)
        else:
            self.nudge.views[DAYS_REMAINING].setStringValue_(
                PAST_DATE)
        if hide:
            self.nudge.views[DAYS_REMAINING_TEXT].setHidden_(True)
            self.nudge.views[DAYS_REMAINING].setHidden_(True)

    def _get_cut_off_warn(self):
        self.cut_off_warn = bool(self.date_diff_seconds < int(
            self.nudge_prefs['cut_off_date_warning']) * 86400)

    def _init_timer_controller(self):
        dct = self.nudge_prefs['dismissal_count_threshold']
        timer_controller = TimerController.new()
        self.nibbler.timer_controller = (
            timer_controller.
            initWithDC_AA_DCT_NO_(NUDGE_DISMISSED_COUNT,
                                  ACCEPTABLE_APPS,
                                  dct,
                                  self.nibbler))

    def _determine_timer(self):
        condition_action = [(self.date_diff_seconds <= 0, self._get_stupidly_aggressive),
                            (self.date_diff_seconds <= 3600, self._get_very_aggressive),
                            (self.date_diff_seconds <= 86400, self._get_more_aggressive),
                            (self.cut_off_warn, self._get_aggressive),
                            (True, self._get_low_pressure)]
        for state in condition_action:
            condition = state[0]
            action = state[1]
            if condition:
                return action
        return None

    def _get_low_pressure(self):
        self._set_buttons_state(ok_button=True)
        return float(self.nudge_prefs['timer_initial'])

    def _get_aggressive(self):
        self._set_buttons_state(understand_button=True)
        return float(self.nudge_prefs['timer_day_3'])

    def _get_more_aggressive(self):
        self._set_buttons_state(understand_button=True)
        return float(self.nudge_prefs['timer_day_1'])

    def _get_very_aggressive(self):
        self._set_buttons_state()
        return float(self.nudge_prefs['timer_final'])

    def _get_stupidly_aggressive(self):
        self._set_buttons_state()
        return float(self.nudge_prefs['timer_elapsed'])

    def _set_buttons_state(self,
                           ok_button=False,
                           understand_button=False):
        self.nudge.views[UNDERSTAND].setHidden_(True)
        self.nudge.views[OK].setHidden_(True)
        if ok_button:
            self.nudge.views[OK].setHidden_(False)
            self.nudge.views[OK].setEnabled_(True)
        if understand_button:
            self.nudge.views[UNDERSTAND].setHidden_(False)
            self.nudge.views[UNDERSTAND].setEnabled_(True)

    def _set_no_cutoff_date_ux(self):
        self._set_days_remaining(hide=True)
        self._set_buttons_hidden_state(ok_button=True)

    def _no_timer(self):
        if self.nudge_prefs['no_timer']:
            self.nibbler.timer.invalidate()
            nudgelog(NO_TIMER)
        else:
            nudgelog(f'Timer is set to {self.timer}')


def _set_Nibbler_timer(timer, timer_controller):
    return (NSTimer
            .scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
                timer, timer_controller, 'activateWindow:', None, True))


if __name__ == '__main__':
    print('This is a library of support tools for the Nudge Tool.')
