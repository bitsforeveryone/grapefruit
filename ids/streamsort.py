import os

STAGING_DIR="staging/"
ROOT_DIR="conversations/"

if not os.path.exists(STAGING_DIR):
    os.makedirs(STAGING_DIR)

if not os.path.exists(ROOT_DIR):
    os.makedirs(ROOT_DIR)

def splicePCAPs():
	for pcap in os.listdir(STAGING_DIR):
		if pcap.endswith(".pcap"):
			print os.system("tcpflow -o {1} -r {0} -T%t_%A:%a-%B:%b".format(STAGING_DIR+pcap, STAGING_DIR))

def createServiceFolders():
	ports = []
	for f in os.listdir(STAGING_DIR):
		if not f.endswith((".pcap", ".xml", ".txt", ".pcapng")):
			dport = int(f.split(":")[-1])
			if dport not in ports:
				ports.append(dport)
				try:
					os.mkdir(ROOT_DIR+str(dport))
				except:
					print "Omitting existent directory '{0}'".format(dport)

def createSizeFolders():
	for f in os.listdir(ROOT_DIR):
		for i in range(1,6):
			try:
				os.mkdir(ROOT_DIR+f+"/"+str(10**i))
			except:
				print "Omitting existent directory '{0}'".format(10**i)

def sortConversations():
	sizes = []
	for f in os.listdir(STAGING_DIR):
		if not f.endswith((".pcap", ".xml", ".txt")):
			dport = int(f.split(":")[-1])
			size = os.path.getsize(STAGING_DIR+f)
			i = 1
			while (size > 10**i):
				i += 1
			print ROOT_DIR+str(dport)+"/"+str(10**(i-1))+"/"+f
			os.rename(STAGING_DIR+f,ROOT_DIR+str(dport)+"/"+str(10**(i-1))+"/"+f)

splicePCAPs()
createServiceFolders()
createSizeFolders()
sortConversations()