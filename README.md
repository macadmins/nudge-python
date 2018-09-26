# Nudge

## Important Information
You most certainly want to customize the following values:

- cutoffdate
- updatetext
- moreinfourl

Also, you will at the very least want to change the `company_logo.png`

## Screenshots
![Screenshot Nudge](/images/nudge_ss.png?raw=true)

## Building this package
You will need to use [munki-pkg](https://github.com/munki/munki-pkg) to build this package

## Credits
This tool would not be possible without [nibbler](https://github.com/pudquick/nibbler), written by [Michael Lynn](https://twitter.com/mikeymikey)

### Notes
Because of the way git works, nudge will not contain the `Logs` folder required for the postinstall to complete.

In order to create a properly working package, you will need to run the following command:
`munkipkg --sync /path/to/cloned_repo/nudge`

## OS Support
The following operating system and versions have been tested.
- 10.10.0, 10.10.5
- 10.11.0, 10.11.6
- 10.12.0, 10.12.6
- 10.13.0 10.13.3, 10.13.6
- 10.14.0

## Options
Essentially every component of the UI is customizable, all through the LaunchAgent.

### Cutoff date
Cut off date in UTC.
```xml
<string>--cutoffdate</string>
<string>2018-12-31-00:00</string>
```

### Cut off date warning
This is the number, in days, of when to start the initial UI warning. When this set of days passes, the user will be required to hit an "I Understand" button, followed by the "Close" button to exit out of the UI.
```xml
<string>--cutoffdatewarning</string>
<string>14</string>
```

### Logo path
A custom logo path. Alternatively, just replace the included company_logo.png
```xml
<string>--logopath</string>
<string>/Some/Custom/Path/company_logo.png</string>
```


### Header1 text
This is the first set of text above the update button.

```xml
<string>--h1text</string>
<string>Ready to start the update?</string>
```

### Header2 text
This is the second set of text above the update button.

```xml
<string>--h2text</string>
<string>Click on the button below.</string>
```

### Minimum OS Version
This is the minimum OS version a machine must be on to not receive this UI.
```xml
<string>--minimumosversion</string>
<string>10.13.6</string>
```

### More info URL
This is the URL to open for the Manual Enrollment button.
```xml
<string>--moreinfourl</string>
<string>https://google.com</string>
```

### No timer
Do not attempt to restore the umad GUI to the front of a user's window.

```xml
<string>--notimer</string>
```

### Paragraph 1 text
This is the text for the first paragraph.
```xml
<string>--paragraph1</string>
<string>A fully up-to-date device is required to ensure that IT can your accurately protect your computer.</string>
```

### Paragraph 2 text
This is the text for the second paragraph.
```xml
<string>--paragraph2</string>
<string>If you do not update your computer, you may lose access to some items necessary for your day-to-day tasks.</string>
```

### Paragraph 3 text
This is the text for the third paragraph.
```xml
<string>--paragraph3</string>
<string>To begin the update, simply click on the button below and follow the provided steps.</string>
```

### Path to app
This is the path to the macOS installer application.
```xml
<string>--pathtoapp</string>
<string>/Applications/Install macOS High Sierra.app</string>
```

### Sub-title text
This is the text right under the main title.
```xml
<string>--subtitletext</string>
<string>A friendly reminder from your local IT team</string>
```

### Timer Day 1
The time, in seconds, to restore the umad GUI to the front of a user's window. This will occur indefinitely until the UI is closed or MDM is enrolled.

This is when the MDM cutoff is one day or less.
```xml
<string>--timerday1</string>
<string>600</string>
```

### Timer Day 3
The time, in seconds, to restore the umad GUI to the front of a user's window. This will occur indefinitely until the UI is closed or MDM is enrolled.

This is when the MDM cutoff is three days or less.
```xml
<string>--timerday3</string>
<string>7200</string>
```

### Timer Elapsed
The time, in seconds, to restore the umad GUI to the front of a user's window. This will occur indefinitely until the UI is closed or MDM is enrolled.

This is when the MDM cutoff has elapsed.
```xml
<string>--timerelapsed</string>
<string>10</string>
```

### Timer Final
The time, in seconds, to restore the umad GUI to the front of a user's window. This will occur indefinitely until the UI is closed or MDM is enrolled.

This is when the MDM cutoff is one hour or less
```xml
<string>--timerfinal</string>
<string>60</string>
```

### Timer Initial
The time, in seconds, to restore the umad GUI to the front of a user's window. This will occur indefinitely until the UI is closed or MDM is enrolled.

This is when the MDM cutoff is over three days.
```xml
<string>--timerinital</string>
<string>14400</string>
```

### Title text
This is the main, bolded text at the very top.
```xml
<string>--titletext</string>
<string>MDM Enrollment</string>
```

### Update screenshot path
A custom update screenshot path. Alternatively, just replace the included update_ss.png
```xml
<string>--updatesspath</string>
<string>/Some/Custom/Path/update_ss.png</string>
```

### Update text
This is the bolded portion of the UI towards the top.
```xml
<string>--updatetext</string>
<string>A security update is required on your machine.</string>
```
