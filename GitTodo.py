import sublime
import sublime_plugin
import os
import sys
import re
import requests
import json
import subprocess
import traceback
import fnmatch

todos_array = ['Todo', 'TODO', 'todo']
fixme_array = ['FIXME', 'Fixme', 'fixme', 'FixMe']
unsupported = ['bitbucket', '192.168', '127.0', 'localhost']

def get_setting(key, default=None):
	settings = sublime.load_settings('GitTodo.sublime-settings')
	os_specific_settings = {}
	return os_specific_settings.get(key, settings.get(key, default))

def getoutput(command):
	out, err = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True).communicate()
	return out.decode().strip()

def get_repo_details(self):
	# only works on current open file
	path, filename = os.path.split(self.view.file_name())

	# Switch to cmd of file
	os.chdir(path + "/")
	GIT_SHOW_ORIGIN = "git remote show origin -n"
	GIT_SHOW_ORIGIN_REGEX = "(.+: )*([\w\d\.]+)[:|@]/?/?(.*)"
	git_config_path = getoutput(GIT_SHOW_ORIGIN)
	p = re.compile(GIT_SHOW_ORIGIN_REGEX)
	parts = p.findall(git_config_path)

	if len(parts) == 0:
		return(False, 'No git config found. Please initiate GIT in this project in order to sync todos and issues.')
	else:
		git_config = parts[0][2]

	if ':' in git_config:
		# SSH format: {domain}:{user}/{repo}.git
		domain, user, repo = git_config.replace(".git", "").replace(":", "/").split("/")
		return ('ssh', domain, user, repo)
	else:
		# HTTP format: {domain}/{user}/{repo}.git
		domain, user, repo = git_config.replace(".git", "").split("/")
		return ('https', domain, user, repo)

class GitTodoFindCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		# Get projects directory.
		directory = get_setting('projects_dir', {})
		# Run on the current open window or if watch_projects is specified.
		config = get_repo_details(self)
		if config[0] == False:
			return(print(config[1]))
		for support in unsupported:
			if support in config[1]:
				print(config[1] + ' Not currently supported')
		GitTodoFindCommand.process_project(directory, config[3])

	def process_project(project_dir, project):
		dir_path = os.path.dirname(project_dir + project + '\\')
		myfiles = GitTodoFindCommand.get_filepaths(dir_path)
		all_todos = [] # Array to store all todos from all files.
		# Loop through each file within the project.
		for nthfile in myfiles:
			todo_array = [] # Array to store all the todo's per file
			start = nthfile.rfind('\\') + 1
			end = len(nthfile)
			filename = nthfile[start:end]

			file = open(nthfile) # Open the nth file.
			for num, line in enumerate(file, 1): # Read each line in the file.
				for todo in todos_array:
					if todo in line: # Check each line for a 'todo'.
						GitTodoFindCommand.process_line('todo', filename, num, line, todo_array)
				for fix in fixme_array:
					if fix in line: # Check each line for a 'fixme'.
						GitTodoFindCommand.process_line('fixme', filename, num, line, todo_array)
			if len(todo_array) > 0:
				all_todos.append(todo_array)# append todos for each file into array of files.
		GitTodoFindCommand.store_local_todos(project, all_todos, dir_path)

	def get_filepaths(directory):
		""" This function will generate the file names in a directory tree by walking the tree either top-down or bottom-up. For each
		directory in the tree rooted at directory top (including top itself), it yields a 3-tuple (dirpath, dirnames, filenames).
		"""
		file_paths = []  # List which will store all of the full filepaths.
		excluded_folders = get_setting('exclude_folders', [])
		excluded_files = get_setting('exclude_files', [])
		# Walk the tree.
		for root, directories, files in os.walk(directory):
			for directory in directories:
				if directory in excluded_folders:
					directories.remove(directory)
			for file in files:
				ext = GitTodoFindCommand.MatchesExtensions(file, excluded_files)
				if ext == False:
					filepath = os.path.join(root, file)
					file_paths.append(filepath)  # Add it to the list.
		return file_paths

	def MatchesExtensions(name,extensions):
		for extension in extensions:
			if fnmatch.fnmatch(name, extension):
				return True
		return False

	def process_line(line_type, file, num, line, todo_array):
		mytodo = Gittodo()
		mytodo.set_filename(file)
		mytodo.set_line(num)
		if line_type == 'fixme':
			mytodo.set_labels('bug')
		# This processes the line, it will return the correct object of format for each todo.
		# todo: [TITLE] (Description of task goes here.) @someone #bug #minor *milestone
		if not line.find('[') > 0 and not line.find(']', line.find('[')) > 0:
			print('Todo was not correctly formatted in file' + file +', @ line '+str(num)+'. Please follow the formatting guidleines @ https://github.com/hipkiss91/GitTodo/blob/master/README.md.')
			print('The minimum required to submit an issue is a title. All incorrectly formatted todos can be found in the gitTodo.txt file')
			for todo_case in todos_array:
				if line.find(todo_case) > 0:
					file_start = line.find(todo_case)
			if line.find('\r\n'):
				file_end = len(line) - 2
			else:
				file_end = len(line)
			todo_bad = line[file_start:file_end]
			mytodo.set_review(True)
			mytodo.set_body(todo_bad)
		else:
			# Process the title. START
			if line.find('[') > 0 and line.find(']') > 0:
				title_start = line.find('[') + 1
				title_end = line.find(']')
				todo_title = line[title_start:title_end]
				mytodo.set_title(todo_title)
			# Process the title. End

			# Process the body. START
			if line.find('(') > 0 and line.find(')') > 0:
				body_start = line.find('(') + 1
				body_end = line.find(')')
				todo_body = line[body_start:body_end]
				mytodo.set_body(todo_body)
			# Process the body. End

			todo_labels = []
			words = line.split()
			for word in words:
				# Process the owner.
				if word.find('@') > -1:
					mytodo.set_assignee(word.strip('@'))
				# Process the labels.
				if word.find('#') > -1:
					todo_labels.append(word.strip('#'))
					mytodo.set_labels(todo_labels)
				# Process the milestones.
				if word.find('*') > -1:
					mytodo.set_milestone(word.strip('*'))

		# Add them all together and pass back to the parent.
		todo_array.append(mytodo)

	def store_local_todos(repo, todo_array, project_dir):
		# Store todo's locally in the root project dir.
		write_path = project_dir + '\\gitTodo.txt'
		try:
			mode = 'a' if os.path.exists(write_path) else 'w'
			with open(write_path, mode) as file:
				path = open(write_path).read()
				for todos in todo_array:
					for todo in todos:
						if todo.review == False:
							GitTodoFindCommand.process_todo(repo, todo)

						issue = json.dumps(todo.__dict__)
						if mode == 'a' and issue not in path: # Checks if it's already in the file.
							file.write(issue + '\n')
						else:
							file.write(issue + '\n')
		except Exception:
			print(traceback.format_exc())

	def process_todo(repo, todo):
		# Process all todos from all files. (setup for git connection.)
		github_account = get_setting('github_details', {})
		USER_NAME	= github_account["username"]
		session 	= GitTodoFindCommand.github_connect(USER_NAME)
		status 		= GitTodoFindCommand.create_issue(USER_NAME, repo, session, todo)
		if status == 201:
			print('Good job, issue was submitted.')
		else:
			print('Error in submitting new issue.')

	def github_connect(USER_NAME):
		github_account = get_setting('github_details', {})
		# Authentication username, password & token.
		USER_PASSWORD 	=  github_account["password"]
		USER_TOKEN		=  github_account["token"]

		# Create an authenticated session to create the issue
		session = requests.Session()
		session.auth = (USER_NAME, USER_PASSWORD)
		return session

	def create_issue(username, repo, session, todo):
		url = 'https://api.github.com/repos/' + username + '/' + repo + '/issues'
		line = 'line: ' + str(todo.line)+ '.  File: ' + todo.filename + '.\n'
		issue = {}
		issue['title'] = todo.title
		if todo.body is not None:
			issue['body'] = line + todo.body
		else:
			issue['body'] = line
		if todo.assignee is not None:
			issue['assignee'] = todo.assignee
		if todo.labels is not None:
			issue['labels'] = todo.labels
		if todo.milestone is not None:
			# Only accepts integers.
			issue['milestone'] = todo.milestone

		req = session.post(url, json.dumps(issue))
		return req.status_code
		# For each created issue, make a callback to determine its number?

	def edit_issue(username, repo, session, issue_num, todo):
		url = 'https://api.github.com/repos/' + username + '/' + repo + '/issues'
		update = {}
		line = 'line: ' + str(todo.line)+ '.  File: ' + todo.filename + '.\n'
		issue = {}
		issue['title'] = todo.title
		if todo.body is not None:
			issue['body'] = line + todo.body
		else:
			issue['body'] = line
		if todo.assignee is not None:
			issue['assignee'] = todo.assignee
		if todo.labels is not None:
			issue['labels'] = todo.labels
		if todo.milestone is not None:
			# Only accepts integers.
			issue['milestone'] = todo.milestone

		req = session.post(url, json.dumps(update))
		return req.status_code


	def close_issue(username, repo, session, issue_num):
		url = 'https://api.github.com/repos/' + username + '/' + repo + '/issues'
		close = {}
		close['state'] = 'close'
		req = session.patch(url, json.dumps())
		return req.status_code

	def fetch_issues(username, repo, session):
		url = 'https://api.github.com/repos/' + username + '/' + repo + '/issues'
		req = session.get(url)
		return req

	def process_fetch(session):
		response = GitTodoFindCommand.fetch_issues(session)
		response_json = response.json()
		response_length = len(response_json)
		for issue in response:
			pass
			# Add to gitTodo.txt file.
			# Check for duplicates.
			# Update with issue numbers

class Gittodo(object):
	review = False
	filename = None
	line = None
	title = None
	assignee = None
	body = None
	labels = None
	milestone = None

	def set_review(self, review):
		self.review = review
		return

	def set_filename(self, filename):
		self.filename = filename
		return

	def set_line(self, line):
		self.line = line
		return

	def set_title(self, title):
		self.title = title
		# return

	def set_body(self, body):
		self.body = body
		return

	def set_assignee(self, assignee):
		self.assignee = assignee
		return

	def set_labels(self, labels):
		self.labels = labels
		return

	def set_milestone(self, milestone):
		self.milestone = milestone
		return
