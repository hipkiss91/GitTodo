import sublime
import sublime_plugin
import os
import sys
import re
import requests
import json
import subprocess
import traceback

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
	git_config_path = getoutput("git remote show origin -n")
	p = re.compile(r"(.+: )*([\w\d\.]+)[:|@]/?/?(.*)")
	parts = p.findall(git_config_path)
	if len(parts) == 0:
		return(False, 'No git config found. Please initiate GIT in this project in order to sync todos and issues.')
	else:
		git_config = parts[0][2]

	if ':' in git_config:
		# if SSH: {domain}:{user}/{repo}.git
		domain, user, repo = git_config.replace(".git", "").replace(":", "/").split("/")
		return ('ssh', domain, user, repo)
	else:
		# if HTTP: {domain}/{user}/{repo}.git
		domain, user, repo = git_config.replace(".git", "").split("/")
		return ('https', domain, user, repo)

class GitTodoFindCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		# Gets current directory.
		directories = get_setting('projects_dir', {})
		projects = get_setting('watch_projects', [])
		# Run on the current open window or if watch_projects is specified.
		config = get_repo_details(self)
		if config[0] == False:
			return(print(config[1]))
		if len(projects) < 1:
			if 'bitbucket' in config[1]:
				print('bitbucket Not currently supported')
				# return(print('bitbucket Not currently supported'))
			if '192.168' in config[1]:
				print('private local repos Not currently supported')
				# return(print('private local repos Not currently supported'))
			GitTodoFindCommand.process_project(directories, config[3])
		else:
			for project in projects:
				if config == project:
					GitTodoFindCommand.process_project(directories, project)
				else:
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
				if 'TODO' in line or 'todo' in line or 'Todo' in line: # Check each line for a 'todo'.
					GitTodoFindCommand.process_line(filename, num, line, todo_array)
			if len(todo_array) > 0:
				all_todos.append(todo_array)# append todos for each file into array of files.
		GitTodoFindCommand.store_local_todos(project, all_todos, dir_path)
		# GitTodoFindCommand.process_todo_array(all_todos)

	def get_filepaths(directory):
		""" This function will generate the file names in a directory tree by walking the tree either top-down or bottom-up. For each
		directory in the tree rooted at directory top (including top itself), it yields a 3-tuple (dirpath, dirnames, filenames).
		"""
		file_paths = []  # List which will store all of the full filepaths.

		# Walk the tree.
		for root, directories, files in os.walk(directory):
			# Currently this only does the current directory, need to adapt for all
			for filename in files:
				# Determine file type.
				ext = filename.split('.')[-1]
				if ext == 'js' or ext == 'html' or ext == 'css':
					# Join the two strings in order to form the full filepath.
					filepath = os.path.join(root, filename)
					file_paths.append(filepath)  # Add it to the list.

		return file_paths  # Self-explanatory.

	def process_line(file, num, line, todo_array):
		# This processes the line, it will return the correct object of format for each todo.
		# todo: [TITLE] Description of task goes here. @someone #bug #minor
		todo_file = file
		if line.find('[') < 0 or line.find(']') < 0 or line.find('@') < 0 or line.find('#') < 0:
			# print('TODO was not correctly formatted in file' + todo_file +', @ line '+str(num)+'. Please follow the formatting guidleines @ [insert URL here].')
			if line.find('TODO'):
				file_start = line.find('TODO')
			if line.find('todo'):
				file_start = line.find('todo')
			if line.find('Todo'):
				file_start = line.find('Todo')
				pass
			file_newline = line.find('\n')
			if file_newline:
				file_end = len(line) - 2
			else:
				file_end = len(line)
			todo_file = line[file_start:file_end]
			# todo_array.append(todo_file)
		else:
			# Process the title. START
			if line.find('[') and line.find(']'):
				title_start = line.find('[') + 1
				title_end = line.find(']')
				todo_title = line[title_start:title_end]
			# Process the title. End

			# Process the summary. START
			if line.find(']') and line.find('.', line.find(']')):
				summary_start = line.find(']') + 2
				summary_end = line.find('.')
				todo_summary = line[summary_start:summary_end]
			# Process the summary. End

			# Process the owner. START
			if line.find('@') and line.find(' ', line.find('@')):
				owner_start = line.find('@') + 1
				owner_end = line.find(' ', owner_start)
				todo_owner = line[owner_start:owner_end]
			# Process the owner. End

			# Process the labels. START
			if line.find('#'):
				todo_labels = []
				num = line.count('#')
				labels_start = line.find('#')
				labels_end = len(line.rstrip('\r\n'))
				if num > 1:
					label_string = line[labels_start:labels_end].split(' ')
					for label in label_string:
						start = 0
						end = len(label)
						todo_labels.append(label[start + 1:end])
				else:
					todo_labels.append(line[labels_start + 1:labels_end])
			# Process the labels. End

			# Add them all together and pass back to the parent.
			todo_array.append({	'filename'	:	todo_file,
								'title'		: 	todo_title,
								'assignee'	:	todo_owner,
								'body'		: 	todo_summary,
								'labels'	:	todo_labels})

	def store_local_todos(repo, todo_array, project_dir):
		# Store todo's locally in the root project dir.
		write_path = project_dir + '\\gitTodo.txt'
		try:
			mode = 'a' if os.path.exists(write_path) else 'w'
			with open(write_path, mode) as file:
				path = open(write_path).read()
				for todo in todo_array:
					if mode == 'a':
						if json.dumps(todo) not in path:
							GitTodoFindCommand.process_todo(repo, todo)
							file.write(json.dumps(todo) + '  \n')
					else:
						GitTodoFindCommand.process_todo(repo, todo)
						file.write(json.dumps(todo) + '  \n')
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
		# issue = {'filename'	:	todo_file, 'title': 'title', 'assignee':'hipkiss91', 'body':'body', 'labels':['labels']}
		print(username, repo)
		url = 'https://api.github.com/repos/' + username + '/Dayamo/issues'
		# url = 'https://api.github.com/repos/' + username + '/' + repo + '/issues'
		issue = {'title': todo[0]['title'], 'assignee': todo[0]['assignee'], 'body': todo[0]['filename'] + '.\n' + todo[0]['body'], 'labels': todo[0]['labels']}
		req = session.post(url, json.dumps(issue))
		return req.status_code
