#!/usr/bin/env python

import select
import socket
import sys
import threading
import random

class Server:
    def __init__(self):
        self.host = ''
        self.staticport = 31337
        self.rollingport = random.randint(10000,20000)
        self.porttimeout = 60
        self.backlog = 5
        self.size = 1024
        self.server = None
        self.threads = []

    def open_sockets(self):
        try:
            self.staticserver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.staticserver.bind((self.host,self.staticport))
            self.staticserver.listen(5)
        except socket.error, (value,message):
            if self.staticserver:
                self.staticserver.close()
            #print "[!] Could not open static socket: " + message
            sys.exit(1)

        try:
            self.rollingserver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.rollingserver.bind((self.host,self.rollingport))
            self.rollingserver.listen(5)
        except socket.error, (value,message):
            if self.rollingserver:
                self.rollingserver.close()
            #print "[!] Could not open rolling socket: " + message
            sys.exit(1)

    def run(self):
        sys.stdout.write("> ")
        self.open_sockets()
        commands = {"quit": exit, "status": self.status}
        input = [self.staticserver,self.rollingserver,sys.stdin]
        running = 1
        while running:
            
            inputready,outputready,exceptready = select.select(input,[],[])
            for s in inputready:
                if s == self.staticserver:
                    # handle the server socket
                    c = StaticClient(self.staticserver.accept())
                    c.start()
                    self.threads.append(c)

                if s == self.rollingserver:
                    # handle the server socket
                    c = RollingClient(self.rollingserver.accept())
                    c.start()
                    self.threads.append(c)

                elif s == sys.stdin:
                    # handle standard input
                    keyboard = sys.stdin.readline().strip()
                    res = keyboard.split()
                    if len(res) > 0:
                        if res[0] in commands:
                            commands[res[0]](*res[1:])
                    sys.stdout.write("> ")

        # close all threads
        self.staticserver.close()
        self.rollingserver.close()
        for c in self.threads:
            c.join()

    def status(self):
        print "---MOTHERSHIP STATUS---"
        print "Static Port: {0}".format(self.staticport)
        print "Rolling Port: {0}".format(self.rollingport)
        print "Port Timeout: {0}".format(self.porttimeout)

class StaticClient(threading.Thread):
    def __init__(self,(client,address)):
        threading.Thread.__init__(self)
        self.client = client
        self.address = address
        self.size = 1024
        #print "[+] New connection from {0}".format(address)

    def run(self):
        running = 1
        while running:
            pass

class RollingClient(threading.Thread):
    def __init__(self,(client,address)):
        threading.Thread.__init__(self)
        self.client = client
        self.address = address
        self.size = 1024
        #print "[+] New connection from {0}".format(address)

    def run(self):
        running = 1
        while running:
            pass              

if __name__ == "__main__":
    s = Server()
    s.run() 