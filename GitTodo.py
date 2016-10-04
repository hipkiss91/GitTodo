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

	# Switch to cwd of file
	os.chdir(path + "/")
	git_config_path = getoutput("git remote show origin -n")
	p = re.compile(r"(.+: )*([\w\d\.]+)[:|@]/?/?(.*)")
	parts = p.findall(git_config_path)
	if len(parts) == 0:
		return(False, 'No git config found. Please initiate GIT in this project in order to sync todos and issues.')
	else:
		git_config = parts[0][2]

	if ':' in git_config:
		# SSH repository format: {domain}:{user}/{repo}.git
		domain, user, repo = git_config.replace(".git", "").replace(":", "/").split("/")
		return ('ssh', domain, user, repo)
	else:
		# HTTP repository format: {domain}/{user}/{repo}.git
		domain, user, repo = git_config.replace(".git", "").split("/")
		return ('https', domain, user, repo)

class GitTodoFindCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		# Gets current directory.
		directories = get_setting('projects_dir', {})
		# Run on the current open window or if watch_projects is specified.
		config = get_repo_details(self)
		if config[0] == False:
			return(print(config[1]))
		GitTodoFindCommand.process_project(directories, config[3])

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
						GitTodoFindCommand.process_line(filename, num, line, todo_array)
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

	def process_line(file, num, line, todo_array):
		mytodo = Gittodo()
		mytodo.set_filename(file)
		mytodo.set_line(num)
		# This processes the line, it will return the correct object of format for each todo.
		# todo: [TITLE] (Description of task goes here.) @someone #bug #minor *milestone
		if not line.find('[') > 0 and not line.find(']', line.find('[')) > 0:
			print('Todo was not correctly formatted in file' + file +', @ line '+str(num)+'. Please follow the formatting guidleines @ https://github.com/hipkiss91/GitTodo/blob/master/README.md.')
			print('The minimum required to submit an issue is a title. All incorrectly formatted todos can be found in the gitTodo.txt file')
			for todo_case in todos_array:
				if line.find(todo_case) > 0:
					file_start = line.find(todo_case)
			file_newline = line.find('\r\n')
			if file_newline:
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

			# Process the summary. START
			if line.find('(') > 0 and line.find(')') > 0:
				body_start = line.find('(') + 1
				body_end = line.find(')')
				todo_body = line[body_start:body_end]
				mytodo.set_body(todo_body)
			# Process the summary. End

			# Process the owner. START
			if line.find('@') > 0 and line.find(' ', line.find('@')) > 0:
				assignee_start = line.find('@') + 1
				assignee_end = line.find(' ', assignee_start)
				todo_assignee = line[assignee_start:assignee_end]
				mytodo.set_assignee(todo_assignee)
			# Process the owner. End

			# Process the labels. START
			if line.find('#') > 0:
				todo_labels = []
				labels = line.count('#')
				labels_start = line.find('#')
				labels_end = len(line.rstrip('\r\n'))
				if labels > 1:
					label_string = line[labels_start:labels_end].split(' ')
					for label in label_string:
						start = 0
						end = len(label)
						todo_labels.append(label[start + 1:end])
						mytodo.set_labels(todo_labels)
				else:
					todo_labels.append(line[labels_start + 1:labels_end])
					mytodo.set_labels(todo_labels)
			# Process the labels. End

			# Process the milestones. START
			if line.find('*') > 0:
				ms_start = line.find('*') + 1
				ms_end = line.find(' ', ms_start)
				todo_ms = line[ms_start:ms_end]
			# Process the milestones. End

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
						issue = json.dumps(todo.__dict__) # JSON dump the object, for file write.
						if mode == 'a':
							if issue not in path: # Checks if it's already in the file.
								if todo.review == False:
									GitTodoFindCommand.process_todo(repo, todo)
								file.write(issue + '\n')
						else:
							if todo.review == False:
								GitTodoFindCommand.process_todo(repo, todo)
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
		# url = 'https://api.github.com/repos/' + username + '/' + repo + '/issues'
		issue = {}
		issue['title'] = todo.title
		if todo.assignee is not None:
			issue['assignee'] = todo.assignee
		line = 'line: ' + str(todo.line)+ '.  File: ' + todo.filename + '.\n'
		if todo.body is not None:
			issue['body'] = line + todo.body
		else:
			issue['body'] = line
		if todo.labels is not None:
			issue['labels'] = todo.labels
		if todo.milestone is not None:
			pass
			# issue['milestone'] = todo.milestone
		req = session.post(url, json.dumps(issue))
		return req.status_code

# A Class for each Todo.
class Gittodo(object):
	# Options and methods are self explanatory.
	review = False # Whether or not to be submitted as an issue or just submitted to the gitTodo.txt for review.
	filename = None
	line = None
	title = None
	assignee = None
	body = None
	labels = None
	milestone = None

	def set_review(self, review):
		self.review = review

	def set_filename(self, filename):
		self.filename = filename

	def set_line(self, line):
		self.line = line

	def set_title(self, title):
		self.title = title

	def set_body(self, body):
		self.body = body

	def set_assignee(self, assignee):
		self.assignee = assignee

	def set_labels(self, labels):
		self.labels = labels

	def set_milestone(self, milestone):
		self.milestone = milestone
