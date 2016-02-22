def runJob(ip):
	# any stdout in here gets redirected to the log file
	# you can check this log by either looking at the log file (same directory),
	# or by using the command 'print <job name> [number of lines]' in the launcher
	print "hello cruel world", "my ip is", ip

	return "l00k_@t_th1s_1337_fl@g" # return flag if successful, False otherwise

def fakeJob(ip):
	return True # Return anything not False here