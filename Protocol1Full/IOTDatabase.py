import sqlite3
import unicodedata

class database_server:

	db_file = '/home/husainshoab/iotsesfinal/Protocol1Full/DB/iot.db' #path to database file
	table_name = 'iot_data' #name of table
	column1 = 'device_id' #field to store device id
	column2 = 'challenge' #field to store challenge
	column3 = 'response' #field to store response
	field_type = 'VARCHAR(16)' 

	def __init__(self):
		self.conn = None
		self.conn_obj = None

	def startDBConnection(self): #starts database connection
		self.conn = sqlite3.connect(self.db_file)
		self.conn.text_factory = bytes
		self.conn_obj = self.conn.cursor()
		
	def create_table(self): #creates the table
		self.conn_obj.execute('CREATE TABLE {tn} ({c1} {ft} PRIMARY KEY, {c2} {ft}, {c3} {ft})'\
					.format(tn=self.table_name, c1=self.column1, ft=self.field_type, c2=self.column2, c3=self.column3))
		
	def insert_entry(self, id, ch, rs): #inserts a tuple into the table - (id, challenge, response)
		try:
			self.conn_obj.execute('INSERT INTO {tn} ({c1}, {c2}, {c3}) VALUES ("{v1}", "{v2}", "{v3}")'\
					.format(tn=self.table_name, c1=self.column1, c2=self.column2, c3=self.column3, v1=id, v2=ch, v3=rs))
		except sqlite3.IntegrityError:
			print('ERROR: ID already exists in PRIMARY KEY column {}'.format(self.column1))
		self.conn.commit()
		
	def return_entry(self, id): # returns (challenge, response) if id match is found
		self.conn_obj.execute('SELECT {c2}, {c3} FROM {tn} WHERE {c1}="{val}"'\
							.format(tn=self.table_name, c1=self.column1, c2=self.column2, c3=self.column3, val=id))
		id_exists = self.conn_obj.fetchone()
		
		if id_exists:
			Cx = id_exists[0]
			Rx = id_exists[1]
			return (str(Cx),str(Rx))
		else:
			print('{} does not exist! Authentication Error!'.format(id))
			return ""

	def update_entry(self,id,ch,rs): # updates the id-matching entry in database
		self.conn_obj.execute('UPDATE {tn} SET {c2}="{v2}",{c3}="{v3}" WHERE {c1}="{val}"'\
					.format(tn=self.table_name, c1=self.column1, c2=self.column2, c3=self.column3, val=id, v2=ch, v3=rs))
		self.conn.commit()

	def drop_table(self): # drops the table
		self.conn_obj.execute('DROP TABLE {tn}'.format(tn=self.table_name))
		self.conn.commit()

	def display_entries(self): # displays the database contents
		self.conn_obj.execute('SELECT * FROM {tn}'.format(tn=self.table_name))
		rows = self.conn_obj.fetchall()
		print('ID\t\t\tChallenge\t\t\tResponse')
		for r in rows:
			print('{}\t{}\t{}'.format(r[0],r[1],r[2]))
	
	def endDBConnection(self): #ends database connection 
		self.conn.close()
