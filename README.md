# Nudge (macadmin's Slack #nudge)

## Important Information
You most certainly want to customize the following values:

- `cut_off_date`
- `main_subtitle_text`
- `more_info_url`

Also, you will at the very least want to change the `company_logo.png`

## Screenshots
![Screenshot Nudge](/images/nudge_ss.png?raw=true)

## Building this package
You will need to use [munki-pkg](https://github.com/munki/munki-pkg) to build this package.

## Credits
This tool would not be possible without [nibbler](https://github.com/pudquick/nibbler), written by [Michael Lynn](https://twitter.com/mikeymikey).

### Notes
Because of the way git works, nudge will not contain the `Logs` folder required for the postinstall to complete.

In order to create a properly working package, you will need to run the following command _before_ building the package:
`munkipkg --sync /path/to/cloned_repo/nudge`.

## OS Support
The following operating system and versions have been tested.
- 10.10.0, 10.10.5
- 10.11.0, 10.11.6
- 10.12.0, 10.12.6
- 10.13.0 10.13.3, 10.13.6
- 10.14 -> 10.14.6

## Configuration File
Essentially every component of the UI is customizable, all through a JSON configuration file. An [example file](/example_config.json) is available within the code repository.

### Defined config file
To define a configuration file, use the `jsonurl` script parameter.
```bash
--jsonurl=https://fake.domain.com/path/to/config.json
```
```bash
--jsonurl=file:///path/to/local/config.json
```

### Default config file
If you prefer to deploy the configuration file to each client, it needs to be placed in the `Resources` directory and named `nudge.json`. If this file exists, `jsonurl` does not need to be set.

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

### No timer
Do not attempt to restore the nudge GUI to the front of a user's window.

```json
"no_timer": false
```

### Timer Day 1
The time, in seconds, to restore the nudge GUI to the front of a user's window. This will occur indefinitely until the UI is closed or macOS update is installed.

This is when the update cutoff is one day or less.
```json
"timer_day_1": 600
```

### Timer Day 3
The time, in seconds, to restore the nudge GUI to the front of a user's window. This will occur indefinitely until the UI is closed or macOS update is installed.

This is when the update cutoff is three days or less.
```json
"timer_day_3": 7200
```

### Timer Elapsed
The time, in seconds, to restore the nudge GUI to the front of a user's window. This will occur indefinitely until the UI is closed or macOS update is installed.

This is when the update cutoff has elapsed.
```json
"timer_elapsed": 10
```

### Timer Final
The time, in seconds, to restore the nudge GUI to the front of a user's window. This will occur indefinitely until the UI is closed or macOS update is installed.

This is when the update is one hour or less.
```json
"timer_final": 60
```

### Timer Initial
The time, in seconds, to restore the nudge GUI to the front of a user's window. This will occur indefinitely until the UI is closed or macOS update is installed.

This is when the update cutoff is over three days.
```json
"timer_initial": 14400
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
