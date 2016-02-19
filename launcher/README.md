# launcher.py

### Launcher Usage
The launcher framework is a REPL runs job files on certain IP's at specified time intervals.  At random times between this, it runs fake jobs as chaff to confuse any network monitoring.  Job files are basic Python files that contain two function that are called by the launcher on a specific IP (each job should be port/exploit specific).  The launcher can handle many jobs at once, along with submitting flags when these seperate job files are successful.  When launched, type 'help' to see all possible commands.

### Job File Usage
Job files must contain two functions:
- runJob(ip, log) -> runs the job on a given ip.  log is a function pointer that takes in n args as a string and prints to a log file. This function should return the flag as a string if successful or False if unsuccessful.
- fakeJob(ip, log) -> runs a fake job on a given ip. log is a function pointer that takes in n args as a string and prints to a log file. Doesn't matter what this returns as it will be ignored. This should work similarily to runJob and will run at random time intervals

Note: anything printed in the job file will be printed in STDOUT, so avoid that

### Known issues

- It currently doesn't kill threads that don't exit normally
- Pwntools support currently doesn't work (pwntools takes away the stdin repl) without breaking the launcher
