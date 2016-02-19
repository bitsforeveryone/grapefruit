# launcher.py

### Usage
Job files must contain two functions:
- runJob(ip, log) -> runs the job on a given ip.  log is a function pointer that takes in n args as a string and prints to a log file. Returns the flag as a string if successful or False if unsuccessful.
- fakeJob(ip, log) -> runs a fake job on a given ip. log is a function pointer that takes in n args as a string and prints to a log file. Doesn't matter what this returns as it will be ignored. This should work similarily to runJob and will run at random time intervals

Note: anything printed in the job file will be printed in STDOUT, so avoid that
