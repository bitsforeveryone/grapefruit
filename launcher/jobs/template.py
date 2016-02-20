def runJob(ip, log):
	# use log.writeLog rather than print
	# you can check this log by either looking in the log file (same directory),
	# or by using the command 'print <job name> [number of lines]' in the launcher
	log.writeLog("hello cruel world", "my ip is", ip)
	return "l00k_@t_th1s_1337_fl@g" # return flag if successful, False otherwise

def fakeJob(ip, log):
	return True # Return anything not False here