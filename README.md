# grapefruit

## Usage
Job files must contain two functions:
    runJob(ip) -> runs the job on a given ip, returns the flag as a string if successful or False if unsuccessful
    fakeJob(ip) -> runs a fake job on a given ip.  This should work similarily to runJob and will run at random time intervals

Note: anything printed in the job file will be printed in STDOUT, so avoid that
