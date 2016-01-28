import sqlite3

def setupDB():
	print "Setting up DB..."
	db = sqlite3.connect('db.db')
	db.cursor().execute("""CREATE TABLE conversations ( 
						filename text primary key,
		                time timestamp,
		                size integer,
		                s_port integer,
		                d_port integer,
		                s_ip text,
		                d_ip text,
		                comment text,
		                flags integer,
		                service text, 
		                round integer, 
		                length integer,
		                foreign key(round) references rounds(num), 
		                foreign key(service) references service(name))
						""")
	db.cursor().execute("""CREATE TABLE rounds (
						num integer primary key unique, 
						s_time timestamp unique)
						""")
	db.cursor().execute("""CREATE TABLE services (
						id integer auto increment unique,
						name text, 
						port integer)
						""")
	db.commit()

setupDB()