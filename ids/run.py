#!/usr/bin/env python

import json
import sqlite3
import subprocess
import xmltodict
from flask import Flask, render_template, send_from_directory, g

app = Flask(__name__)

CONVO_DIR="conversations/"
STAGING_DIR="staging/"
services = []

DATABASE = 'db.db'
def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = sqlite3.connect(DATABASE)
    return g.sqlite_db

def readReport(filepath):
	doc = {}
	with open(filepath,'r') as fd:
		doc = xmltodict.parse(fd.read())
	return doc['dfxml']['configuration'][1]['fileobject']

def parseReport(filepath):
	doc = {}
	i = 0
	with open(filepath,'r') as fd:
		doc = xmltodict.parse(fd.read())
	doc = doc['dfxml']['configuration'][1]['fileobject']
	for convo in doc:
		print str(i), str(convo['tcpflow'])
		get_db().execute("""INSERT INTO conversations 
			             (time,s_port,d_port,s_ip,d_ip, round, service) 
			             VALUES
			             (?, ?, ?, ?, ?, ?, ?)
			             """, (convo['tcpflow']['@startime'], convo['tcpflow']['@srcport'], convo['tcpflow']['@dstport'], convo['tcpflow']['@src_ipn'], convo['tcpflow']['@dst_ipn'],0,"battleship"))
		g.sqlite_db.commit()
		


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
	res = get_db().execute("SELECT name FROM services").fetchall()
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

    serviceObj=get_db().execute("SELECT * FROM services WHERE name = (?)", [service]).fetchone()
    conversations=get_db().execute("SELECT * FROM conversations WHERE service = (?)", [service]).fetchall()
    return render_template("pages/service.html", service=serviceObj, conversations=conversations)

@app.route('/services/<string:service>/<int:roundNum>')
def conversations(service, roundNum):
    if service not in services:
        return "Service not found.", 404

    service=get_db().execute("SELECT * FROM services WHERE name = (?)", [service]).fetchone()
    roundNum=get_db().execute("SELECT * FROM rounds ORDER BY round ASC LIMIT 1")
    return render_template("pages/conversations.html", round=roundNum, service=service, convoNum=convoNum, graphData=graphData)

@app.route('/debug/report')
def debugReport():
	parseReport("staging/report.xml")
	return str(readReport("staging/report.xml"))

@app.route('/')
@app.route('/index.html')
def index():
	getServices()
	return render_template("pages/index.html", serviceNum=len(services))
	
if __name__ == '__main__':
    app.run(debug=True)
