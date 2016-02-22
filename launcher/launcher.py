#!/usr/bin/env python

############### CUSTOMIZATION OPTIONS ###############

currentteam = 8 # change this to your team number.  This number will _never_ have a job run against it
number_of_teams = 12 # change this to the number of teams
default_interval = 5 * 60 # 5 minutes
default_chaff = 10 # Chance of chaff getting sent in any given second.  For example, there is a 1 in 10 chance of chaff getting sent.  Set to zero for no chaff

def getIpFromStation(station):
	# this needs to return an IP for a given station number
	return "10.0.%d.2" % station

def submit(flag, station, job):
	# this is where you'll implement automatic submission
	# this will print to the log
	print 'Submitting flag {%s} from IP %s' % (flag, getIpFromStation(station))

############### DON'T MESS WITH STUFF BELOW THIS LINE (unless you know what you're doing) ###############

import sys, imp, os, time, random, json, urllib, urllib2, multiprocessing, readline, threading, re
from multiprocessing.managers import BaseManager

sys.path.insert(0, './jobs')

class Logger:
	def __init__(self, log):
		self.buffer = ""
		self.log = log

	def write(self, info):
		self.buffer += info
		if self.buffer[-1] == "\n":
			self.log.writeLog(self.buffer)
			self.buffer = ""

	def flush(self):
		pass

class LogClass:
	def init(self, name, log_file):
		self.log_location = log_file
		self.log_cache = ""
		self.name = name

		if os.path.isfile(self.log_location):
			f = open(self.log_location, "r")
			self.log_cache = f.read()
			f.close()

	def writeLog(self, *info):
		try: 
			combine = " ".join([str(x) for x in info])
			if combine[-1] == "\n":
				combine = combine[:-1]
			log_string = "[%s %s]: %s\n" % (time.strftime("%x"), time.strftime("%X"), combine)
			self.log_cache = self.log_cache + log_string
			f = open(self.log_location, "a")
			f.write(log_string)
			f.close()
			return True
		except:
			return False # how do we log if the log crashes?

	def getLines(self, numberOfLines):
		res = ""
		for line in self.log_cache.split("\n")[-numberOfLines-1:-1]:
			res += line.rstrip() + "\n"
		return res[:-1]

class MyManager(BaseManager):
	pass

MyManager.register('Logger', LogClass)
# MyManager.register('PostFlag', PostFlag)

class Job:
	def __init__(self, name, location, imp={}):
		self.name = name
		self.location = location
		self.log_location = location + ".log"
		self.enabled = imp['enabled'] if 'enabled' in imp else False
		self.stations = imp['stations'] if 'stations' in imp else range(1, number_of_teams+1)
		if currentteam in self.stations:
			self.stations.remove(currentteam)
		self.lastRun = 0
		self.interval = imp['interval'] if 'interval' in imp else default_interval
		self.threads = {}

		manager = MyManager()
		manager.start()
		self.logger = manager.Logger()
		#self.poster = manager.PostFlag()
		self.logger.init(self.name, self.log_location)

		print "Created new job %s [%s]" % (self.name, self.location)

		if not self.enabled:
			print "Job not enabled"
		else:
			print "Job enabled"

	def __repr__(self):
		res = "%s [%s]\n" % (self.name, ("Enabled" if self.enabled else "Disabled"))
		res += "\tStations: [%s]\n" % ", ".join(str(x) for x in self.stations)
		res += "\tRun Interval: %d seconds" % self.interval
		return res

	def writeLog(self, *info):
		self.logger.writeLog(*info)

	def postFlag(self, station, flag):
		self.poster.submit(flag, station, self.name, self.logger)

	def enable(self):
		self.enabled = True
		print "Enabled job %s" % self.name
		self.beginJob()
		return True

	def disable(self):
		self.enabled = False
		for i in self.stations:
			self.killThread(i, True, True)
		print "Disabled job %s" % self.name
		return True

	def delete(self):
		try:
			self.enabled = False
			for i in self.stations:
				self.killThread(i, True, True)
			print "Successfully deleted job %s" % self.name
			return True
		except:
			return False

	def changeStations(self, stations):
		oldStations = self.stations
		validStations = range(1, number_of_teams+1)
		if currentteam in validStations:
			validStations.remove(currentteam)
		self.stations = [x for x in stations if x in validStations]

		for station in oldStations:
			if station not in self.stations:
				self.killThread(station, True, True)
		
		print "Successfully changed stations for %s to [%s]" % (self.name, ", ".join(str(x) for x in self.stations))
		return True

	def changeInterval(self, interval):
		if str(interval).isdigit():
			if int(interval) > 0:
				self.interval = interval
				print "Successfully changed run interval to %d" % self.interval
				return True

		print "%s is not a valid interval (number greater than zero)" % str(interval)
		return False

	def beginJob(self, real=True): # If real, runs runJob and otherwise runs fakeJob (chaff)
		if real:
			self.writeLog("Starting job %s" % self.name)
			self.lastRun = time.time()

		for station in self.stations:
			self.spawnThread(station, real)

		return True

	def killThread(self, station, real=False, fake=False):
		if station in self.threads:
			currThread = self.threads[station]
			try:
				if real and "real" in currThread and currThread["real"].is_alive():
					currThread["real"].terminate()
			except:
				pass

			try:
				if fake and "fake" in currThread and currThread["fake"].is_alive():
					currThread["fake"].terminate()
			except:
				pass

			if real and fake:
				del self.threads[station]

			return True
		else:
			return False

	def spawnThread(self, station, real):
		if real:
			self.killThread(station, True)
		else:
			self.killThread(station, False, True)

		if not station in self.threads:
			self.threads[station] = {}

		realLoc = "real" if real else "fake"
		self.threads[station][realLoc] = multiprocessing.Process(target=self.runOnStation, args=(station, real))
		self.threads[station][realLoc].daemon = True
		self.threads[station][realLoc].start()

	def runOnStation(self, station, real):
		try:
			log = Logger(self.logger)
			sys.stdout = log
			sys.stderr = log

			filepath = self.location

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
				if real:
					flag = getattr(py_mod, expected_func)(getIpFromStation(station))
					if flag:
						print "SUCCESS: Job %s exited on station %d with flag: %s" % (self.name, station, flag)
						submit(flag, station, self)
						return True
					else:
						print "FAIL: Job %s couldn't find a flag from station %d" % (self.name, station)
						return False
				else:
					getattr(py_mod, expected_func)(getIpFromStation(station))
					print "Job %s ran a fake job on station %d" % (self.name, station)
					return True
			else:
				print "Job %s doesn't have a %s definition" % (self.name, expected_func)
			return False
		except Exception as e:
			print "Job %s for station %d crashed: %s" % (self.name, station, str(e))
			return False

	def printLog(self, numberOfLines):
		numberOfLines = int(numberOfLines) if str(numberOfLines).isdigit() and int(numberOfLines) > 0 else 10

		print ">>> PRINTING LAST %d LINES OF %s <<<" % (numberOfLines, self.log_location)

		print self.logger.getLines(numberOfLines)

		print ">>> FINISHED PRINTING FROM %s <<<" % self.log_location

	def export(self):
		return {"name": self.name, "location": self.location, "enabled": self.enabled, "interval": self.interval, "stations": self.stations}

class Usage:
	def __init__(self, func, usage, optional=False):
		self.func = func
		self.usage = usage
		self.optional = optional

	def __call__(self, s):
		return self.func(s) # should return tuple (bool worked, return value)

	def __repr__(self):
		return "".join(["<" if not self.optional else "[", self.usage, ">" if not self.optional else "]"])

class Command:
	def __init__(self, name, hel, winner, *usage):
		self.usage = usage
		self.winner = winner
		self.name = name
		self.help = hel

	def __call__(self, *s):
		options = []
		for usage in range(len(self.usage)):
			if usage < len(s):
				(worked, res) = self.usage[usage](s[usage])
				if worked:
					options.append(res)
				else:
					if self.usage[usage].optional:
						break
					else:
						print res
						print self
						return False
			else:
				if self.usage[usage].optional:
					break
				else:
					print self
					return False

		self.winner(*options)

	def __repr__(self):
		return "Usage: " + self.name + " " + " ".join(str(x) for x in self.usage)

class Launcher:
	def __init__(self):
		self.version = "v1.0.0"
		self.jobs = {}
		self.commands = {
			"add": Command("add", "add a new job", self.createJob, Usage(self.checkFileExists, "job file"), Usage(self.checkJobNotExists, "job name")),
			"enable": Command("enable", "begin running job", lambda job: job.enable(), Usage(self.checkJobExists, "job name")),
			"disable": Command("disable", "stop running job and kill any threads it is currently running", lambda job: job.disable(), Usage(self.checkJobExists, "job name")),
			"delete": Command("delete", "stop running job, kill any threads it is running, and remove it from launcher", self.deleteJob, Usage(self.checkJobExists, "job name")),
			"list": Command("list", "list all information on current jobs", self.listJobs, Usage(self.checkJobExists, "job name", True)),
			"stations": Command("stations", "change stations that a job will run on", lambda job, stations: job.changeStations(stations), Usage(self.checkJobExists, "job name"), Usage(self.checkIfInts, "stations separated by commas")),
			"interval": Command("interval", "changes the time interval between running the job", lambda job, interval=default_interval: job.changeInterval(interval), Usage(self.checkJobExists, "job name"), Usage(lambda i: (True, int(i)) if i.isdigit() and int(i) > 0 else (False, "%s is not a valid interval (number greater than zero)" % i), "interval in seconds")),
			"help": Command("help", "show information from all commands", self.commandHelp, Usage(self.commandExists, "command name", True)),
			"quit": Command("quit", "kill all jobs and exit out of launcher", self.quitLauncher),
			"print": Command("print", "print most recent lines from the log file", lambda job, lines=10: job.printLog(lines), Usage(self.checkJobExists, "job name"), Usage(lambda i: (True, int(i)) if i.isdigit() and int(i) > 0 else (False, "%s is not a valid number of lines (number greater than zero)" % i), "number of lines", True)),
			"export": Command("export", "export all jobs to a job file to be imported later", self.exportJobs, Usage(lambda i: (True, str(i)), "export location"))
		}

	def checkJobExists(self, name):
		if name in self.jobs:
			return (True, self.jobs[name])
		else:
			return (False, "No job with name '%s' exists" % name)

	def checkJobNotExists(self, name):
		if name not in self.jobs:
			return (True, name)
		else:
			return (False, "Job with name '%s' already exists" % name)

	def checkFileExists(self, location):
		if os.path.isfile(location):
			return (True, location)
		else:
			return (False, "There is no file at location '%s'" % location)

	def checkIfInts(self, stat):
		nstat = []
		for i in stat.split(","):
			if i.isdigit():
				nstat.append(int(i))
		if len(nstat) > 0:
			return (True, nstat)
		else:
			return (False, "Stations must be integers separated by commas with no spaces")

	def createJob(self, location, name):
		self.jobs[name] = Job(name, location)

	def deleteJob(self, job):
		job.delete()
		del self.jobs[job.name]

	def listJobs(self, job=False):
		if job != False:
			print job
		else:
			if len(self.jobs) > 0:
				for key in self.jobs.keys():
					print self.jobs[key]
			else:
				print "No jobs created yet"

	def commandExists(self, name):
		if name in self.commands:
			return (True, self.commands[name])
		else:
			return (False, "There is no command with that name")

	def commandHelp(self, command=False):
		if command != False:
			print "%s -> %s" % (command.name, command.help)
			print "\t" + str(command)
		else:
			print "Grapefruit Exploit Launcher %s\n" % self.version
			print "All grapefruit commands:\n"
			for c in self.commands.keys():
				print "\t%s -> %s" % (self.commands[c].name, self.commands[c].help)
				print "\t\t" + str(self.commands[c])
			print ""

	def quitLauncher(self):
		for key in self.jobs.keys():
			self.jobs[key].delete()
		quit()

	def exportJobs(self, location):
		njobs = {}
		try:
			for key in self.jobs.keys():
				njobs[key] = self.jobs[key].export()

			nf = open(location, "w")
			nf.write(json.dumps(njobs))
			nf.close()

			print "Successfully exported jobs to %s" % location
			return True
		except:
			print "Failed to export jobs to %s" % location
			return False

	def loopJobs(self):
		while True:
			for job in self.jobs.keys():
				if self.jobs[job].enabled:
					if time.time() - self.jobs[job].lastRun >= self.jobs[job].interval:
						try:
							self.jobs[job].beginJob()
						except:
							self.jobs[job].writeLog("There was an error running this job")
					else:
						if default_chaff > 0 and random.randint(0, default_chaff) == default_chaff:
							try:
								self.jobs[job].beginJob(False)
							except:
								pass # Don't care if this fails; it's just chaff
			time.sleep(1)

	def start(self):
		x = raw_input("Would you like to import a previous jobs file? [y/n]: ")

		if x.lower() == "y" or x.lower() == "yes":
			fi = raw_input("Enter the file name: ")
			try:
				f = open(fi.strip(), "r")
				njobs = json.loads(f.read())
				f.close()

				print "Attempting to import jobs file\n"

				for key in njobs.keys():
					self.jobs[key] = Job(njobs[key]["name"], njobs[key]["location"], njobs[key])

				print "\nSuccessfully imported jobs file"
			except:
				print "Could not import jobs file"

		looper = threading.Thread(target=self.loopJobs)
		looper.setDaemon(True)
		looper.start()

		comp = Completer(self.commands.keys())
		# we want to treat '/' as part of a word, so override the delimiters
		readline.set_completer_delims(' \t\n;')
		readline.parse_and_bind("tab: complete")
		readline.set_completer(comp.complete)

		print "\nType 'help' to for usage\n"
		while True:
			res = raw_input("> ")
			if len(res) > 0:
				res = res.rstrip().split(" ")
				if res[0] in self.commands:
					self.commands[res[0]](*res[1:])
				else:
					print "Not a valid command. Type 'help' for usage"

# http://stackoverflow.com/questions/5637124/tab-completion-in-pythons-raw-input

class Completer(object):

	def __init__(self, commands):
		self.commands = commands
		self.re_space = re.compile('.*\s+$', re.M)

	def _listdir(self, root):
		res = []
		for name in os.listdir(root):
			path = os.path.join(root, name)
			if os.path.isdir(path):
				name += os.sep
			res.append(name)
		return res

	def _complete_path(self, path=None):
		if not path:
			return self._listdir('.')
		dirname, rest = os.path.split(path)
		tmp = dirname if dirname else '.'
		res = [os.path.join(dirname, p) for p in self._listdir(tmp) if p.startswith(rest)]
		# more than one match, or single match which does not exist (typo)
		if len(res) > 1 or not os.path.exists(path):
			return res
		# resolved to a single directory, so return list of files below it
		if os.path.isdir(path):
			return [os.path.join(path, p) for p in self._listdir(path)]
		# exact file match terminates this completion
		return [path + ' ']

	def complete_extra(self, args):
		if not args:
			return self._complete_path('.')
		# treat the last arg as a path and complete it
		return self._complete_path(args[-1])

	def complete(self, text, state):
		buffer = readline.get_line_buffer()
		line = readline.get_line_buffer().split()

		# show all commands
		if not line:
			return [c + ' ' for c in self.commands][state]
		# account for last argument ending in a space
		if self.re_space.match(buffer):
			line.append('')
		# resolve command to the implementation function
		cmd = line[0].strip()
		if cmd in self.commands:
			args = line[1:]
			if args:
				return (self.complete_extra(args) + [None])[state]
			return [cmd + ' '][state]
		results = [c + ' ' for c in self.commands if c.startswith(cmd)] + [None]
		return results[state]

if __name__ == "__main__":
	Launcher().start()