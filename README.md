# GitTodo
Allows developers within SublimeText 3 to automatically publish issues to a public repo on github through the use of properly formatted TODO's.

## v1.0.0 improvements:
```
- NEW FEATURE: Account for bugs using the prefix 'FIXME'.
- Other (See messages/1.0.0.txt)  
```

# Install
GitTodo is currently only available here. It is currently being reviewed to be included in the Sublime Text Package Control. Once GitTodo has been approved it can be found under `GitTodo` in Package Control.

#### Git Clone
If you are forking this project, or for whatever reason do not want to use Package Control, you can install this package another way. First, go to your packages directory (Preferences -> Browse Packages) - then run git clone.

# Usage
`ctrl+alt+t` Initiates the command.  
Any errors that may occur can be viewed in the Sublime Text Console `Ctrl+'`.

## Navigating results
The list of `TODO's` generated for a given project can be reviewed, as JSON output, in the root of the project under the file name `gitTodo.txt`.

## TODO Format
The current format of accepted `TODO's` are as follows:  
`TODO: [TITLE] (This is the description/body of the issue.) @Assignee #bug #minor *milestone`  
`FIXME's` have also been added to GitTodo and can also be accepted in the following format:  
`FIXME: [TITLE] (This is the description/body of the issue.) @Assignee #bug #minor *milestone`  
The current accepted format for milestones are integers. This requires a knowledge of the project milestones and their corresponding integer values. A key/value pair is being worked on which will assign either a date or title of the milestone to the integer for said milestone.  

### Note: Minimum requirements for submitting an issue is the `[TITLE]`. Description, assignee, labels and milestones are optional.  
### `FIXME` submitted issues are the same as `TODO` with the exception of being automatically assigned the label: `bug`. Further labels, for example priority, can be specified as well.


# Config
An example of the current configuration is available in the plugin and is as below. It allows a user to specify both files and folders to exclude as well as github account details for connecting and generating the issues.

```
{
    "exclude_folders": [
        ".git",
        "node_modules",
        "images",
        "fonts",
        "lib",
        "libs",
        "Examples",
        "sass",
        "ie"
    ],
    "exclude_files": [
        "*.gitignore",
        "*.json",
        "*.md",
        "*.txt",
        "*.jpg",
        "*.png",
        "*.htc",
        "*.svg",
        "*.gif",
        "*.min.js",
        "*.min.css",
        "*.map"
    ],
    "github_details":{
        "username": "hipkiss91",
        "password": "password"
    },
    "projects_dir": "C:\\wamp64\\www\\"
}

```

## Current known issues/improvements actively being worked on:
```
# TODO: Process multi-line TODO's.
# TODO: Private github repos
# TODO: Other git accounts.
# TODO: Change/Alter Issues
# TODO: Close Issues
```


# License

The MIT License (MIT)

Copyright (c) 2016 Jonathan Hipkiss (hipkiss91)

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
