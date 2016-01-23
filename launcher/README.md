# launcher.py

### Usage
Job files must contain two functions:
- runJob(ip, log) -> runs the job on a given ip.  log is a function pointer that takes in n args as a string. Returns the flag as a string if successful or False if unsuccessful.
- fakeJob(ip, log) -> runs a fake job on a given ip. log is a function pointer that takes in n args as a string. Returns the flag as a string if successful or False if unsuccessful. This should work similarily to runJob and will run at random time intervals

Note: anything printed in the job file will be printed in STDOUT, so avoid that