DB=db.db

all: db
	./splitcap.sh "data/*.pcap*"

db:
ifneq ($(wildcard $(DB)),)
	echo 'database exists'
else
	sqlite3 $(DB) "CREATE TABLE IF NOT EXISTS conversations ( filename text,time timestamp primary key,size integer,s_port integer,d_port integer,s_ip text,d_ip text,comment text,flags integer,service integer, round integer, length integer,foreign key(round) references rounds(num), foreign key(service) references service(id));"
	sqlite3 $(DB) "CREATE TABLE IF NOT EXISTS rounds (num integer primary key unique);" 
	sqlite3 $(DB) "CREATE TABLE IF NOT EXISTS services (id integer primary key unique,name text unique, port integer unique);"
	sqlite3 $(DB) "CREATE TABLE IF NOT EXISTS alerts (id integer primary key,timePassed timestamp,timeFound timestamp,regex text,seen integer default 0,round integer,foreign key(timePassed) references conversations(time),foreign key(regex) references regexes(regex)foreign key(round) references rounds(num)CONSTRAINT unq UNIQUE (timePassed, regex));"
	sqlite3 $(DB) "CREATE TABLE IF NOT EXISTS regexes (regex text unique,lastRound integer default 0);"
	mkdir -p data/conversations
#	mkdir -p data/done
endif

clean:
	rm db.db
	rm -rf data/conversations/*
#	mv data/done/* data/.
