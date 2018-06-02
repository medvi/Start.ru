import argparse
import random
import json

from mysql import connector

TABLES = {}
TABLES['Projects'] = (
	"CREATE TABLE IF NOT EXISTS Projects ("
	"  id INT NOT NULL AUTO_INCREMENT,"
	"  name VARCHAR(100) NOT NULL,"
	"  description VARCHAR(1000) NULL,"
	"  PRIMARY KEY (id)"
	") ENGINE=InnoDB"
)

TABLES['Executors'] = (
	"CREATE TABLE IF NOT EXISTS Executors ("
	"  id INT NOT NULL AUTO_INCREMENT,"
	"  name VARCHAR(100) NOT NULL,"
	"  PRIMARY KEY (id)"
	") ENGINE=InnoDB"
)

TABLES['Tasks'] = (
	"CREATE TABLE IF NOT EXISTS Tasks ("
	"  id INT NOT NULL AUTO_INCREMENT,"
	"  project_id INT NOT NULL,"
	"  executor_id INT,"
	"  name VARCHAR(100) NOT NULL,"
	"  description VARCHAR(1000) NULL,"
	"  story_point INT NOT NULL,"
	"  PRIMARY KEY (id),"
	"  FOREIGN KEY (project_id)"
	"    REFERENCES Projects(id)"
	"    ON DELETE CASCADE,"
	"  FOREIGN KEY (executor_id)"
	"    REFERENCES Executors(id)"
	"    ON DELETE SET NULL"
	") ENGINE=InnoDB"
)

TABLES['ExecutorsProjects'] = (
	"CREATE TABLE IF NOT EXISTS ExecutorsProjects ("
	"  id INT NOT NULL AUTO_INCREMENT,"
	"  executor_id INT NOT NULL,"
	"  project_id INT NOT NULL,"
	"  PRIMARY KEY (id),"
	"  FOREIGN KEY (executor_id)"
	"    REFERENCES Executors(id)"
	"    ON DELETE CASCADE"
	") ENGINE=InnoDB"
)

PROJECTS_COUNT = 10
TASKS_COUNT = 50
EXECUTORS_COUNT = 10

def create_tables(con, cursor):
	for name, query in TABLES.items():
		try:
			print("creating tables: {}".format(name))
			cursor.execute(query)
			con.commit()
		except connector.Error as error:
			print(error.msg)


def clear_database(con, cursor):
	query = "DELETE FROM %s"
	for name, _ in TABLES.items():
		cursor.execute(query % name)

	con.commit()

def execute_many(con, cursor, query, dbargs, msg):
	try:
		print(msg, end='')
		cursor.executemany(query, dbargs)
		con.commit()
	except connector.Error as error:
		print(error.msg)
		return

	print("OK")


def populate_projects(con, cursor):
	query = 'INSERT INTO Projects (name, description) VALUES (%s, %s)'
	dbargs = [
		(
			'Project {}'.format(i), 
			"It is project's description {}".format(i),
		) for i in range(PROJECTS_COUNT)
	]

	execute_many(con, cursor, query, dbargs, "Populating projects...")


def populate_tasks(con, cursor):
	cursor.execute('SELECT id FROM Projects')
	projects = list(cursor.fetchall())

	cursor.execute('SELECT project_id FROM Tasks')
	tasks = list(cursor.fetchall())

	queryTasks = 'INSERT INTO Tasks (project_id, name, description, story_point) '\
			'VALUES (%s, %s, %s, %s)'

	dbargs = []
	for i in range(TASKS_COUNT):
		rand_project = random.randint(0, len(projects)-1)
		tasks_in_project = [t for t in tasks if t[0] == projects[rand_project][0]]
		new_task = len(tasks_in_project)+1

		dbargsTasks.append((
			projects[rand_project][0],
			'Task {}'.format(new_task),
			"It is task's description {}".format(new_task),
			random.randint(0, 10),
		))
		tasks.append(projects[rand_project])

	execute_many(con, cursor, query, dbargs, "Populating tasks...")


def populate_executors(con, cursor):
	query = "INSERT INTO Executors (name) VALUES (%s)"
	dbargs = [
		(
			'Executor {}'.format(i),
		) for i in range(EXECUTORS_COUNT)
	]

	execute_many(con, cursor, query, dbargs, "Populating executors...")


def populate_executors_projects(con, cursor):
	cursor.execute('SELECT id FROM Projects')
	projects = list(cursor.fetchall())

	cursor.execute('SELECT id FROM Executors')
	executors = list(cursor.fetchall())

	query = "INSERT INTO ExecutorsProjects (executor_id, project_id) VALUES (%s, %s)"
	dbargs = []
	for i in range(PROJECTS_COUNT):
		e_temp = list(executors)
		for j in range(random.randint(1, EXECUTORS_COUNT-1)):
			ch = random.choice(e_temp)
			e_temp.remove(ch)
			dbargs.append(
				(
					projects[i][0],
					ch[0],
				)
			)

	execute_many(con, cursor, query, dbargs, "Populating executors_projects...")


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument(
		"-c",
		"--clear",
		help="Clear database",
		action="store_true",
	)
	args = parser.parse_args()

	with open('config.json', 'r') as f:
		config = json.load(f)

	con = connector.connect(
		user=config['MYSQL_DATABASE_USER'],
		password=config['MYSQL_DATABASE_PASSWORD'],
		host=config['MYSQL_DATABASE_HOST'],
		database=config['MYSQL_DATABASE_DB']
	)
	cursor = con.cursor()

	try:
		if args.clear:
			clear_database(con, cursor)

		create_tables(con, cursor)

		populate_projects(con, cursor)
		populate_executors(con, cursor)
		populate_executors_projects(con, cursor)

		cursor.close()
	except connector.Error as error:
		print(error)
	finally:
		con.close()

