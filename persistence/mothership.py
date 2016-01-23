#!/usr/bin/env python

import select
import socket
import sys
import threading
import random
import time
import copy
import json

host = '127.0.0.1'
staticport = 31341

class Server:
    def __init__(self):
        self.host = '127.0.0.1'
        self.porttimeout = 5
        self.backlog = 5
        self.size = 1024
        self.server = None
        self.rollingthreads = []

    def open_socket(self):
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind((self.host,staticport))
            self.server.listen(5)
        except socket.error, (value,message):
            if self.server:
                self.server.close()
            #print "[!] Could not open static socket: " + message
            sys.exit(1)

    def run(self):
        self.open_socket()
        self.input = [self.server,sys.stdin]
        commands = {"quit": exit, "status": self.status, "porttimeout": self.changePortTimeout}
        running = 1
        while running:
            inputready,outputready,exceptready = select.select(self.input,[],[],1)
            for s in inputready:
                if s == self.server:
                    # handle the server socket
                    c = RollingClient(self.server.accept())
                    c.start()
                    self.rollingthreads.append(c)

                elif s == sys.stdin:
                    # handle standard input
                    keyboard = sys.stdin.readline()
                    res = keyboard.split()
                    if len(res) > 0:
                        if res[0] in commands:
                            commands[res[0]](*res[1:])

        # close all threads
        self.server.close()

        for c in self.rollingthreads:
            c.join()

    def changePortTimeout(self, timeout):
        self.porttimeout = int(timeout)

    def status(self):
        print "---MOTHERSHIP STATUS---"
        print "Static Port: {0}".format(staticport)                      

class RollingClient(threading.Thread):
    def __init__(self,(client,address)):
        threading.Thread.__init__(self)
        self.client = client
        self.address = address
        self.size = 1024
        self.timeout = 15
        self.newport = -1
        #print "[+] New connection from {0}".format(address)
        
        
    def roll(self):
        try:
            self.newport = random.randint(10000,30000)
            data = {"code": "print 'lol'", "newport": self.newport}
            self.client.send(json.dumps(data) + chr(255))
            self.client.close()
            self.newsock = socket.socket()
            self.newsock.settimeout(5)
            self.newsock.bind((host,self.newport))
            self.newsock.listen(5)
        except Exception as e:
            print self.name + ": "+str(e)


    def readuntil(self, s):
        b = ""
        while chr(255) not in b:
            b += s.recv(1)
        return b

    def run(self):
        running = 1
        while(1):
            self.roll()

            try:
                self.client, self.address = self.newsock.accept()
            except Exception as e:
                print e
                break

            data = self.readuntil(self.client)
            data = json.loads(data[:-1])
            print "'{0}' from {1}".format(data, self.address)
            time.sleep(1)
            
            

if __name__ == "__main__":
    s = Server()
    s.run() 