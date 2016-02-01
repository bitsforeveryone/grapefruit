import sqlite3

def setupDB():
	print "Setting up DB..."
	db = sqlite3.connect('db.db')
	db.cursor().execute("""CREATE TABLE conversations ( 
		                filename text,
		                time timestamp primary key,
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
		                id integer unique,
		                name text, 
		                port integer primary key unique)
		                """)
	db.cursor().execute("""CREATE TABLE alerts (
		                id integer primary key,
		                filename text,
		                regex text,
		                seen integer default 0,
		                round integer,
		                foreign key(filename) references conversations(filename),
		                foreign key(regex) references regexes(regex)
		                foreign key(round) references rounds(num)
		                CONSTRAINT unq UNIQUE (filename, regex))
		                """)
	db.cursor().execute("""CREATE TABLE regexes (
		                regex text unique,
		                lastRound integer default 0)
		                """)


	db.cursor().execute("INSERT INTO services (name,port) VALUES ('sheepheap', 3000)")
	db.cursor().execute("INSERT INTO services (name,port) VALUES ('battleship', 3001)")
	db.cursor().execute("INSERT INTO services (name,port) VALUES ('banananana', 3002)")
	db.cursor().execute("INSERT INTO services (name,port) VALUES ('imoutofnames', 3003)")
	db.cursor().execute("INSERT INTO rounds VALUES (0, datetime('now'))")
	db.commit()

setupDB()