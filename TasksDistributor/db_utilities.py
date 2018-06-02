from flaskext.mysql import MySQL
from mysql import connector
import random

class TasksDistributorDB:
	def __init__(self, app):
		self.mysql = MySQL()
		self.mysql.init_app(app)

	def get_all_rows(self, table):
		try:
			connection = self.mysql.connect()
			cursor = connection.cursor()

			query = "SELECT * FROM {}".format(table)
			cursor.execute(query)
			return cursor.fetchall()
		except connector.Error as error:
			print(error)
			return []
		finally:
			cursor.close()
			connection.close()

	def create_task(self, project_id, executor_id, story_point):
		try:
			connection = self.mysql.connect()
			cursor = connection.cursor()

			projects = self.get_all_rows('Projects')
			tasks = self.get_all_rows('Tasks')
			tasks_in_project = [t for t in tasks if str(t[1]) == project_id]
			new_task = len(tasks_in_project)+1

			query = """
				INSERT INTO Tasks (
					project_id, executor_id, name, 
					description, story_point
				) 
				VALUES (%s, %s, %s, %s, %s)
			"""
			dbargs = (
				project_id, 
				executor_id,
				'Task {}'.format(new_task),
				"It is task's description {}".format(new_task),
				story_point,
			)
			cursor.execute(query, dbargs)
			connection.commit()

			return cursor.lastrowid
		except connector.Error as error:
			print(error)
			return -1
		finally:
			cursor.close()
			connection.close()

	def find_executor_id(self, project_id):
		try:
			connection = self.mysql.connect()
			cursor = connection.cursor()

			query = """
				SELECT mins.executor_id, SUM(mins.story_point) as min FROM (
					SELECT available_executors.executor_id, story_point FROM Tasks 
					RIGHT OUTER JOIN (
						SELECT executor_id FROM ExecutorsProjects 
						WHERE project_id = %s
					) as available_executors 
					ON Tasks.executor_id = available_executors.executor_id
				) as mins 
				GROUP BY mins.executor_id ORDER BY min ASC LIMIT 1;
			"""
			dbargs = (project_id,)
			cursor.execute(query, dbargs)
			db_executor = cursor.fetchall()
			return db_executor[0][0]
		except connector.Error as error:
			print(error)
			return -1
		finally:
			cursor.close()
			connection.close()

