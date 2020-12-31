import sqlite3
import pyodbc


class Database:
	def insert_entry(self):
		pass

	def service(self):
		pass

	def __init__(self, database, user, password):
		conn = pyodbc.connect(
			'DSN={0};UID={1};PWD={2}'.format(database, user, password), timeout=1)
		cursor = conn.cursor()
		cursor.execute('Select * from usu_tetiqbag')
		for row in cursor.fetchall():
			print(row)
