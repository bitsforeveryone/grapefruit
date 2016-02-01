#!/usr/bin/env python

import re
import os
import sqlite3, json

from math import ceil, log10
from flask import Flask, render_template, send_from_directory, g, request, redirect, url_for

app = Flask(__name__)

DEBUG=False

CURRENT_ROUND = 1
CONVO_DIR="conversations/"
STAGING_DIR="staging/"
services = []

DATABASE = 'db.db'
def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = sqlite3.connect(DATABASE)
    return g.sqlite_db
def getCharts(service, conversations):
	graph = {}
	graph['element'] = "morris-bar-chart"
	graph['data'] = []
	graph['xkey'] = 'x'
	graph['ykeys'] = ['y']
	graph['labels'] = ['Size'] 
	port = service[1]
	bins = [0, 0, 0, 0, 0, 0, 0]
	for convo in conversations:
		if convo[2] != 0:
			bins[int(ceil(log10(convo[2]))-1)] += 1
	for n in range(len(bins)):
		graph['data'].append({"x": 10**n, "y": bins[n]})
	return json.dumps(graph)
def getServices():
	res = get_db().execute("SELECT name FROM services").fetchall()
	for service in res:
		if (service[0] not in services):
			services.append(service[0])
	return res
def getAlerts():
	alerts = get_db().execute("SELECT * FROM alerts WHERE seen != 1").fetchall()
	return alerts

def generateAlerts():
	patterns = []
	regexs = get_db().execute("SELECT regex FROM regexes WHERE lastRound < ?", 
	                         [CURRENT_ROUND])
	for reg in regexs:
		patterns.append(reg[0])

	for f in os.listdir("conversations/"):
		for pattern in patterns:
			patternReg = re.compile(r'{0}'.format(pattern))
			for match in re.finditer(patternReg, open("conversations/"+f,'r').read()):
				get_db().execute("UPDATE regexes SET lastRound = ? WHERE regex = ?",
				                 [CURRENT_ROUND, pattern])
				try:
					get_db().execute("INSERT INTO alerts (filename, regex, round) VALUES (?,?,?)",
					                 [f,pattern, CURRENT_ROUND-1])
				except sqlite3.IntegrityError:
					break
				get_db().commit()

@app.route('/bower_components/<path:path>')
def send_bower(path):
    return send_from_directory('./templates/bower_components', path)

@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('./templates/js', path)

@app.route('/dist/<path:path>')
def send_dist(path):
    return send_from_directory('./templates/dist', path)

@app.route('/conversations/<path:path>')
def send_convo(path):
    return send_from_directory('./conversations', path)

@app.route('/services')
def serviceList():
	services = getServices()
	return render_template("pages/services.html", services=services)

@app.route('/services/<string:service>')
def service(service):
    if service not in services:
        return "Service not found.", 404

    sort = request.args.get('sortby') if request.args.get('sortby') else "time"
    serviceObj=get_db().execute("SELECT * FROM services WHERE name = (?)", [service]).fetchone()
    conversations=get_db().execute("SELECT * FROM conversations WHERE service = (?) ORDER BY {0}".format(sort), [service]).fetchall()
    return render_template("pages/service.html", service=serviceObj, conversations=conversations, convoLen=len(conversations), graphData=getCharts(service,conversations))

@app.route('/services/<string:service>/<int:roundNum>')
def conversations(service, roundNum):
    if service not in services:
        return "Service not found.", 404

    sort = str(request.args.get('sortby').replace("'", "").replace("*", "")) if request.args.get('sortby') else "time"
    serviceObj=get_db().execute("SELECT * FROM services WHERE name = (?)", [service]).fetchone()
    conversations=get_db().execute("SELECT * FROM conversations WHERE service = (?) AND round = (?) ORDER BY {0}".format(sort), [service, roundNum]).fetchall()
    print type(conversations)
    for convo in conversations:
    	print convo
    return render_template("pages/service.html", service=serviceObj, conversations=conversations, convoLen=len(conversations), graphData=getCharts(service,conversations))

@app.route('/regex', methods=['POST'])
def addRegex():
	pattern = request.form['regex']
	get_db().execute("INSERT INTO regexes (regex) VALUES (?)", [pattern])
	get_db().commit()
	return redirect("/debug/alerts")

@app.route('/alerts/dismiss/<int:idnum>')
def dismissAlert(idnum):
	get_db().execute("UPDATE alerts SET seen=1 WHERE id=(?)", [idnum])
	get_db().commit()
	return redirect("/alerts")

@app.route('/alerts/clear')
def clearAlerts():
	get_db().execute("UPDATE alerts SET seen=0")
	get_db().commit()
	return redirect("/alerts")

@app.route('/alerts')
def alertDashboard():
	return render_template('pages/alerts.html', alerts=getAlerts())

# TODO: REMOVE THIS
@app.route('/debug/report')
def debugReport():
	parseReport("conversations/report.xml")
	return redirect("/")
@app.route('/debug/alerts')
def alerts():
	generateAlerts()			
	return redirect("/alerts")

@app.route('/')
@app.route('/index.html')
def index():
	getServices()
	numAlerts = get_db().execute("SELECT count(*) FROM alerts WHERE seen != 1").fetchone()[0]
	return render_template("pages/index.html", serviceNum=len(services), alertNum=numAlerts)
	
if __name__ == '__main__':
    app.run(debug=DEBUG, host='0.0.0.0')
