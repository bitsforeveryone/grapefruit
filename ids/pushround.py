#!/usr/bin/env python

import os
import sqlite3
import xmltodict, json

from flask import g

CURRENT_ROUND = 1
CONVO_DIR="conversations/"
STAGING_DIR="staging/"
services = []

DATABASE = 'db.db'
def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = sqlite3.connect(DATABASE)
    return g.sqlite_db

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
		                (filename, size, time, s_port, d_port, s_ip, d_ip, round, service) VALUES         
		                (?, ?, ?, ?, ?, ?, ?, ?, (SELECT name FROM services WHERE port = (?) OR port = (?) ) )""", 
		                (fname.replace('staging/','conversations'), convo['filesize'], convo['tcpflow']['@startime'], 
		                convo['tcpflow']['@srcport'], convo['tcpflow']['@dstport'], convo['tcpflow']['@src_ipn'],
		                convo['tcpflow']['@dst_ipn'],0,convo['tcpflow']['@dstport'],convo['tcpflow']['@srcport']))
		g.sqlite_db.commit()
