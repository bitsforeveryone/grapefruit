import sqlite3
from flask import Flask, render_template, send_from_directory, g

app = Flask(__name__)

services = []

DATABASE = 'db.db'
def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = sqlite3.connect(DATABASE)
    return g.sqlite_db

@app.route('/bower_components/<path:path>')
def send_bower(path):
    return send_from_directory('templates/bower_components', path)

@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('templates/js', path)

@app.route('/dist/<path:path>')
def send_dist(path):
    return send_from_directory('templates/dist', path)

def getServices():
	res = get_db().execute("SELECT * FROM services").fetchall()
	for service in res:
		if (service[0] not in services):
			services.append(service[0])
	return res

@app.route('/services')
def serviceList():
	services = getServices()
	return render_template("pages/services.html", services=services)

@app.route('/services/<string:service>')
def service(service):
    if service not in services:
        return "Service not found.", 404

    service=get_db().execute("SELECT * FROM services WHERE name = (?)", [service]).fetchone()

    return render_template("pages/service.html", service=service)

@app.route('/services/<string:service>/<int:roundNum>')
def conversations(service, roundNum):
    if service not in services:
        return "Service not found.", 404
    return render_template("pages/conversations.html", round=roundNum, service=service)

@app.route('/')
@app.route('/index.html')
def index():
	return render_template("pages/index.html", serviceNum=len(services))

def setupDB():
	with app.app_context():
		print "Setting up DB..."
		db = sqlite3.connect('db.db')
		db.cursor().execute("CREATE TABLE rounds (round text primary key unique, time timestamp)")
		db.cursor().execute("CREATE TABLE services (name text primary key, port integer)")
		db.commit()

		db.cursor().execute("INSERT INTO services VALUES ('battleship',1337)")
		db.commit()

if __name__ == '__main__':
    app.run()
