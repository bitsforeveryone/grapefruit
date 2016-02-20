# launcher.py

### Launcher
The launcher framework is a REPL that runs job files on certain IP's at specified time intervals.  At random times between this, it runs fake jobs as chaff to confuse any network monitoring.  Job files are basic Python files that contain two function that are called by the launcher on a specific IP (each job should be port/exploit specific).  The launcher can handle many jobs at once, along with submitting flags when these seperate job files are successful.  When launched, type 'help' to see all possible commands.

*Edit the settings at the top of launcher.py before using in a competition setting*

### Demo Usage
- `python launcher.py` or `./launcher.py` You don't need to import any jobs files
- `add jobs/template.py testjob` Adds new job named 'testjob'
- `stations testjob 1,3,7` Changes the default stations to 3 specific stations
- `interval testjob 15` This job will now run every 15 seconds, with random fake jobs (chaff) running at other times
- `enable testjob` Actually enables the job and starts running it on the time interval against desired stations
- `print testjob 15` Let's see the last 15 lines of the log
- `disable testjob` Let's hide it for a bit before someone catches on
- `export jobsfile.jobs` Let's save our jobs for a later time (you can now import them too)
- `delete testjob` Kills testjob
- `exit` Kills all running jobs then gracefully exits

### Job File Usage
Job files must contain two functions:
- runJob(ip, log) -> runs the job on a given ip.  log is a function pointer that takes in n args as a string and prints to a log file (use log.writeLog() in place of print). This function should return the flag as a string if successful or False if unsuccessful.
- fakeJob(ip, log) -> runs a fake job on a given ip. log is a function pointer that takes in n args as a string and prints to a log file (use log.writeLog() in place of print). Doesn't matter what this returns as it will be ignored. This should work similarily to runJob and will run at random time intervals

Note: anything printed in the job file will be printed in STDOUT, so avoid that