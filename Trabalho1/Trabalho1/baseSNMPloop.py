from snimpy.manager import Manager as M
from snimpy.manager import load
from snimpy import mib
import matplotlib.pyplot as plt
import time
import re
import argparse
lastTime = time.time()
def IPfromOctetString(t,s):
	if t==1 or t==3:	#IPv4 global, non-global
		return '.'.join(['%d' % ord(x) for x in s])
	elif t==2 or t==4:	#IPv6 global, non-global
		a=':'.join(['%02X%02X' % (ord(s[i]),ord(s[i+1])) for i in range(0,16,2)])
		return re.sub(':{1,}:','::',re.sub(':0*',':',a))

def main():
	
	mib.path(mib.path()+":/usr/share/mibs/cisco")
	load("SNMPv2-MIB")
	load("IF-MIB")
	load("IP-MIB")
	load("RFC1213-MIB")
	load("CISCO-QUEUE-MIB")
	#Requires MIB RFC-1212 (add to /usr/share/mibs/ietf/)

	parser = argparse.ArgumentParser()
	parser.add_argument('-r', '--router', nargs='?',required=True, help='address of router to monitor')
	parser.add_argument('-s', '--sinterval', type=int, help='sampling interval (seconds)',default=5)
	args=parser.parse_args()
	myInterval = args.sinterval
	print(args)

	
	#Creates SNMP manager for router with address args.router
	m=M(args.router,'private',3, secname='uDDR',authprotocol="MD5", authpassword="authpass",privprotocol="AES", privpassword="privpass")

	print(m.sysDescr)	#Gets sysDescr from SNMPv2-MIB

	print("===")

	print(m.ifDescr.items()) #Lists (order, name) interfaces in ifDescr from IF-MIB

	for i, name in m.ifDescr.items():
		print("Interface order %d: %s" % (i, name))

	print("===")

	print(m.ipAddressIfIndex.items()) #Lists ((adr.type,adr),order) interfaces in ipAddressIfIndex from IP-MIB

	ifWithAddr={};	#Stores (order, first adr.) of all interfaces
	for addr, i in m.ipAddressIfIndex.items():
		if not i in ifWithAddr:
			ifWithAddr.update({i:IPfromOctetString(addr[0],addr[1])})
		print('%s, Interface order: %d, %s'%(IPfromOctetString(addr[0],addr[1]),i,m.ifDescr[i]))

	print(ifWithAddr)

	print("===========================================================")
	f = open("InOutPkts.txt",'w')
	fByte = open("InOutBytes.txt", 'w')
	last_outpackets = [None]*10
	last_inPkts = [None]*10
	last_outByte = [0]*10
	last_inByte = [0]*10
	for i, name in m.ifHCOutUcastPkts.items():
		last_outpackets[i] = name
	for i, name in m.ifHCInUcastPkts.items():
		last_inPkts[i] = name
	for i, name in m.ifHCOutOctets.items():
		last_outByte[i] = name
	for i, name in m.ifHCInOctets.items():
		last_inByte[i] = name
	listInterfaces=[]
	listValues = []
	try:
		while(True):
			listInterfaces=[]
			listValues = []
			printFlag = False
			interval = time.time()
			if((interval - lastTime) >= myInterval):
				global lastTime 
				lastTime = time.time()
				printFlag=True
			if(printFlag == True):
				print("		==Out Packets==")
				f.write("Router : %s	==Out Packets==\n" % args.router)
				for i, name in m.ifHCOutUcastPkts.items():
					print("Interface %d: Packets send in the last interval: %s" % (i,(name - last_outpackets[i])))
					f.write("Interface %d: Packets send in the last interval: %s\n" % (i,(name - last_outpackets[i])));
					listInterfaces = listInterfaces + [int(i)]
					listValues = listValues + [int(name - last_outpackets[i])]
					last_outpackets[i]=name
				plt.plot(listInterfaces,listValues)
				plt.title("Out Packets")
				plt.ylabel("Out Packets")
				plt.xlabel("Interfaces")
				plt.show()
				print("		==In Packets==")
				f.write("Router : %s	==In Packets==\n" % args.router)
				listInterfaces=[]
				listValues = []
				for i, name in m.ifHCInUcastPkts.items():
					print("Interface %d: Packets receive in the last interval: %s" % (i,(name - last_inPkts[i])))
					f.write("Interface %d: Packets receive in the last interval: %s\n" % (i,(name - last_inPkts[i])))
					listInterfaces = listInterfaces + [int(i)]
					listValues = listValues + [int(name - last_inPkts[i])]
					last_inPkts[i]=name
				plt.plot(listInterfaces,listValues)
				plt.title("==In Packets==")
				plt.ylabel("In Packets")
				plt.xlabel("Interfaces")
				plt.show()
				f.write("===============================================\n")
				print("		==Out Bytes==")
				listInterfaces=[]
				listValues = []
				fByte.write("Router : %s	==Out Bytes==\n" % args.router)
				for i, name in m.ifHCOutOctets.items():
					print("Interface %d: Bytes send in the last interval: %s" % (i,(name - last_outByte[i])))
					fByte.write("Interface %d: Bytes send in the last interval: %s\n" % (i,(name - last_outByte[i])))
					listInterfaces = listInterfaces + [int(i)]
					listValues = listValues + [int(name - last_outByte[i])]
					last_outByte[i] = name
				plt.plot(listInterfaces,listValues)
				plt.title("==Out Bytes==")
				plt.ylabel("Out Bytes")
				plt.xlabel("Interfaces")
				plt.show()
				print("		==In Bytes==")
				listInterfaces=[]
				listValues = []
				fByte.write("Router : %s	==In Bytes==\n" % args.router)
				for i, name in m.ifHCInOctets.items():
					print("Interface %d: Bytes receive in the last interval: %s" % (i,(name - last_inByte[i])))
					fByte.write("Interface %d: Bytes receive in the last interval: %s\n" % (i,(name - last_inByte[i])))
					listInterfaces = listInterfaces + [int(i)]
					listValues = listValues + [int(name - last_inByte[i])]
					last_inByte[i] = name	
				plt.plot(listInterfaces,listValues)
				plt.title("==In Bytes==")
				plt.ylabel("In Bytes")
				plt.xlabel("Interfaces")
				plt.show()
				fByte.write("===============================================\n")
	except KeyboardInterrupt:
		f.close()
		exit

if __name__ == "__main__":
	main()
