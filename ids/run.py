#!/usr/bin/env python

import json
import sqlite3
import subprocess
import xmltodict
from flask import Flask, render_template, send_from_directory, g, request

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
	fname = ""
	for convo in doc:
		try:
			fname = convo['filename']
		except KeyError:
			pass

		get_db().execute("""INSERT INTO conversations 
			             (filename, time, s_port, d_port, s_ip, d_ip, round, service) 
			             VALUES
			             (?, ?, ?, ?, ?, ?, ?, (SELECT name FROM services WHERE port = (?) OR port = (?) ) )
			             """, (fname.replace('staging/','conversations'), convo['tcpflow']['@startime'], convo['tcpflow']['@srcport'], convo['tcpflow']['@dstport'], convo['tcpflow']['@src_ipn'], convo['tcpflow']['@dst_ipn'],0,convo['tcpflow']['@dstport'],convo['tcpflow']['@srcport']))
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

@app.route('/conversations/<path:path>')
def send_convo(path):
    return send_from_directory('./conversations', path)


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

    sort = request.args.get('sortby') if request.args.get('sortby') else "time"
    print sort
    serviceObj=get_db().execute("SELECT * FROM services WHERE name = (?)", [service]).fetchone()
    conversations=get_db().execute("SELECT * FROM conversations WHERE service = (?) ORDER BY {0}".format(str(sort)), [service]).fetchall()
    print type(conversations)
    for convo in conversations:
    	print convo
    return render_template("pages/service.html", service=serviceObj, conversations=conversations, convoLen=len(conversations))

@app.route('/services/<string:service>/<int:roundNum>')
def conversations(service, roundNum):
    if service not in services:
        return "Service not found.", 404

    sort = request.args.get('sortby') if request.args.get('sortby') else "time"
    print sort
    serviceObj=get_db().execute("SELECT * FROM services WHERE name = (?)", [service]).fetchone()
    conversations=get_db().execute("SELECT * FROM conversations WHERE service = (?) AND round = (?) ORDER BY {0}".format(str(sort)), [service,roundNum]).fetchall()
    print type(conversations)
    for convo in conversations:
    	print convo
    return render_template("pages/service.html", service=serviceObj, conversations=conversations, convoLen=len(conversations))

@app.route('/debug/report')
def debugReport():
	parseReport("conversations/report.xml")
	return str(readReport("conversations/report.xml"))

@app.route('/')
@app.route('/index.html')
def index():
	getServices()
	return render_template("pages/index.html", serviceNum=len(services))
	
if __name__ == '__main__':
    app.run(debug=True)
