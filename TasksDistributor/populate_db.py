import random

from models import *
from index import db

PROJECTS_COUNT = 10
TASKS_COUNT = 50
EXECUTORS_COUNT = 10

def populate_projects(executors):
	projects = []
	for i in range(PROJECTS_COUNT):
		project = Project(
			name='Project {}'.format(i),
			description='It is project\'s description {}'.format(i),
		)

		rand_executors = random.sample(
			executors, random.randint(1, len(executors)-1)
		)
		for e in rand_executors:
			project.executors.append(e)

		projects.append(project)

	return projects


def populate_executors():
	return [
		Executor(name='Executor {}'.format(i)) 
		for i in range(EXECUTORS_COUNT)
	]


if __name__ == "__main__":
	executors = populate_executors()
	[db.session.add(e) for e in executors]
	db.session.commit()
	print('Successful insertion into the EXECUTOR!')

	projects = populate_projects(executors)
	[db.session.add(p) for p in projects]
	db.session.commit()
	print('Successful insertion into the PROJECT and EXECUTOR_PROJECT!')
