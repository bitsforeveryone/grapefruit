#!/usr/bin/env python

import sys, threading, imp, os, time, random, json

jobs = {}
logs = {}
log_cache = {}
currentteam = 1 # change this to our team number
number_of_teams = 9 # change this to the number of teams

sys.path.insert(0, './jobs')

def writeLog(name, info):
	try:
		log = logs[name]
		nstring = "[" + time.strftime("%x") + " " + time.strftime("%X") + "]: " + info + "\n"
		log.write(nstring)
		log_cache[name] += nstring
	except:
		pass # only doing this so this will never crash

def addScript(commands):
	if len(commands) != 3:
		print "incorrect usage. see help"
		return False

	name = commands[2]
	location = commands[1]
	if name not in jobs:
		jobs[name] = {"location": location, "log": location + ".log", "enabled": False, "stations": range(number_of_teams), "lastRun": 0, "interval": 5 * 60}
		f = open(jobs[name]["log"], "a+")
		log_cache[name] = f.read()
		f.close()
		logs[name] = open(jobs[name]["log"], "a+")
		jobs[name]["stations"].remove(currentteam)
		print "Added new job " + name + " -> " + location
		print "Job not enabled"
		return True
	else:
		print "job already exists for that name"
		return False

def enableScript(commands):
	if len(commands) != 2:
		print "incorrect usage. see help"
		return False

	name = commands[1]
	if name in jobs:
		jobs[name]["enabled"] = True
		print "Enabled job " + name
		beginJob(name)
		return True
	else:
		print "job does not exist for that name"
		return False

def disableScript(commands):
	if len(commands) != 2:
		print "incorrect usage. see help"
		return False

	name = commands[1]
	if name in jobs:
		jobs[name]["enabled"] = False
		print "Disabled job " + name
		return True
	else:
		print "job does not exist for that name"
		return False

def deleteScript(commands):
	if len(commands) != 2:
		print "incorrect usage. see help"
		return False

	name = commands[1]
	if name in jobs:
		del jobs[name]
		logs[name].close()
		del logs[name]
		print "Deleted job " + name
		return True
	else:
		print "job does not exist for that name"
		return False

def jobinfo(name):
	if name not in jobs:
		print "job does not exist for that name"
		return

	res = name + " [" + ("Enabled" if jobs[name]["enabled"] else "Disabled") + "]\n"
	res += "\tStations: [" + ", ".join(str(x) for x in jobs[name]["stations"]) + "]\n"
	res += "\tRun Interval: " + str(jobs[name]["interval"]) + " seconds"
	return res


def listJobs(commands):
	if len(jobs) == 0:
		print "No current jobs"
		return

	if len(commands) == 2:
		print jobinfo(commands[1])
	else:
		for key in jobs.keys():
			print jobinfo(key)

def changeStations(commands):
	if len(commands) < 2:
		print "incorrect usage. see help"
		return

	name = commands[1]

	if name not in jobs:
		print "job does not exist for that name"
		return

	stations = []

	if len(commands) == 3:
		sta = commands[2].split(",")
		sta = [int(x) for x in sta if int(x) >= 0 and int(x) < number_of_teams and int(x) != currentteam]
		jobs[name]["stations"] = sta
		print "Successfully changed stations for " + name + " to [" + ", ".join(str(x) for x in sta) + "]"

def changeInterval(commands):
	if len(commands) < 3:
		print "incorrect usage. see help"
		return

	name = commands[1]
	interval = int(commands[2]) if commands[2].isdigit() else 0

	if name not in jobs:
		print "job does not exist for that name"
		return

	if interval <= 5:
		print "interval needs to be at least 5 seconds"
		return

	jobs[name]["interval"] = interval
	print "Successfully changed time interval to " + str(interval) + " seconds for job " + name

def help(commands):
	print "Welcome to launch master 9000\n"
	print "Useful commands:"
	print "\th -> help"
	print "\tq -> quit"
	print "\ta -> add a new job"
	print "\t\tUsage: a <job_path> <name>"
	print "\te -> enable a disabled job"
	print "\t\tUsage: e <name>"
	print "\td -> disable a enabled job"
	print "\t\tUsage: d <name>"
	print "\tr -> delete a job"
	print "\t\tUsage: r <name>"
	print "\tl -> list job information"
	print "\t\tUsage: l [name]"
	print "\t\tLists all jobs if name isn't specified"
	print "\ts -> change stations to attack"
	print "\t\tUsage: s <name> [station numbers seperated by commas]"
	print "\ti -> change job interval (in seconds)"
	print "\t\tUsage: i <name> <interval_time>"
	print "\tp -> print last # of lines from job log file"
	print "\t\tUsage: p <name> <number_of_lines>"
	print "\tx -> export jobs to file to import later"
	print "\t\tUsage: x <file_name>"

def quitLauncher(commands):
	for name in logs.keys():
		logs[name].close()
		del logs[name]
	quit()

def postFlag(station, flag, jobName):
	#submit with curl?
	return

def getIpFromStation(station):
	return "133.33.37." + str(station)

class LogObject(object):
	def __init__(self, n):
		self.name = n
	def __call__(self, *p, **k):
		writeLog(self.name, " ".join([str(x) for x in p]))

def launchJob(name, station, real=True):
	try:
		job = jobs[name]
		filepath = job['location']

		mod_name,file_ext = os.path.splitext(os.path.split(filepath)[-1])

		if file_ext.lower() == '.py':
			py_mod = imp.load_source(mod_name, filepath)

		elif file_ext.lower() == '.pyc':
			py_mod = imp.load_compiled(mod_name, filepath)

		if real:
			expected_func = "runJob"
		else:
			expected_func = "fakeJob"

		if hasattr(py_mod, expected_func):
			log = LogObject(name)

			if real:
				flag = getattr(py_mod, expected_func)(getIpFromStation(station), log)
				if flag:
					postFlag(station, flag, name)
					writeLog(name, "Job " + name + " exited successfully on station " + str(station) + " with flag: " + flag)
					return True
				else:
					writeLog(name, "Job " + name + " couldn't find a flag from station " + str(station))
					return False
			else:
				getattr(py_mod, expected_func)(getIpFromStation(station), log)
				writeLog(name, "Job " + name + " ran a fake job on station " + str(station))
		else:
			writeLog(name, "Job " + name + " doesn't have a " + expected_func + " definition")
			return False
	except:
		writeLog(name, "Job " + name + " for station " + str(station) + " crashed")
		return False

def launchThread(name, station, real):
	job = jobs[name]
	t = threading.Thread(target=launchJob, args=(name, station, real))
	t.setDaemon(True)
	t.start()

def beginJob(name, real=True):
	if real:
		writeLog(name, "Beginning job " + name)
	else:
		writeLog(name, "Beginning fake job " + name)

	job = jobs[name]
	if real:
		job["lastRun"] = time.time()
	for station in job['stations']:
		launchThread(name, station, real)

def printLog(commands):
	if len(commands) < 3:
		print "incorrect usage. see help"
		return

	name = commands[1]
	lines = int(commands[2]) if commands[2].isdigit() else 10

	if name not in jobs:
		print "job does not exist for that name"
		return

	if lines <= 0:
		print "needs to be at least 1 line"
		return

	log = log_cache[name]
	job = jobs[name]
	i = 0

	print ">>> PRINTING LAST " + str(lines) + " LINES OF " + job["log"] + " <<<"

	for line in reversed(log.split("\n")):
		if i > lines:
			break
		else:
			if i > 0:
				print line.rstrip()
			i += 1

	print ">>> FINISHED PRINTING FROM " + job["log"] + " <<<"

def exportJobs(commands):
	if len(commands) < 2:
		print "incorrect usage. see help"
		return

	fi = commands[1]

	nf = open(fi, "w")
	nf.write(json.dumps(jobs))
	nf.close()

	print "Successfully exported jobs to " + fi

def loopJobs():
	while True:
		for job in jobs.keys():
			if jobs[job]['enabled']:
				if time.time() - jobs[job]['lastRun'] >= jobs[job]['interval']:
					try:
						beginJob(job)
					except:
						pass
				else:
					if random.randint(0, 10) == 7:
						try:
							beginJob(job, False)
						except:
							pass
		time.sleep(2)

def launcher():
	x = raw_input("Would you like to import a previous jobs file? [y/n]: ")

	if x.lower() == "y":
		fi = raw_input("Enter the file name: ")
		try:
			f = open(fi, "r")
			njobs = json.loads(f.read())
			for key in njobs.keys():
				jobs[key] = njobs[key]
				fi = open(jobs[key]["log"], "a+")
				log_cache[key] = fi.read()
				fi.close()
				logs[key] = open(jobs[key]["log"], "a+")
			f.close()
			print "Successfully imported jobs file"
		except:
			print "Could not import jobs file"
			pass

	looper = threading.Thread(target=loopJobs)
	looper.setDaemon(True)
	looper.start()

	commands = {"help": help, "h" : help, "quit": quitLauncher, "q": quitLauncher, "a": addScript, "e": enableScript, "d": disableScript, "r": deleteScript, "l": listJobs, "s": changeStations, "i": changeInterval, "p": printLog, "x": exportJobs}
	print "\nType 'help' to see usage\n"
	while True:
		res = raw_input("> ")
		res = res.split()
		if len(res) > 0:
			if res[0] in commands:
				commands[res[0]](res)



launcher()
