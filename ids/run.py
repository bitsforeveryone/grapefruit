#!/usr/bin/env python

import json
import sqlite3
import subprocess
from flask import Flask, render_template, send_from_directory, g

app = Flask(__name__)

CONVO_DIR="conversations/"
services = []

DATABASE = 'db.db'
def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = sqlite3.connect(DATABASE)
    return g.sqlite_db

@app.route('/bower_components/<path:path>')
def send_bower(path):
    return send_from_directory('./templates/bower_components', path)

@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('./templates/js', path)

@app.route('/dist/<path:path>')
def send_dist(path):
    return send_from_directory('./templates/dist', path)

def getServices():
	res = get_db().execute("SELECT * FROM services").fetchall()
	for service in res:
		if (service[0] not in services):
			services.append(service[0])
	return res

def getConversationGraphData(service):
	graph = {}
	graph['element'] = "morris-bar-chart"
	graph['data'] = []
	graph['xkey'] = 'x'
	graph['ykeys'] = ['y']
	graph['labels'] = ['Size'] 
	port = service[1]
	for i in range(1,6):
		graph['data'].append({"x": 10**i, "y": int(subprocess.check_output("find {0}/{1} -type f | wc -l".format(CONVO_DIR+str(port), 10**i), shell=True).strip())})
	return json.dumps(graph)

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
    graphData = getConversationGraphData(service)

    return render_template("pages/service.html", service=service, convoNum=convoNum, graphData=graphData)

@app.route('/services/<string:service>/<int:roundNum>')
def conversations(service, roundNum):
    if service not in services:
        return "Service not found.", 404

    service=get_db().execute("SELECT * FROM services WHERE name = (?)", [service]).fetchone()
    roundNum=get_db().execute("SELECT * FROM rounds ORDER BY round ASC LIMIT 1")
    convoNum = getConversationsByService(service)
    graphData = getConversationGraphData(service)
    return render_template("pages/conversations.html", round=roundNum, service=service, convoNum=convoNum, graphData=graphData)

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
