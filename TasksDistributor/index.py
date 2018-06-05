import random
import json
import sys
import os

from flask_sqlalchemy import SQLAlchemy
from flask import render_template
from flask import request
from flask import Flask
from flask import flash

from flask_wtf import CSRFProtect
from models import *

app = Flask(__name__)

# read database settings from config.json
with open('config.json', 'r') as f:
	config = json.load(f)

# set database settings
for key, value in config.items():
	app.config[key] = value

app.config['SECRET_KEY'] = os.urandom(30)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://{}:{}@{}/{}'.format(
	config['MYSQL_DATABASE_USER'],
	config['MYSQL_DATABASE_PASSWORD'],
	config['MYSQL_DATABASE_HOST'],
	config['MYSQL_DATABASE_DB']
)

db = SQLAlchemy(app)
db.init_app(app)

csrf = CSRFProtect()
csrf.init_app(app)

@app.route('/', methods=['POST', 'GET'])
def distribute_tasks():
	if request.method == 'POST':
		project_id = request.form['project_id']
		story_point = request.form['story_point']

		if project_id and story_point:
			# find project executors
			executor_in_projects = db.session.query(Executor).filter(
				Executor.projects.any(
					id=int(project_id)
				)
			).all()

			# find an executor with a min total load
			min_e = min(executor_in_projects, key=lambda e: e.get_total_load())

			# create a task with a specific executor_id
			task_no = min_e.tasks.count()+1
			task = Task(
				project_id=project_id,
				executor_id=min_e.id,
				name='Task {}'.format(task_no),
				description='It is task\'s {} description'.format(task_no),
				story_point=story_point
			)
			db.session.add(task)
			db.session.commit()

	projects = db.session.query(Project).all()
	executors = db.session.query(Executor).all()

	return render_template(
		'index.html',
		executors=executors,
		projects=projects
	)

if __name__ == "__main__":
	app.run()
