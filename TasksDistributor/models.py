from flask_sqlalchemy import SQLAlchemy

from index import db

ExecutorProject = db.Table(
	'executor_project',
	db.Column(
		'executor_id',
		db.Integer,
		db.ForeignKey('executor.id'),
		primary_key=True
	),
	db.Column(
		'project_id',
		db.Integer,
		db.ForeignKey('project.id'),
		primary_key=True
	)
)

class Project(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(100), unique=True, nullable=False)
	description = db.Column(db.String(100))
	tasks = db.relationship('Task', backref='project', lazy=True)
	executors = db.relationship(
		'Executor', 
		secondary=ExecutorProject, 
		lazy='subquery',
		backref=db.backref('projects', lazy=True)
	)

	def __repr__(self):
		return '<Project {}>'.format(self.name)

class Executor(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(100), unique=True, nullable=False)
	tasks = db.relationship('Task', backref='executor', lazy='dynamic')

	def get_total_load(self):
		return sum(t.story_point for t in self.tasks)

	def __repr__(self):
		return '<Executor {}>'.format(self.name)

class Task(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
	executor_id = db.Column(db.Integer, db.ForeignKey('executor.id'), nullable=False)
	name = db.Column(db.String(100), nullable=False)
	description = db.Column(db.String(100))
	story_point = db.Column(db.Integer)

	def __repr__(self):
		return '<Task {}>'.format(self.name)
