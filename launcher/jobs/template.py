def runJob(ip, log):
	log("hello cruel world", "my ip is", ip)
	return "flag" # return flag if successful, False otherwise

def fakeJob(ip, log):
	return True # Return anything not False here