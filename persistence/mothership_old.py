#!/usr/bin/env python

import select
import socket
import sys
import threading
import random
import time
import copy

staticport = 31336
rollingport = random.randint(10000,20000)

class Server:
    def __init__(self):
        self.host = '127.0.0.1'
        self.porttimeout = 60
        self.porttimer = threading.Thread(target=self.changePortTimer)
        self.porttimer.start()
        self.backlog = 5
        self.size = 1024
        self.server = None
        self.staticthreads = []
        self.rollingthreads = []

    def open_sockets(self):
        try:
            self.staticserver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.staticserver.bind((self.host,staticport))
            self.staticserver.listen(5)
        except socket.error, (value,message):
            if self.staticserver:
                self.staticserver.close()
            #print "[!] Could not open static socket: " + message
            sys.exit(1)

        try:
            self.rollingserver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.rollingserver.bind((self.host,rollingport))
            self.rollingserver.listen(5)
        except socket.error, (value,message):
            if self.rollingserver:
                self.rollingserver.close()
            #print "[!] Could not open rolling socket: " + message
            sys.exit(1)

    def run(self):
        self.open_sockets()
        self.input = [self.staticserver,self.rollingserver,sys.stdin]
        commands = {"quit": exit, "status": self.status, "porttimeout": self.changePortTimeout}
        running = 1
        while running:
            sys.stdout.write("> ")
            inputready,outputready,exceptready = select.select(self.input,[],[],1)
            for s in inputready:
                if s == self.staticserver:
                    # handle the server socket
                    c = StaticClient(self.staticserver.accept())
                    c.start()
                    self.staticthreads.append(c)

                if s == self.rollingserver:
                    print self.rollingserver
                    # handle the server socket
                    c = RollingClient(self.rollingserver.accept())
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
        self.staticserver.close()
        self.rollingserver.close()
        for c in self.staticthreads:
            c.join()

        for c in self.rollingthreads:
            c.join()

    def changePortTimeout(self, timeout):
        self.porttimeout = int(timeout)

    def status(self):
        print "---MOTHERSHIP STATUS---"
        print "Static Port: {0}".format(staticport)
        print "Rolling Port: {0}".format(rollingport)
        print "Port Timeout: {0}".format(self.porttimeout)

    def changePortTimer(self):
        while (1):
            time.sleep(self.porttimeout)
            rollingport = random.randint(10000,20000)
            self.rollingserver.close()

            newserver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            newserver.bind((self.host,rollingport))
            newserver.listen(5)
            self.rollingserver=copy.copy(newserver)
            self.input[1] = self.rollingserver

            for c in self.rollingthreads:
                try:
                    c.client.send("NEWPORT "+str(rollingport)+"\n")
                except:
                    c.join()



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
            self.client.send("CODE print 'lol'\n")
            self.client.send("NEWPORT "+str(rollingport)+"\n")
            running = 0

class RollingClient(threading.Thread):
    def __init__(self,(client,address)):
        threading.Thread.__init__(self)
        self.client = client
        self.address = address
        self.size = 1024
        #print "[+] New connection from {0}".format(address)

    def run(self):
        running = 1
        try:
            self.client.send("CODE print 'lol'\n")
        except:
            self.client.close()
        while(1):
            pass
            
            

if __name__ == "__main__":
    s = Server()
    s.run() 