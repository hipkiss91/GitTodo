# GitTodo
Allows developers within SublimeText 3 to automatically publish issues to a public repo on github through the use of properly formatted TODO's.

## v0.2.0 improvements:
```
- Include milestones.
- Transform 'todos' into one condition.
- Transform array of files to filter in/out.
- Define a classic annotation pattern.
- Other (See messages/0.2.0.txt)
```

# Install
GitTodo is currently only available here. I am looking at getting it in the sublime package control.

#### Git Clone
If you are forking this project, or for whatever reason do not want to use Package Control, you can install this package another way. First, go to your packages directory (Preferences -> Browse Packages) - then run git clone.

# Usage
`ctrl+alt+t` Initiates the command.

## Navigating results
The list of `TODO's` generated for a given project can be reviewed, as JSON output, in the root of the project under the file name `gitTodo.txt`.

## TODO Format
The current format of accepted `TODO's` are as follows:
`TODO: [TITLE] (This is the description/body of the issue.) @Assignee #bug #minor *milestone`
### Note: Punctuation is important.


# Config
An example of the current configuration is available in the plugin and is as below. It allows a user to specify both files and folders to exclude as well as github account details for connecting and generating the issues. A project directory and projects within that directory can also be specified. Furthermore, if a user has not added there project to the list then a user may still create issues, for that project, by using the command `ctrl+alt+t` and given that the config details remain the same.

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
		"password": "NuFwZoIbJgTh7RrT",
		"token": 	"insert access token here"
	},
	"projects_dir": "C:\\wamp64\\www\\",
	"watch_projects":[
		"supersecretproject",
		"project1"
	]
}

```

## Current known issues/improvements actively being worked on:
```
# TODO: Process multi-line TODO's.
# TODO: Private github repos
# TODO: Other git accounts.
# TODO: Change/Alter Issues
# TODO: Delete Issues
# TODO: Account for bugs using the prefix 'FIXME'.
```


# License

The MIT License (MIT)

Copyright (c) 2016 Jonathan Hipkiss (hipkiss91)

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
