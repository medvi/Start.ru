import random
import json
import os

from flask import render_template
from flask import request
from flask import Flask
from flask import flash

from flask_wtf import CSRFProtect
from db_utilities import *

app = Flask(__name__)

# read database settings from config.json
with open('config.json', 'r') as f:
	config = json.load(f)

# set database settings
for key, value in config.items():
	app.config[key] = value

app.config['SECRET_KEY'] = os.urandom(30)

db = TasksDistributorDB(app)

csrf = CSRFProtect()
csrf.init_app(app)

@app.route('/', methods=['POST', 'GET'])
def distribute_tasks():
	projects = db.get_all_rows('Projects')
	executors = [list(e) for e in db.get_all_rows('Executors')]

	if request.method == 'POST':
		project_id = request.form['project_id']
		story_point = request.form['story_point']

		if project_id and story_point:
			executor_id = db.find_executor_id(project_id)

			inserted_task_id = db.create_task(
				project_id, executor_id, story_point
			)
			if inserted_task_id < 0:
				print(
					"Some problems occured while creating "
					"a record in the table 'Tasks' =("
				)
				flash(
					"Невозможно создать задачу с project_id='{}'"
					"и story_point='{}'"
					.format(project_id, story_point)
				)
			else:
				print('Task created!')
				flash('Задача добавлена!')
		else:
			print('Cann\'t create task!')
			flash(
				"Невозможно создать задачу с project_id='{}'"
				"и story_point='{}'"
				.format(project_id, story_point)
			)

	executors_projects = db.get_all_rows('ExecutorsProjects')
	executors_projects = sorted(executors_projects, key=lambda x: x[2])
	tasks = db.get_all_rows('Tasks')

	# for a description of this loop, see below
	executors_projects_tasks = []
	for executor in executors:
		prs = []
		total_load = 0
		for p in executors_projects:
			if executor[0] == p[1]:
				prs.append([])
				prs[-1].append(p[2])
				for project in projects:
					if project[0] == p[2]:
						prs[-1].append(project[1])
						prs[-1].append(project[2])
				prs[-1].append([])
				for t in tasks:
					if t[1] == p[2] and t[2] == executor[0]:
						total_load += t[5]
						prs[-1][-1].append((t[0], t[3], t[4], t[5]))

		executors_projects_tasks.append([
			executor[0], executor[1], total_load, prs
		])

# for example, executors_projects_tasks =
#	[
# 		[
#			executor1_id, executor1_name, total_load, [
# 				[
#					project1_id, project1_name, project1_description, [
#						(task1_id, task1_name, task1_description, story_point), 
#						(task1_id, task1_name, task1_description, story_point) 
#					]
#				], 
# 				[
#					project2_id, project2_name, project2_description, [
#						(task1_id, task1_name, task1_description, story_point), 
#						(task2_id, task2_name, task2_description, story_point) 
#					]
#				] 
#		], ...
#	]
# i.e. executors with all their projects and tasks

	return render_template(
		'index.html', projects=projects, 
		executors_projects_tasks=executors_projects_tasks,
	)

if __name__ == "__main__":
	app.run()
