# Nudge (macadmin's Slack #nudge)

## Nudge functionality overview
- Nudge, rather than trying to install updates, merely prompts users to install updates via an approved method (System Preferences, Munki, Jamf, etc.).
- By default, Nudge will open every 30 minutes, at the 0 and 30 minute mark. This is because of the default launch agent. If you find this behavior too aggressive, please change the launch agent.
- The timers are for if the user minimizes/hides the window. It will re-load the window into the foreground, taking precedence over any window.
- If you want a certain time (in seconds) between notifications, you can set that using the `time_between_notifications` preference.
- Read Alan Siu's [Introduction to Nudge](https://www.alansiu.net/2019/12/24/nudge/) blog post for a more in-depth introduction to Nudge.

## Embedded Python
As of v2.0, Nudge now uses its own embedded python (currently v3.8). This is due to Apple's upcoming removal of Python2.

Gurl has been updated from the Munki 4.0 release.

Nibbler has been updated to support python 3.

### Building embedded python framework

To reduce the size of the git repository, you **must** create your own Python. To do this, simply run the `./build_python_framework` script within the repository.

This process was tested on Catalina only.

```
./build_python_framework

Cloning relocatable-python tool from github...
Cloning into '/tmp/relocatable-python-git'...
remote: Enumerating objects: 28, done.
remote: Counting objects: 100% (28/28), done.
remote: Compressing objects: 100% (19/19), done.
remote: Total 78 (delta 12), reused 19 (delta 9), pack-reused 50
Unpacking objects: 100% (78/78), done.
Downloading https://www.python.org/ftp/python/3.8.0/python-3.8.0-macosx10.9.pkg...

...

Done!
Customized, relocatable framework is at /Library/nudge/Python.framework
Moving Python.framework to nudge munki-pkg payload folder
Taking ownership of the file to not break git
```

## Important Information
Since version 2.1 a new way of configuration have been included. From now on Profiles is the preferred method to configure Nudge. In addition to that the JSON file format has changed, you can see an [example JSON file](/example_config.json) in the code repository.

You most certainly want to customize the following values:

- `cut_off_date`
- `main_subtitle_text`
- `more_info_url`
- `minimum_os_version`
- `minimum_os_sub_build_version`

Also, you will at the very least want to change the `company_logo.png`

## Screenshots
![Screenshot Nudge](/images/nudge_ss.png?raw=true)

## Building this package
You will need to use [munki-pkg](https://github.com/munki/munki-pkg) to build this package.

## Credits
This tool would not be possible without [nibbler](https://github.com/pudquick/nibbler), written by [Michael Lynn](https://twitter.com/mikeymikey).

## OS Support v1
The following operating system and versions have been tested.
- 10.10.0, 10.10.5
- 10.11.0, 10.11.6
- 10.12.0, 10.12.6
- 10.13.0 10.13.3, 10.13.6
- 10.14 -> 10.14.6
- 10.15 -> 10.15.1

## OS Support v2 (embedded python)
The following operating system and versions have been tested with the embedded python.
- 10.14
- 10.15

## Configuration File
Essentially every component of the UI is customizable, all through a JSON configuration file or a Profile (or MCX). An [example json file](/example_config.json) plus an [example profile](/example_profile.mobileconfig) are available within the code repository.

### Defined JSON config file
To define a configuration file, use the `jsonurl` script parameter.
```bash
--jsonurl=https://fake.domain.com/path/to/config.json
```
```bash
--jsonurl=file:///path/to/local/config.json
```

### Default config file
A Profile will have precedence over any other method of configuration and in this case the `jsonurl` does not need to be set.
If you prefer to deploy the JSON configuration file to each client, it needs to be placed in the `Resources` directory and named `nudge.json`. If this file exists, `jsonurl` does not need to be set either.

## Preferences
A description of each preference is listed below.

### Cutoff date
Cut off date in UTC.
```json
"cut_off_date": "2018-12-31-00:00"
```

### Cut off date warning
This is the number, in days, of when to start the initial UI warning. When this set of days passes, the user will be required to hit the **I Understand** button, followed by the **Close** button to exit out of the UI.
```json
"cut_off_date_warning": 14
```

### Logo path
A custom logo path. Alternatively, just replace the included `company_logo.png`.
```json
"logo_path": "/Some/Custom/Path/company_logo.png"
```

### Button Title text
This is the first set of text above the **Update Machine** button.

```json
"button_title_text": "Ready to start the update?"
```

### Button Sub-title text
This is the second set of text above the **Update Machine** button.

```json
"button_sub_titletext": "Click on the button below."
```

### Dismissal Count Threshold
This is the amount of times a user can disregard nudge before more aggressive behaviors kick in.

```json
"dismissal_count_threshold": 100
```

### URL for self-servicing upgrade app
This is the full URL for a local self-servicing app such as Jamf Self
Service or Munki Managed Software Center linking directly to a Jamf
policy or Munki catalog item to install a major version upgrade.

This is useful in situations where users do not have administrative
privileges and cannot run `Install macOS...app` directly. This option
has no effect on minor version _updates_ – only full version OS upgrades.

Provide a full URL with the correct protocol for your self-servicing
app.

- Open Jamf Self Service to main page: `jamfselfservice://content`
- Open Jamf Self Service to view a policy by ID number: `jamfselfservice://content?entity=policy&id=<id>&action=view`
- Open Jamf Self Service to execute a policy by ID number: `jamfselfservice://content?entity=policy&id=<id>&action=execute`
- Open Manage Software Center to the detail page for an item: `munki://detail-<item name>`

```json
"local_url_for_upgrade": "jamfselfservice://content?entity=policy&id=<id>&action=view"
```

Note: If `local_url_for_upgrade` is provided, `path_to_app` is **ignored**
in the configuration file.

### Minimum OS Version
This is the minimum OS version a machine must be on to not receive this UI.
```json
"minimum_os_version": "10.13.6"
```

### Minimum OS Sub Version

This is the minimum OS version a machine must be on to not receive this UI.
```json
"minimum_os_sub_build_version": "18G103"
```

### More info URL
This is the URL to open when the **More Info** button is clicked.
```json
"more_info_url": "https://google.com"
```

### Main Title text
This is the main, bolded text at the very top.
```json
"main_title_text": "macOS Update"
```

### Main Sub-title text
This is the text right under the main title.
```json
"main_subtitle_text": "A friendly reminder from your local IT team"
```

### Paragraph Title text
This is the bolded portion of the UI towards the top.
```json
"paragraph_title_text": "A security update is required on your machine."
```

### Paragraph 1 text
This is the text for the first paragraph.
```json
"paragraph1_text": "A fully up-to-date device is required to ensure that IT can your accurately protect your computer."
```

### Paragraph 2 text
This is the text for the second paragraph.
```json
"paragraph2_text": "If you do not update your computer, you may lose access to some items necessary for your day-to-day tasks."
```

### Paragraph 3 text
This is the text for the third paragraph.
```json
"paragraph3_text": "To begin the update, simply click on the button below and follow the provided steps."
```

### Path to app
This is the path to the macOS installer application.
```json
"path_to_app": "/Applications/Install macOS High Sierra.app"
```

Note: This setting is ignored when `local_url_for_upgrade` is provided.

### Time Between Notifications
Instead of having the Nudge GUI appear every half hour, you can express the time between notification in seconds.
*The notifications still base its behaviour in how the LaunchAgent works so every half hour it will check for this time between notifications.
```json
"time_between_notifications": 0
```

### No timer
Do not attempt to restore the nudge GUI to the front of a user's window.

```json
"no_timer": false
```

### Timer Initial
The time, in seconds, to restore the nudge GUI to the front of a user's window. This will occur indefinitely until the UI is closed or macOS update is installed.

This is when the update cutoff is over three days.
```json
"timer_initial": 14400
```

### Timer Day 3
The time, in seconds, to restore the nudge GUI to the front of a user's window. This will occur indefinitely until the UI is closed or macOS update is installed.

This is when the update cutoff is three days or less.
```json
"timer_day_3": 7200
```

### Timer Day 1
The time, in seconds, to restore the nudge GUI to the front of a user's window. This will occur indefinitely until the UI is closed or macOS update is installed.

This is when the update cutoff is one day or less.
```json
"timer_day_1": 600
```

### Timer Final
The time, in seconds, to restore the nudge GUI to the front of a user's window. This will occur indefinitely until the UI is closed or macOS update is installed.

This is when the update is one hour or less.
```json
"timer_final": 60
```

### Timer Elapsed
The time, in seconds, to restore the nudge GUI to the front of a user's window. This will occur indefinitely until the UI is closed or macOS update is installed.

This is when the update cutoff has elapsed.
```json
"timer_elapsed": 10
```

### Update screenshot path
A custom update screenshot path. Alternatively, just replace the included `update_ss.png`.
```json
"screenshot_path": "/Some/Custom/Path/update_ss.png"
```

### Random Delay
Randomize the UI popup by up to 20 minutes.
```json
"random_delay": true
```

### Update Minor
Perform Apple Software Updates.
```json
"update_minor": true
```

### Update Minor Days
Grace period before UI pops up to prompt for minor updates.
```json
"update_minor_days": 14
```
