import sqlite3
import subprocess
from flask import Flask, render_template, send_from_directory, g

app = Flask(__name__)

CONVO_DIR="conversations/"
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

def getConversationsByService(service):
	port = service[1]
	return subprocess.check_output("find {0} -type f | wc -l".format(CONVO_DIR+str(port)), shell=True)

@app.route('/services')
def serviceList():
	services = getServices()
	return render_template("pages/services.html", services=services)

@app.route('/services/<string:service>')
def service(service):
    if service not in services:
        return "Service not found.", 404

    service=get_db().execute("SELECT * FROM services WHERE name = (?)", [service]).fetchone()
    convoNum = getConversationsByService(service)
    return render_template("pages/service.html", service=service, convoNum=convoNum)

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
    app.run(debug=True)
