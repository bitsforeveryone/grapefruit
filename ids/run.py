#!/usr/bin/env python

import re
import os
import sqlite3, json
import StringIO

from hexdump import hexdump
from math import ceil, log10
from flask import Flask, render_template, send_from_directory, g, request, redirect, url_for, send_file

app = Flask(__name__)

DEBUG=True
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
	bins = [0]*10
	for convo in conversations:
		if convo[2] != 0:
			bins[int(ceil(log10(convo[2]))-1)] += 1
	for n in range(len(bins)):
		graph['data'].append({"x": 10**n, "y": bins[n]})
	return json.dumps(graph)

def getNumAlerts():
	numAlerts = get_db().execute("SELECT count(*) FROM alerts WHERE seen != 1").fetchone()[0]
	return numAlerts

def getNumServices():
	numServices = get_db().execute("SELECT count(*) FROM services").fetchone()[0]
	return numServices

def getNumRounds():
	numRounds = get_db().execute("SELECT count(*) FROM rounds").fetchone()[0]
	return numRounds

def getRegexes():
	regexes = get_db().execute("SELECT * FROM regexes").fetchall()
	return regexes

def getServices():
	res = get_db().execute("SELECT * FROM services").fetchall()
	print len(res)
	return res

def getAlerts():
	alerts = get_db().execute("SELECT * FROM alerts as a JOIN conversations as c ON a.timePassed = c.time JOIN services as s ON c.service=s.id WHERE seen != 1").fetchall()
	return alerts

def generateAlerts():
	patterns = []
	files = []
	regexs = get_db().execute("SELECT regex FROM regexes WHERE lastRound < (SELECT MAX(num) FROM rounds)").fetchall()
	for reg in regexs:
		patterns.append(reg[0])

	conversations = get_db().execute("SELECT filename FROM conversations").fetchall()
	for conv in conversations:
		files.append(conv[0])

	for f in files:
		for pattern in patterns:
			patternReg = re.compile(r'{0}'.format(pattern))
			get_db().execute("UPDATE regexes SET lastRound = (SELECT MAX(num) FROM rounds) WHERE regex = ?",
				                [pattern])

			for match in re.finditer(patternReg, open(f,'r').read()):
				try:
					get_db().execute("INSERT INTO alerts (timeFound, timePassed, regex, round) VALUES (datetime('now'),(SELECT time FROM conversations WHERE filename = ?),?,(SELECT MAX(num) FROM rounds))",
					                 [f,pattern])
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

@app.route('/data/conversations/<path:path>')
def send_convo(path):
    return send_from_directory('./data/conversations', path)

@app.route('/hex/<path:path>')
def send_hex(path):
	with open(path,'rb') as f:
		xd = f.read()
	strIO = StringIO.StringIO()
	strIO.write(xd)
	strIO.seek(0)
	return send_file(strIO,attachment_filename="{}.html".format(path),as_attachment=False)

@app.route('/rename', methods=['POST'])
def rename():
	cur = request.form['cur']
	new = request.form['new']
	get_db().execute("UPDATE services SET name=? WHERE name=?", [new,cur])
	get_db().commit()
	return redirect("/services")

@app.route('/services')
def serviceList():
	services = getServices()
	return render_template("pages/services.html", roundNum=getNumRounds(), serviceNum=getNumServices(), alertNum=getNumAlerts(), services=services)

@app.route('/services/<string:service>')
def service(service):
    serviceObj=get_db().execute("SELECT * FROM services WHERE name = (?)", [service]).fetchone()
    conversations=get_db().execute("SELECT * FROM conversations WHERE service = (select id from services where name=(?)) ORDER BY time", [service]).fetchall()
    return render_template("pages/service.html", roundNum=getNumRounds(), serviceNum=getNumServices(), alertNum=getNumAlerts(), service=serviceObj, conversations=conversations, convoLen=len(conversations), graphData=getCharts(service,conversations))

@app.route('/services/<string:service>/<int:roundNum>')
def conversations(service, roundNum):
    serviceObj=get_db().execute("SELECT * FROM services WHERE name = (?)", [service]).fetchone()
    conversations=get_db().execute("SELECT * FROM conversations WHERE service = (select id from services where name=(?)) AND round = (?) ORDER BY time", [service, roundNum]).fetchall()
    print type(conversations)
    for convo in conversations:
    	print convo
    return render_template("pages/service.html", roundNum=getNumRounds(), serviceNum=getNumServices(), alertNum=getNumAlerts(), service=serviceObj, conversations=conversations, convoLen=len(conversations), graphData=getCharts(service,conversations))

@app.route('/rounds')
def roundList():
	rounds = get_db().execute("SELECT r.num, count(*) FROM rounds as r JOIN conversations as c ON r.num = c.round")
	return render_template("pages/rounds.html", roundNum=getNumRounds(), serviceNum=getNumServices(), alertNum=getNumAlerts(), rounds=rounds)

@app.route('/regex/delete/<int:id>')
def delRegex(id):
	get_db().execute("DELETE FROM regexes WHERE id = ?", [id])
	get_db().commit()
	return redirect("/alerts")

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
	return render_template('pages/alerts.html', roundNum=getNumRounds(), serviceNum=getNumServices(), alertNum=getNumAlerts(), alerts=getAlerts(), regexes=getRegexes())

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
	return render_template("pages/index.html", roundNum=getNumRounds(), serviceNum=getNumServices(), alertNum=getNumAlerts())
	
if __name__ == '__main__':
    app.run(debug=DEBUG,host="0.0.0.0",port=5000)
