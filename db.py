import sqlite3
import pyodbc


class Database:
	def insert_entry(self):
		pass

	def service(self):
		pass

	def __init__(self):
		conn = pyodbc.connect(
			'DSN=Sapiens;UID=sa;PWD=pds2772@', timeout=1)
		cursor = conn.cursor()
		cursor.execute('Select * from usu_tetiqbag')
		for row in cursor.fetchall():
			print(row)


Database()
